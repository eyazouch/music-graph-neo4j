"""
Neo4j Explorer Page
"""
import streamlit as st
from utils.api_client import APIClient
from utils.visualizations import create_network_graph, create_genre_evolution_chart
import pandas as pd

st.set_page_config(page_title="Neo4j Explorer", page_icon="🔍", layout="wide")

# Initialiser API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

st.title("🔍 Neo4j Graph Explorer")
st.markdown("Explore the graph database: artist networks, genre relationships, and track connections")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Search", "🎸 Artist Network", "📈 Genre Evolution", "🏆 Top Charts"])

# TAB 1: Search
with tab1:
    st.subheader("Search Tracks and Artists")
    
    search_query = st.text_input("🔎 Search by track or artist name", placeholder="e.g., Bohemian Rhapsody, Queen...")
    
    if search_query:
        with st.spinner("Searching..."):
            results = api.search_tracks(search_query, limit=20)
        
        if 'error' not in results and results:
            st.success(f"Found {len(results)} results")
            
            df = pd.DataFrame(results)
            df['year'] = df['year'].fillna(0).astype(int)
            
            st.dataframe(
                df,
                column_config={
                    "track": st.column_config.TextColumn("Track", width="medium"),
                    "artist": st.column_config.TextColumn("Artist", width="medium"),
                    "popularity": st.column_config.ProgressColumn("Popularity", min_value=0, max_value=100),
                    "year": st.column_config.NumberColumn("Year", format="%d"),
                },
                hide_index=True,
                use_container_width=True
            )
        elif results:
            st.warning("No results found")
        else:
            st.error("Search failed")

# TAB 2: Artist Network
with tab2:
    st.subheader("Artist Collaboration Network")
    st.markdown("Visualize artist connections through shared genres (Neo4j graph traversal)")
    
    artist_name = st.text_input("Enter artist name", placeholder="e.g., The Beatles")
    
    if artist_name:
        with st.spinner("Building network..."):
            network_data = api.get_artist_network(artist_name)
        
        if 'error' not in network_data and network_data:
            st.success(f"Found {len(network_data)} related artists")
            
            # Network graph
            fig = create_network_graph(network_data, artist_name)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Table des similarités
            with st.expander("📊 View similarity details"):
                df = pd.DataFrame(network_data)
                st.dataframe(
                    df[['related_artist', 'similarity', 'common_genres']],
                    hide_index=True,
                    use_container_width=True
                )
        elif network_data:
            st.warning("No related artists found")
        else:
            st.error("Failed to load network")

# TAB 3: Genre Evolution
with tab3:
    st.subheader("Genre Evolution Over Time")
    st.markdown("Track how genres have evolved from 2000 to 2023")
    
    with st.spinner("Loading evolution data..."):
        evolution_data = api.get_genre_evolution()
    
    if 'error' not in evolution_data and evolution_data:
        fig = create_genre_evolution_chart(evolution_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        df = pd.DataFrame(evolution_data)
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Years Covered", df['year'].nunique())
            st.metric("Total Genres", df['genre'].nunique())
        
        with col2:
            peak_year = df.groupby('year')['tracks'].sum().idxmax()
            st.metric("Peak Year", int(peak_year))
            st.metric("Peak Tracks", f"{df.groupby('year')['tracks'].sum().max():,}")
    else:
        st.error("Failed to load evolution data")

# TAB 4: Top Charts
with tab4:
    st.subheader("Top Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎸 Top Genres")
        top_genres = api.get_top_genres(limit=15)
        
        if 'error' not in top_genres and top_genres:
            df_genres = pd.DataFrame(top_genres)
            
            import plotly.express as px
            fig = px.bar(
                df_genres,
                x='track_count',
                y='genre',
                orientation='h',
                title="Top Genres by Track Count",
                color='track_count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
            st.plotly_chart(fig, use_container_width=True)
        elif not top_genres:
             st.warning("No genres found")
        else:
            st.error("Failed to load top genres")
    
    with col2:
        st.markdown("### 🎤 Top Artists")
        top_artists = api.get_top_artists(limit=15)
        
        if 'error' not in top_artists and top_artists:
            df_artists = pd.DataFrame(top_artists)
            
            fig = px.bar(
                df_artists,
                x='avg_popularity',
                y='artist',
                orientation='h',
                title="Top Artists by Average Popularity",
                color='avg_popularity',
                color_continuous_scale='Plasma',
                hover_data=['track_count']
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
            st.plotly_chart(fig, use_container_width=True)
        elif not top_artists:
             st.warning("No artists found")
        else:
            st.error("Failed to load top artists")

st.divider()
st.info("💡 **Neo4j Power**: All queries leverage graph traversal for lightning-fast relationship discovery!")