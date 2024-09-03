from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from src.pipeline.rag_pipeline import run_rag_pipeline, collect_user_feedback

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <body>
            <h1>D&D 5e Q&A System</h1>
            <form action="/query" method="post">
                <input type="text" name="question" placeholder="Enter your D&D 5e question">
                <input type="submit" value="Ask">
            </form>
        </body>
    </html>
    """

@app.post("/query", response_class=HTMLResponse)
async def query(question: str = Form(...)):
    result = run_rag_pipeline(question)
    return f"""
    <html>
        <body>
            <h1>Answer</h1>
            <p><strong>Question:</strong> {result['question']}</p>
            <p><strong>Answer:</strong> {result['answer']}</p>
            <h2>Was this answer helpful?</h2>
            <form action="/feedback" method="post">
                <input type="hidden" name="question" value="{question}">
                <input type="hidden" name="answer" value="{result['answer']}">
                <input type="submit" name="rating" value="Yes">
                <input type="submit" name="rating" value="No">
            </form>
        </body>
    </html>
    """

@app.post("/feedback")
async def feedback(question: str = Form(...), answer: str = Form(...), rating: str = Form(...)):
    user_rating = 1 if rating == "Yes" else 0
    feedback = collect_user_feedback(question, answer, user_rating)
    return {"message": "Thank you for your feedback!"}

# Run with: uvicorn src.app.main:app --reload