"""
Music Recommendation System - Data Preprocessing
Prepare data for Neo4j (graph) and MongoDB (documents)

Input: Raw dataset (15,150 tracks)
Output: Clean CSV files ready for import
"""

import pandas as pd
import hashlib
import json
from pathlib import Path
import re

print("="*80)
print("MUSIC RECOMMENDATION SYSTEM - DATA PREPROCESSING")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Input
INPUT_FILE = r"C:\Users\Eya\Desktop\music-graph-neo4j\data\raw\ClassicHit.csv"

# Output directories
OUTPUT_DIR = Path(r"C:\Users\Eya\Desktop\music-graph-neo4j\data\processed")
NEO4J_DIR = OUTPUT_DIR / "neo4j"
MONGODB_DIR = OUTPUT_DIR / "mongodb"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
NEO4J_DIR.mkdir(exist_ok=True)
MONGODB_DIR.mkdir(exist_ok=True)

print(f"\n📂 Input:  {INPUT_FILE}")
print(f"📂 Output: {OUTPUT_DIR}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_text(text):
    """Normalize text: lowercase, strip, remove extra spaces"""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text

def create_id(text, prefix=""):
    """Create unique ID from text using MD5 hash"""
    if pd.isna(text):
        text = "unknown"
    hash_object = hashlib.md5(str(text).encode())
    unique_id = hash_object.hexdigest()[:12]
    return f"{prefix}{unique_id}" if prefix else unique_id

def normalize_genre(genre):
    """Normalize genre names"""
    genre = normalize_text(genre)
    # Convert to title case
    genre = genre.title()
    # Handle special cases
    genre_map = {
        'R&B': 'R&B',
        'Edm': 'EDM',
        'Alt. Rock': 'Alternative Rock',
        'Alt Rock': 'Alternative Rock'
    }
    return genre_map.get(genre, genre)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n" + "="*80)
print("1. LOADING DATA")
print("="*80)

df = pd.read_csv(INPUT_FILE)
print(f"✅ Loaded {len(df):,} tracks")
print(f"   Columns: {list(df.columns)}")

# ============================================================================
# DATA CLEANING
# ============================================================================

print("\n" + "="*80)
print("2. DATA CLEANING")
print("="*80)

# Remove duplicates
initial_count = len(df)
df = df.drop_duplicates()
removed = initial_count - len(df)
print(f"✅ Removed {removed} duplicate(s)")

# Normalize text columns
print("\n📝 Normalizing text columns...")
df['Track_Clean'] = df['Track'].apply(normalize_text)
df['Artist_Clean'] = df['Artist'].apply(normalize_text)
df['Genre_Clean'] = df['Genre'].apply(normalize_genre)

print("✅ Text normalization complete")

# Check for empty values after cleaning
empty_tracks = df['Track_Clean'].str.len() == 0
empty_artists = df['Artist_Clean'].str.len() == 0
empty_genres = df['Genre_Clean'].str.len() == 0

if empty_tracks.any() or empty_artists.any() or empty_genres.any():
    print(f"⚠️  Warning: Found empty values")
    print(f"   Empty tracks: {empty_tracks.sum()}")
    print(f"   Empty artists: {empty_artists.sum()}")
    print(f"   Empty genres: {empty_genres.sum()}")
    # Remove rows with empty critical fields
    df = df[~(empty_tracks | empty_artists | empty_genres)]
    print(f"   Removed rows with empty values: {len(df):,} tracks remaining")

# ============================================================================
# CREATE UNIQUE IDs
# ============================================================================

print("\n" + "="*80)
print("3. CREATING UNIQUE IDs")
print("="*80)

# Track ID: unique per Track + Artist + Year combination
df['track_id'] = df.apply(
    lambda row: create_id(f"{row['Track_Clean']}_{row['Artist_Clean']}_{row['Year']}", "trk_"),
    axis=1
)

# Artist ID: unique per artist name
df['artist_id'] = df['Artist_Clean'].apply(lambda x: create_id(x, "art_"))

# Genre ID: unique per genre name
df['genre_id'] = df['Genre_Clean'].apply(lambda x: create_id(x, "gen_"))

print(f"✅ Track IDs created:  {df['track_id'].nunique():,} unique")
print(f"✅ Artist IDs created: {df['artist_id'].nunique():,} unique")
print(f"✅ Genre IDs created:  {df['genre_id'].nunique():,} unique")

# ============================================================================
# NEO4J DATA PREPARATION
# ============================================================================

print("\n" + "="*80)
print("4. PREPARING NEO4J DATA (Nodes & Relationships)")
print("="*80)

# ---------- NODES ----------

# Tracks
tracks_neo4j = df[[
    'track_id', 'Track', 'Track_Clean', 'Year', 'Duration', 'Popularity'
]].drop_duplicates(subset=['track_id'])

tracks_neo4j.columns = ['track_id', 'name', 'name_normalized', 'year', 'duration', 'popularity']
tracks_neo4j_file = NEO4J_DIR / "tracks.csv"
tracks_neo4j.to_csv(tracks_neo4j_file, index=False)
print(f"✅ Tracks nodes: {len(tracks_neo4j):,} → {tracks_neo4j_file}")

# Artists
artists_neo4j = df[['artist_id', 'Artist', 'Artist_Clean']].drop_duplicates(subset=['artist_id'])
artists_neo4j.columns = ['artist_id', 'name', 'name_normalized']
artists_neo4j_file = NEO4J_DIR / "artists.csv"
artists_neo4j.to_csv(artists_neo4j_file, index=False)
print(f"✅ Artists nodes: {len(artists_neo4j):,} → {artists_neo4j_file}")

# Genres
genres_neo4j = df[['genre_id', 'Genre_Clean']].drop_duplicates(subset=['genre_id'])
genres_neo4j.columns = ['genre_id', 'name']
genres_neo4j_file = NEO4J_DIR / "genres.csv"
genres_neo4j.to_csv(genres_neo4j_file, index=False)
print(f"✅ Genres nodes: {len(genres_neo4j):,} → {genres_neo4j_file}")

# ---------- RELATIONSHIPS ----------

# Track -[:PERFORMED_BY]-> Artist
performed_by = df[['track_id', 'artist_id']].drop_duplicates()
performed_by_file = NEO4J_DIR / "performed_by.csv"
performed_by.to_csv(performed_by_file, index=False)
print(f"✅ PERFORMED_BY relationships: {len(performed_by):,} → {performed_by_file}")

# Track -[:HAS_GENRE]-> Genre
has_genre = df[['track_id', 'genre_id']].drop_duplicates()
has_genre_file = NEO4J_DIR / "has_genre.csv"
has_genre.to_csv(has_genre_file, index=False)
print(f"✅ HAS_GENRE relationships: {len(has_genre):,} → {has_genre_file}")

# Artist -[:PERFORMS]-> Genre (aggregated)
artist_genre = df[['artist_id', 'genre_id']].drop_duplicates()
performs_file = NEO4J_DIR / "performs.csv"
artist_genre.to_csv(performs_file, index=False)
print(f"✅ PERFORMS relationships: {len(artist_genre):,} → {performs_file}")

# ============================================================================
# MONGODB DATA PREPARATION
# ============================================================================

print("\n" + "="*80)
print("5. PREPARING MONGODB DATA (Documents)")
print("="*80)

# Create MongoDB documents with audio features and metadata
mongodb_docs = df[[
    'track_id',
    'Danceability', 'Energy', 'Valence', 'Tempo',
    'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness',
    'Loudness', 'Key', 'Mode', 'Time_Signature',
    'Popularity', 'Duration', 'Year'
]].copy()

# Rename columns to match MongoDB convention
mongodb_docs.columns = [
    '_id',
    'danceability', 'energy', 'valence', 'tempo',
    'acousticness', 'instrumentalness', 'liveness', 'speechiness',
    'loudness', 'key', 'mode', 'time_signature',
    'popularity', 'duration', 'year'
]

# Save as CSV
mongodb_csv_file = MONGODB_DIR / "audio_features.csv"
mongodb_docs.to_csv(mongodb_csv_file, index=False)
print(f"✅ Audio features CSV: {len(mongodb_docs):,} documents → {mongodb_csv_file}")

# Save as JSON (alternative format)
mongodb_json_file = MONGODB_DIR / "audio_features.json"
mongodb_docs_list = mongodb_docs.to_dict('records')
with open(mongodb_json_file, 'w', encoding='utf-8') as f:
    json.dump(mongodb_docs_list, f, indent=2)
print(f"✅ Audio features JSON: {len(mongodb_docs_list):,} documents → {mongodb_json_file}")

# ============================================================================
# STATISTICS & SUMMARY
# ============================================================================

print("\n" + "="*80)
print("6. PREPROCESSING SUMMARY")
print("="*80)

stats = {
    'total_tracks': len(df),
    'unique_artists': df['artist_id'].nunique(),
    'unique_genres': df['genre_id'].nunique(),
    'year_range': f"{df['Year'].min()} - {df['Year'].max()}",
    'avg_popularity': round(df['Popularity'].mean(), 2),
    'neo4j_nodes': len(tracks_neo4j) + len(artists_neo4j) + len(genres_neo4j),
    'neo4j_relationships': len(performed_by) + len(has_genre) + len(artist_genre),
    'mongodb_documents': len(mongodb_docs)
}

print("\n📊 DATASET STATISTICS:")
for key, value in stats.items():
    print(f"   {key:.<30} {value}")

# Genre distribution
print("\n📊 GENRE DISTRIBUTION:")
genre_dist = df['Genre_Clean'].value_counts().head(10)
for genre, count in genre_dist.items():
    pct = (count / len(df)) * 100
    print(f"   {genre:.<25} {count:>6,} ({pct:>5.1f}%)")

# Year distribution
print("\n📊 YEAR DISTRIBUTION:")
year_dist = df['Year'].value_counts().sort_index()
print(f"   Years: {year_dist.index.min()} - {year_dist.index.max()}")
print(f"   Most tracks from: {year_dist.idxmax()} ({year_dist.max():,} tracks)")

# ============================================================================
# SAVE METADATA
# ============================================================================

metadata = {
    'preprocessing_info': {
        'input_file': str(INPUT_FILE),
        'total_tracks_processed': len(df),
        'preprocessing_steps': [
            'Removed duplicates',
            'Normalized text (tracks, artists, genres)',
            'Created unique IDs (track_id, artist_id, genre_id)',
            'Prepared Neo4j nodes and relationships',
            'Prepared MongoDB documents'
        ]
    },
    'statistics': stats,
    'neo4j_files': {
        'nodes': {
            'tracks': str(tracks_neo4j_file),
            'artists': str(artists_neo4j_file),
            'genres': str(genres_neo4j_file)
        },
        'relationships': {
            'performed_by': str(performed_by_file),
            'has_genre': str(has_genre_file),
            'performs': str(performs_file)
        }
    },
    'mongodb_files': {
        'csv': str(mongodb_csv_file),
        'json': str(mongodb_json_file)
    }
}

metadata_file = OUTPUT_DIR / "preprocessing_metadata.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Metadata saved: {metadata_file}")

# ============================================================================
# COMPLETION
# ============================================================================

print("\n" + "="*80)
print("✅ PREPROCESSING COMPLETE!")
print("="*80)
print("\n📁 Generated Files:")
print(f"\n   Neo4j Files ({NEO4J_DIR}):")
print(f"   • tracks.csv      : {len(tracks_neo4j):,} nodes")
print(f"   • artists.csv     : {len(artists_neo4j):,} nodes")
print(f"   • genres.csv      : {len(genres_neo4j):,} nodes")
print(f"   • performed_by.csv: {len(performed_by):,} relationships")
print(f"   • has_genre.csv   : {len(has_genre):,} relationships")
print(f"   • performs.csv    : {len(artist_genre):,} relationships")

print(f"\n   MongoDB Files ({MONGODB_DIR}):")
print(f"   • audio_features.csv  : {len(mongodb_docs):,} documents")
print(f"   • audio_features.json : {len(mongodb_docs_list):,} documents")

print(f"\n   Metadata:")
print(f"   • preprocessing_metadata.json")

print("\n🚀 Next Steps:")
print("   1. Import Neo4j data   → neo4j_import.py")
print("   2. Import MongoDB data → mongodb_import.py")
print("   3. Verify data in databases")

print("\n" + "="*80)
