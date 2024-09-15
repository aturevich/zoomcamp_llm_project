import os
from dotenv import load_dotenv

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file (two levels up)
dotenv_path = os.path.join(script_dir, "..", "..", ".env")

print(f"Looking for .env file at: {dotenv_path}")
print(f".env file exists: {os.path.exists(dotenv_path)}")

# Load the .env file explicitly
load_dotenv(dotenv_path)

# Elasticsearch configuration
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX_NAME = os.getenv("ES_INDEX_NAME", "dnd_5e_srd")

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

# Data directory
DATA_DIR = os.getenv("DATA_DIR", "./data/dnd_srd")

print(f"OLLAMA_URL: {OLLAMA_URL}")
print(f"OLLAMA_MODEL: {OLLAMA_MODEL}")
