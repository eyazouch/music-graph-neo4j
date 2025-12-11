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
            error_msg = f"Connection error: {str(e)}"
            if "Connection refused" in str(e):
                error_msg += " (Is the backend running on http://localhost:8000?)"
            return {"error": error_msg}
    
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
        return self._get("/neo4j/genres/evolution")
    
    # MongoDB endpoints
    def get_mongodb_stats(self) -> Dict:
        return self._get("/mongodb/stats")
    
    def get_audio_distribution(self) -> Dict:
        return self._get("/mongodb/audio/distribution")
    
    def get_genre_audio_profiles(self) -> List[Dict]:
        return self._get("/mongodb/audio/genre-profiles")
    
    def get_mood_clusters(self) -> List[Dict]:
        return self._get("/mongodb/audio/mood-clusters")
    
    def get_track_details(self, track_id: str) -> Dict:
        return self._get(f"/mongodb/track/{track_id}")
    
    def find_similar_tracks(self, track_id: str, limit: int = 10) -> List[Dict]:
        return self._get(f"/mongodb/similar/{track_id}", {"limit": limit})
    
    # Health check
    def health_check(self) -> Dict:
        return self._get("/health")