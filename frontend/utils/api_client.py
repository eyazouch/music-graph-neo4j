"""
Client API pour communiquer avec le backend FastAPI
"""
import requests
from typing import Dict, List, Any, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Requête GET générique"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # More helpful error for connection refused
            if "Max retries exceeded" in str(e):
                return {"error": "Connection refused. Is the Backend running on http://localhost:8000?"}
            return {"error": str(e)}

    def _post(self, endpoint: str, json_data: Dict = None) -> Any:
        """Requête POST générique"""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=json_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    # Neo4j endpoints
    def get_neo4j_stats(self) -> Dict:
        return self._get("/neo4j/stats")
    
    def get_top_genres(self, limit: int = 10) -> List[Dict]:
        return self._get("/neo4j/genres/top", {"limit": limit})
    
    def get_top_artists(self, limit: int = 10) -> List[Dict]:
        return self._get("/neo4j/artists/top", {"limit": limit})
    
    def get_artist_network(self, artist_name: str) -> List[Dict]:
        return self._get(f"/neo4j/artist/network/{artist_name}")
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Dict]:
        return self._get("/neo4j/search", {"q": query, "limit": limit})
    
    def get_genre_evolution(self) -> List[Dict]:
        """Evolution des genres"""
        return self._get("/neo4j/genres/evolution")

    def get_all_genres(self) -> List[str]:
        """Liste de tous les genres"""
        return self._get("/neo4j/genres/all")

    def get_artists_by_genre(self, genre: str) -> List[str]:
        """Artistes par genre"""
        return self._get(f"/neo4j/artists/by-genre/{genre}")

    def get_recommendations_by_selection(self, genre: str, artist: str) -> List[Dict]:
        """Recommandations par sélection"""
        return self._get("/neo4j/recommendations/by-selection", params={"genre": genre, "artist": artist})

    def get_network_advanced(self, genres: List[str], artists: List[str]) -> Dict:
        """Structure du graphe avancé"""
        return self._post("/neo4j/network/advanced", json_data={"genres": genres, "artists": artists})

    def get_recommendations_advanced(self, genres: List[str], artists: List[str], years: List[int]) -> List[Dict]:
        """Recommandations avancées"""
        return self._post("/neo4j/recommendations/advanced", json_data={"genres": genres, "artists": artists, "years": years})

    # MongoDB endpoints
    def get_mongodb_stats(self) -> Dict:
        return self._get("/mongodb/stats")
    
    def get_audio_distribution(self) -> Dict:
        return self._get("/mongodb/audio/distribution")
    
    def get_genre_audio_profiles(self) -> List[Dict]:
        return self._get("/mongodb/audio/genre-profiles")
    
    def get_audio_evolution(self) -> List[Dict]:
        """Evolution temporelle"""
        return self._get("/mongodb/analytics/evolution")

    def get_feature_correlations(self) -> List[Dict]:
        """Données de corrélation"""
        return self._get("/mongodb/analytics/correlations")
    
    def get_mood_clusters(self) -> List[Dict]:
        return self._get("/mongodb/audio/mood-clusters")
    
    def get_track_details(self, track_id: str) -> Dict:
        return self._get(f"/mongodb/track/{track_id}")
    
    def find_similar_tracks(self, track_id: str, limit: int = 10) -> List[Dict]:
        return self._get(f"/mongodb/similar/{track_id}", {"limit": limit})
    
    # Health check
    def health_check(self) -> Dict:
        return self._get("/health")