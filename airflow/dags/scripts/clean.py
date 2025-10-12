import pandas as pd
import ast
from pathlib import Path
import os,sys
def clean_skills(skills_str):
    try:
        if pd.isna(skills_str):
            return {}
        return ast.literal_eval(skills_str.replace("'", "\""))
    except:
        print(f"Failed to parse: {skills_str}")
        return {}

def clean_data(input_dir, output_dir):
    from pathlib import Path

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    companies = pd.read_csv(input_dir / "companies.csv")
    companies['required_skills'] = companies['required_skills'].apply(clean_skills)
    companies.to_csv(output_dir / "companies_clean.csv", index=False)

    employment = pd.read_csv(input_dir / "employment.csv")
    employment['skills_used'] = employment['skills_used'].apply(clean_skills)
    employment.to_csv(output_dir / "employment_clean.csv", index=False)

    jobs = pd.read_csv(input_dir / "jobs.csv")
    jobs['required_skills'] = jobs['required_skills'].apply(clean_skills)
    jobs.to_csv(output_dir / "jobs_clean.csv", index=False)

    users = pd.read_csv(input_dir / "users.csv")
    users['skills'] = users['skills'].apply(clean_skills)
    users['skills_used'] = users['skills_used'].apply(clean_skills)
    users.to_csv(output_dir / "users_clean.csv", index=False)
