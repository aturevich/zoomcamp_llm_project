import os
import logging
import asyncio
from fastapi import Depends, FastAPI, Request, HTTPException, Query as FastAPIQuery
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field, ValidationError
from src.pipeline.rag_pipeline import run_rag_pipeline, collect_user_feedback
from src.ingestion.elasticsearch_ingestion import (
    retrieve_relevant_documents,
    get_elasticsearch_client,
)
from src.ingestion.query_rewriting import rewrite_and_expand_query
from src.utils.service_locator import service_locator
import time
from src.utils.dashboard_metrics import (
    process_feedback_data,
    calculate_response_time_stats,
    analyze_query_topics,
    aggregate_error_info,
    track_system_usage,
    analyze_answer_metrics,
)
from sqlalchemy.orm import Session
from src.database import models, database
import json
from math import ceil
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Debug: Print current working directory and contents of static directory
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(
    f"Contents of static directory: {os.listdir('static') if os.path.exists('static') else 'Directory not found'}"
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="/app/src/templates")


class Query(BaseModel):
    question: str


class FeedbackModel(BaseModel):
    interaction_id: Optional[int] = None
    rating: int = Field(..., ge=-1, le=1)
    comment: Optional[str] = None

    @validator("rating")
    def validate_rating(cls, v):
        logger.info(f"Validating rating: {v}")
        if v not in [-1, 1]:
            logger.error(f"Invalid rating value: {v}")
            raise ValueError("Rating must be either -1 or 1")
        return v


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/query")
async def query(query: Query, db: Session = Depends(database.get_db)):
    start_time = time.time()
    result = run_rag_pipeline(query.question)
    end_time = time.time()
    response_time = end_time - start_time

    # Store interaction in the database
    db_interaction = models.Interaction(
        query=query.question,
        response=result["answer"],
        response_time=response_time,
        retrieval_metrics=json.dumps(result["retrieval_metrics"]),  # Add this line
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)

    return {
        "question": result["question"],
        "answer": result["answer"],
        "retrieval_metrics": result["retrieval_metrics"],
        "file_references": result.get("file_references", []),  # Add this line
    }


@app.post("/feedback")
async def feedback(feedback: FeedbackModel, db: Session = Depends(database.get_db)):
    try:
        db_feedback = models.Feedback(
            interaction_id=feedback.interaction_id,
            rating=feedback.rating,
            comment=feedback.comment,
        )
        db.add(db_feedback)
        db.commit()
        logger.info(f"Feedback recorded successfully: {db_feedback.id}")
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/query")
async def process_query(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received data: {data}")
        if "text" not in data:
            raise HTTPException(
                status_code=422, detail="Missing 'text' field in request body"
            )
        query_text = data["text"]

        # Run the RAG pipeline
        result = run_rag_pipeline(query_text)
        logger.info(f"Full RAG pipeline result: {result}")

        return {
            "question": result["question"],
            "answer": result["answer"],
            "retrieval_metrics": result["retrieval_metrics"],
            "file_references": result.get("file_references", []),
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def feedback(feedback: FeedbackModel, db: Session = Depends(database.get_db)):
    try:
        db_feedback = models.Feedback(
            interaction_id=feedback.interaction_id,
            rating=feedback.rating,
            comment=feedback.comment,
        )
        db.add(db_feedback)
        db.commit()
        logger.info(f"Feedback recorded successfully: {db_feedback.id}")
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/dashboard/response_time")
async def get_dashboard_response_time(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return JSONResponse(content=calculate_response_time_stats(interactions))


@app.get("/api/dashboard/query_topics")
async def get_dashboard_query_topics(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return JSONResponse(content=analyze_query_topics(interactions))


@app.get("/api/dashboard/errors")
async def get_dashboard_errors(db: Session = Depends(database.get_db)):
    interactions = (
        db.query(models.Interaction).filter(models.Interaction.error.isnot(None)).all()
    )
    error_info = aggregate_error_info(interactions)
    return JSONResponse(content=error_info)


@app.get("/api/dashboard/usage")
async def get_dashboard_usage(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return JSONResponse(content=track_system_usage(interactions))


@app.get("/api/dashboard/answer_metrics")
async def get_dashboard_answer_metrics(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    metrics = analyze_answer_metrics(interactions)
    print("Answer Metrics:", metrics)  # Add this line
    return JSONResponse(content=metrics)


from fastapi import Depends
from src.utils.service_locator import ServiceLocator


async def get_service_locator():
    return ServiceLocator()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from src.database.database import engine
from src.database import models

models.Base.metadata.create_all(bind=engine)


@app.get("/render-markdown/{file_path:path}", response_class=PlainTextResponse)
async def render_markdown(file_path: str):
    try:
        base_path = "/app/data/dnd_srd"
        cleaned_path = file_path.lstrip("./").replace("data/dnd_srd/", "", 1)
        full_path = os.path.join(base_path, cleaned_path)
        print(f"Attempting to read file: {full_path}")  # Debug log

        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=404, detail=f"File not found: {cleaned_path}"
            )

        with open(full_path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError


@app.on_event("startup")
async def startup_event():
    global es
    max_retries = 30
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            es = get_elasticsearch_client()
            # Test the connection
            es.info()
            print(f"Successfully connected to Elasticsearch on attempt {attempt + 1}")
            return
        except Exception as e:
            print(
                f"Failed to connect to Elasticsearch (attempt {attempt + 1}/{max_retries}): {str(e)}"
            )
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("Failed to connect to Elasticsearch after multiple attempts")
                raise


@app.get("/api/dashboard/feedback")
async def get_dashboard_feedback(db: Session = Depends(database.get_db)):
    feedback = db.query(models.Feedback).all()
    return process_feedback_data(feedback)


@app.get("/api/dashboard/response_time")
async def get_dashboard_response_time(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return calculate_response_time_stats(interactions)


@app.get("/api/dashboard/query_topics")
async def get_dashboard_query_topics(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return analyze_query_topics(interactions)


@app.get("/api/dashboard/usage")
async def get_dashboard_usage(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return track_system_usage(interactions)


@app.get("/api/dashboard/answer_metrics")
async def get_dashboard_answer_metrics(db: Session = Depends(database.get_db)):
    interactions = db.query(models.Interaction).all()
    return analyze_answer_metrics(interactions)
