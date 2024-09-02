import re
from nltk.corpus import wordnet

import nltk
nltk.download('wordnet')

def rewrite_user_query(query):
    # Implement D&D specific spell checking
    query = spell_check_dnd(query)
    
    # Expand query with D&D specific synonyms
    query = expand_query_with_synonyms(query)
    
    # Normalize D&D specific terms
    query = normalize_dnd_terms(query)
    
    return query

def spell_check_dnd(query):
    # Implement D&D specific spell checking
    # This is a placeholder and should be replaced with actual implementation
    return query

def expand_query_with_synonyms(query):
    expanded_terms = []
    for word in query.split():
        synonyms = wordnet.synsets(word)
        if synonyms:
            expanded_terms.append(word)
            expanded_terms.extend([lemma.name() for synset in synonyms for lemma in synset.lemmas()])
        else:
            expanded_terms.append(word)
    return ' '.join(set(expanded_terms))

def normalize_dnd_terms(query):
    # Normalize common D&D abbreviations and terms
    normalizations = {
        'hp': 'hit points',
        'ac': 'armor class',
        'dex': 'dexterity',
        # Add more D&D specific normalizations
    }
    for abbr, full in normalizations.items():
        query = re.sub(r'\b' + abbr + r'\b', full, query, flags=re.IGNORECASE)
    return query
