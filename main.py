from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.ingestion.query_rewriting import rewrite_and_expand_query

app = FastAPI()

class Query(BaseModel):
    text: str

@app.post("/query")
async def process_query(query: Query):
    try:
        rewritten_query = rewrite_and_expand_query(query.text)
        results = retrieve_relevant_documents(rewritten_query, method='semantic', top_k=5, rerank=True)
        return {"original_query": query.text, "rewritten_query": rewritten_query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the D&D 5e SRD Assistant API"}
