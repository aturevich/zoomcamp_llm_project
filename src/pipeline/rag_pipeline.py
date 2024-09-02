import logging
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.models.ollama_interface import rag_query
from src.evaluation.metrics import evaluate_retrieval
from src.utils.config import OLLAMA_URL, OLLAMA_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_rag_pipeline(user_question):
    logger.info(f"Received question: {user_question}")
    logger.info(f"Using Ollama URL: {OLLAMA_URL}")
    logger.info(f"Using Ollama Model: {OLLAMA_MODEL}")
    
    try:
        # Retrieve relevant documents from Elasticsearch
        relevant_docs = retrieve_relevant_documents(user_question)
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        
        # Evaluate retrieval
        retrieval_metrics = evaluate_retrieval(user_question, relevant_docs)
        logger.info(f"Retrieval metrics: {retrieval_metrics}")
        
        # Combine the content of relevant documents
        context = "\n".join([doc['content'] for doc in relevant_docs])
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
    question = "How does leveling up work in D&D 5e?"
    result = run_rag_pipeline(question)
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Retrieval Metrics: {result['retrieval_metrics']}")
