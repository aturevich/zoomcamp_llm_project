import requests

url = "http://localhost:11434/api/generate"
data = {"model": "mistral:latest", "prompt": "Hello, world!", "stream": False}

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    response.raise_for_status()
    print(response.json())
except requests.RequestException as e:
    print(f"Error: {str(e)}")
    print(f"Response content: {e.response.content if e.response else 'No response'}")
