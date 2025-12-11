"""
Hybrid Recommendation System Page
"""
import streamlit as st
from utils.api_client import APIClient
import pandas as pd

st.set_page_config(page_title="Recommendations", page_icon="🎵", layout="wide")

# Initialiser API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

st.title("🎵 Hybrid Music Recommendation System")
st.markdown("Combining **Neo4j graph relationships** with **MongoDB audio similarity**")

# Méthode de recherche
st.subheader("🔎 Find a Track to Start")

search_query = st.text_input("Search for a track or artist", placeholder="e.g., Imagine Dragons, Radioactive...")

if search_query:
    with st.spinner("Searching tracks..."):
        search_results = api.search_tracks(search_query, limit=10)
    
    if 'error' not in search_results and search_results:
        st.success(f"Found {len(search_results)} tracks")
        
        # Sélection de track
        df_search = pd.DataFrame(search_results)
        
        # Display search results
        selected_idx = st.selectbox(
            "Select a track",
            range(len(df_search)),
            format_func=lambda i: f"{df_search.iloc[i]['track']} - {df_search.iloc[i]['artist']} ({df_search.iloc[i].get('year', 'N/A')})"
        )
        
        if selected_idx is not None:
            selected_track = df_search.iloc[selected_idx]
            track_id = selected_track['id']
            
            st.divider()
            
            # Afficher les détails de la track
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 🎵 Selected Track")
                st.markdown(f"**{selected_track['track']}**")
                st.markdown(f"*by {selected_track['artist']}*")
                st.metric("Popularity", f"{selected_track['popularity']}/100")
                if selected_track.get('year'):
                    st.metric("Year", int(selected_track['year']))
            
            with col2:
                # Récupérer les détails MongoDB
                with st.spinner("Loading track details from MongoDB..."):
                    track_details = api.get_track_details(track_id)
                
                if 'error' not in track_details and track_details:
                    st.markdown("### 📊 Audio Features")
                    
                    features_cols = st.columns(4)
                    with features_cols[0]:
                        st.metric("💃 Danceability", f"{track_details.get('danceability', 0):.3f}")
                    with features_cols[1]:
                        st.metric("⚡ Energy", f"{track_details.get('energy', 0):.3f}")
                    with features_cols[2]:
                        st.metric("😊 Valence", f"{track_details.get('valence', 0):.3f}")
                    with features_cols[3]:
                        st.metric("🎸 Acousticness", f"{track_details.get('acousticness', 0):.3f}")
            
            st.divider()
            
            # RECOMMANDATIONS
            st.subheader("🎯 Recommendations")
            
            rec_method = st.radio(
                "Choose recommendation method",
                ["🔗 Graph-based (Neo4j)", "🎵 Audio Similarity (MongoDB)", "🔥 Hybrid (Both)"],
                horizontal=True
            )
            
            if st.button("Generate Recommendations", type="primary"):
                if "Graph" in rec_method:
                    st.markdown("#### 🔗 Graph-based Recommendations")
                    st.info("Based on artist network and genre relationships (Neo4j)")
                    
                    # Simuler des recommandations basées sur le graphe
                    # (En réalité, tu créerais un endpoint API pour ça)
                    network = api.get_artist_network(selected_track['artist'])
                    if network and 'error' not in network:
                        st.write(f"Found {len(network)} related artists")
                        # Ici tu ferais une vraie requête pour trouver des tracks populaires de ces artistes
                
                if "Audio" in rec_method:
                    st.markdown("#### 🎵 Audio Similarity Recommendations")
                    st.info("Based on audio features similarity (MongoDB)")
                    
                    with st.spinner("Finding similar tracks..."):
                        similar_tracks = api.find_similar_tracks(track_id, limit=10)
                    
                    if 'error' not in similar_tracks and similar_tracks:
                        st.success(f"Found {len(similar_tracks)} similar tracks")
                        
                        df_similar = pd.DataFrame(similar_tracks)
                        st.dataframe(
                            df_similar[['track_name', 'artist_name', 'danceability', 'energy', 'valence']],
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.warning("No similar tracks found")
                
                if "Hybrid" in rec_method:
                    st.markdown("#### 🔥 Hybrid Recommendations")
                    st.info("Combining graph relationships + audio similarity for best results!")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**From Graph (Genre/Artist)**")
                        # Ici tu combineras les deux approches
                    
                    with col_b:
                        st.markdown("**From Audio Features**")
                        similar_tracks = api.find_similar_tracks(track_id, limit=5)
                        if similar_tracks and 'error' not in similar_tracks:
                            for track in similar_tracks:
                                st.write(f"🎵 {track['track_name']} - {track['artist_name']}")
    else:
        st.warning("No tracks found")

st.divider()
st.info("💡 **Hybrid approach** combines the power of graph traversal (relationships) with document similarity (audio features)!")