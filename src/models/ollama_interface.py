import requests
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")


def query_ollama(prompt, context):
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "context": context,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error querying Ollama: {e}")
        return None


def rag_query(question, context, max_tokens=300):
    prompt = f"""Given the following context, answer the question. If the answer is not in the context, say "I don't have enough information to answer that question."

Context: {context}

Question: {question}

Answer:"""

    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "max_tokens": max_tokens,
    }

    try:
        logger.info(f"Sending request to Ollama API: {OLLAMA_URL}")
        response = requests.post(OLLAMA_URL, json=data, timeout=240)  # Set a timeout
        response.raise_for_status()
        return response.json()["response"]
    except requests.RequestException as e:
        logger.error(f"Error querying Ollama: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your request."


def warmup_ollama():
    logger.info("Warming up Ollama model...")
    rag_query("Warmup question", "Warmup context")
    logger.info("Ollama model warmed up")


if __name__ == "__main__":
    # Test the Ollama interface
    test_question = "What are the basic rules for combat in D&D 5e?"
    test_context = "Combat in D&D 5e is turn-based. Each round, players roll initiative to determine turn order. On their turn, a character can move and take one action, such as attacking or casting a spell."

    result = rag_query(test_question, test_context)
    print(f"Question: {test_question}")
    print(f"Answer: {result}")
