import logging
from src.ingestion.elasticsearch_ingestion import retrieve_relevant_documents
from src.evaluation.metrics import evaluate_relevance
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_retrieval_methods(test_questions, top_k=3):
    methods = {
        'keyword': 'keyword',
        'bm25': 'bm25',
        'semantic': 'semantic',
        'hybrid': 'hybrid'
    }
    
    results = {}
    
    for method_name, method in methods.items():
        logger.info(f"Evaluating {method_name} retrieval method")
        method_results = []
        
        for question in tqdm(test_questions, desc="Batches"):
            relevant_docs = retrieve_relevant_documents(question, method=method, top_k=top_k)
            relevance_scores = evaluate_relevance(question, relevant_docs, top_k=top_k)
            method_results.extend(relevance_scores)
        
        results[method_name] = {
            'average_relevance': sum(method_results) / len(method_results),
            'max_relevance': max(method_results),
            'min_relevance': min(method_results)
        }
    
    return results

if __name__ == "__main__":
    test_questions = [
        "How does leveling up work in D&D 5e?",
        "What are the different types of magic in D&D?",
        "How does combat work in D&D 5e?",
        "What are the main character classes in D&D 5e?",
        "How do saving throws work in D&D 5e?"
    ]
    
    top_k = 3  # You can adjust this value as needed
    results = evaluate_retrieval_methods(test_questions, top_k=top_k)
    
    print("\nRetrieval Method Evaluation Results:")
    for method, metrics in results.items():
        print(f"\n{method.capitalize()} Search:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    best_method = max(results, key=lambda x: results[x]['average_relevance'])
    print(f"\nBest performing method: {best_method}")

    # Add this line to see the full results dictionary
    print("\nFull results:", results)