# 🎵 Music Graph Recommendation System

Système de recommandation musicale utilisant Neo4j (graph database) et MongoDB.

**Projet académique NoSQL - 2024**

---

## 📊 Statut du projet

- ✅ **Jour 1** : Infrastructure complète (Neo4j + MongoDB)
- ⏳ **Jour 2** : Dataset + Enrichissement Last.fm
- ⏳ **Jour 3** : Algorithmes + Analytics
- ⏳ **Jour 4** : Dashboard + Finalisation

---

## 🛠️ Stack Technique

- **Neo4j 5.15** : Graph database
- **MongoDB 7** : Document store
- **Docker** : Containerisation
- **Python 3.12** : Scripts et API
- **Last.fm API** : Enrichissement données

---

## 🚀 Démarrage rapide
```bash
# Cloner le projet
git clone [URL]
cd music-graph-neo4j

# Démarrer l'infrastructure
docker-compose up -d

# Accéder à Neo4j Browser
http://localhost:7474
User: neo4j / Pass: password123

# Accéder à MongoDB
MongoDB Compass: mongodb://localhost:27017
```

---

## 📁 Structure du projet
```
music-graph-neo4j/
├── data/              # Datasets
├── enrichment/        # Scripts enrichissement
├── neo4j_queries/     # Requêtes Cypher
├── api/               # FastAPI
├── frontend/          # Streamlit dashboard
├── tests/             # Tests
├── docs/              # Documentation
└── docker-compose.yml
```

---

## 📚 Documentation

- [Jour 1 - Infrastructure](docs/DAY1_REPORT.md)
- [Architecture](docs/ARCHITECTURE.md) _(à venir)_
- [Requêtes Cypher](docs/CYPHER_QUERIES.md) _(à venir)_

---

## 👤 Auteur

**Eya**  
Projet NoSQL - 2024