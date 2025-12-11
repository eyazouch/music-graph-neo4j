"""
Service pour les opérations MongoDB
"""
from pymongo import MongoClient
from typing import List, Dict, Any
from config import settings

class MongoDBService:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB]
        self.tracks = self.db.tracks
    
    def close(self):
        self.client.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistiques MongoDB"""
        try:
            return {
                "total_tracks": self.tracks.count_documents({}),
                "database_size": self.db.command("dbStats")["dataSize"],
                "collections": self.db.list_collection_names()
            }
        except Exception as e:
            print(f"Error getting MongoDB stats: {e}")
            return {"error": str(e)}
    
    def get_audio_features_distribution(self) -> Dict[str, Any]:
        """Distribution des audio features (pour visualisation créative)"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_danceability": {"$avg": "$danceability"},
                    "avg_energy": {"$avg": "$energy"},
                    "avg_valence": {"$avg": "$valence"},
                    "avg_acousticness": {"$avg": "$acousticness"},
                    "avg_instrumentalness": {"$avg": "$instrumentalness"},
                    "avg_liveness": {"$avg": "$liveness"},
                    "avg_speechiness": {"$avg": "$speechiness"}
                }
            }
        ]
        result = list(self.tracks.aggregate(pipeline))
        return result[0] if result else {}
    
    def get_genre_audio_profiles(self) -> List[Dict[str, Any]]:
        """Profil audio moyen par genre (MongoDB aggregation)"""
        try:
            pipeline = [
                {
                    "$unwind": "$genres"
                },
                {
                    "$group": {
                        "_id": "$genres",
                        "danceability": {"$avg": "$danceability"},
                        "energy": {"$avg": "$energy"},
                        "valence": {"$avg": "$valence"},
                        "acousticness": {"$avg": "$acousticness"},
                        "tempo": {"$avg": "$tempo"},
                        "track_count": {"$sum": 1}
                    }
                },
                {
                    "$match": {"track_count": {"$gte": 50}}
                },
                {
                    "$sort": {"track_count": -1}
                },
                {
                    "$limit": 15
                }
            ]
            return list(self.tracks.aggregate(pipeline))
        except Exception as e:
            print(f"Error in get_genre_audio_profiles: {e}")
            # Return empty list instead of crashing, handling the missing 'genres' field case
            return []
    
    def get_energy_valence_clusters(self) -> List[Dict[str, Any]]:
        """Clusters énergie x valence (mood mapping)"""
        pipeline = [
            {
                "$project": {
                    "track_name": 1,
                    "artist_name": 1,
                    "energy": 1,
                    "valence": 1,
                    "popularity": 1,
                    "mood": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$and": [
                                            {"$gte": ["$energy", 0.7]},
                                            {"$gte": ["$valence", 0.7]}
                                        ]
                                    },
                                    "then": "Euphoric"
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$gte": ["$energy", 0.7]},
                                            {"$lt": ["$valence", 0.3]}
                                        ]
                                    },
                                    "then": "Angry"
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$lt": ["$energy", 0.3]},
                                            {"$gte": ["$valence", 0.7]}
                                        ]
                                    },
                                    "then": "Peaceful"
                                },
                                {
                                    "case": {
                                        "$and": [
                                            {"$lt": ["$energy", 0.3]},
                                            {"$lt": ["$valence", 0.3]}
                                        ]
                                    },
                                    "then": "Sad"
                                }
                            ],
                            "default": "Neutral"
                        }
                    }
                }
            },
            {
                "$sample": {"size": 1000}
            }
        ]
        return list(self.tracks.aggregate(pipeline))
    
    def get_track_by_id(self, track_id: str) -> Dict[str, Any]:
        """Récupérer une track par ID"""
        return self.tracks.find_one({"track_id": track_id}, {"_id": 0})
    
    def find_similar_by_audio(self, track_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Trouver des tracks similaires par audio features"""
        track = self.get_track_by_id(track_id)
        if not track:
            return []
        
        # Recherche par similarité (simple distance euclidienne simulée)
        pipeline = [
            {
                "$match": {
                    "track_id": {"$ne": track_id},
                    "danceability": {
                        "$gte": track["danceability"] - 0.2,
                        "$lte": track["danceability"] + 0.2
                    },
                    "energy": {
                        "$gte": track["energy"] - 0.2,
                        "$lte": track["energy"] + 0.2
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "track_id": 1,
                    "track_name": 1,
                    "artist_name": 1,
                    "danceability": 1,
                    "energy": 1,
                    "valence": 1
                }
            },
            {
                "$limit": limit
            }
        ]
        return list(self.tracks.aggregate(pipeline))

# Instance globale
mongodb_service = MongoDBService()