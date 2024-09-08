from sentence_transformers import SentenceTransformer

def get_sentence_transformer():
    return SentenceTransformer('all-MiniLM-L6-v2')
