# Music Graph Recommendation System

A hybrid music recommendation system combining Neo4j (Graph Database) and MongoDB (Document Database) to provide personalized track recommendations and analytics.

---

## 🚀 How to Run & Fixes Applied

### ✅ Fixes Applied
1.  **Backend (`backend/services/mongodb_service.py`)**:
    -   Modified `get_genre_audio_profiles` to be robust against missing data. It now wraps the aggregation in a try/except block and handles cases where the `genres` field might be missing in MongoDB documents (returning an empty list instead of crashing).
    -   Wrapped `get_stats` in error handling to prevent the dashboard from breaking if MongoDB is down.
2.  **Frontend (`frontend/utils/api_client.py`)**:
    -   Improved error messages. If the connection is refused, it now explicitly suggests ensuring the backend is running on `http://localhost:8000`.

## 🏃 How to Run the Project

### 1. Prerequisites
Ensure you have Docker running and Python installed.

### 2. Start Databases (Docker)
Open a terminal in the project root (`music-graph-neo4j`) and run:
```bash
docker-compose up -d
```
Verify they are running:
```bash
docker ps
```

### 3. Setup Python Environment
If you haven't already:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. **CRITICAL: Import Data**
Your database is currently empty, which is why you see errors like "Failed to load evolution data". Run these scripts in order:

```bash
# 1. Prepare data
python scripts/preprocess_music_data.py

# 2. Import into Neo4j
python scripts/neo4j_import.py

# 3. Import into MongoDB
python scripts/mongodb_import.py
```

**⚠️ TROUBLESHOOTING:**
If you see "ModuleNotFoundError", your terminal is deviating from the virtual environment. **Run these commands instead:**
```powershell
venv\Scripts\python scripts/neo4j_import.py
venv\Scripts/python scripts/mongodb_import.py
```

### 5. Run the Backend
Open a **new terminal**, ensure you are in the project root, and run:
```powershell
# Go to backend directory
cd backend

# Run with explicit python path to avoid "command not found" errors
..\venv\Scripts\python -m uvicorn main:app --reload --port 8000
```
*It should say: `Uvicorn running on http://127.0.0.1:8000`*

### 5. Run the Frontend
Open a **third terminal**, activate the venv, and run:
```bash
cd frontend
python -m streamlit run app.py --server.port 8501
```

**⚠️ TROUBLESHOOTING:**
If you see "No module named streamlit", your terminal is not using the virtual environment. **Run this command instead:**
```powershell
..\venv\Scripts\python -m streamlit run app.py --server.port 8501
```

### 6. Access
-   **Dashboard**: [http://localhost:8501](http://localhost:8501)
-   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (user: `neo4j`, pass: `password123`)

## ⚠️ Important Note on Data
The "Genre Profiles" feature in the dashboard relies on a `genres` field in MongoDB. Based on the project summary, this field might not be present in the MongoDB documents (only in Neo4j).
-   If the charts for Genre Profiles are empty, this is expected behavior due to the data schema. The changes I made ensure the app **will not crash** because of this.