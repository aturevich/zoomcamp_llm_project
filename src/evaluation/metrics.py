from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_relevance_score(query, document):
    query_embedding = model.encode([query])
    doc_embedding = model.encode([document])
    return cosine_similarity(query_embedding, doc_embedding)[0][0]

def evaluate_retrieval(query, retrieved_docs):
    scores = [doc.get('_score', 0) for doc in retrieved_docs]
    return {
        "num_retrieved": len(retrieved_docs),
        "average_relevance": sum(scores) / len(scores) if scores else 0,
        "max_relevance": max(scores) if scores else 0,
        "min_relevance": min(scores) if scores else 0
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

def evaluate_answer(reference_answer, generated_answer):
    # BLEU score
    reference = reference_answer.split()
    candidate = generated_answer.split()
    bleu_score = sentence_bleu([reference], candidate)
    
    # ROUGE score
    rouge = Rouge()
    rouge_scores = rouge.get_scores(generated_answer, reference_answer)[0]
    
    return {
        "bleu_score": bleu_score,
        "rouge_1_f": rouge_scores['rouge-1']['f'],
        "rouge_2_f": rouge_scores['rouge-2']['f'],
        "rouge_l_f": rouge_scores['rouge-l']['f']
    }

# You can add more evaluation metrics here, such as BLEU score for generated answers
