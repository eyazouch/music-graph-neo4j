"""
Routes API pour Neo4j
"""
from fastapi import APIRouter, HTTPException
from services.neo4j_service import neo4j_service

router = APIRouter(prefix="/neo4j", tags=["Neo4j"])

@router.get("/stats")
async def get_neo4j_stats():
    """Statistiques de la base Neo4j"""
    try:
        return neo4j_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres/top")
async def get_top_genres(limit: int = 10):
    """Top genres par nombre de tracks"""
    try:
        return neo4j_service.get_top_genres(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists/top")
async def get_top_artists(limit: int = 10):
    """Top artistes par popularité"""
    try:
        return neo4j_service.get_top_artists(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artist/network/{artist_name}")
async def get_artist_network(artist_name: str):
    """Réseau de collaboration d'un artiste"""
    try:
        return neo4j_service.get_artist_network(artist_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_tracks(q: str, limit: int = 20):
    """Recherche de tracks"""
    try:
        return neo4j_service.search_tracks(q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres/evolution")
async def get_genre_evolution():
    """Évolution des genres par année"""
    try:
        return neo4j_service.get_genre_evolution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))