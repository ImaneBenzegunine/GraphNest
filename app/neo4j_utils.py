from neo4j import GraphDatabase
import os

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def get_recommendations(user_id):
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_SKILL]->(s:Skill)
    MATCH (j:Job)-[:REQUIRES_SKILL]->(s)
    RETURN j.title AS job, count(s) AS matching_skills
    ORDER BY matching_skills DESC
    LIMIT 10
    """
    with driver.session() as session:
        result = session.run(query, user_id=user_id)
        return [dict(record) for record in result]