"""
Neo4j Data Import Script
Import preprocessed music data into Neo4j graph database

Prerequisites:
- Neo4j Docker container running
- Preprocessed CSV files ready
"""

from neo4j import GraphDatabase
import pandas as pd
from pathlib import Path
import time

print("="*80)
print("NEO4J DATA IMPORT - MUSIC RECOMMENDATION SYSTEM")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Neo4j connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password123"  # Your Neo4j password

# Data files
# Data files
# Use relative path from this script location
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed" / "neo4j"

FILES = {
    'tracks': DATA_DIR / "tracks.csv",
    'artists': DATA_DIR / "artists.csv",
    'genres': DATA_DIR / "genres.csv",
    'performed_by': DATA_DIR / "performed_by.csv",
    'has_genre': DATA_DIR / "has_genre.csv",
    'performs': DATA_DIR / "performs.csv"
}

print(f"\n📂 Data directory: {DATA_DIR}")
print(f"🔗 Neo4j URI: {NEO4J_URI}")

# ============================================================================
# VERIFY FILES
# ============================================================================

print("\n" + "="*80)
print("1. VERIFYING FILES")
print("="*80)

all_files_exist = True
for name, filepath in FILES.items():
    exists = filepath.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {name:.<20} {filepath}")
    if not exists:
        all_files_exist = False

if not all_files_exist:
    print("\n❌ ERROR: Some files are missing!")
    print("Please run preprocess_music_data.py first")
    exit(1)

print("\n✅ All files verified!")

# ============================================================================
# CONNECT TO NEO4J
# ============================================================================

print("\n" + "="*80)
print("2. CONNECTING TO NEO4J")
print("="*80)

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Test connection
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        result.single()
    
    print("✅ Connected to Neo4j successfully!")
    
except Exception as e:
    print(f"❌ ERROR: Cannot connect to Neo4j")
    print(f"   {str(e)}")
    print("\n💡 Make sure:")
    print("   1. Docker container is running: docker ps")
    print("   2. Neo4j is accessible at bolt://localhost:7687")
    print("   3. Password is correct")
    exit(1)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clear_database(session):
    """Clear all nodes and relationships"""
    print("\n🗑️  Clearing existing data...")
    session.run("MATCH (n) DETACH DELETE n")
    print("✅ Database cleared")

def create_constraints(session):
    """Create uniqueness constraints"""
    print("\n🔒 Creating constraints...")
    
    constraints = [
        "CREATE CONSTRAINT track_id IF NOT EXISTS FOR (t:Track) REQUIRE t.track_id IS UNIQUE",
        "CREATE CONSTRAINT artist_id IF NOT EXISTS FOR (a:Artist) REQUIRE a.artist_id IS UNIQUE",
        "CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.genre_id IS UNIQUE"
    ]
    
    for constraint in constraints:
        try:
            session.run(constraint)
            print(f"✅ {constraint.split('(')[1].split(')')[0]}")
        except Exception as e:
            print(f"⚠️  Constraint may already exist: {str(e)[:50]}")
    
    print("✅ Constraints created")

def create_indexes(session):
    """Create indexes for better query performance"""
    print("\n📊 Creating indexes...")
    
    indexes = [
        "CREATE INDEX track_year IF NOT EXISTS FOR (t:Track) ON (t.year)",
        "CREATE INDEX track_popularity IF NOT EXISTS FOR (t:Track) ON (t.popularity)",
        "CREATE INDEX artist_name IF NOT EXISTS FOR (a:Artist) ON (a.name)",
        "CREATE INDEX genre_name IF NOT EXISTS FOR (g:Genre) ON (g.name)"
    ]
    
    for index in indexes:
        try:
            session.run(index)
            print(f"✅ {index.split('ON')[1].strip() if 'ON' in index else 'Index created'}")
        except Exception as e:
            print(f"⚠️  Index may already exist: {str(e)[:50]}")
    
    print("✅ Indexes created")

