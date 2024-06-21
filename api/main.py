from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from datetime import datetime

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)
metadata = MetaData()

reviews = Table(
    "reviews",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("pull_request", Integer),
    Column("comments", String),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

class Review(BaseModel):
    pull_request: int
    comments: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/reviews/")
async def create_review(review: Review):
    query = reviews.insert().values(
        pull_request=review.pull_request, comments=review.comments
    )
    last_record_id = await database.execute(query)
    return {**review.dict(), "id": last_record_id}

@app.get("/reviews/", response_model=List[Review])
async def read_reviews():
    query = reviews.select()
    return await database.fetch_all(query)
