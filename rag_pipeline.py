from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.models.ollama_interface import rag_query
from src.utils.config import ES_INDEX_NAME, DATA_DIR

def run_rag_pipeline(user_question):
    # Retrieve relevant documents from Elasticsearch
    relevant_docs = retrieve_relevant_documents(user_question)
    
    # Combine the content of relevant documents
    context = "\n".join([doc['content'] for doc in relevant_docs])
    
    # Generate answer using Ollama
    answer = rag_query(user_question, context)
    
    return answer

if __name__ == "__main__":
    # Test the RAG pipeline
    test_question = "How does a wizard prepare spells in D&D 5e?"
    result = run_rag_pipeline(test_question)
    print(f"Question: {test_question}")
    print(f"Answer: {result}")
