import geopandas as gpd
import folium
import pandas as pd
import json
from shapely.geometry import Point
import os
from folium.plugins import MarkerCluster

# Step 1: Load the department boundaries from france-geojson
departments_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
departments_gdf = gpd.read_file(departments_url)

# Step 2: Load the department extremes CSV
dept_extremes_df = pd.read_csv('data/points-extremes-des-departements-metropolitains-de-france.csv')

# Step 3: Load the bridge data
def load_bridge_data(file_path):
    bridges = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        if 'elements' in data and isinstance(data['elements'], list):
            print(f"Nombre d'objets dans 'elements' : {len(data['elements'])}")
            for idx, feature in enumerate(data['elements']):
                if feature.get('type').lower() == 'way' and 'geometry' in feature:
                    for coord in feature['geometry']:
                        bridges.append({
                            'lat': coord['lat'],
                            'lon': coord['lon'],
                            'name': feature['tags'].get('name', 'Unknown'),
                            'bridge_type': feature['tags'].get('highway', feature['tags'].get('railway', 'Unknown')),
                            'bridge': feature['tags'].get('bridge', 'yes')
                        })
                else:
                    print(f"Objet {idx} ignoré : type={feature.get('type', 'inconnu')}, geometry={'présent' if 'geometry' in feature else 'absent'}")
        else:
            print("Erreur : Le JSON ne contient pas de propriété 'elements' ou ce n'est pas une liste.")
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} n'a pas été trouvé.")
        return pd.DataFrame()
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {file_path} n'est pas un JSON valide.")
        return pd.DataFrame()
    print(f"Nombre de points de ponts chargés : {len(bridges)}")
    return pd.DataFrame(bridges)

# Load bridge data
bridge_df = load_bridge_data('data/bridges.json')

if bridge_df.empty:
    print("Aucune donnée de pont chargée. Arrêt du script.")
    exit()

# Step 4: Convert bridge data to GeoDataFrame
geometry = [Point(xy) for xy in zip(bridge_df['lon'], bridge_df['lat'])]
bridge_gdf = gpd.GeoDataFrame(bridge_df, geometry=geometry, crs="EPSG:4326")

# Step 5: Spatial join with departments
departments_gdf = departments_gdf.to_crs(epsg=4326)
bridge_gdf = bridge_gdf.to_crs(epsg=4326)
joined_gdf = gpd.sjoin(bridge_gdf, departments_gdf, how="left", predicate="within")

# Extract department name and code
joined_gdf['dept_name'] = joined_gdf['nom'].fillna('Unknown')
joined_gdf['dept_code'] = joined_gdf['code'].fillna('Unknown')

# Step 6: Validate with department extremes from CSV
def check_dept_extremes(lat, lon, extremes_df):
    for _, row in extremes_df.iterrows():
        dept = str(row['Departement'])
        if (row['Latitude la plus au sud'] <= lat <= row['Latitude la plus au nord'] and
            row['Longitude la plus à l’ouest'] <= lon <= row['Longitude la plus à l’est']):
            return dept
    return 'Unknown'

joined_gdf['dept_code_csv'] = joined_gdf.apply(
    lambda row: check_dept_extremes(row['lat'], row['lon'], dept_extremes_df), axis=1)

# Step 7: Save to CSV
output_df = joined_gdf[['lat', 'lon', 'name', 'bridge_type', 'bridge', 'dept_name', 'dept_code', 'dept_code_csv']]
output_df.to_csv('bridges_with_departments.csv', index=False)
print("Fichier CSV 'bridges_with_departments.csv' généré avec les coordonnées et départements.")

# Step 8: Create an interactive map with Folium
m = folium.Map(location=[46.6031, 1.8883], zoom_start=6, tiles="cartodbpositron")

# Add department boundaries
folium.GeoJson(
    departments_gdf,
    style_function=lambda x: {'fillColor': 'transparent', 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.1},
    name="Départements"
).add_to(m)

# Assign a unique color to each department
unique_depts = joined_gdf['dept_name'].unique()
colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'darkred', 'darkgreen', 'cadetblue', 'pink']
dept_colors = {dept: colors[i % len(colors)] for i, dept in enumerate(unique_depts)}

# Add bridge points with clustering
marker_cluster = MarkerCluster().add_to(m)
for idx, row in joined_gdf.iterrows():
    if pd.notnull(row.geometry):
        dept = row['dept_name']
        color = dept_colors.get(dept, 'gray')
        popup_text = (f"Bridge: {row['name']}<br>Type: {row['bridge_type']}<br>"
                      f"Department: {dept} ({row['dept_code']})<br>"
                      f"CSV Dept: {row['dept_code_csv']}")
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=200)
        ).add_to(marker_cluster)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
m.save('france_bridges_map_with_departments.html')
print("La carte a été générée et sauvegardée sous 'france_bridges_map_with_departments.html'")