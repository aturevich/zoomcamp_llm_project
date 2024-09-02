import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.query_rewriting import rewrite_query, expand_dnd_specific_terms, rewrite_and_expand_query

def test_rewrite_query():
    test_cases = [
        "How to attack in combat",
        "What are the rules for spellcasting",
        "Explain character creation",
        "How does initiative work"
    ]

    print("Testing rewrite_query function:")
    for query in test_cases:
        rewritten = rewrite_query(query)
        print(f"Original: {query}")
        print(f"Rewritten: {rewritten}")
        print()

def test_expand_dnd_specific_terms():
    test_cases = [
        "What's the AC of a dragon",
        "How to calculate HP",
        "DM tips for new players",
        "Difference between PC and NPC",
        "Best STR build for fighter"
    ]

    print("Testing expand_dnd_specific_terms function:")
    for query in test_cases:
        expanded = expand_dnd_specific_terms(query)
        print(f"Original: {query}")
        print(f"Expanded: {expanded}")
        print()

def test_rewrite_and_expand_query():
    test_cases = [
        "How to increase AC",
        "Best spells for high INT wizard",
        "Rules for grappling in combat",
        "How to balance CR for new DM"
    ]

    print("Testing rewrite_and_expand_query function:")
    for query in test_cases:
        rewritten_and_expanded = rewrite_and_expand_query(query)
        print(f"Original: {query}")
        print(f"Rewritten and Expanded: {rewritten_and_expanded}")
        print()

if __name__ == "__main__":
    test_rewrite_query()
    print("\n" + "="*50 + "\n")
    test_expand_dnd_specific_terms()
    print("\n" + "="*50 + "\n")
    test_rewrite_and_expand_query()
