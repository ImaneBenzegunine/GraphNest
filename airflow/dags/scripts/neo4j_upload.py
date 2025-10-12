from neo4j import GraphDatabase
import pandas as pd
import os


def upload_to_neo4j(clean_dir):
    uri = "bolt://neo4j:7687"
    auth = ("neo4j", "StrongPass123")

    driver = GraphDatabase.driver(uri, auth=auth)

    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

            # Companies
            company_file = os.path.join(clean_dir, 'companies_clean.csv')
            if os.path.exists(company_file):
                df = pd.read_csv(company_file)
                for _, row in df.iterrows():
                    session.run("""
                        CREATE (c:Company {id: $id, name: $name, required_skills: $skills})
                    """, {
                        'id': row['company_id'],
                        'name': row['name'],
                        'skills': row['required_skills']
                    })

            # TODO: Repeat for users, jobs, employment...

    finally:
        driver.close()
