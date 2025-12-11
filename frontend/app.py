"""
Streamlit App - Page d'accueil
"""
import streamlit as st
from utils.api_client import APIClient

# Configuration
st.set_page_config(
    page_title="Music Recommendation System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser le client API
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1DB954;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1DB954;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎵 Music Recommendation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">NoSQL-Powered Music Discovery with Neo4j & MongoDB</div>', unsafe_allow_html=True)

# Health check
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    health = api.health_check()
    if 'error' not in health:
        st.success("✅ API Backend: Online")
    else:
        st.error("❌ API Backend: Offline")
        st.stop()

st.divider()

# Statistiques globales
st.subheader("📊 Database Statistics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Neo4j Graph Database")
    neo4j_stats = api.get_neo4j_stats()
    
    if 'error' not in neo4j_stats:
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric("🎵 Tracks", f"{neo4j_stats['tracks']:,}")
            st.metric("🎤 Artists", f"{neo4j_stats['artists']:,}")
        with metric_cols[1]:
            st.metric("🎸 Genres", f"{neo4j_stats['genres']:,}")
            st.metric("🔗 Relationships", f"{neo4j_stats['relationships']:,}")
    else:
        st.error("Failed to load Neo4j stats")

with col2:
    st.markdown("### MongoDB Document Store")
    mongo_stats = api.get_mongodb_stats()
    
    if 'error' not in mongo_stats:
        st.metric("📄 Total Documents", f"{mongo_stats['total_tracks']:,}")
        st.metric("💾 Database Size", f"{mongo_stats['database_size'] / (1024**2):.2f} MB")
        st.info(f"Collections: {', '.join(mongo_stats['collections'])}")
    else:
        st.error("Failed to load MongoDB stats")

st.divider()

# Features du système
st.subheader("🚀 System Features")

features = [
    {
        "icon": "🔍",
        "title": "Neo4j Explorer",
        "description": "Visualize artist networks, genre relationships, and graph-based queries"
    },
    {
        "icon": "📊",
        "title": "MongoDB Analytics",
        "description": "Creative visualizations of audio features, mood mapping, and genre profiles"
    },
    {
        "icon": "🎵",
        "title": "Hybrid Recommendations",
        "description": "Combine graph relationships with audio similarity for smart recommendations"
    }
]

cols = st.columns(3)
for idx, feature in enumerate(features):
    with cols[idx]:
        st.markdown(f"""
        <div class="feature-card">
            <h2>{feature['icon']}</h2>
            <h3>{feature['title']}</h3>
            <p>{feature['description']}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Quick insights
st.subheader("🎯 Quick Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 5 Genres by Track Count")
    top_genres = api.get_top_genres(limit=5)
    
    if 'error' not in top_genres:
        for genre in top_genres:
            st.progress(genre['track_count'] / top_genres[0]['track_count'], 
                       text=f"{genre['genre']}: {genre['track_count']:,} tracks")
    else:
        st.error("Failed to load top genres")

with col2:
    st.markdown("#### Top 5 Artists by Popularity")
    top_artists = api.get_top_artists(limit=5)
    
    if 'error' not in top_artists:
        for artist in top_artists:
            st.progress(artist['avg_popularity'] / 100, 
                       text=f"{artist['artist']}: {artist['avg_popularity']:.1f}/100")
    else:
        st.error("Failed to load top artists")

st.divider()

# Navigation
st.info("👈 **Navigate using the sidebar** to explore Neo4j graphs, MongoDB analytics, or get music recommendations!")