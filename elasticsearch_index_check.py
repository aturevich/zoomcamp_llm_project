from elasticsearch import Elasticsearch
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Define the index name
index_name = 'dnd_5e_srd'

def check_index_content():
    # Get total number of documents
    stats = es.indices.stats(index=index_name)
    total_docs = stats['indices'][index_name]['total']['docs']['count']
    logging.info(f"Total documents in index: {total_docs}")

    # Search for all documents
    result = es.search(index=index_name, body={"query": {"match_all": {}}, "size": total_docs})
    
    # Check for duplicates
    file_paths = {}
    for hit in result['hits']['hits']:
        file_path = hit['_source']['file_path']
        if file_path in file_paths:
            file_paths[file_path].append(hit['_id'])
        else:
            file_paths[file_path] = [hit['_id']]
    
    # Report findings
    unique_docs = len(file_paths)
    logging.info(f"Number of unique file paths: {unique_docs}")
    
    duplicates = {path: ids for path, ids in file_paths.items() if len(ids) > 1}
    if duplicates:
        logging.warning(f"Found {len(duplicates)} documents with duplicate file paths:")
        for path, ids in duplicates.items():
            logging.warning(f"  {path}: {len(ids)} occurrences")
    else:
        logging.info("No duplicates found based on file paths.")

    # Sample of indexed documents
    logging.info("Sample of indexed documents:")
    for i, hit in enumerate(result['hits']['hits'][:5]):  # Show first 5 documents
        logging.info(f"Document {i+1}:")
        logging.info(f"  ID: {hit['_id']}")
        logging.info(f"  Title: {hit['_source'].get('title', 'N/A')}")
        logging.info(f"  Category: {hit['_source'].get('category', 'N/A')}")
        logging.info(f"  File Path: {hit['_source'].get('file_path', 'N/A')}")
        logging.info("---")

if __name__ == "__main__":
    check_index_content()