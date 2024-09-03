import re
from sentence_transformers import SentenceTransformer, util
import torch
import logging

logger = logging.getLogger(__name__)

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

def rerank_documents(query, documents, top_k=5):
    if not documents:
        return []

    query_embedding = model.encode(query, convert_to_tensor=True)
    doc_embeddings = model.encode([doc['content'] for doc in documents], convert_to_tensor=True)
    
    cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]
    cos_scores = cos_scores.cpu().tolist()

    query_terms = set(re.findall(r'\w+', query.lower()))
    
    reranked_docs = []
    for i, doc in enumerate(documents):
        doc_terms = set(re.findall(r'\w+', doc['content'].lower()))
        
        semantic_score = cos_scores[i]
        keyword_score = len(query_terms.intersection(doc_terms)) / len(query_terms)
        initial_score = doc['_score']
        content_length = len(doc['content'])
        
        # Adjust weights here
        combined_score = (
            0.4 * semantic_score +
            0.3 * keyword_score +
            0.2 * initial_score +
            0.1 * min(1.0, content_length / 1000)  # Favor longer content, up to 1000 chars
        )
        
        reranked_docs.append((doc, combined_score))

    reranked_docs.sort(key=lambda x: x[1], reverse=True)
    
    logger.info(f"Reranking scores: {[score for _, score in reranked_docs[:top_k]]}")

    return [doc for doc, _ in reranked_docs[:top_k]]
