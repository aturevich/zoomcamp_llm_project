import os
from dotenv import load_dotenv
import hashlib
import markdown
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers, NotFoundError, ConnectionError
import logging
import json
import re
from src.utils.config import ES_HOST, ES_INDEX_NAME
import numpy as np
from sentence_transformers import SentenceTransformer, util
from .query_rewriting import rewrite_and_expand_query
from .query_processing import rewrite_user_query
from .reranking import rerank_documents
import time
import yaml
from pathlib import Path

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Elasticsearch configuration
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
ES_INDEX_NAME = os.getenv("ES_INDEX_NAME", "dnd_5e_srd")

# Directory containing your Markdown files
data_directory = os.getenv("DATA_DIRECTORY", "./data/dnd_srd")


def get_elasticsearch_client(max_retries=30, delay=10):
    for i in range(max_retries):
        try:
            es = Elasticsearch(
                [ES_HOST],
                http_auth=(
                    (ES_USERNAME, ES_PASSWORD) if ES_USERNAME and ES_PASSWORD else None
                ),
            )
            if es.ping():
                logger.info("Successfully connected to Elasticsearch")
                return es
        except ConnectionError:
            logger.warning(
                f"Connection to Elasticsearch failed (attempt {i+1}/{max_retries}). Retrying in {delay} seconds..."
            )
            time.sleep(delay)
    raise Exception("Failed to connect to Elasticsearch after multiple attempts")


def delete_index_if_exists(es, index_name):
    if es.indices.exists(index=index_name):
        try:
            es.indices.delete(index=index_name)
            logger.info(f"Deleted existing index: {index_name}")
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
    else:
        logger.info(f"Index {index_name} does not exist. No need to delete.")


def initialize_elasticsearch():
    es = get_elasticsearch_client()
    if not es.indices.exists(index=ES_INDEX_NAME):
        create_index_with_mapping()
    return es


# Global Elasticsearch client
es = get_elasticsearch_client()

# Initialize the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_document_id(file_path):
    with open(file_path, "rb") as file:
        return hashlib.md5(file.read()).hexdigest()


def get_category_subcategory(file_path):
    parts = file_path.split(os.sep)
    category = parts[-2] if len(parts) > 1 else "Uncategorized"
    subcategory = os.path.splitext(parts[-1])[0]
    return category, subcategory


def extract_tags(content):
    # Extract tags from content (e.g., based on headers or specific patterns)
    tags = re.findall(r"#(\w+)", content)
    return list(set(tags))


def parse_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        title = table.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
        title = title.text if title else "Untitled Table"
        content = str(table)
        tables.append({"title": title, "content": content})
    return tables


def parse_lists(soup):
    lists = []
    for list_elem in soup.find_all(["ul", "ol"]):
        title = list_elem.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
        title = title.text if title else "Untitled List"
        items = [li.text for li in list_elem.find_all("li")]
        lists.append({"title": title, "items": items})
    return lists


def determine_document_type(file_path):
    folder_name = os.path.basename(os.path.dirname(file_path)).lower()
    return folder_name.replace(" ", "_")


