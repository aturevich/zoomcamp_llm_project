from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, ConnectionError
import time

def connect_with_retry(max_retries=5, delay=5):
    for i in range(max_retries):
        try:
            es = Elasticsearch(['http://localhost:9200'])
            es.info()
            print("Successfully connected to Elasticsearch")
            return es
        except ConnectionError:
            if i < max_retries - 1:
                print(f"Connection failed. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Could not connect to Elasticsearch.")
                raise

# Connect to Elasticsearch
es = connect_with_retry()

# Define the index name
index_name = 'dnd_5e_srd'

# Define the mapping
mapping = {
    'properties': {
        'title': {'type': 'keyword'},
        'content': {
            'type': 'text',
            'analyzer': 'standard',
            'fields': {
                'keyword': {'type': 'keyword'}
            }
        },
        'category': {'type': 'keyword'},
        'subcategory': {'type': 'keyword'},
        'tags': {'type': 'keyword'},
        'file_path': {'type': 'keyword'}
    }
}

# Create the index with the mapping
try:
    es.indices.create(index=index_name, body={'mappings': mapping})
    print(f"Index '{index_name}' created successfully.")
except RequestError as e:
    if e.error == 'resource_already_exists_exception':
        print(f"Index '{index_name}' already exists. Skipping creation.")
    else:
        raise e

# Optionally, you can add some basic settings to the index
index_settings = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    }
}

try:
    es.indices.put_settings(index=index_name, body=index_settings)
    print(f"Settings applied to index '{index_name}'.")
except Exception as e:
    print(f"Error applying settings: {e}")

print("Elasticsearch setup complete.")