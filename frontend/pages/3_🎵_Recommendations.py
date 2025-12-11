"""
Hybrid Recommendation System Page
"""
import streamlit as st
from utils.api_client import APIClient
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="Discovery", page_icon="🔭", layout="wide")

# Init API
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

st.title("🔭 Music Discovery Engine")
st.markdown("Explore the *Music Knowledge Graph* by selecting your favorite genres and artists.")

# Helper functions with Caching
@st.cache_data(ttl=3600)
def load_all_genres():
    return api.get_all_genres()

@st.cache_data(ttl=3600)
def load_artists_for_genre(genre):
    return api.get_artists_by_genre(genre)

@st.cache_data(ttl=3600)
def load_evolution_data():
    return api.get_genre_evolution()

# Initial Data Load
with st.spinner("Loading knowledge base..."):
    all_genres = load_all_genres()
    # Pre-fetch evolution data for years list
    evolution_data = load_evolution_data()
    if evolution_data and 'error' not in evolution_data:
        all_years = sorted(list(set(d['year'] for d in evolution_data)), reverse=True)
    else:
        all_years = list(range(2024, 1950, -1))

if not all_genres or 'error' in all_genres:
    st.error("Could not connect to Knowledge Graph. Please ensure backend is running.")
    st.stop()

# --- FILTERS SECTION ---
with st.container():
    st.subheader("1. define your scope")
    
    st.markdown("##### 🏷️ Select Genres")
    # Genres as Pills
    selected_genres = st.pills(
        "Genres",
        all_genres,
        selection_mode="multi",
        key="genre_pills"
    )
    
    # Load artists dynamically based on genre selection
    if selected_genres:
        # Union of artists from selected genres
        available_artists = set()
        for g in selected_genres:
            artists = load_artists_for_genre(g)
            if artists and 'error' not in artists:
                available_artists.update(artists)
        artist_options = sorted(list(available_artists))
    else:
        artist_options = []

    if artist_options:
        st.markdown("##### 🎤 Select Artists")
        # Artists as Pills (Limit to top 50 to avoid clutter, or use multiselect if too many)
        if len(artist_options) > 50:
            st.caption(f"Found {len(artist_options)} artists. Showing top 50.")
            selected_artists = st.pills(
                "Artists",
                artist_options[:50], 
                selection_mode="multi",
                key="artist_pills"
            )
        else:
            selected_artists = st.pills(
                "Artists",
                artist_options,
                selection_mode="multi",
                key="artist_pills"
            )
    else:
        selected_artists = []

    st.markdown("##### 📅 Select Years")
    # Years as Pills (Grouped or just list)
    # Filter years to reasonable recent usage or all
    selected_years = st.pills(
        "Years",
        all_years[:30], # Top 30 recent years?
        selection_mode="multi",
        key="year_pills"
    )
    if len(all_years) > 30:
        st.caption("Showing most recent years. Use backend for fuller history.")

# --- VISUALIZATION SECTION ---
if selected_genres and selected_artists:
    st.divider()
    st.subheader("2. visualize connections")
    
    with st.spinner("Building network graph..."):
        network_data = api.get_network_advanced(selected_genres, selected_artists)
    
    if network_data and network_data.get('nodes'):
        # Build AGraph
        nodes = []
        edges = []
        
        # Add Nodes
        for n in network_data['nodes']:
            color = "#FF4B4B" if n['type'] == 'artist' else "#1DB954" # Red for Artist, Green for Genre
            nodes.append(Node(
                id=n['id'], 
                label=n['label'], 
                size=15, # Smaller nodes for performance
                color=color,
                symbolType="circle"
            ))
            
        # Add Edges
        # Limit edges for performance if necessary
        for l in network_data['links']:
            edges.append(Edge(
                source=l['source'], 
                target=l['target'], 
                color="#555555"
            ))
            
        config = Config(
            width=1200, 
            height=800, 
            directed=True,
            physics=True, # Re-enable physics for layout
            hierarchical=False,
            nodeHighlightBehavior=True, 
            highlightColor="#F7A7A6",
            collapsible=False,
            # Physics settings to spread nodes out (fix "Dot" issue)
            # but stabilize quickly
             physicsOptions={
                "barnesHut": {
                    "gravitationalConstant": -4000,
                    "centralGravity": 0.3,
                    "springLength": 95,
                    "springConstant": 0.04,
                    "damping": 0.09,
                    "avoidOverlap": 0.1
                },
                "stabilization": {
                    "enabled": True,
                    "iterations": 1000,
                    "updateInterval": 100,
                    "onlyDynamicEdges": False,
                    "fit": True
                }
            }
        )
        
        # Render Graph
        return_value = agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("No direct connections found between selections yet.")

# --- RESULTS SECTION ---
if st.button("🚀 Discover Recommendations", type="primary", use_container_width=True):
    if not selected_genres and not selected_artists:
        st.warning("Please select at least one genre or artist.")
    else:
        st.divider()
        st.subheader("3. recommended tracks")
        
        with st.spinner("Analyzing graph and audio features..."):
            recommendations = api.get_recommendations_advanced(
                selected_genres, 
                selected_artists, 
                selected_years if selected_years else []
            )
            
        if recommendations and 'error' not in recommendations:
            # Display as a nice grid
            for i in range(0, len(recommendations), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(recommendations):
                        track = recommendations[i+j]
                        with cols[j]:
                            st.info(f"**{track['track']}**  \n"
                                    f"👤 {track['artist']}  \n"
                                    f"📅 {track.get('year', 'N/A')} | 🔥 {track['popularity']}")
        else:
            st.warning("No tracks found matching all criteria. Try expanding your search.")
            
st.markdown("---")
st.caption("Music Knowledge Graph Engine v1.0")