"""
MongoDB Analytics Page - Creative Visualizations
"""
import streamlit as st
from utils.api_client import APIClient
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="MongoDB Analytics", page_icon="📊", layout="wide")

# Init API
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

api = st.session_state.api_client

st.title("📊 MongoDB Analytics Dashboard")
st.markdown("Advanced audio feature analysis powered by document aggregations.")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎨 Audio Features", 
    "🎭 Mood Mapping", 
    "🕰️ Time Travel", 
    "🧊 3D Audio Space", 
    "🔥 Correlation Heatmap"
])

# 1. AUDIO FEATURES (Existing)
with tab1:
    st.subheader("Global Audio Features Distribution")
    with st.spinner("Loading audio features..."):
        audio_dist = api.get_audio_distribution()
    
    if 'error' not in audio_dist and audio_dist:
        # Simple Radar
        categories = ['Dance', 'Energy', 'Valence', 'Acoustic', 'Live', 'Speech']
        values = [
            audio_dist.get('avg_danceability', 0),
            audio_dist.get('avg_energy', 0),
            audio_dist.get('avg_valence', 0),
            audio_dist.get('avg_acousticness', 0),
            audio_dist.get('avg_liveness', 0),
            audio_dist.get('avg_speechiness', 0)
        ]
        fig = go.Figure(data=go.Scatterpolar(
            r=values, theta=categories, fill='toself', line_color='#1DB954'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to load data.")

# 2. MOOD MAPPING (Existing)
with tab2:
    st.subheader("Mood Map (Energy vs Valence)")
    with st.spinner("Clustering moods..."):
        mood_data = api.get_mood_clusters()
    
    if mood_data and 'error' not in mood_data:
        df_mood = pd.DataFrame(mood_data)
        fig = px.scatter(
            df_mood, x='valence', y='energy', color='mood', 
            hover_data=['track_name', 'artist_name'],
            color_discrete_map={'Euphoric': '#1DB954', 'Sad': '#3498DB', 'Angry': '#E74C3C', 'Peaceful': '#F1C40F'}
        )
        st.plotly_chart(fig, use_container_width=True)

# 3. TIME TRAVEL (New)
with tab3:
    st.subheader("🕰️ Time Travel: Evolution of Music")
    st.markdown("How has music changed from the 1960s to today?")
    
    with st.spinner("Analyzing historical trends..."):
        evolution = api.get_audio_evolution()
        
    if evolution and 'error' not in evolution:
        df_ev = pd.DataFrame(evolution)
        df_ev['year'] = df_ev['_id'] # Rename _id to year
        
        # Line Chart
        fig = px.line(
            df_ev, x='year', 
            y=['avg_energy', 'avg_danceability', 'avg_acousticness'],
            labels={'value': 'Level (0-1)', 'year': 'Year'},
            title="Energy vs Acousticness Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("📉 Note how **Acousticness** drops while **Energy** rises over the decades!")

# 4. 3D SPACE (New)
with tab4:
    st.subheader("🧊 3D Audio Space")
    st.markdown("Explore tracks in a 3D volume defined by Danceability, Energy, and Valence.")
    
    if mood_data and 'error' not in mood_data:
        # Reuse mood data sample for 3D plot
        df_3d = pd.DataFrame(mood_data)
        
        fig_3d = px.scatter_3d(
            df_3d, x='danceability', y='energy', z='valence',
            color='mood', size='popularity', opacity=0.7,
            hover_data=['track_name', 'artist_name'],
            color_discrete_map={'Euphoric': '#1DB954', 'Sad': '#3498DB', 'Angry': '#E74C3C', 'Peaceful': '#F1C40F'},
            height=700
        )
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.warning("Go to 'Mood Mapping' tab to load data first.")

# 5. HEATMAP (New)
with tab5:
    st.subheader("🔥 Feature Correlations")
    st.markdown("Scientific correlation matrix of audio features.")
    
    with st.spinner("Calculating correlations..."):
        corr_data = api.get_feature_correlations()
        
    if corr_data and 'error' not in corr_data:
        df_corr = pd.DataFrame(corr_data)
        # Select numeric columns only
        numeric_cols = ['danceability', 'energy', 'valence', 'acousticness', 
                       'instrumentalness', 'liveness', 'speechiness', 'loudness', 'popularity']
        corr_matrix = df_corr[numeric_cols].corr()
        
        fig_heat = px.imshow(
            corr_matrix, 
            text_auto=".2f",
            color_continuous_scale='RdBu_r', 
            aspect="auto",
            title="Pearson Correlation Coefficient Matrix"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
