import requests
import logging
from src.utils.config import OLLAMA_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

def query_ollama(prompt, model=OLLAMA_MODEL):
    url = OLLAMA_URL
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    logger.info(f"Using model: {model}")
    logger.info(f"Sending request to: {url}")
    logger.info(f"Request data: {data}")
    try:
        response = requests.post(url, json=data)
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Response content: {e.response.content if e.response else 'No response'}")
        raise Exception(f"Error querying Ollama: {str(e)}")

def rag_query(question, context):
    prompt = f"""
Context: {context[:1000]}  # Limit context to first 1000 characters

Question: {question}

Please answer the question based on the given context. If the answer cannot be found in the context, please say "I don't have enough information to answer that question."

Answer:
"""
    logger.info(f"RAG Query Prompt: {prompt}")
    return query_ollama(prompt)

if __name__ == "__main__":
    # Test the Ollama interface
    test_question = "What are the basic rules for combat in D&D 5e?"
    test_context = "Combat in D&D 5e is turn-based. Each round, players roll initiative to determine turn order. On their turn, a character can move and take one action, such as attacking or casting a spell."
    
    result = rag_query(test_question, test_context)
    print(f"Question: {test_question}")
    print(f"Answer: {result}")
