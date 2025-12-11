# 🎵 Music Graph Recommendation System

Système de recommandation musicale hybride utilisant **Neo4j** (graph database) et **MongoDB** (document store).

**Projet académique NoSQL - 2024**

---

## 📊 Statut du projet

- ✅ **Jour 1** : Infrastructure complète (Docker + Neo4j + MongoDB)
- ✅ **Jour 2** : Dataset + Preprocessing + Import bases de données
- ⏳ **Jour 3** : API REST + Algorithmes de recommandation
- ⏳ **Jour 4** : Dashboard Streamlit + Documentation finale

**Progression : 50% ✅**

---

## 🎯 Objectifs

Créer un système de recommandation musicale hybride exploitant :
- **Neo4j** : Relations entre tracks, artistes, genres (graph-based recommendations)
- **MongoDB** : Audio features Spotify (content-based recommendations)

### Fonctionnalités
- ✅ Recommandations par genre et artiste similaire
- ✅ Recommandations par audio features (danceability, energy, valence)
- ✅ Filtres temporels (par décennie/année)
- ⏳ Recherche multicritères
- ⏳ Playlists dynamiques
- ⏳ Dashboard interactif

---

## 📊 Dataset

**Source** : Spotify Dataset (Kaggle)

| Métrique | Valeur |
|----------|--------|
| **Tracks** | 15,150 |
| **Artistes** | 3,083 |
| **Genres** | 19 |
| **Période** | 1899-2024 (125 ans) |
| **Audio Features** | 12 (Spotify API) |

### Genres disponibles
Pop, Rock, Metal, Jazz, Country, R&B, Rap, EDM, Punk, Alternative Rock, et 9 autres.

### Audio Features
- **Mood** : valence, energy, danceability
- **Caractéristiques** : tempo, loudness, acousticness, instrumentalness
- **Autres** : speechiness, liveness, key, mode, time_signature

---

## 🛠️ Stack Technique

| Technologie | Version | Usage |
|-------------|---------|-------|
| **Neo4j** | 5.15 Community | Graph database + APOC + GDS |
| **MongoDB** | 7.0 | Document store |
| **Docker** | Latest | Containerisation |
| **Python** | 3.12+ | Backend + Scripts |
| **FastAPI** | 0.104+ | REST API _(à venir)_ |
| **Streamlit** | 1.29+ | Dashboard _(à venir)_ |

### Librairies Python principales
```
pandas, numpy          # Data processing
neo4j, pymongo         # Database drivers
fastapi, uvicorn       # API REST
streamlit, plotly      # Visualisations
```

---

## 🚀 Installation et Démarrage

### Prérequis
- Docker & Docker Compose
- Python 3.12+
- Git

### 1. Cloner le projet
```bash
git clone [URL_DU_REPO]
cd music-graph-neo4j
```

### 2. Démarrer l'infrastructure
```bash
# Lancer Neo4j + MongoDB
docker-compose up -d

# Vérifier que les containers tournent
docker ps
```

### 3. Setup Python
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Preprocessing et Import
```bash
# Preprocessing du dataset
python preprocess_music_data.py

# Import dans Neo4j
python neo4j_import.py

# Import dans MongoDB
python mongodb_import.py
```

### 5. Accéder aux interfaces

**Neo4j Browser**
```
URL  : http://localhost:7474
User : neo4j
Pass : password123
```

**MongoDB Compass** _(optionnel)_
```
URI : mongodb://localhost:27017
Database : music_recommendation
Collection : audio_features
```

---

## 📁 Structure du projet

