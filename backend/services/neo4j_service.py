"""
Service pour les opérations Neo4j
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any
from config import settings

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        self.driver.close()
    
    def get_stats(self) -> Dict[str, int]:
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Track) WITH count(t) as tracks
                    MATCH (a:Artist) WITH tracks, count(a) as artists
                    MATCH (g:Genre) WITH tracks, artists, count(g) as genres
                    MATCH ()-[r]->() 
                    RETURN tracks, artists, genres, count(r) as relationships
                """)
                record = result.single()
                return {
                    "tracks": record["tracks"],
                    "artists": record["artists"],
                    "genres": record["genres"],
                    "relationships": record["relationships"]
                }
        except Exception as e:
            print(f"Neo4j Error (get_stats): {e}")
            return {"tracks": 0, "artists": 0, "genres": 0, "relationships": 0, "error": str(e)}
    
    def get_top_genres(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Top genres par nombre de tracks"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Track)-[:HAS_GENRE]->(g:Genre)
                    RETURN g.name as genre, count(t) as track_count
                    ORDER BY track_count DESC
                    LIMIT $limit
                """, limit=limit)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_top_genres): {e}")
            return []
    
    def get_top_artists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Top artistes par popularité moyenne"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Artist)<-[:PERFORMED_BY]-(t:Track)
                    RETURN a.name as artist, 
                           count(t) as track_count,
                           avg(t.popularity) as avg_popularity
                    ORDER BY avg_popularity DESC
                    LIMIT $limit
                """, limit=limit)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_top_artists): {e}")
            return []
    
    def get_artist_network(self, artist_name: str, depth: int = 2) -> Dict[str, Any]:
        """Réseau de collaboration d'un artiste (via genres communs)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a1:Artist {name: $artist_name})-[:PERFORMS]->(g:Genre)
                      <-[:PERFORMS]-(a2:Artist)
                WHERE a1 <> a2
                WITH a1, a2, collect(g.name) as common_genres
                RETURN a1.name as artist, a2.name as related_artist, 
                       common_genres, size(common_genres) as similarity
                ORDER BY similarity DESC
                LIMIT 20
            """, artist_name=artist_name)
            return [dict(record) for record in result]
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Recherche de tracks par nom"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist)
                WHERE toLower(t.name) CONTAINS toLower($query)
                   OR toLower(a.name) CONTAINS toLower($query)
                RETURN t.track_id as id, t.name as track, a.name as artist, 
                       t.popularity as popularity, t.year as year
                ORDER BY t.popularity DESC
                LIMIT $limit
            """, query=query, limit=limit)
            return [dict(record) for record in result]
    
    def get_genre_evolution(self) -> List[Dict[str, Any]]:
        """Évolution des genres par année"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (t:Track)-[:HAS_GENRE]->(g:Genre)
                    WHERE t.year IS NOT NULL
                    WITH g.name as genre, t.year as year, count(t) as tracks
                    WHERE year >= 2000 AND year <= 2023
                    RETURN genre, year, tracks
                    ORDER BY year, tracks DESC
                """)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_genre_evolution): {e}")
            return []

    def get_all_genres(self) -> List[str]:
        """Retourne la liste de tous les genres"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (g:Genre)
                    RETURN g.name as name
                    ORDER BY name
                """)
                return [record["name"] for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_all_genres): {e}")
            return []

    def get_artists_by_genre(self, genre: str) -> List[str]:
        """Retourne la liste des artistes pour un genre donné"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Artist)-[:PERFORMS]->(g:Genre {name: $genre})
                    RETURN DISTINCT a.name as name
                    ORDER BY name
                """, genre=genre)
                return [record["name"] for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_artists_by_genre): {e}")
            return []

    def get_recommendations_by_selection(self, genre: str, artist: str) -> List[Dict[str, Any]]:
        """Recommandations basées sur le genre et l'artiste sélectionnés"""
        try:
            with self.driver.session() as session:
                # Récupère les tracks de l'artiste dans ce genre (ou juste de l'artiste)
                # Et aussi quelques tracks similaires du même genre mais d'autres artistes
                result = session.run("""
                    MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist {name: $artist})
                    OPTIONAL MATCH (t)-[:HAS_GENRE]->(g:Genre {name: $genre})
                    RETURN t.track_id as id, t.name as track, a.name as artist, 
                           t.popularity as popularity, t.year as year
                    ORDER BY t.popularity DESC
                    LIMIT 10
                """, genre=genre, artist=artist)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_recommendations_by_selection): {e}")
            return []

    def get_network_structure(self, genres: List[str], artists: List[str]) -> Dict[str, Any]:
        """Récupère la structure du réseau pour visualisation"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    // Trouve les noeuds sélectionnés et leurs relations directes
                    MATCH (a:Artist)-[:PERFORMS]->(g:Genre)
                    WHERE (g.name IN $genres OR a.name IN $artists)
                    AND (a.name IN $artists OR g.name IN $genres)
                    
                    // Retourne les noeuds et relations
                    RETURN collect(DISTINCT {id: 'g_' + g.name, label: g.name, type: 'genre'}) as genre_nodes,
                           collect(DISTINCT {id: 'a_' + a.name, label: a.name, type: 'artist'}) as artist_nodes,
                           collect(DISTINCT {source: 'a_' + a.name, target: 'g_' + g.name}) as links
                    LIMIT 25
                """, genres=genres, artists=artists)
                
                record = result.single()
                if not record:
                    return {"nodes": [], "links": []}
                
                nodes = record['genre_nodes'] + record['artist_nodes']
                links = record['links']
                return {"nodes": nodes, "links": links}
        except Exception as e:
            print(f"Neo4j Error (get_network_structure): {e}")
            return {"nodes": [], "links": []}

    def get_advanced_recommendations(self, genres: List[str], artists: List[str], years: List[int]) -> List[Dict[str, Any]]:
        """Recommandations avancées avec filtres multiples"""
        try:
            with self.driver.session() as session:
                # Construit la query dynamique selon les filtres présents
                query = """
                    MATCH (t:Track)-[:PERFORMED_BY]->(a:Artist)
                    MATCH (t)-[:HAS_GENRE]->(g:Genre)
                    WHERE 1=1
                """
                params = {}
                
                if genres:
                    query += " AND g.name IN $genres"
                    params['genres'] = genres
                
                if artists:
                    query += " AND a.name IN $artists"
                    params['artists'] = artists
                    
                if years:
                    query += " AND t.year IN $years"
                    params['years'] = years
                
                query += """
                    RETURN DISTINCT t.track_id as id, t.name as track, a.name as artist, 
                           g.name as genre, t.year as year, t.popularity as popularity
                    ORDER BY t.popularity DESC
                    LIMIT 20
                """
                
                result = session.run(query, **params)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Neo4j Error (get_advanced_recommendations): {e}")
            return []

# Instance globale
neo4j_service = Neo4jService()