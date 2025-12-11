"""
Routes API pour MongoDB
"""
from fastapi import APIRouter, HTTPException
from services.mongodb_service import mongodb_service

router = APIRouter(prefix="/mongodb", tags=["MongoDB"])

@router.get("/stats")
async def get_mongodb_stats():
    """Statistiques MongoDB"""
    try:
        return mongodb_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/distribution")
async def get_audio_distribution():
    """Distribution des audio features"""
    try:
        return mongodb_service.get_audio_features_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/genre-profiles")
async def get_genre_audio_profiles():
    """Profils audio par genre"""
    try:
        return mongodb_service.get_genre_audio_profiles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/mood-clusters")
async def get_mood_clusters():
    """Clusters de mood (énergie x valence)"""
    try:
        return mongodb_service.get_energy_valence_clusters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/track/{track_id}")
async def get_track(track_id: str):
    """Détails d'une track"""
    try:
        track = mongodb_service.get_track_by_id(track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{track_id}")
async def find_similar(track_id: str, limit: int = 10):
    """Tracks similaires par audio features"""
    try:
        return mongodb_service.find_similar_by_audio(track_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))