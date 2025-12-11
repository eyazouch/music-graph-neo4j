"""
MongoDB Analytics Page - Creative Visualizations
"""
import streamlit as st
from utils.api_client import APIClient
from utils.visualizations import (
    create_radar_chart, 
    create_genre_radar_comparison,
    create_mood_scatter,
    create_audio_feature_bars
)

st.set_page_config(page_title="MongoDB Analytics", page_icon="📊", layout="wide")

# Initialiser API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

st.title("📊 MongoDB Analytics Dashboard")
st.markdown("Creative visualizations of audio features stored in MongoDB document database")

# Tabs
tab1, tab2, tab3 = st.tabs(["🎨 Audio Features", "🎭 Mood Mapping", "🎸 Genre Profiles"])

# TAB 1: Audio Features Distribution
with tab1:
    st.subheader("Global Audio Features Distribution")
    
    with st.spinner("Loading audio features from MongoDB..."):
        audio_dist = api.get_audio_distribution()
    
    if 'error' not in audio_dist and audio_dist:
        # Radar chart
        fig = create_radar_chart(audio_dist, "Average Audio Profile (All Tracks)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Métriques
        st.markdown("### 📈 Feature Breakdown")
        cols = st.columns(4)
        
        features = [
            ('avg_danceability', 'Danceability', '💃'),
            ('avg_energy', 'Energy', '⚡'),
            ('avg_valence', 'Valence', '😊'),
            ('avg_acousticness', 'Acousticness', '🎸')
        ]
        
        for idx, (key, label, emoji) in enumerate(features):
            with cols[idx]:
                value = audio_dist.get(key, 0)
                st.metric(f"{emoji} {label}", f"{value:.3f}")
        
        cols2 = st.columns(3)
        features2 = [
            ('avg_instrumentalness', 'Instrumentalness', '🎹'),
            ('avg_liveness', 'Liveness', '🎤'),
            ('avg_speechiness', 'Speechiness', '🗣️')
        ]
        
        for idx, (key, label, emoji) in enumerate(features2):
            with cols2[idx]:
                value = audio_dist.get(key, 0)
                st.metric(f"{emoji} {label}", f"{value:.3f}")
    else:
        st.error("Failed to load audio features")

# TAB 2: Mood Mapping
with tab2:
    st.subheader("Mood Map: Energy vs Valence")
    st.markdown("MongoDB aggregation pipeline to cluster tracks by emotional characteristics")
    
    with st.spinner("Running MongoDB aggregation pipeline..."):
        mood_data = api.get_mood_clusters()
    
    if 'error' not in mood_data and mood_data:
        # Scatter plot
        fig = create_mood_scatter(mood_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Mood distribution
        import pandas as pd
        df = pd.DataFrame(mood_data)
        mood_counts = df['mood'].value_counts()
        
        st.markdown("### 🎭 Mood Distribution")
        cols = st.columns(5)
        
        mood_emojis = {
            'Euphoric': '😁',
            'Angry': '😠',
            'Peaceful': '😌',
            'Sad': '😢',
            'Neutral': '😐'
        }
        
        for idx, (mood, count) in enumerate(mood_counts.items()):
            with cols[idx % 5]:
                st.metric(f"{mood_emojis.get(mood, '🎵')} {mood}", f"{count:,}")
    else:
        st.error("Failed to load mood data")

# TAB 3: Genre Audio Profiles
with tab3:
    st.subheader("Genre Audio Profiles")
    st.markdown("Compare audio characteristics across genres using MongoDB aggregations")
    
    with st.spinner("Aggregating genre profiles..."):
        genre_profiles = api.get_genre_audio_profiles()
    
    if 'error' not in genre_profiles and genre_profiles:
        # Radar comparison
        fig = create_genre_radar_comparison(genre_profiles, top_n=5)
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature selector
        st.markdown("### 🎯 Feature Deep Dive")
        feature = st.selectbox(
            "Select audio feature to analyze",
            ['energy', 'danceability', 'valence', 'acousticness', 'tempo']
        )
        
        fig_bar = create_audio_feature_bars(genre_profiles, feature)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Table view
        with st.expander("📋 View full genre profile data"):
            import pandas as pd
            df = pd.DataFrame(genre_profiles)
            df = df.rename(columns={'_id': 'Genre'})
            st.dataframe(
                df[['Genre', 'danceability', 'energy', 'valence', 'acousticness', 'track_count']],
                hide_index=True,
                use_container_width=True
            )
    else:
        st.error("Failed to load genre profiles")

st.divider()
st.info("💡 **MongoDB Power**: All visualizations powered by flexible aggregation pipelines and document queries!")
