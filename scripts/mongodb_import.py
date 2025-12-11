"""
MongoDB Data Import Script
Import audio features and metadata into MongoDB

Prerequisites:
- MongoDB Docker container running
- Preprocessed JSON/CSV files ready
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, BulkWriteError
import json
import pandas as pd
from pathlib import Path
import time

print("="*80)
print("MONGODB DATA IMPORT - MUSIC RECOMMENDATION SYSTEM")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "music_recommendation"
COLLECTION_NAME = "audio_features"

# Data files
# Data files
# Use relative path from this script location
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed" / "mongodb"
JSON_FILE = DATA_DIR / "audio_features.json"
CSV_FILE = DATA_DIR / "audio_features.csv"

print(f"\n📂 Data directory: {DATA_DIR}")
print(f"🔗 MongoDB URI: {MONGO_URI}")
print(f"💾 Database: {DATABASE_NAME}")
print(f"📦 Collection: {COLLECTION_NAME}")

# ============================================================================
# VERIFY FILES
# ============================================================================

print("\n" + "="*80)
print("1. VERIFYING FILES")
print("="*80)

json_exists = JSON_FILE.exists()
csv_exists = CSV_FILE.exists()

print(f"{'✅' if json_exists else '❌'} JSON file: {JSON_FILE}")
print(f"{'✅' if csv_exists else '❌'} CSV file:  {CSV_FILE}")

if not json_exists and not csv_exists:
    print("\n❌ ERROR: No data files found!")
    print("Please run preprocess_music_data.py first")
    exit(1)

# Choose file to import (prefer JSON)
use_json = json_exists
data_file = JSON_FILE if use_json else CSV_FILE
print(f"\n📥 Using: {data_file.name}")

# ============================================================================
# CONNECT TO MONGODB
# ============================================================================

print("\n" + "="*80)
print("2. CONNECTING TO MONGODB")
print("="*80)

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
    
    # Get database and collection
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    # Get server info
    server_info = client.server_info()
    print(f"📊 MongoDB version: {server_info['version']}")
    
except ConnectionFailure as e:
    print(f"❌ ERROR: Cannot connect to MongoDB")
    print(f"   {str(e)}")
    print("\n💡 Make sure:")
    print("   1. Docker container is running: docker ps")
    print("   2. MongoDB is accessible at localhost:27017")
    exit(1)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n" + "="*80)
print("3. LOADING DATA")
print("="*80)

start_load = time.time()

if use_json:
    print("📄 Loading JSON file...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    print(f"✅ Loaded {len(documents):,} documents from JSON")
else:
    print("📄 Loading CSV file...")
    df = pd.read_csv(CSV_FILE)
    documents = df.to_dict('records')
    print(f"✅ Loaded {len(documents):,} documents from CSV")

load_time = time.time() - start_load
print(f"⏱️  Load time: {load_time:.2f}s")

# Show sample document
print("\n📋 Sample document:")
sample = documents[0]
for key, value in list(sample.items())[:8]:
    print(f"   {key:.<20} {value}")
print(f"   ... and {len(sample)-8} more fields")

# ============================================================================
# PREPARE COLLECTION
# ============================================================================

print("\n" + "="*80)
print("4. PREPARING COLLECTION")
print("="*80)

# Check if collection exists and has data
existing_count = collection.count_documents({})
if existing_count > 0:
    print(f"⚠️  Collection already has {existing_count:,} documents")
    print("🗑️  Dropping existing collection...")
    collection.drop()
    print("✅ Collection dropped")

# ============================================================================
# CREATE INDEXES
# ============================================================================

print("\n📊 Creating indexes...")

indexes = [
    ("_id", 1),  # Already exists by default
    ("popularity", -1),
    ("year", 1),
    ("danceability", -1),
    ("energy", -1),
    ("valence", -1)
]

for field, direction in indexes[1:]:  # Skip _id
    try:
        collection.create_index([(field, direction)])
        print(f"✅ Index on '{field}' created")
    except Exception as e:
        print(f"⚠️  Index on '{field}': {str(e)[:50]}")

print("✅ Indexes created")

# ============================================================================
# IMPORT DATA
# ============================================================================

print("\n" + "="*80)
print("5. IMPORTING DATA")
print("="*80)

start_import = time.time()

# Import in batches
batch_size = 1000
total_batches = (len(documents) + batch_size - 1) // batch_size
inserted_count = 0

print(f"📥 Importing {len(documents):,} documents in batches of {batch_size}...")

for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    
    try:
        result = collection.insert_many(batch, ordered=False)
        inserted_count += len(result.inserted_ids)
        
        current_batch = (i // batch_size) + 1
        progress = (inserted_count / len(documents)) * 100
        print(f"   Batch {current_batch}/{total_batches} | {inserted_count:,}/{len(documents):,} ({progress:.1f}%)", end='\r')
        
    except BulkWriteError as e:
        print(f"\n⚠️  Batch {current_batch} had errors: {len(e.details['writeErrors'])} documents failed")
        inserted_count += len(batch) - len(e.details['writeErrors'])

print()  # New line after progress
import_time = time.time() - start_import

print(f"\n✅ Import complete!")
print(f"   Inserted: {inserted_count:,} documents")
print(f"   Time: {import_time:.2f}s")
print(f"   Speed: {int(inserted_count/import_time):,} docs/sec")

# ============================================================================
# VERIFY IMPORT
# ============================================================================

print("\n" + "="*80)
print("6. VERIFYING IMPORT")
print("="*80)

# Count documents
total_docs = collection.count_documents({})
print(f"📊 Total documents in collection: {total_docs:,}")

# Collection stats
stats = db.command("collStats", COLLECTION_NAME)
print(f"💾 Storage size: {stats['size'] / 1024 / 1024:.2f} MB")
print(f"📇 Index size: {stats.get('totalIndexSize', 0) / 1024 / 1024:.2f} MB")

# Sample queries
print("\n" + "="*80)
print("7. SAMPLE QUERIES")
print("="*80)

# Most popular tracks
print("\n🔥 Top 5 most popular tracks:")
results = collection.find().sort("popularity", -1).limit(5)
for i, doc in enumerate(results, 1):
    print(f"   {i}. Track ID: {doc['_id']}")
    print(f"      Popularity: {doc['popularity']}")
    print(f"      Danceability: {doc['danceability']:.3f}, Energy: {doc['energy']:.3f}")

# Most danceable tracks
print("\n💃 Top 5 most danceable tracks:")
results = collection.find().sort("danceability", -1).limit(5)
for i, doc in enumerate(results, 1):
    print(f"   {i}. Track ID: {doc['_id']}")
    print(f"      Danceability: {doc['danceability']:.3f}")
    print(f"      Energy: {doc['energy']:.3f}, Valence: {doc['valence']:.3f}")

# Most energetic tracks
print("\n⚡ Top 5 most energetic tracks:")
results = collection.find().sort("energy", -1).limit(5)
for i, doc in enumerate(results, 1):
    print(f"   {i}. Track ID: {doc['_id']}")
    print(f"      Energy: {doc['energy']:.3f}")
    print(f"      Loudness: {doc['loudness']:.2f} dB")

# Average audio features
print("\n📊 Average audio features:")
pipeline = [
    {
        "$group": {
            "_id": None,
            "avg_danceability": {"$avg": "$danceability"},
            "avg_energy": {"$avg": "$energy"},
            "avg_valence": {"$avg": "$valence"},
            "avg_tempo": {"$avg": "$tempo"},
            "avg_popularity": {"$avg": "$popularity"}
        }
    }
]
result = list(collection.aggregate(pipeline))[0]
print(f"   Danceability: {result['avg_danceability']:.3f}")
print(f"   Energy:       {result['avg_energy']:.3f}")
print(f"   Valence:      {result['avg_valence']:.3f}")
print(f"   Tempo:        {result['avg_tempo']:.1f} BPM")
print(f"   Popularity:   {result['avg_popularity']:.1f}")

# Distribution by decade
print("\n📅 Tracks by decade:")
pipeline = [
    {
        "$group": {
            "_id": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]},
            "count": {"$sum": 1}
        }
    },
    {"$sort": {"_id": 1}},
    {"$limit": 10}
]
results = collection.aggregate(pipeline)
for doc in results:
    decade = int(doc['_id'])
    count = doc['count']
    print(f"   {decade}s: {count:>6,} tracks")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✅ MONGODB IMPORT COMPLETE!")
print("="*80)

print(f"\n📊 Summary:")
print(f"   Database:    {DATABASE_NAME}")
print(f"   Collection:  {COLLECTION_NAME}")
print(f"   Documents:   {total_docs:,}")
print(f"   Import time: {import_time:.2f}s")

print("\n🎯 Next steps:")
print("   1. Verify in MongoDB Compass: mongodb://localhost:27017")
print("   2. Test aggregation queries")
print("   3. Build recommendation API")

print("\n💡 Access MongoDB:")
print(f"   URI: {MONGO_URI}")
print(f"   Database: {DATABASE_NAME}")
print(f"   Collection: {COLLECTION_NAME}")

print("\n" + "="*80)

# Close connection
client.close()
