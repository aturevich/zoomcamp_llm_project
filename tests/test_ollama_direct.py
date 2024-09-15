import requests
import os
from dotenv import load_dotenv

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
dotenv_path = os.path.join(script_dir, ".env")

print(f"Looking for .env file at: {dotenv_path}")
print(f".env file exists: {os.path.exists(dotenv_path)}")

print("Before load_dotenv:")
print(f"OLLAMA_URL: {os.getenv('OLLAMA_URL')}")
print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")

# Load the .env file explicitly
load_dotenv(dotenv_path)

print("After load_dotenv:")
print(f"OLLAMA_URL: {os.getenv('OLLAMA_URL')}")
print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL')}")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

print(f"Final OLLAMA_URL: {OLLAMA_URL}")
print(f"Final OLLAMA_MODEL: {OLLAMA_MODEL}")


def query_ollama(prompt, model=OLLAMA_MODEL):
    url = OLLAMA_URL
    data = {"model": model, "prompt": prompt, "stream": False}
    print(f"Using model: {model}")
    print(f"Sending request to: {url}")
    print(f"Request data: {data}")
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        response.raise_for_status()
        return response.json()["response"]
    except requests.RequestException as e:
        print(f"Error details: {str(e)}")
        print(
            f"Response content: {e.response.content if e.response else 'No response'}"
        )
        raise Exception(f"Error querying Ollama: {str(e)}")


if __name__ == "__main__":
    try:
        result = query_ollama("Hello, world!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