```
music-graph-neo4j/
│
├── data/
│   ├── raw/                        # Dataset brut
│   │   └── dataset.csv
│   └── processed/
│       ├── neo4j/                  # CSV pour Neo4j
│       │   ├── tracks.csv
│       │   ├── artists.csv
│       │   ├── genres.csv
│       │   ├── performed_by.csv
│       │   ├── has_genre.csv
│       │   └── performs.csv
│       ├── mongodb/                # JSON/CSV pour MongoDB
│       │   ├── audio_features.json
│       │   └── audio_features.csv
│       └── preprocessing_metadata.json
│
├── scripts/                        # Scripts d'import
│   ├── preprocess_music_data.py
│   ├── neo4j_import.py
│   ├── mongodb_import.py
│   └── verify_mongodb_years.py
│
├── notebooks/                      # Jupyter notebooks
│   └── dataset_exploration.ipynb
│
├── api/                           # REST API (à venir)
│   ├── main.py
│   ├── routes/
│   └── services/
│
├── frontend/                      # Dashboard (à venir)
│   └── app.py
│
├── tests/                         # Tests unitaires
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── NEO4J_QUERIES.md
│   └── MONGODB_QUERIES.md
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🗄️ Architecture des Données

### Neo4j - Modèle de Graphe

```
Nodes:
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Track  │     │ Artist  │     │  Genre  │
├─────────┤     ├─────────┤     ├─────────┤
│ id      │     │ id      │     │ id      │
│ name    │     │ name    │     │ name    │
│ year    │     │ ...     │     └─────────┘
│ ...     │     └─────────┘
└─────────┘

Relationships:
(Track)-[:PERFORMED_BY]->(Artist)
(Track)-[:HAS_GENRE]->(Genre)
(Artist)-[:PERFORMS]->(Genre)
```

**Statistiques Neo4j** :
- 18,062 nodes (14,960 tracks + 3,083 artists + 19 genres)
- 33,503 relationships

### MongoDB - Schéma Document

```json
{
  "_id": "trk_891ae000cab4",
  "danceability": 0.616,
  "energy": 0.511,
  "valence": 0.604,
  "tempo": 132.015,
  "acousticness": 0.0384,
  "instrumentalness": 0.0,
  "liveness": 0.15,
  "speechiness": 0.045,
  "loudness": -7.5,
  "key": 5,
  "mode": 1,
  "time_signature": 4,
  "popularity": 67,
  "duration": 210000,
  "year": 2015
}
```

**Statistiques MongoDB** :
- 14,960 documents
- 5 indexes (popularity, year, danceability, energy, valence)

---

## 🔍 Exemples de Requêtes

### Neo4j (Cypher)

**Top 10 artistes les plus prolifiques**
```cypher
MATCH (a:Artist)<-[:PERFORMED_BY]-(t:Track)
RETURN a.name AS Artist, count(t) AS TrackCount
ORDER BY TrackCount DESC
LIMIT 10
```

**Recommandations par genre**
```cypher
MATCH (seed:Track {name: "Your Song"})-[:HAS_GENRE]->(g:Genre)
MATCH (similar:Track)-[:HAS_GENRE]->(g)
WHERE seed <> similar
RETURN similar.name AS Track, 
       similar.popularity AS Popularity
