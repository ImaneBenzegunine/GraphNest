from neo4j import GraphDatabase

def get_top_connected_users(limit=5):
    driver = GraphDatabase.driver("bolt://neo4j:7687", 
                                auth=("neo4j", "root"))
    
    query = """
    MATCH (u:User)
    RETURN u.id as user, u.connection_count as connections
    ORDER BY connections DESC
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]