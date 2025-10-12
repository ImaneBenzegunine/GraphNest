import os
import pyorient
import pandas as pd
import ast
import time
from path import CLEAN_DATA_DIR
# Configuration
ORIENTDB_HOST = 'localhost'  # or 'orientdb' if running in Docker
ORIENTDB_PORT = 2480
DB_NAME = 'skills_graph'
DB_USER = 'root'
DB_PASSWORD = 'admin'

def safe_literal_eval(data):
    """Safely evaluate string containing Python literal structures"""
    try:
        return ast.literal_eval(data) if pd.notna(data) else {}
    except (ValueError, SyntaxError):
        return {}

def connect_to_orientdb():
    """Establish connection to OrientDB"""
    max_retries = 5
    retry_delay = 10  # seconds
    import socket
    print("*"*50)
    print("Resolved IP:", socket.gethostbyname(ORIENTDB_HOST))
    print("*"*50)
    for attempt in range(max_retries):
        try:
            print(f"Connection attempt {attempt + 1}...")
            
            client = pyorient.OrientDB(ORIENTDB_HOST, ORIENTDB_PORT)
            client.connect(DB_USER, DB_PASSWORD)
            
            if not client.db_exists(DB_NAME, pyorient.STORAGE_TYPE_PLOCAL):
                print(f"Creating database {DB_NAME}...")
                client.db_create(DB_NAME, pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_PLOCAL)
            
            client.db_open(DB_NAME, DB_USER, DB_PASSWORD)
            print("Successfully connected to OrientDB!")
            return client
            
        except Exception as e:
            print(f"Connection failed (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)

def initialize_schema(client):
    """Initialize the database schema"""
    # Vertex classes
    client.command("CREATE CLASS User EXTENDS V")
    client.command("CREATE CLASS Company EXTENDS V")
    client.command("CREATE CLASS Job EXTENDS V")
    client.command("CREATE CLASS Skill EXTENDS V")
    
    # Edge classes
    client.command("CREATE CLASS Employment EXTENDS E")
    client.command("CREATE CLASS HasSkill EXTENDS E")
    client.command("CREATE CLASS RequiresSkill EXTENDS E")
    
    # User properties
    client.command("CREATE PROPERTY User.user_id INTEGER")
    client.command("CREATE PROPERTY User.name STRING")
    client.command("CREATE PROPERTY User.email STRING")
    client.command("CREATE PROPERTY User.job_title STRING")
    client.command("CREATE PROPERTY User.company STRING")
    client.command("CREATE INDEX User.user_id UNIQUE")
    
    # Company properties
    client.command("CREATE PROPERTY Company.company_id INTEGER")
    client.command("CREATE PROPERTY Company.name STRING")
    client.command("CREATE PROPERTY Company.position STRING")
    client.command("CREATE INDEX Company.company_id UNIQUE")
    
    # Job properties
    client.command("CREATE PROPERTY Job.job_id INTEGER")
    client.command("CREATE PROPERTY Job.title STRING")
    client.command("CREATE PROPERTY Job.type STRING")
    client.command("CREATE PROPERTY Job.salary STRING")
    client.command("CREATE PROPERTY Job.is_internship BOOLEAN")
    client.command("CREATE INDEX Job.job_id UNIQUE")
    
    # Skill properties
    client.command("CREATE PROPERTY Skill.name STRING")
    client.command("CREATE INDEX Skill.name UNIQUE")
    
    # Edge properties
    client.command("CREATE PROPERTY Employment.position STRING")
    client.command("CREATE PROPERTY Employment.start_date STRING")
    client.command("CREATE PROPERTY Employment.end_date STRING")
    client.command("CREATE PROPERTY HasSkill.level INTEGER")
    client.command("CREATE PROPERTY RequiresSkill.level INTEGER")

def create_vertex(client, class_name, properties):
    """Create vertex and return RID"""
    placeholders = ", ".join([f"{k} = :{k}" for k in properties.keys()])
    query = f"CREATE VERTEX {class_name} SET {placeholders} RETURN @rid"
    result = client.command(query, properties)
    return result[0]._rid if result else None

def create_edge(client, edge_class, from_rid, to_rid, properties=None):
    """Create edge between vertices"""
    properties = properties or {}
    placeholders = ", ".join([f"{k} = :{k}" for k in properties.keys()])
    set_clause = f"SET {placeholders}" if placeholders else ""
    query = f"CREATE EDGE {edge_class} FROM {from_rid} TO {to_rid} {set_clause}"
    client.command(query, properties)

def get_or_create_skill(client, skill_name):
    """Get or create skill vertex"""
    result = client.command(f"SELECT FROM Skill WHERE name = '{skill_name}'")
    if result:
        return result[0]._rid
    return create_vertex(client, "Skill", {'name': skill_name})

def load_data(client):
    """Load all CSV data into OrientDB"""
    def get_data_path(filename):
        path = os.path.join(CLEAN_DATA_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found: {path}")
        return path

    # Load Users
    users_df = pd.read_csv(get_data_path("users_clean.csv"))
    for _, row in users_df.iterrows():
        user_rid = create_vertex(client, "User", {
            'user_id': int(row['user_id']),
            'name': row['name'],
            'email': row['email'],
            'job_title': row['job_title'],
            'company': row['company']
        })
        
        skills = safe_literal_eval(row['skills'])
        for skill_name, level in skills.items():
            skill_rid = get_or_create_skill(client, skill_name)
            create_edge(client, "HasSkill", user_rid, skill_rid, {'level': int(level)})

    # Load Companies
    companies_df = pd.read_csv(get_data_path("companies_clean.csv"))
    for _, row in companies_df.iterrows():
        company_rid = create_vertex(client, "Company", {
            'company_id': int(row['company_id']),
            'name': row['name'],
            'position': row['position']
        })
        
        skills = safe_literal_eval(row['required_skills'])
        for skill_name, level in skills.items():
            skill_rid = get_or_create_skill(client, skill_name)
            create_edge(client, "RequiresSkill", company_rid, skill_rid, {'level': int(level)})

    # Load Jobs
    jobs_df = pd.read_csv(get_data_path("jobs_clean.csv"))
    for _, row in jobs_df.iterrows():
        job_rid = create_vertex(client, "Job", {
            'job_id': int(row['job_id']),
            'title': row['title'],
            'type': row['type'],
            'salary': row['salary'],
            'is_internship': bool(row['is_internship'])
        })
        
        skills = safe_literal_eval(row['required_skills'])
        for skill_name, level in skills.items():
            skill_rid = get_or_create_skill(client, skill_name)
            create_edge(client, "RequiresSkill", job_rid, skill_rid, {'level': int(level)})

def main():
    client = None
    try:
        client = connect_to_orientdb()
        initialize_schema(client)
        load_data(client)
        print("Data import completed successfully!")
    except Exception as e:
        print(f"Error during import: {str(e)}")
    finally:
        if client:
            client.db_close()

if __name__ == "__main__":
    main()