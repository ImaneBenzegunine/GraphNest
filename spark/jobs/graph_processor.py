from pyspark.sql import SparkSession
from utils import neo4j_write

def process_network():  
    spark = SparkSession.builder.appName("NetworkETL").getOrCreate()
    
    # Read raw connections
    df = spark.read.csv("/data/clean_data/users_clean.csv", header=True)
    
    # Calculate connection counts
    connections = df.groupBy("user_id").count()
    
    # Write to Neo4j
    connections.foreachPartition(
        lambda rows: neo4j_write(
            rows, 
            "MERGE (u:User {id: $id}) SET u.connection_count = $count",
            "bolt://neo4j:7687",
            "neo4j",
            "root"
        )
    )

if __name__ == "__main__":
    process_network()