def read_markdown_file(file_path):
    logger.info(f"Reading markdown file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Convert Markdown to HTML
        html = markdown.markdown(content, extensions=["tables"])

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = soup.find(["h1", "h2", "h3"])
        title = (
            title.text if title else os.path.splitext(os.path.basename(file_path))[0]
        )

        # Remove title from content
        if title:
            title_tag = soup.find(["h1", "h2", "h3"])
            title_tag.extract()

        # Extract main content
        main_content = soup.get_text(separator="\n", strip=True)

        # Extract category, subcategory, and tags
        category, subcategory = get_category_subcategory(file_path)
        tags = extract_tags(content)

        # Parse tables and lists
        tables = parse_tables(soup)
        lists = parse_lists(soup)

        # Determine document type
        doc_type = determine_document_type(file_path)

        # Create document
        document = {
            "title": title,
            "content": main_content,
            "category": category,
            "subcategory": subcategory,
            "tags": tags,
            "file_path": file_path,
            "tables": tables,
            "lists": lists,
            "content_vector": model.encode(main_content).tolist(),
            "type": doc_type,  # Add the document type
        }

        logger.info(f"Successfully processed file: {file_path}")
        return document
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return None


def create_index_with_mapping():
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "content": {"type": "text", "analyzer": "standard"},
                "category": {"type": "keyword"},
                "subcategory": {"type": "keyword"},
                "file_path": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "tables": {
                    "type": "nested",
                    "properties": {
                        "title": {"type": "text"},
                        "content": {"type": "text"},
                    },
                },
                "lists": {
                    "type": "nested",
                    "properties": {
                        "title": {"type": "text"},
                        "items": {"type": "text"},
                    },
                },
                "content_vector": {
                    "type": "dense_vector",
                    "dims": 384,  # Adjust this to match your model's output dimension
                },
                "type": {"type": "keyword"},
            }
        }
    }

    if es.indices.exists(index=ES_INDEX_NAME):
        es.indices.delete(index=ES_INDEX_NAME)
        logger.info(f"Deleted existing index: {ES_INDEX_NAME}")

    es.indices.create(index=ES_INDEX_NAME, body=mapping)
    logger.info(f"Created index with mapping: {ES_INDEX_NAME}")


def reindex_documents():
    # Get all documents from the data directory
    documents = []
    for root, dirs, files in os.walk(data_directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                document = read_markdown_file(file_path)
                if document:
                    documents.append(document)

    # Prepare documents for indexing
    actions = []
    for doc in documents:
        doc_id = get_document_id(doc["file_path"])
        actions.append(
            {
                "_op_type": "index",
                "_index": ES_INDEX_NAME,
                "_id": doc_id,
                "_source": doc,
            }
        )

    # Index documents
    helpers.bulk(es, actions)
    logger.info(f"Indexed {len(actions)} documents")


# Add this function before the retrieve_relevant_documents function
def encode_query(query):
    return model.encode(query).tolist()


def retrieve_relevant_documents(
    query, method="semantic", top_k=5, rerank=True, rewrite_query=True
):
    if rewrite_query:
        original_query = query
        query = rewrite_and_expand_query(query)
        print(f"Original query: {original_query}")
        print(f"Rewritten query: {query}")

    if method == "semantic":
        search_body = {
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "must": [{"match": {"content": query}}],
                            "should": [
                                {"match_phrase": {"content": phrase}}
                                for phrase in query.split()
                            ],
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                        "params": {"query_vector": encode_query(query)},
                    },
                }
            },
            "size": top_k * 2,  # Retrieve more results for reranking
        }
    elif method == "keyword":
        # Implement keyword search
        pass
    elif method == "bm25":
        # Implement BM25 search (already done)
        pass
    elif method == "hybrid":
        # Implement hybrid search
        pass
    else:
        raise ValueError(f"Unknown retrieval method: {method}")

    results = es.search(index=ES_INDEX_NAME, body=search_body)
    documents = [hit["_source"] for hit in results["hits"]["hits"]]

    for doc, hit in zip(documents, results["hits"]["hits"]):
        doc["_score"] = hit["_score"]

    if rerank:
        documents = rerank_documents(query, documents, top_k=top_k)
    else:
        documents = documents[:top_k]

    return documents


def index_files(directory):
    logger.info(f"Starting indexing process for directory: {directory}")
    indexed_count = 0
    for root, dirs, files in os.walk(directory):
        logger.info(f"Scanning directory: {root}")
        logger.info(f"Found {len(files)} files")
        for file in files:
            logger.info(f"Processing file: {file}")
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                document = read_markdown_file(file_path)
                if document:
                    doc_id = get_document_id(file_path)
                    yield {"_index": ES_INDEX_NAME, "_id": doc_id, "_source": document}
                    indexed_count += 1
                    logger.info(f"Prepared document for indexing: {file_path}")
                else:
                    logger.warning(f"Failed to process document: {file_path}")
            else:
                logger.info(f"Skipping non-markdown file: {file}")
    logger.info(f"Prepared {indexed_count} documents for indexing")
    return indexed_count


def count_nested_objects(actions):
    nested_count = 0
    for action in actions:
        doc = action["_source"]
        nested_count += len(doc.get("tables", []))
        nested_count += len(doc.get("lists", []))
    return nested_count


