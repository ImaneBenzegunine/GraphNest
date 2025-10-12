from fastapi import FastAPI
from neo4j_utils import get_recommendations

app = FastAPI()

@app.get("/recommend/{user_id}")
async def recommend_jobs(user_id: str):
    return get_recommendations(user_id)