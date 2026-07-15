"""
Phase 1: Semantic Food Database Matcher
Uses TF-IDF + character n-gram cosine similarity to match
VLM/YOLO-identified food names to the IFCT nutrition database.

Much more robust than simple keyword maps — handles:
  - Synonyms:     "Steamed Basmati Rice" → "Cooked White Rice"
  - Typos:        "panear butter" → "Paneer Butter Masala"
  - Partial names: "dal" → "Yellow Dal Tadka"
  - Regional aliases: "Dahi" → "Curd / Raita"
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Optional

# ─── Canonical IFCT Database food names & aliases ───────────────────────────
# Keys must match exactly with FOOD_DENSITY_NUTRITION keys in cv_pipeline.py
FOOD_ALIASES: dict[str, list[str]] = {
    "Cooked White Rice": [
        "rice", "steamed rice", "plain rice", "basmati rice", "white rice",
        "boiled rice", "cooked rice", "steam rice", "chawal", "bhat"
    ],
    "Jeera Rice": [
        "jeera rice", "cumin rice", "pulao", "pilaf", "zeera rice"
    ],
    "Roti / Chapati": [
        "roti", "chapati", "chapatti", "phulka", "whole wheat roti",
        "wheat bread", "flatbread", "atta roti"
    ],
    "Naan": [
        "naan", "nan", "leavened bread", "tandoor naan", "butter naan",
        "garlic naan"
    ],
    "Paratha": [
        "paratha", "paratha", "stuffed bread", "aloo paratha", "layered bread"
    ],
    "Puri": [
        "puri", "poori", "fried bread", "deep fried bread"
    ],
    "Idli": [
        "idli", "idly", "steamed dumpling", "rice cake", "fermented rice cake"
    ],
    "Dosa": [
        "dosa", "dose", "rice crepe", "fermented crepe", "plain dosa"
    ],
    "Masala Dosa": [
        "masala dosa", "stuffed dosa", "potato dosa", "masala dose"
    ],
    "Upma": [
        "upma", "upma", "semolina porridge", "rava upma", "sooji upma"
    ],
    "Poha": [
        "poha", "pohe", "flattened rice", "beaten rice", "aval"
    ],
    "Yellow Dal Tadka": [
        "dal", "dal tadka", "toor dal", "moong dal", "masoor dal", "arhar dal",
        "yellow dal", "lentil soup", "lentils", "dhal", "daal"
    ],
    "Dal Makhani": [
        "dal makhani", "makhani dal", "black dal", "urad dal", "kali dal",
        "black lentil"
    ],
    "Rajma": [
        "rajma", "rajmah", "kidney beans", "red kidney beans", "rajma masala"
    ],
    "Chole / Chana Masala": [
        "chole", "chana masala", "chickpea curry", "chick pea", "chickpeas",
        "garbanzo", "channa", "kabuli chana"
    ],
    "Sambar": [
        "sambar", "sambhar", "rasam", "vegetable lentil soup", "sambar dal"
    ],
    "Paneer Butter Masala": [
        "paneer butter masala", "butter paneer", "paneer makhani", "paneer",
        "cottage cheese curry", "paneer masala"
    ],
    "Shahi Paneer": [
        "shahi paneer", "mughlai paneer", "cream paneer", "rich paneer curry"
    ],
    "Palak Paneer": [
        "palak paneer", "saag paneer", "spinach paneer", "spinach cottage cheese"
    ],
    "Curd / Raita": [
        "curd", "raita", "yogurt", "dahi", "plain yogurt", "boondi raita",
        "cucumber raita", "lassi", "dahi"
    ],
    "Lassi": [
        "lassi", "sweet lassi", "salted lassi", "mango lassi", "yogurt drink"
    ],
    "Mixed Vegetable Salad": [
        "salad", "vegetable salad", "green salad", "mixed salad", "onion",
        "tomato", "cucumber salad", "kachumber", "slaw"
    ],
    "Aloo Gobi": [
        "aloo gobi", "potato cauliflower", "gobi aloo", "potato and cauliflower"
    ],
    "Bhindi / Okra Fry": [
        "bhindi", "okra", "lady finger", "bhendi", "okra fry"
    ],
    "Baingan Bharta": [
        "baingan bharta", "eggplant", "brinjal", "baingan", "aubergine",
        "roasted eggplant"
    ],
    "Green Chutney": [
        "green chutney", "chutney", "mint chutney", "coriander chutney",
        "dip", "sauce", "condiment"
    ],
    "Pickle / Achar": [
        "pickle", "achar", "achaar", "mango pickle", "mixed pickle",
        "lime pickle"
    ],
    "Chicken Biryani": [
        "chicken biryani", "biryani", "biriyani", "veg biryani", "dum biryani",
        "hyderabadi biryani", "rice biryani"
    ],
    "Chicken Curry": [
        "chicken curry", "murgh curry", "chicken gravy", "chicken masala"
    ],
    "Butter Chicken": [
        "butter chicken", "murgh makhani", "chicken makhani", "tikka masala"
    ],
    "Mutton Curry": [
        "mutton curry", "lamb curry", "mutton masala", "goat curry"
    ],
    "Fish Curry": [
        "fish curry", "macher jhol", "fish masala", "fish gravy", "fish"
    ],
    "Boiled Egg": [
        "boiled egg", "egg", "hard boiled egg", "anda", "scrambled egg",
        "omelette", "fried egg"
    ],
    "Egg Curry": [
        "egg curry", "anda curry", "egg masala", "devil egg curry"
    ],
    "Gulab Jamun": [
        "gulab jamun", "dessert", "sweet", "mithai", "khoya balls",
        "milk solid sweet"
    ],
    "Papad": [
        "papad", "poppadom", "poppadum", "papadum", "lentil cracker",
        "crispy wafer"
    ],
}

# Build an inverted flat corpus for vectorization
# Each entry: (canonical_name, document_text)
_CORPUS: list[tuple[str, str]] = []
for canonical, aliases in FOOD_ALIASES.items():
    doc = " ".join([canonical] + aliases)
    _CORPUS.append((canonical, doc))


# ─── Vectorization helpers ────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """
    Splits text into:
    - Unigrams (individual words)
    - Character bigrams (for typo resilience)
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    words = text.split()
    bigrams = [text[i:i+2] for i in range(len(text) - 1) if text[i] != " " and text[i+1] != " "]
    return words + bigrams


