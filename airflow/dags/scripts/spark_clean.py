from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import MapType, StringType
import ast

# Register UDF for cleaning skills
def clean_skills(skills_str):
    try:
        if not skills_str or skills_str.lower() == 'nan':
            return {}
        return ast.literal_eval(skills_str.replace("'", "\""))
    except:
        print(f"Failed to parse: {skills_str}")
        return {}

clean_skills_udf = udf(clean_skills, MapType(StringType(), StringType()))

def clean_data(spark, input_path, output_path):
    # Read all CSV files
    companies = spark.read.csv(f"{input_path}/companies.csv", header=True)
    employment = spark.read.csv(f"{input_path}/employment.csv", header=True)
    jobs = spark.read.csv(f"{input_path}/jobs.csv", header=True)
    users = spark.read.csv(f"{input_path}/users.csv", header=True)

    # Clean each DataFrame
    companies_clean = companies.withColumn("required_skills", clean_skills_udf(companies["required_skills"]))
    employment_clean = employment.withColumn("skills_used", clean_skills_udf(employment["skills_used"]))
    jobs_clean = jobs.withColumn("required_skills", clean_skills_udf(jobs["required_skills"]))
    users_clean = users.withColumn("skills", clean_skills_udf(users["skills"])) \
                      .withColumn("skills_used", clean_skills_udf(users["skills_used"]))

    # Write cleaned DataFrames
    companies_clean.write.mode("overwrite").csv(f"{output_path}/companies_clean")
    employment_clean.write.mode("overwrite").csv(f"{output_path}/employment_clean")
    jobs_clean.write.mode("overwrite").csv(f"{output_path}/jobs_clean")
    users_clean.write.mode("overwrite").csv(f"{output_path}/users_clean")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("ProfessionalNetworkCleaner") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
        .getOrCreate()
    
    import sys
    clean_data(spark, sys.argv[1], sys.argv[2])
    spark.stop()