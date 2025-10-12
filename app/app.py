import streamlit as st
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "StrongPass123"))

def get_users():
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u.name as name LIMIT 10")
        return [record["name"] for record in result]

st.title("Professional Network")
st.write("Top users:")
st.write(get_users())