ORDER BY Popularity DESC
LIMIT 10
```

**Graphe d'un artiste**
```cypher
MATCH path = (a:Artist {name: "Elton John"})-[*1..2]-(connected)
RETURN path
LIMIT 100
```

### MongoDB (JavaScript)

**Tracks avec audio features similaires**
```javascript
db.audio_features.find({
  danceability: { $gte: 0.7, $lte: 0.9 },
  energy: { $gte: 0.6, $lte: 0.8 },
  valence: { $gt: 0.5 }
}).sort({ popularity: -1 }).limit(10)
```

**Distribution temporelle**
```javascript
db.audio_features.aggregate([
  { 
    $group: {
      _id: { $multiply: [{ $floor: { $divide: ["$year", 10] }}, 10] },
      count: { $sum: 1 },
      avgPopularity: { $avg: "$popularity" }
    }
  },
  { $sort: { _id: 1 }}
])
```

---

## 📈 Algorithmes de Recommandation

### 1. Graph-Based (Neo4j)
- **Recommandations par genre** : Tracks partageant le(s) même(s) genre(s)
- **Artistes similaires** : Basé sur les genres communs
- **Collaborative filtering** : "Fans also listened to..."

### 2. Content-Based (MongoDB)
- **Audio features similarity** : Distance euclidienne sur danceability, energy, valence
- **Mood-based** : Filtres sur caractéristiques (party, chill, workout)
- **Temporal filtering** : Par décennie/année

### 3. Hybride (Neo4j + MongoDB)
- Combinaison des deux approches avec scoring pondéré
- Exemple : Genre (50%) + Audio Features (30%) + Popularité (20%)

---

## 🎛️ API REST _(à venir)_

### Endpoints prévus

```
GET  /api/tracks/search?q={query}
GET  /api/tracks/{id}
GET  /api/tracks/{id}/recommendations
GET  /api/artists/{id}
GET  /api/genres
POST /api/recommendations/hybrid
```

---

## 📊 Dashboard _(à venir)_

### Fonctionnalités prévues
- 🔍 Recherche de tracks
- 🎵 Recommandations interactives
- 📊 Visualisations (graphes Neo4j, distributions)
- 🎚️ Filtres dynamiques (genre, année, mood)
- 📈 Statistiques en temps réel

---

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests d'intégration
pytest tests/integration/

# Coverage
pytest --cov=api tests/
```

---

## 📚 Documentation Complète

- **[Architecture Détaillée](docs/ARCHITECTURE.md)** : Schémas et design decisions
- **[Requêtes Neo4j](docs/NEO4J_QUERIES.md)** : Collection complète de requêtes Cypher
- **[Requêtes MongoDB](docs/MONGODB_QUERIES.md)** : Agrégations et filtres
- **[API Documentation](docs/API.md)** : Endpoints et exemples

---

## 🔧 Maintenance

### Commandes utiles

```bash
# Redémarrer les bases de données
docker-compose restart

# Voir les logs
docker logs music-neo4j
docker logs music-mongodb

# Arrêter tout
docker-compose down

# Nettoyer les volumes (⚠️ perte de données)
docker-compose down -v
```

### Backup

```bash
# Neo4j backup
docker exec music-neo4j neo4j-admin database dump neo4j --to-path=/backups

# MongoDB backup
docker exec music-mongodb mongodump --out=/backups
```

---

## 🐛 Troubleshooting

**Neo4j ne démarre pas ?**
```bash
docker logs music-neo4j
# Attendre 20-30s après docker-compose up
```

**Erreur de connexion MongoDB ?**
```bash
docker ps  # Vérifier que music-mongodb tourne
docker restart music-mongodb
```

**Import Neo4j échoue ?**
- Vérifier que le preprocessing a bien été exécuté
- Vérifier les chemins des fichiers CSV
- S'assurer que Neo4j est démarré et accessible

---

## 🤝 Contribution

Ce projet est académique. Pour toute suggestion :
1. Ouvrir une issue
2. Proposer une pull request
3. Contacter l'auteur

---

## 📝 Licence

Projet académique - 2024

---

## 👤 Auteur

**Eya**
**Ahmed**   
Projet NoSQL - Système de Recommandation Musicale  
Décembre 2024

---

## 🙏 Remerciements

- Dataset : Spotify via Kaggle
- Technologies : Neo4j, MongoDB, Docker
- Communauté NoSQL

---

## 📊 Statistiques du Projet

| Métrique | Valeur |
|----------|--------|
| Lines of Code | ~2,000+ |
| Fichiers Python | 8 |
| Scripts SQL/Cypher | 20+ |
| Containers Docker | 2 |
| Nodes Neo4j | 18,062 |
| Documents MongoDB | 14,960 |
| Temps de développement | 4 jours |

---

**🚀 Projet en cours - Dernière mise à jour : Décembre 2024**