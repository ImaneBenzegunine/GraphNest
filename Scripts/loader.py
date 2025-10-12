import os
import pyorient
import pandas as pd
import ast

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
CLEAN_DATA_DIR = os.path.join(BASE_DIR, "data", "clean_data")

# Docker-compatible path fallback
if not os.path.exists(CLEAN_DATA_DIR):
    CLEAN_DATA_DIR = "/app/data"  # Fallback to Docker volume path

# OrientDB Configuration
ORIENTDB_HOST = os.getenv('ORIENTDB_HOST', 'orientdb')
ORIENTDB_PORT = int(os.getenv('ORIENTDB_PORT', 2480))
DB_NAME = os.getenv('ORIENTDB_DB', 'database_1')
DB_USER = os.getenv('ORIENTDB_USER', 'root')
DB_PASSWORD = os.getenv('ORIENTDB_PASSWORD', 'admin')

def get_data_path(filename):
    """Get cross-platform compatible data path"""
    local_path = os.path.join(CLEAN_DATA_DIR, filename)
    if os.path.exists(local_path):
        return local_path
    return os.path.join("/data", filename)  # Docker fallback

def connect_to_orientdb():
    """Establish connection to OrientDB with environment awareness"""
    max_retries = 3
    is_docker = os.path.exists('/.dockerenv')  # Check if running in Docker
    
    for attempt in range(max_retries):
        try:
            host = ORIENTDB_HOST if is_docker else 'localhost'
            client = pyorient.OrientDB(host, ORIENTDB_PORT)
            
            # Remove the serialization_type parameter as it's not supported in newer pyorient versions
            session_id = client.connect(DB_USER, DB_PASSWORD)
            
            if not client.db_exists(DB_NAME):
                print(f"Creating database {DB_NAME}...")
                client.db_create(DB_NAME, pyorient.DB_TYPE_GRAPH, pyorient.STORAGE_TYPE_PLOCAL)
            
            client.db_open(DB_NAME, DB_USER, DB_PASSWORD)
            return client
            
        except pyorient.PyOrientWrongProtocolVersionException:
            if is_docker:
                raise RuntimeError("Incompatible OrientDB version. Use image: orientdb:3.1.10")
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Connection failed (attempt {attempt + 1}), retrying...")
            time.sleep(10)

def safe_literal_eval(data):
    """Safely evaluate string containing Python literal structures"""
    try:
        return ast.literal_eval(data) if pd.notna(data) else {}
    except (ValueError, SyntaxError):
        return {}

def create_vertex(client, class_name, properties):
    """Safe vertex creation with parameterized query"""
    placeholders = ", ".join([f"{k} = :{k}" for k in properties.keys()])
    query = f"CREATE VERTEX {class_name} SET {placeholders}"
    client.command(query, {k: str(v) if isinstance(v, (dict, list)) else v 
                         for k, v in properties.items()})

def create_edge(client, edge_class, from_rid, to_rid, properties):
    """Safe edge creation with parameterized query"""
    placeholders = ", ".join([f"{k} = :{k}" for k in properties.keys()])
    query = f"CREATE EDGE {edge_class} FROM {from_rid} TO {to_rid} SET {placeholders}"
    client.command(query, properties)

def load_data(client):
    """Load all data into OrientDB"""
    # Load Users
    users_df = pd.read_csv(f"{CLEAN_DATA_DIR}/users_clean.csv")
    for _, row in users_df.iterrows():
        create_vertex(client, "User", {
            'user_id': row['user_id'],
            'name': row['name'],
            'email': row['email'],
            'job_title': row['job_title'],
            'company': row['company'],
            'skills': safe_literal_eval(row['skills'])
        })

    # Load Companies
    companies_df = pd.read_csv(f"{CLEAN_DATA_DIR}/companies_clean.csv")
    for _, row in companies_df.iterrows():
        create_vertex(client, "Company", {
            'company_id': row['company_id'],
            'name': row['name'],
            'position': row['position'],
            'required_skills': safe_literal_eval(row['required_skills'])
        })

    # Load Jobs
    jobs_df = pd.read_csv(f"{CLEAN_DATA_DIR}/jobs_clean.csv")
    for _, row in jobs_df.iterrows():
        create_vertex(client, "Job", {
            'job_id': row['job_id'],
            'company': row['company'],
            'title': row['title'],
            'type': row['type'],
            'salary': row['salary'],
            'required_skills': safe_literal_eval(row['required_skills']),
            'is_internship': row['is_internship']
        })

    # Create Employment Edges
    employment_df = pd.read_csv(f"{CLEAN_DATA_DIR}/employment_clean.csv")
    for _, row in employment_df.iterrows():
        user = client.query(f"SELECT FROM User WHERE user_id = {row['user_id']}")
        company = client.query(f"SELECT FROM Company WHERE company_id = {row['company_id']}")
        if user and company:
            create_edge(client, "Employment", 
                       user[0]._rid, 
                       company[0]._rid, {
                'position': row['position'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'skills_used': safe_literal_eval(row['skills_used'])
            })
     # Similarly for other files:
    companies_df = pd.read_csv(get_data_path("companies_clean.csv"))
    jobs_df = pd.read_csv(get_data_path("jobs_clean.csv"))
    employment_df = pd.read_csv(get_data_path("employment_clean.csv"))
def main():
    client = None
    try:
        print("Connecting to OrientDB...")
        client = connect_to_orientdb()
        print("Loading data...")
        load_data(client)
        print("Data loading completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        if client:
            client.db_close()

if __name__ == "__main__":
    import time  # For retry delays
    main()