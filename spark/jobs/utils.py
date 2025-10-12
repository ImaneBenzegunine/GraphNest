from neo4j import GraphDatabase

def neo4j_write(rows, query, uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for row in rows:
            session.run(query, parameters=row.asDict())
    driver.close()