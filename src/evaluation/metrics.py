from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_relevance_score(query, document):
    query_embedding = model.encode([query])
    doc_embedding = model.encode([document])
    return cosine_similarity(query_embedding, doc_embedding)[0][0]

def evaluate_retrieval(query, retrieved_docs):
    scores = [calculate_relevance_score(query, doc['content']) for doc in retrieved_docs]
    return {
        "average_relevance": sum(scores) / len(scores),
        "max_relevance": max(scores),
        "min_relevance": min(scores)
    }

def evaluate_relevance(question, retrieved_docs, top_k=3):
    if not retrieved_docs:
        return [0] * top_k

    # Encode the question and retrieved documents
    question_embedding = model.encode(question)
    doc_embeddings = model.encode([doc['content'] for doc in retrieved_docs])

    # Calculate cosine similarities
    similarities = np.dot(doc_embeddings, question_embedding) / (
        np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(question_embedding)
    )

    # Sort similarities and pad with zeros if necessary
    sorted_similarities = sorted(similarities, reverse=True)
    padded_similarities = sorted_similarities[:top_k] + [0] * (top_k - len(sorted_similarities))

    return padded_similarities

# You can add more evaluation metrics here, such as BLEU score for generated answers