# Delete existing index
delete_index_if_exists(es, ES_INDEX_NAME)

# Create index with mapping
create_index_with_mapping()

# Bulk index the documents
try:
    actions = list(index_files(data_directory))
    logger.info(f"Total actions prepared for indexing: {len(actions)}")
    if len(actions) == 0:
        logger.warning(
            "No documents prepared for indexing. Check the data directory and file processing."
        )
    nested_objects = count_nested_objects(actions)
    logger.info(
        f"Prepared {len(actions)} top-level documents and {nested_objects} nested objects"
    )
    success, failed = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
    logger.info(f"Indexed {success} documents successfully.")
    if failed:
        logger.error(f"{len(failed)} documents failed to index:")
        for item in failed:
            logger.error(f"Error: {item['index']['error']}")
            logger.error(f"Document: {json.dumps(item['index']['data'], indent=2)}")
except Exception as e:
    logger.error(f"An error occurred during bulk indexing: {e}")

# Refresh the index
try:
    es.indices.refresh(index=ES_INDEX_NAME)
    logger.info(f"Refreshed index: {ES_INDEX_NAME}")
except Exception as e:
    logger.error(f"Error refreshing index: {e}")

# Print index stats
try:
    stats = es.indices.stats(index=ES_INDEX_NAME)
    doc_count = stats["indices"][ES_INDEX_NAME]["total"]["docs"]["count"]
    logger.info(f"Total documents in index: {doc_count}")

    if doc_count != len(actions):
        logger.warning(
            f"Mismatch in document count. Expected: {len(actions)}, Actual: {doc_count}"
        )

    search_result = es.search(
        index=ES_INDEX_NAME, body={"query": {"match_all": {}}, "size": 1}
    )
    logger.info(
        f"Sample document: {json.dumps(search_result['hits']['hits'][0]['_source'], indent=2)}"
    )
except Exception as e:
    logger.error(f"Error retrieving index stats: {e}")

# Calculate total expected documents
total_expected = len(actions) + nested_objects
logger.info(f"Total expected documents (including nested): {total_expected}")

logger.info("Indexing process completed.")


def keyword_search(query, index_name=ES_INDEX_NAME, top_k=3):
    search_body = {"query": {"match": {"content": query}}, "size": top_k}
    results = es.search(index=index_name, body=search_body)
    return [hit["_source"] for hit in results["hits"]["hits"]]


def bm25_search(query, index_name=ES_INDEX_NAME, top_k=3):
    search_body = {
        "query": {"match": {"content": {"query": query, "fuzziness": "AUTO"}}},
        "size": top_k,
    }
    results = es.search(index=index_name, body=search_body)
    return [hit["_source"] for hit in results["hits"]["hits"]]


def semantic_search(query, index_name=ES_INDEX_NAME, top_k=3):
    try:
        query_vector = model.encode(query).tolist()
        search_body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                        "params": {"query_vector": query_vector},
                    },
                }
            },
            "size": top_k,
        }
        logger.info(f"Semantic search query: {search_body}")
        results = es.search(index=index_name, body=search_body)
        return [hit["_source"] for hit in results["hits"]["hits"]]
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}")
        logger.info("Falling back to keyword search")
        return keyword_search(query, index_name, top_k)


def hybrid_search(query, index_name=ES_INDEX_NAME, top_k=3, alpha=0.5):
    try:
        query_vector = model.encode(query).tolist()
        search_body = {
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {"match": {"content": query}},
                                {"match": {"title": query}},
                            ]
                        }
                    },
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, 'content_vector') * {alpha} + _score * (1 - {alpha})",
                        "params": {"query_vector": query_vector},
                    },
                }
            },
            "size": top_k,
        }
        logger.info(f"Hybrid search query: {search_body}")
        results = es.search(index=index_name, body=search_body)
        return [hit["_source"] for hit in results["hits"]["hits"]]
    except Exception as e:
        logger.error(f"Error in hybrid search: {str(e)}")
        logger.info("Falling back to keyword search")
        return keyword_search(query, index_name, top_k)
