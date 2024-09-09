import os
import logging
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.pipeline.rag_pipeline import run_rag_pipeline, collect_user_feedback
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.ingestion.query_rewriting import rewrite_and_expand_query

logging.basicConfig(level=logging.DEBUG)
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
logger.debug(f"Contents of static directory: {os.listdir('static') if os.path.exists('static') else 'Directory not found'}")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="/app/src/templates")

class Query(BaseModel):
    question: str

class FeedbackModel(BaseModel):
    question: str
    answer: str
    rating: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def query(query: Query):
    result = run_rag_pipeline(query.question)
    return {
        "question": result['question'],
        "answer": result['answer'],
        "retrieval_metrics": result['retrieval_metrics']
    }

@app.post("/feedback")
async def feedback(feedback: FeedbackModel):
    user_rating = 1 if feedback.rating == "Yes" else 0
    result = collect_user_feedback(feedback.question, feedback.answer, user_rating)
    return {"message": "Thank you for your feedback!"}

@app.post("/api/query")
async def process_query(query: Query):
    try:
        rewritten_query = rewrite_and_expand_query(query.text)
        results = retrieve_relevant_documents(rewritten_query, method='semantic', top_k=5, rerank=True)
        return {"original_query": query.text, "rewritten_query": rewritten_query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
