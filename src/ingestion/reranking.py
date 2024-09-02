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
    
    # Convert to Python list
    cos_scores = cos_scores.cpu().tolist()

    # Calculate keyword matching score
    query_terms = set(re.findall(r'\w+', query.lower()))
    keyword_scores = []
    for doc in documents:
        doc_terms = set(re.findall(r'\w+', doc['content'].lower()))
        keyword_score = len(query_terms.intersection(doc_terms)) / len(query_terms)
        keyword_scores.append(keyword_score)

    # Combine semantic similarity, initial score, and keyword matching
    combined_scores = [(doc, (doc['_score'] + sem_score + kw_score) / 3) 
                       for doc, sem_score, kw_score in zip(documents, cos_scores, keyword_scores)]

    # Sort by combined score in descending order
    reranked_docs = sorted(combined_scores, key=lambda x: x[1], reverse=True)

    logger.info(f"Reranking scores: {[score for _, score in reranked_docs[:top_k]]}")

    return [doc for doc, _ in reranked_docs[:top_k]]
