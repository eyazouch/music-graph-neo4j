"""
Visualisations créatives pour MongoDB et Neo4j
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict

def create_radar_chart(data: Dict, title: str = "Audio Features Profile"):
    """Radar chart pour profil audio"""
    categories = ['Danceability', 'Energy', 'Valence', 'Acousticness', 
                  'Instrumentalness', 'Liveness', 'Speechiness']
    
    values = [
        data.get('avg_danceability', 0),
        data.get('avg_energy', 0),
        data.get('avg_valence', 0),
        data.get('avg_acousticness', 0),
        data.get('avg_instrumentalness', 0),
        data.get('avg_liveness', 0),
        data.get('avg_speechiness', 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Average',
        line=dict(color='#1DB954', width=2),
        fillcolor='rgba(29, 185, 84, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=False,
        title=title,
        height=500
    )
    
    return fig

def create_genre_radar_comparison(genres_data: List[Dict], top_n: int = 5):
    """Comparer plusieurs genres en radar chart"""
    fig = go.Figure()
    
    categories = ['Danceability', 'Energy', 'Valence', 'Acousticness']
    colors = px.colors.qualitative.Set2
    
    for idx, genre in enumerate(genres_data[:top_n]):
        values = [
            genre.get('danceability', 0),
            genre.get('energy', 0),
            genre.get('valence', 0),
            genre.get('acousticness', 0)
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=genre['_id'],
            line=dict(color=colors[idx % len(colors)], width=2)
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Genre Audio Profiles Comparison",
        height=600
    )
    
    return fig

def create_mood_scatter(mood_data: List[Dict]):
    """Scatter plot Energy vs Valence (Mood Mapping)"""
    df = pd.DataFrame(mood_data)
    
    fig = px.scatter(
        df,
        x='valence',
        y='energy',
        color='mood',
        size='popularity',
        hover_data=['track_name', 'artist_name'],
        title="Mood Map: Energy vs Valence",
        labels={'valence': 'Valence (Positivity)', 'energy': 'Energy'},
        color_discrete_map={
            'Euphoric': '#1DB954',
            'Angry': '#E74C3C',
            'Peaceful': '#3498DB',
            'Sad': '#9B59B6',
            'Neutral': '#95A5A6'
        },
        height=600
    )
    
    # Ajouter des lignes de séparation
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.3)
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray", opacity=0.3)
    
    # Annotations des quadrants
    fig.add_annotation(x=0.85, y=0.85, text="😁 Euphoric", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.15, y=0.85, text="😠 Angry", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.85, y=0.15, text="😌 Peaceful", showarrow=False, font=dict(size=14))
    fig.add_annotation(x=0.15, y=0.15, text="😢 Sad", showarrow=False, font=dict(size=14))
    
    fig.update_layout(
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1])
    )
    
    return fig

def create_genre_evolution_chart(evolution_data: List[Dict]):
    """Évolution des genres dans le temps"""
    df = pd.DataFrame(evolution_data)
    
    # Top 8 genres
    top_genres = df.groupby('genre')['tracks'].sum().nlargest(8).index
    df_filtered = df[df['genre'].isin(top_genres)]
    
    fig = px.line(
        df_filtered,
        x='year',
        y='tracks',
        color='genre',
        title="Genre Evolution Over Time",
        labels={'year': 'Year', 'tracks': 'Number of Tracks'},
        height=500
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=2),
        hovermode='x unified'
    )
    
    return fig

def create_network_graph(network_data: List[Dict], center_artist: str):
    """Graphe de réseau d'artistes (Neo4j visualization)"""
    if not network_data:
        return None
    
    # Créer les noeuds et liens
    nodes = set([center_artist])
    edges = []
    
    for record in network_data:
        nodes.add(record['related_artist'])
        edges.append({
            'source': center_artist,
            'target': record['related_artist'],
            'weight': record['similarity']
        })
    
    # Positions circulaires
    import math
    n = len(nodes)
    node_list = list(nodes)
    
    # Position centrale pour l'artiste principal
    node_x = [0]
    node_y = [0]
    node_names = [center_artist]
    node_colors = ['#1DB954']
    
    # Positions circulaires pour les autres (exclure l'artiste principal de la liste des autres)
    other_nodes = [n for n in node_list if n != center_artist]

    for i, node in enumerate(other_nodes, 1):
        angle = 2 * math.pi * i / len(other_nodes) if other_nodes else 0
        node_x.append(math.cos(angle))
        node_y.append(math.sin(angle))
        node_names.append(node)
        node_colors.append('#3498DB')
    
    # Créer les liens
    edge_x = []
    edge_y = []
    
    for edge in edges:
        source_idx = node_names.index(edge['source'])
        target_idx = node_names.index(edge['target'])
        
        edge_x.extend([node_x[source_idx], node_x[target_idx], None])
        edge_y.extend([node_y[source_idx], node_y[target_idx], None])
    
    # Créer la figure
    fig = go.Figure()
    
    # Ajouter les liens
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Ajouter les noeuds
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=20, color=node_colors, line=dict(width=2, color='white')),
        text=node_names,
        textposition='top center',
        hoverinfo='text',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f"Artist Network: {center_artist}",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_audio_feature_bars(genres_data: List[Dict], feature: str = 'energy'):
    """Bar chart pour une feature spécifique par genre"""
    df = pd.DataFrame(genres_data).sort_values(feature, ascending=True)
    
    fig = px.bar(
        df,
        y='_id',
        x=feature,
        orientation='h',
        title=f"{feature.capitalize()} by Genre",
        labels={'_id': 'Genre', feature: feature.capitalize()},
        color=feature,
        color_continuous_scale='Viridis',
        height=600
    )
    
    return fig