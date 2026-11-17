# Music Graph

Système de recommandation musicale hybride qui combine une base orientée graphe (Neo4j) et une base orientée documents (MongoDB).

Neo4j modélise les relations entre morceaux, artistes et genres pour les recommandations et l'exploration du réseau d'artistes. MongoDB stocke les caractéristiques audio des morceaux (énergie, tempo, valence, etc.) pour les analyses statistiques et la recherche de morceaux similaires.

## Architecture

```
Streamlit (frontend)  ->  FastAPI (backend)  ->  Neo4j    : graphe Track / Artist / Genre
                                             ->  MongoDB  : caractéristiques audio
```

| Composant | Technologies |
|---|---|
| Bases de données | Neo4j 5.15 (APOC, Graph Data Science), MongoDB 7 |
| API | Python, FastAPI, Uvicorn, Pydantic |
| Interface | Streamlit, Plotly, streamlit-agraph |
| Préparation des données | Pandas, NumPy, Jupyter |

### Modèle de graphe

- Nœuds : `Track`, `Artist`, `Genre`
- Relations : `PERFORMED_BY` (morceau vers artiste), `HAS_GENRE` (morceau vers genre), `PERFORMS` (artiste vers genre)

## Fonctionnalités

- Exploration du graphe : recherche d'artistes, réseau d'un artiste, top genres et top artistes
- Recommandations à partir d'une sélection de genres et d'artistes
- Analyses audio : distributions, profils par genre, clusters d'humeur, corrélations, évolution dans le temps
- Recherche de morceaux similaires à partir de leurs caractéristiques audio

## Structure du dépôt

```
backend/     API FastAPI (routes Neo4j et MongoDB, services d'accès aux bases)
frontend/    Tableau de bord Streamlit (exploration, analyses, recommandations)
scripts/     Prétraitement du jeu de données et import dans Neo4j et MongoDB
data/        Données prétraitées prêtes à l'import
notebooks/   Exploration initiale du jeu de données
docs/        Notes de mise en place de l'infrastructure
```

## Installation

### Prérequis

- Docker et Docker Compose
- Python 3.10 ou plus récent

### 1. Lancer les bases de données

```bash
docker compose up -d
```

### 2. Installer les dépendances Python

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

### 3. Importer les données

Les fichiers prétraités sont fournis dans `data/processed/`. Pour les régénérer à partir du jeu de données brut, placer `ClassicHit.csv` dans `data/raw/` puis lancer `python scripts/preprocess_music_data.py`.

```bash
python scripts/neo4j_import.py
python scripts/mongodb_import.py
```

### 4. Lancer l'API et l'interface

```bash
cd backend
uvicorn main:app --reload --port 8000
```

```bash
cd frontend
streamlit run app.py --server.port 8501
```

| Service | Adresse |
|---|---|
| Tableau de bord | http://localhost:8501 |
| Documentation de l'API | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 (`neo4j` / `password123`, configuration locale uniquement) |

## Limites connues

Les profils audio par genre reposent sur un champ `genres` qui n'est présent que dans Neo4j. Si ce champ est absent des documents MongoDB, les graphiques correspondants restent vides ; l'API renvoie alors une liste vide au lieu d'une erreur.
