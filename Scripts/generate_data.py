from faker import Faker
from faker.providers import DynamicProvider
import random
import pandas as pd
import os, path
from path import BASE_DIR, PATH_GENE_DATA
from pathlib import Path  # Better path handling than os.path

# Custom providers
professional_skills = DynamicProvider(
    provider_name="professional_skills",
    elements=["Python", "Spark", "OrientDB", "SQL", "Data Engineering", 
              "Machine Learning", "Java", "Scala", "Pandas", "PySpark"]
)

internship_types = DynamicProvider(
    provider_name="internship",
    elements=["PFA", "PFE", "Summer Internship", "Research Internship"]
)

job_titles = DynamicProvider(
    provider_name="job_titles",
    elements=["Data Engineer", "Graph Analyst", "ETL Developer", 
             "Data Scientist", "ML Engineer", "Database Admin"]
)

companies = DynamicProvider(
    provider_name="company",
    elements=["IBM", "Oracle", "AWS", "Meta", "Accenture", 
              "Google", "Microsoft", "Amazon"]
)

fake = Faker()
fake.add_provider(professional_skills)
fake.add_provider(job_titles)
fake.add_provider(companies)
fake.add_provider(internship_types)


def generate_user(num_users=100):
    """Generate user data with skill ratings (1-5)"""
    users = []
    for _ in range(num_users):
        # Generate between 3-8 skills with ratings 1-5
        num_skills = random.randint(3, 8)
        skills = {skill: random.randint(1, 5) for skill in random.sample(professional_skills.elements, num_skills)}
        
        users.append({
            "user_id": fake.unique.random_number(digits=8),
            "name": fake.name(),
            "email": fake.email(),
            "job_title": fake.job_titles(),
            "company": fake.company(),
            "skills": skills,
            "company": fake.company(),
            "position": fake.job_titles(),
            "duration_years": random.randint(1, 5),
            "skills_used": random.sample(
                        list(skills.keys()), 
                        min(random.randint(2, 5), len(skills))  # Take the smaller value
                    )
                
        })
    return pd.DataFrame(users)
def generate_company(num_companies=20):
    """Generate company data with current employees"""
    companies = []
    for _ in range(num_companies):
        company_name = fake.company()
        companies.append({
            "company_id": fake.unique.random_number(digits=6),
            "name": company_name,
            "position": fake.job_titles(),
            "required_skills": {skill: random.randint(3, 5) for skill in random.sample(professional_skills.elements, random.randint(3, 5))}
                
        })
    return pd.DataFrame(companies)

def generate_jobs(num_jobs=50):
    """Generate job postings with skill requirements"""
    jobs = []
    for _ in range(num_jobs):
        job_type = random.choice(["Full-time", "Part-time", "Contract", "Internship"])
        jobs.append({
            "job_id": fake.unique.random_number(digits=4),
            "company": fake.company(),
            "title": fake.job_titles(),
            "type": job_type,
            "salary": random.randint(10000, 90000) if job_type != "Internship" else random.randint(1000, 5000),
            "required_skills": {skill: random.randint(3, 5) for skill in random.sample(professional_skills.elements, random.randint(3, 5))},
            "is_internship": job_type == "Internship",
            "internship_type": fake.internship() if job_type == "Internship" else None
        })
    return pd.DataFrame(jobs)

def generate_employment_history(users_df, companies_df, num_connections=200):
    """Generate employment relationships between users and companies"""
    employment = []
    for _ in range(num_connections):
        user = random.choice(users_df['user_id'])
        company = random.choice(companies_df['company_id'])
        employment.append({
            "employment_id": fake.unique.random_number(digits=5),
            "user_id": user,
            "company_id": company,
            "position": fake.job_titles(),
            "start_date": fake.date_this_decade(),
            "end_date": fake.date_this_decade() if random.random() > 0.7 else None,  # 30% chance of being current
            "skills_used": random.sample(professional_skills.elements, random.randint(2, 5))
        })
    return pd.DataFrame(employment)

#save the data

 
import shutil


def save_data(data_dict, output_dir=PATH_GENE_DATA):
    """Save all generated DataFrames to CSV files in specified directory
    
    Args:
        data_dict (dict): Dictionary of {name: DataFrame} pairs
        output_dir (str): Directory path to save files
        prefix (str): Prefix for all filenames
    """
    # Convert to Path object if it's not already
    output_path = Path(output_dir)
    
    # Remove directory if it exists
    if output_path.exists() and output_path.is_dir():
        shutil.rmtree(output_path)
    
    # Create directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    for name, df in data_dict.items():
        # Create full filepath
        filename = f'{name}.csv'
        filepath = os.path.join(output_dir, filename)
        
        # Save with proper path handling
        df.to_csv(filepath, index=False)
        print(f"Saved {filename} to {output_dir}")


# Generate the data
print("Generating sample data...")
users_df = generate_user(100)  # 100 users
companies_df = generate_company(20)  # 20 companies
jobs_df = generate_jobs(50)  # 50 job postings
employment_df = generate_employment_history(users_df, companies_df, 200)  # 200 employment records

# Save to CSV
data = {
    'users': users_df,
    'companies': companies_df,
    'jobs': jobs_df,
    'employment': employment_df
}
save_data(data)
print("Data generation complete! Saved to CSV files.")
