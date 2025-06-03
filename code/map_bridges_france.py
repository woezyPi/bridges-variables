import geopandas as gpd
import folium
import pandas as pd
import json
from shapely.geometry import Point
import os

# Step 1: Load the commune boundaries from france-geojson
communes_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson"
communes_gdf = gpd.read_file(communes_url)

# Step 2: Load the bridge data
def load_bridge_data(file_path, chunk_size=100000):
    bridges = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Vérifier si le JSON a une propriété "elements"
            if 'elements' in data and isinstance(data['elements'], list):
                print(f"Nombre d'objets dans 'elements' : {len(data['elements'])}")
                for i, feature in enumerate(data['elements']):
                    if feature.get('type') == 'way' and 'geometry' in feature:
                        for coord in feature['geometry']:
                            bridges.append({
                                'lat': coord['lat'],
                                'lon': coord['lon'],
                                'name': feature['tags'].get('name', 'Unknown'),
                                'highway': feature['tags'].get('highway', feature['tags'].get('railway', 'Unknown')),
                                'bridge': feature['tags'].get('bridge', 'yes')
                            })
                    else:
                        print(f"Objet {i} ignoré : type={feature.get('type', 'inconnu')}, geometry={'présent' if 'geometry' in feature else 'absent'}")
            else:
                print("Erreur : Le JSON ne contient pas de propriété 'elements' ou ce n'est pas une liste.")
                return pd.DataFrame()
    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} n'a pas été trouvé. Vérifiez le chemin ou créez le fichier.")
        return pd.DataFrame()
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier {file_path} n'est pas un JSON valide.")
        return pd.DataFrame()
    print(f"Nombre de ponts chargés : {len(bridges)}")
    return pd.DataFrame(bridges)

# Load bridge data
bridge_df = load_bridge_data('bridges.json')

# Vérifier si le DataFrame est vide
if bridge_df.empty:
    print("Aucune donnée de pont chargée. Arrêt du script.")
    exit()

# Convert bridge data to GeoDataFrame
geometry = [Point(xy) for xy in zip(bridge_df['lon'], bridge_df['lat'])]
bridge_gdf = gpd.GeoDataFrame(bridge_df, geometry=geometry, crs="EPSG:4326")

# Step 3: Spatial join to match bridges with communes
communes_gdf = communes_gdf.to_crs(epsg=4326)
bridge_gdf = bridge_gdf.to_crs(epsg=4326)
joined_gdf = gpd.sjoin(bridge_gdf, communes_gdf, how="left", predicate="within")

# Step 4: Create an interactive map with Folium
m = folium.Map(location=[46.6031, 1.8883], zoom_start=6, tiles="cartodbpositron")
folium.GeoJson(
    communes_gdf,
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.1
    }
).add_to(m)

# Add bridge points
for idx, row in joined_gdf.iterrows():
    if pd.notnull(row.geometry):
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=folium.Popup(
                f"Bridge: {row['name']}<br>Type: {row['highway']}<br>Commune: {row.get('nom', 'Unknown')}",
                max_width=200
            )
        ).add_to(m)

# Save the map to an HTML file
m.save('france_bridges_map.html')
print("La carte a été générée et sauvegardée sous 'france_bridges_map.html'")