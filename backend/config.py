"""
Configuration centralisée pour l'API
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password123"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "music_recommendation"
    
    # API
    API_TITLE: str = "Music Recommendation API"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()