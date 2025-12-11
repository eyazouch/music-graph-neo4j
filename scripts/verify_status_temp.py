from neo4j import GraphDatabase
from pymongo import MongoClient
import os
import sys

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"
MONGO_URI = "mongodb://localhost:27017"

def check_db():
    print("-" * 50)
    print("NEO4J CHECK")
    print("-" * 50)
    print(f"Connecting to Neo4j at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            print("[OK] Connection successful!")
            
            # Check counts
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"[INFO] Total Nodes: {count}")
            
            if count == 0:
                print("[WARN] Database appears empty. Did you run the import scripts?")
            else:
                print("[OK] Database has content.")
    except Exception as e:
        print(f"[ERR] Neo4j Connection failed: {e}")
    finally:
        if 'driver' in locals():
            driver.close()

    print("\n" + "-" * 50)
    print("MONGODB CHECK")
    print("-" * 50)
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("[OK] Connection successful!")
        
        db = client["music_recommendation"]
        count = db.audio_features.count_documents({})
        print(f"[INFO] Total Documents: {count}")
        
        if count == 0:
            print("[WARN] Collection appears empty.")
        else:
            print("[OK] Collection has content.")
        client.close()
    except Exception as e:
        print(f"[ERR] MongoDB connection failed: {e}")

if __name__ == "__main__":
    check_db()
