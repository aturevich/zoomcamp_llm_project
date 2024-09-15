import nltk
from nltk.corpus import wordnet
import re

# Download required NLTK data
nltk.download("wordnet", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)

# Custom D&D synonym dictionary
dnd_synonyms = {
    "attack": ["strike", "hit", "assault"],
    "spell": ["magic", "incantation", "enchantment"],
    "character": ["player", "adventurer", "hero"],
    "combat": ["battle", "fight", "conflict"],
    "wizard": ["mage", "sorcerer", "spellcaster"],
    "fighter": ["warrior", "soldier", "combatant"],
    "class": ["category", "type"],
    "increase": ["boost", "enhance"],
    "high": ["great", "elevated"],
    "balance": ["equilibrate", "adjust"],
    "new": ["novice", "beginner"],
    "grappling": ["wrestling", "grabbing"],
    "spellcasting": ["spell-casting", "casting spells"],
    "initiative": ["first action", "starting action"],
    "dungeon": ["underground complex", "labyrinth"],
    "master": ["leader", "guide"],
    # Add more D&D-specific synonyms here
}

# Words to not expand
stop_words = set(
    [
        "how",
        "to",
        "for",
        "in",
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "does",
        "best",
        "work",
        "rules",
        "explain",
        "calculate",
        "difference",
        "between",
        "build",
    ]
)


def get_dnd_synonyms(word):
    return dnd_synonyms.get(word.lower(), [])


def get_wordnet_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if (
                lemma.name() != word
                and lemma.name() not in synonyms
                and "_" not in lemma.name()
            ):
                synonyms.append(lemma.name())
    return synonyms[:1]  # Limit to top 1 synonym


def rewrite_query(query):
    words = re.findall(r"\w+", query.lower())
    expanded_query = []

    for word in words:
        if word in stop_words:
            expanded_query.append(word)
        else:
            dnd_syns = get_dnd_synonyms(word)
            if not dnd_syns:
                wordnet_syns = get_wordnet_synonyms(word)
                all_syns = wordnet_syns[
                    :1
                ]  # Use only one WordNet synonym if no D&D synonyms
            else:
                all_syns = dnd_syns[:2]  # Use up to two D&D synonyms

            if all_syns:
                expanded_query.append(f"({word} OR {' OR '.join(all_syns)})")
            else:
                expanded_query.append(word)

    rewritten_query = " ".join(expanded_query)
    return rewritten_query


def expand_dnd_specific_terms(query):
    dnd_expansions = {
        "ac": "armor class",
        "hp": "hit points",
        "dm": "dungeon master",
        "pc": "player character",
        "npc": "non-player character",
        "xp": "experience points",
        "aoe": "area of effect",
        "dpr": "damage per round",
        "cr": "challenge rating",
        "dc": "difficulty class",
        "dex": "dexterity",
        "str": "strength",
        "con": "constitution",
        "int": "intelligence",
        "wis": "wisdom",
        "cha": "charisma",
    }

    words = query.split()
    expanded_words = [dnd_expansions.get(word.lower(), word) for word in words]
    return " ".join(expanded_words)


def rewrite_and_expand_query(query):
    expanded_query = expand_dnd_specific_terms(query)
    rewritten_query = rewrite_query(expanded_query)
    return rewritten_query
