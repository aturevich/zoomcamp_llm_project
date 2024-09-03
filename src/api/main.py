from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.pipeline.rag_pipeline import run_rag_pipeline, collect_user_feedback
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.ingestion.query_rewriting import rewrite_and_expand_query

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

class Query(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query", response_class=HTMLResponse)
async def query(request: Request, question: str = Form(...)):
    result = run_rag_pipeline(question)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "question": result['question'],
        "answer": result['answer'],
        "retrieval_metrics": result['retrieval_metrics']
    })

@app.post("/feedback")
async def feedback(question: str = Form(...), answer: str = Form(...), rating: str = Form(...)):
    user_rating = 1 if rating == "Yes" else 0
    feedback = collect_user_feedback(question, answer, user_rating)
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
