import logging
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.models.ollama_interface import rag_query, warmup_ollama
from src.evaluation.metrics import evaluate_retrieval, evaluate_answer
from src.utils.config import OLLAMA_URL, OLLAMA_MODEL
from src.ingestion.reranking import rerank_documents
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_user_feedback(question, generated_answer, user_rating):
    feedback = {
        "question": question,
        "generated_answer": generated_answer,
        "user_rating": user_rating
    }
    store_feedback(feedback)
    logger.info(f"Collected user feedback: {feedback}")
    return feedback

def store_feedback(feedback):
    feedback_file = Path("feedback.json")
    if feedback_file.exists():
        with feedback_file.open("r+") as f:
            data = json.load(f)
            data.append(feedback)
            f.seek(0)
            json.dump(data, f, indent=2)
    else:
        with feedback_file.open("w") as f:
            json.dump([feedback], f, indent=2)

def run_rag_pipeline(user_question, reference_answer=None):
    logger.info(f"Received question: {user_question}")
    logger.info(f"Using Ollama URL: {OLLAMA_URL}")
    logger.info(f"Using Ollama Model: {OLLAMA_MODEL}")
    
    try:
        # Retrieve relevant documents from Elasticsearch
        relevant_docs = retrieve_relevant_documents(user_question, method='semantic', top_k=10)
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        
        # Rerank documents
        reranked_docs = rerank_documents(user_question, relevant_docs, top_k=5)
        logger.info(f"Reranked to {len(reranked_docs)} documents")
        
        # Evaluate retrieval
        retrieval_metrics = evaluate_retrieval(user_question, reranked_docs)
        logger.info(f"Retrieval metrics: {retrieval_metrics}")
        
        # Combine the content of relevant documents
        context = "\n".join([doc['content'] for doc in reranked_docs])
        context = context[:2000]  # Limit context to 2000 characters
        logger.info(f"Context length: {len(context)}")
        
        # Generate answer using Ollama
        logger.info("Calling rag_query function")
        answer = rag_query(user_question, context)
        logger.info(f"Generated answer: {answer}")
        
        return {
            "question": user_question,
            "answer": answer,
            "retrieval_metrics": retrieval_metrics
        }
    except Exception as e:
        logger.exception(f"Error in RAG pipeline: {str(e)}")
        return {
            "question": user_question,
            "answer": f"An error occurred: {str(e)}",
            "retrieval_metrics": None
        }

if __name__ == "__main__":
    warmup_ollama()  # Warm up the Ollama model
    question = "How does leveling up work in D&D 5e?"
    result = run_rag_pipeline(question)
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Retrieval Metrics: {result['retrieval_metrics']}")
