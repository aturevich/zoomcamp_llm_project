import logging
from datetime import datetime
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.models.ollama_interface import rag_query, warmup_ollama
from src.evaluation.metrics import evaluate_retrieval, evaluate_answer
from src.utils.config import OLLAMA_URL, OLLAMA_MODEL
from src.ingestion.reranking import rerank_documents
import json
from pathlib import Path
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the tokenizer globally to avoid reloading it for each function call
tokenizer = AutoTokenizer.from_pretrained(
    "gpt2"
)  # You can change this to match your model


def collect_user_feedback(
    question, generated_answer, user_rating, response_time=0, topic=None, error=None
):
    feedback = {
        "question": question,
        "generated_answer": generated_answer,
        "user_rating": user_rating,
        "response_time": response_time,
        "topic": topic,
        "error": error,
        "timestamp": datetime.now().isoformat(),
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


def run_rag_pipeline(query):
    logger.info(f"Received question: {query}")
    logger.info(f"Using Ollama URL: {OLLAMA_URL}")
    logger.info(f"Using Ollama Model: {OLLAMA_MODEL}")

    try:
        # Retrieve relevant documents from Elasticsearch
        relevant_docs = retrieve_relevant_documents(query, method="semantic", top_k=10)
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")

        # Rerank documents
        reranked_docs = rerank_documents(query, relevant_docs, top_k=5)
        logger.info(f"Reranked to {len(reranked_docs)} documents")

        # Combine the content of relevant documents
        context = "\n".join([doc.get("content", "") for doc in reranked_docs])
        context = context[:2000]  # Limit context to 2000 characters
        logger.info(f"Context length: {len(context)}")

        # Generate answer using Ollama
        logger.info("Calling rag_query function")
        answer = rag_query(query, context)
        logger.info(f"Generated answer: {answer}")

        # Calculate tokens for both query and answer
        query_tokens = calculate_total_tokens(query)
        answer_tokens = calculate_total_tokens(answer)
        total_tokens = query_tokens + answer_tokens

        retrieval_metrics = {
            "num_retrieved": len(relevant_docs),
            "average_relevance": (
                sum(doc.get("score", 0) for doc in relevant_docs) / len(relevant_docs)
                if relevant_docs
                else 0
            ),
            "max_relevance": max(
                (doc.get("score", 0) for doc in relevant_docs), default=0
            ),
            "min_relevance": min(
                (doc.get("score", 0) for doc in relevant_docs), default=0
            ),
            "total_tokens": total_tokens,
            "query_tokens": query_tokens,
            "answer_tokens": answer_tokens,
        }

        # Add file references to the response
        file_references = [
            doc.get("file_path", "") for doc in relevant_docs if "file_path" in doc
        ]
        logger.info(f"Collected file references: {file_references}")

        result = {
            "question": query,
            "answer": answer,
            "retrieval_metrics": retrieval_metrics,
            "file_references": file_references,
        }
        logger.info(f"RAG pipeline result: {result}")
        return result
    except Exception as e:
        logger.exception(f"Error in RAG pipeline: {str(e)}")
        return {
            "question": query,
            "answer": f"An error occurred: {str(e)}",
            "retrieval_metrics": {
                "num_retrieved": 0,
                "average_relevance": 0,
                "max_relevance": 0,
                "min_relevance": 0,
                "total_tokens": 0,
                "query_tokens": 0,
                "answer_tokens": 0,
            },
        }


def calculate_total_tokens(text):
    return len(tokenizer.encode(text))


if __name__ == "__main__":
    warmup_ollama()  # Warm up the Ollama model
    question = "How does leveling up work in D&D 5e?"
    result = run_rag_pipeline(question)
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Retrieval Metrics: {result['retrieval_metrics']}")