def _build_idf(corpus_docs: list[list[str]]) -> dict[str, float]:
    """Compute IDF weights from the corpus."""
    N = len(corpus_docs)
    df: Counter = Counter()
    for doc in corpus_docs:
        for token in set(doc):
            df[token] += 1
    return {token: math.log((N + 1) / (count + 1)) + 1 for token, count in df.items()}


def _tf_idf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    """Compute TF-IDF sparse vector for a token list."""
    tf: Counter = Counter(tokens)
    total = len(tokens) or 1
    return {t: (count / total) * idf.get(t, 0.0) for t, count in tf.items()}


def _cosine_similarity(v1: dict[str, float], v2: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    dot = sum(v1.get(t, 0.0) * score for t, score in v2.items())
    norm1 = math.sqrt(sum(s ** 2 for s in v1.values()))
    norm2 = math.sqrt(sum(s ** 2 for s in v2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


# ─── Pre-compute corpus TF-IDF vectors at module load time ───────────────────
_tokenized_corpus = [_tokenize(doc) for _, doc in _CORPUS]
_idf = _build_idf(_tokenized_corpus)
_corpus_vectors = [
    (name, _tf_idf_vector(tokens, _idf))
    for (name, _), tokens in zip(_CORPUS, _tokenized_corpus)
]


# ─── Public API ───────────────────────────────────────────────────────────────

def match_food_semantic(
    query: str,
    top_k: int = 1,
    min_similarity: float = 0.05,
    fallback: str = "Paneer Butter Masala"
) -> tuple[str, float]:
    """
    Semantically matches a food name string to the closest entry in the
    IFCT nutrition database using TF-IDF + character bigram cosine similarity.

    Args:
        query:          The food name returned by the VLM / detector.
        top_k:          How many candidates to return (default 1).
        min_similarity: Minimum cosine similarity to be considered a match.
                        Below this threshold, the fallback is returned.
        fallback:       Canonical name to return when no match exceeds threshold.

    Returns:
        (matched_canonical_name, similarity_score)
    """
    query_tokens = _tokenize(query)
    query_vector  = _tf_idf_vector(query_tokens, _idf)

    scored: list[tuple[float, str]] = []
    for name, corpus_vec in _corpus_vectors:
        sim = _cosine_similarity(query_vector, corpus_vec)
        scored.append((sim, name))

    scored.sort(reverse=True)
    best_score, best_name = scored[0]

    print(f"[SemanticMatcher] '{query}' -> '{best_name}' (score={best_score:.3f})")

    if best_score < min_similarity:
        print(f"[SemanticMatcher] Score below threshold ({min_similarity}), using fallback: '{fallback}'")
        return fallback, 0.0

    return best_name, best_score


def match_food_semantic_batch(queries: list[str]) -> list[tuple[str, float]]:
    """
    Batch version of match_food_semantic for multiple food items.

    Args:
        queries: List of food name strings.

    Returns:
        List of (matched_name, similarity_score) tuples.
    """
    return [match_food_semantic(q) for q in queries]
