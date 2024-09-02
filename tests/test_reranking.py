import sys
import os
import logging

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.ingestion.query_rewriting import rewrite_and_expand_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_results(results, title):
    print(f"\n{title}:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['title']} (Score: {doc.get('_score', 'N/A'):.4f})")
        print(f"   Excerpt: {doc['content'][:100]}...")  # Print first 100 characters of content

def test_reranking_and_query_rewriting():
    queries = [
        "What are the rules for grappling in combat?",
        "How does AC work in DnD?",
        "Explain the difference between a PC and an NPC",
        "What's the DC for a difficult strength check?"
    ]

    for query in queries:
        print(f"\n\nTesting query: {query}")
        
        results_without_rewrite = retrieve_relevant_documents(query, method='semantic', top_k=5, rerank=True, rewrite_query=False)
        
        rewritten_query = rewrite_and_expand_query(query)
        print(f"Rewritten query: {rewritten_query}")
        results_with_rewrite = retrieve_relevant_documents(rewritten_query, method='semantic', top_k=5, rerank=True, rewrite_query=False)
        
        print_results(results_without_rewrite, "Results without query rewriting")
        print_results(results_with_rewrite, "Results with query rewriting")
        
        if results_without_rewrite != results_with_rewrite:
            print("\nQuery rewriting has changed the results.")
            different_docs = set(doc['title'] for doc in results_with_rewrite) - set(doc['title'] for doc in results_without_rewrite)
            print(f"New documents introduced by query rewriting: {different_docs}")
        else:
            print("\nQuery rewriting did not change the results for this query.")

if __name__ == "__main__":
    test_reranking_and_query_rewriting()
