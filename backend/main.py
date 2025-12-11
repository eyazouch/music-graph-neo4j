"""
FastAPI Backend pour Music Recommendation System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import neo4j_routes, mongodb_routes
from config import settings

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API Backend pour système de recommandation musicale NoSQL"
)

# CORS pour Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(neo4j_routes.router)
app.include_router(mongodb_routes.router)

@app.get("/")
async def root():
    return {
        "message": "Music Recommendation API",
        "version": settings.API_VERSION,
        "endpoints": {
            "neo4j": "/neo4j",
            "mongodb": "/mongodb",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}