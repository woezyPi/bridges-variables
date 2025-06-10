# Croisement des cartes de tous les ponts de France

Ce projet vise à centraliser et visualiser les ponts de France en les croisant avec les couches administratives (régions, départements et communes) afin d’obtenir une cartographie interactive et dynamique. Le but est d’enrichir cette base avec des variables affectant la santé des ouvrages (âge, type de structure, trafic, environnement) pour identifier les ponts à risque et prioriser les interventions.

## Objectifs principaux
✅ Intégrer et fusionner les données des ponts avec les limites administratives (GeoJSON).  
✅ Visualiser et filtrer les ponts par région, département et commune.  
✅ Associer des variables clés affectant la santé des ponts (trafic, environnement, météo, etc.).  
✅ Créer un outil d’aide à la décision pour la maintenance et la gestion des infrastructures.

## Technologies utilisées
- Python (GeoPandas, Folium)
- Docker (pour la reproductibilité)
- Données OpenStreetMap et Copernicus Sentinel-1 (pour l’analyse environnementale)
- Données administratives (France GeoJSON)

## Public cible
Ce projet est destiné aux ingénieurs, collectivités territoriales et chercheurs travaillant sur la gestion et l’entretien des infrastructures.

##DB
https://land.copernicus.eu/en/products/corine-land-cover/clc2018 (informations sur la couverture et l’usage des sols à travers l’Europe. C’est un inventaire paneuropéen qui cartographie les surfaces terrestres selon différents types d’occupation du sol (forêts, zones urbaines, zones agricoles, etc.) 

## À venir
- Ajout d’analyses prédictives sur la santé des ponts.  
- Création de dashboards interactifs pour le suivi des ponts.  
- Intégration d’alertes automatisées en fonction des données environnementales.

---