def load_nodes(session, node_type, csv_file, properties):
    """Load nodes from CSV file"""
    print(f"\n📥 Loading {node_type} nodes...")
    
    df = pd.read_csv(csv_file)
    start_time = time.time()
    
    # Build Cypher query
    props_str = ", ".join([f"{k}: row.{v}" for k, v in properties.items()])
    query = f"""
    UNWIND $rows AS row
    CREATE (n:{node_type} {{{props_str}}})
    """
    
    # Convert DataFrame to list of dicts
    rows = df.to_dict('records')
    
    # Import in batches
    batch_size = 1000
    total_batches = (len(rows) + batch_size - 1) // batch_size
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        session.run(query, rows=batch)
        
        current_batch = (i // batch_size) + 1
        print(f"   Batch {current_batch}/{total_batches} ({len(batch)} nodes)", end='\r')
    
    elapsed = time.time() - start_time
    print(f"\n✅ Loaded {len(rows):,} {node_type} nodes in {elapsed:.2f}s")
    
    return len(rows)

def load_relationships(session, rel_type, csv_file, from_node, to_node, from_id, to_id):
    """Load relationships from CSV file"""
    print(f"\n🔗 Loading {rel_type} relationships...")
    
    df = pd.read_csv(csv_file)
    start_time = time.time()
    
    query = f"""
    UNWIND $rows AS row
    MATCH (from:{from_node} {{{from_id}: row.{from_id}}})
    MATCH (to:{to_node} {{{to_id}: row.{to_id}}})
    CREATE (from)-[:{rel_type}]->(to)
    """
    
    # Convert DataFrame to list of dicts
    rows = df.to_dict('records')
    
    # Import in batches
    batch_size = 1000
    total_batches = (len(rows) + batch_size - 1) // batch_size
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        session.run(query, rows=batch)
        
        current_batch = (i // batch_size) + 1
        print(f"   Batch {current_batch}/{total_batches} ({len(batch)} relationships)", end='\r')
    
    elapsed = time.time() - start_time
    print(f"\n✅ Loaded {len(rows):,} {rel_type} relationships in {elapsed:.2f}s")
    
    return len(rows)

# ============================================================================
# IMPORT DATA
# ============================================================================

print("\n" + "="*80)
print("3. IMPORTING DATA")
print("="*80)

total_start = time.time()
stats = {
    'nodes': {},
    'relationships': {}
}

with driver.session() as session:
    # Clear existing data
    clear_database(session)
    
    # Create constraints and indexes
    create_constraints(session)
    create_indexes(session)
    
    # Import nodes
    print("\n" + "-"*80)
    print("IMPORTING NODES")
    print("-"*80)
    
    stats['nodes']['Track'] = load_nodes(
        session, "Track", FILES['tracks'],
        {
            'track_id': 'track_id',
            'name': 'name',
            'name_normalized': 'name_normalized',
            'year': 'year',
            'duration': 'duration',
            'popularity': 'popularity'
        }
    )
    
    stats['nodes']['Artist'] = load_nodes(
        session, "Artist", FILES['artists'],
        {
            'artist_id': 'artist_id',
            'name': 'name',
            'name_normalized': 'name_normalized'
        }
    )
    
    stats['nodes']['Genre'] = load_nodes(
        session, "Genre", FILES['genres'],
        {
            'genre_id': 'genre_id',
            'name': 'name'
        }
    )
    
    # Import relationships
    print("\n" + "-"*80)
    print("IMPORTING RELATIONSHIPS")
    print("-"*80)
    
    stats['relationships']['PERFORMED_BY'] = load_relationships(
        session, "PERFORMED_BY", FILES['performed_by'],
        "Track", "Artist", "track_id", "artist_id"
    )
    
    stats['relationships']['HAS_GENRE'] = load_relationships(
        session, "HAS_GENRE", FILES['has_genre'],
        "Track", "Genre", "track_id", "genre_id"
    )
    
    stats['relationships']['PERFORMS'] = load_relationships(
        session, "PERFORMS", FILES['performs'],
        "Artist", "Genre", "artist_id", "genre_id"
    )

total_time = time.time() - total_start

# ============================================================================
# VERIFY IMPORT
# ============================================================================

print("\n" + "="*80)
print("4. VERIFYING IMPORT")
print("="*80)

with driver.session() as session:
    # Count nodes
    result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
    print("\n📊 Node counts:")
    for record in result:
        print(f"   {record['label']:.<20} {record['count']:>6,}")
    
    # Count relationships
    result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
    print("\n🔗 Relationship counts:")
    for record in result:
        print(f"   {record['type']:.<20} {record['count']:>6,}")

# ============================================================================
# SAMPLE QUERIES
# ============================================================================

print("\n" + "="*80)
print("5. SAMPLE QUERIES")
print("="*80)

with driver.session() as session:
    # Sample tracks
    print("\n🎵 Sample tracks:")
    result = session.run("""
        MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist)
        RETURN t.name AS track, a.name AS artist, t.year AS year
        LIMIT 5
    """)
    for record in result:
        print(f"   • '{record['track']}' by {record['artist']} ({record['year']})")
    
    # Most popular genre
    print("\n🎸 Most popular genre:")
    result = session.run("""
        MATCH (g:Genre)<-[:HAS_GENRE]-(t:Track)
        RETURN g.name AS genre, count(t) AS tracks
        ORDER BY tracks DESC
        LIMIT 1
    """)
    record = result.single()
    print(f"   {record['genre']} with {record['tracks']:,} tracks")
    
    # Most prolific artist
    print("\n⭐ Most prolific artist:")
    result = session.run("""
        MATCH (a:Artist)<-[:PERFORMED_BY]-(t:Track)
        RETURN a.name AS artist, count(t) AS tracks
        ORDER BY tracks DESC
        LIMIT 1
    """)
    record = result.single()
    print(f"   {record['artist']} with {record['tracks']:,} tracks")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✅ IMPORT COMPLETE!")
print("="*80)

print(f"\n⏱️  Total import time: {total_time:.2f}s")

print("\n📊 Summary:")
print(f"   Nodes imported:")
for node_type, count in stats['nodes'].items():
    print(f"      • {node_type:.<15} {count:>6,}")

print(f"\n   Relationships imported:")
for rel_type, count in stats['relationships'].items():
    print(f"      • {rel_type:.<15} {count:>6,}")

total_nodes = sum(stats['nodes'].values())
total_rels = sum(stats['relationships'].values())
print(f"\n   Total: {total_nodes:,} nodes, {total_rels:,} relationships")

print("\n🎯 Next steps:")
print("   1. Open Neo4j Browser: http://localhost:7474")
print("   2. Test some queries")
print("   3. Import MongoDB data → mongodb_import.py")

print("\n" + "="*80)

# Close driver
driver.close()
