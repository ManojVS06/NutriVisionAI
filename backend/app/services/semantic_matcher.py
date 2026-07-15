"""
Phase 1: Semantic Food Database Matcher
Uses TF-IDF + character n-gram cosine similarity to match
VLM/YOLO-identified food names to the full IFCT 2017 database.

Auto-builds its corpus from ALL 158 foods in ifct_database.py
plus a curated regional alias list — no manual maintenance needed
when new foods are added to the database.

Handles:
  - Synonyms:       "Steamed Basmati Rice" -> "Cooked White Rice"
  - Typos:          "panear butter"        -> "Paneer Butter Masala"
  - Partial names:  "dal"                  -> "Yellow Dal Tadka"
  - Regional names: "Dahi"                 -> "Curd / Raita"
  - Hindi names:    "Murgh Makhani"        -> "Butter Chicken"
  - English names:  "Lentil Soup"          -> "Yellow Dal Tadka"
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Optional

# Import the full IFCT 2017 database (158 foods)
from app.data.ifct_database import IFCT_DATABASE, ALL_FOOD_NAMES

# ─── Curated regional + synonym alias list ───────────────────────────────────
# This extends the canonical food name with alternate names, Hindi names,
# English descriptions and common misspellings.
# Auto-combined with the canonical name for TF-IDF vectorisation.
FOOD_ALIASES: dict[str, list[str]] = {
    # ── Cereals & Rice ──────────────────────────────────────────────────────
    "Cooked White Rice": [
        "rice", "steamed rice", "plain rice", "basmati rice", "white rice",
        "boiled rice", "cooked rice", "steam rice", "chawal", "bhat",
        "long grain rice", "sona masoori", "ponni rice"
    ],
    "Cooked Brown Rice": [
        "brown rice", "whole grain rice", "unpolished rice", "bhura chawal"
    ],
    "Cooked Parboiled Rice": [
        "parboiled rice", "ukda chawal", "sela rice", "converted rice"
    ],
    "Jeera Rice": [
        "jeera rice", "cumin rice", "zeera rice", "pulao", "pilaf",
        "cumin pilaf"
    ],
    "Lemon Rice": [
        "lemon rice", "chitranna", "elumichai sadam", "nimbu chawal"
    ],
    "Curd Rice": [
        "curd rice", "dahi rice", "thayir sadam", "mosaranna", "yogurt rice"
    ],
    "Khichdi": [
        "khichdi", "khichri", "pongal", "rice lentil porridge",
        "one pot meal", "comfort food rice"
    ],
    "Chicken Biryani": [
        "chicken biryani", "biryani", "biriyani", "dum biryani",
        "hyderabadi biryani", "lucknowi biryani", "kacchi biryani"
    ],
    "Veg Biryani": [
        "veg biryani", "vegetable biryani", "veg dum biryani",
        "veg pulao biryani"
    ],
    "Mutton Biryani": [
        "mutton biryani", "lamb biryani", "gosht biryani"
    ],
    "Fried Rice": [
        "fried rice", "chinese fried rice", "egg fried rice",
        "indo chinese fried rice", "veg fried rice"
    ],
    "Roti / Chapati": [
        "roti", "chapati", "chapatti", "phulka", "whole wheat roti",
        "wheat roti", "flatbread", "atta roti", "indian bread",
        "whole wheat bread"
    ],
    "Naan": [
        "naan", "nan", "leavened bread", "tandoor naan", "butter naan",
        "garlic naan", "tandoori naan"
    ],
    "Paratha": [
        "paratha", "parantha", "layered bread", "stuffed paratha",
        "pan fried bread", "ghee paratha"
    ],
    "Aloo Paratha": [
        "aloo paratha", "potato paratha", "stuffed potato bread",
        "aloo ka paratha"
    ],
    "Puri": [
        "puri", "poori", "fried bread", "deep fried bread", "puri bhaji"
    ],
    "Bhatura": [
        "bhatura", "bhature", "fried leavened bread", "chole bhature",
        "fluffy fried bread"
    ],
    "Idli": [
        "idli", "idly", "steamed dumpling", "rice cake",
        "fermented rice cake", "south indian idli"
    ],
    "Dosa": [
        "dosa", "dose", "rice crepe", "fermented crepe", "plain dosa",
        "crispy dosa", "paper dosa"
    ],
    "Masala Dosa": [
        "masala dosa", "stuffed dosa", "potato dosa", "masala dose",
        "mysore masala dosa"
    ],
    "Uttapam": [
        "uttapam", "oothappam", "thick dosa", "vegetable pancake"
    ],
    "Appam": [
        "appam", "aapam", "hoppers", "bowl shaped pancake", "rice appam"
    ],
    "Upma": [
        "upma", "semolina porridge", "rava upma", "sooji upma",
        "suji upma", "uppittu"
    ],
    "Poha": [
        "poha", "pohe", "flattened rice", "beaten rice", "aval",
        "avalakki", "chivda"
    ],
    "Bajra Roti": [
        "bajra roti", "pearl millet roti", "bajra bread", "millet flatbread"
    ],
    "Ragi / Finger Millet Porridge": [
        "ragi", "finger millet", "ragi porridge", "ragi mudde",
        "nachni", "mandua", "ragi java"
    ],
    "Jowar Roti": [
        "jowar roti", "sorghum roti", "jowar bread", "jolada roti"
    ],
    "Pesarattu": [
        "pesarattu", "moong dal dosa", "green gram dosa", "pesara dosa"
    ],
    "Dhokla": [
        "dhokla", "khaman dhokla", "steamed gram flour cake",
        "gujarati snack", "khaman"
    ],

    # ── Pulses & Dals ────────────────────────────────────────────────────────
    "Yellow Dal Tadka": [
        "dal", "dal tadka", "toor dal", "arhar dal", "yellow dal",
        "lentil soup", "lentils", "dhal", "daal", "moong dal",
        "masoor dal", "split lentil", "yellow lentil"
    ],
    "Dal Makhani": [
        "dal makhani", "makhani dal", "black dal", "urad dal curry",
        "black lentil dal", "kali dal", "creamy black dal"
    ],
    "Moong Dal": [
        "moong dal", "mung dal", "green gram dal", "mung lentil",
        "split moong", "yellow moong"
    ],
    "Masoor Dal": [
        "masoor dal", "red lentil dal", "masur dal", "red dal",
        "pink lentil"
    ],
    "Urad Dal": [
        "urad dal", "black gram dal", "white urad", "split urad",
        "urad dhal"
    ],
    "Chana Dal": [
        "chana dal", "split chickpea", "bengal gram dal",
        "cholar dal", "chana dal curry"
    ],
    "Rajma": [
        "rajma", "rajmah", "kidney beans", "red kidney beans",
        "rajma masala", "kidney bean curry"
    ],
    "Chole / Chana Masala": [
        "chole", "chana masala", "chickpea curry", "chick pea",
        "chickpeas", "garbanzo", "channa", "kabuli chana",
        "white chickpea"
    ],
    "Sambar": [
        "sambar", "sambhar", "south indian sambar", "vegetable lentil soup",
        "drumstick sambar", "idli sambar"
    ],
    "Rasam": [
        "rasam", "pepper water", "tomato rasam", "tamarind soup",
        "south indian rasam", "saaru"
    ],
    "Pav Bhaji": [
        "pav bhaji", "pav bhaaji", "mumbai pav bhaji",
        "street food bhaji", "mashed vegetable curry"
    ],
    "Kadhi": [
        "kadhi", "kadi", "yogurt curry", "besan kadhi",
        "pakora kadhi", "punjabi kadhi"
    ],
    "Dal Fry": [
        "dal fry", "tempered dal", "fried dal", "restaurant dal"
    ],
    "Lobia / Black Eyed Pea Curry": [
        "lobia", "black eyed peas", "cowpea curry", "chawli",
        "rongi", "lobhia"
    ],
    "Sprouts Salad": [
        "sprouts", "sprout salad", "mixed sprouts", "moong sprouts",
        "germinated seeds"
    ],
    "Moong Dal Chilla": [
        "moong dal chilla", "dal pancake", "moong cheela",
        "lentil pancake", "protein pancake"
    ],
    "Cooked Black Chickpeas": [
        "kala chana", "black chickpeas", "desi chana", "brown chickpea",
        "kaala chana"
    ],
    "Matar Paneer": [
        "matar paneer", "peas paneer", "mutter paneer",
        "green pea cottage cheese"
    ],

    # ── Dairy & Eggs ─────────────────────────────────────────────────────────
    "Paneer Butter Masala": [
        "paneer butter masala", "butter paneer", "paneer makhani",
        "paneer", "cottage cheese curry", "paneer masala",
        "creamy paneer"
    ],
    "Shahi Paneer": [
        "shahi paneer", "mughlai paneer", "royal paneer",
        "cream paneer curry"
    ],
    "Palak Paneer": [
        "palak paneer", "saag paneer", "spinach paneer",
        "spinach cottage cheese", "palak cottage cheese"
    ],
    "Kadai Paneer": [
        "kadai paneer", "karahi paneer", "wok paneer",
        "kadhai paneer", "spiced paneer"
    ],
    "Curd / Raita": [
        "curd", "raita", "yogurt", "dahi", "plain yogurt",
        "boondi raita", "cucumber raita", "dahi"
    ],
    "Lassi": [
        "lassi", "sweet lassi", "salted lassi", "yogurt drink",
        "punjabi lassi"
    ],
    "Mango Lassi": [
        "mango lassi", "aam lassi", "mango yogurt drink"
    ],
    "Paneer (Raw)": [
        "paneer", "raw paneer", "cottage cheese", "chenna",
        "fresh paneer"
    ],
    "Boiled Egg": [
        "boiled egg", "egg", "hard boiled egg", "anda",
        "soft boiled egg", "whole egg"
    ],
    "Egg Curry": [
        "egg curry", "anda curry", "egg masala", "anda masala",
        "boiled egg curry"
    ],
    "Omelette": [
        "omelette", "omelet", "egg omelette", "masala omelette",
        "plain omelette"
    ],
    "Egg Bhurji / Scrambled Egg": [
        "egg bhurji", "scrambled egg", "anda bhurji",
        "spiced scrambled egg"
    ],

    # ── Raw Vegetables ───────────────────────────────────────────────────────
    "Tomato": [
        "tomato", "tamatar", "raw tomato", "sliced tomato"
    ],
    "Onion": [
        "onion", "pyaz", "kanda", "raw onion", "sliced onion"
    ],
    "Potato": [
        "potato", "aloo", "raw potato", "boiled potato"
    ],
    "Carrot": [
        "carrot", "gajar", "raw carrot"
    ],
    "Spinach / Palak": [
        "spinach", "palak", "raw spinach", "saag", "leafy greens"
    ],
    "Cauliflower / Gobi": [
        "cauliflower", "gobi", "phool gobi", "raw cauliflower"
    ],
    "Lady Finger / Bhindi": [
        "bhindi", "okra", "lady finger", "bhindi raw"
    ],
    "Brinjal / Baingan": [
        "brinjal", "baingan", "eggplant", "aubergine", "raw baingan"
    ],
    "Cucumber": [
        "cucumber", "kheera", "kakdi", "raw cucumber"
    ],
    "Capsicum / Bell Pepper": [
        "capsicum", "bell pepper", "shimla mirch", "green pepper"
    ],
    "Bitter Gourd / Karela": [
        "karela", "bitter gourd", "bitter melon", "momordica"
    ],
    "Radish / Mooli": [
        "radish", "mooli", "white radish", "daikon"
    ],
    "Bottle Gourd / Lauki": [
        "lauki", "bottle gourd", "dudhi", "ghia", "calabash"
    ],
    "Drumstick / Moringa": [
        "drumstick", "moringa", "sahjan", "murungai", "drumstick vegetable"
    ],
    "Green Peas": [
        "green peas", "matar", "fresh peas", "garden peas"
    ],
    "Mushroom": [
        "mushroom", "button mushroom", "khumbi"
    ],
    "Corn / Maize": [
        "corn", "maize", "bhutta", "sweet corn", "makai"
    ],
    "Sweet Potato": [
        "sweet potato", "shakarkandi", "shakarkand"
    ],

    # ── Cooked Vegetable Dishes ──────────────────────────────────────────────
    "Mixed Vegetable Salad": [
        "salad", "vegetable salad", "green salad", "mixed salad",
        "kachumber", "side salad", "fresh salad"
    ],
    "Aloo Gobi": [
        "aloo gobi", "potato cauliflower", "gobi aloo",
        "potato cauliflower sabzi"
    ],
    "Bhindi / Okra Fry": [
        "bhindi fry", "okra fry", "fried okra", "bhindi masala",
        "sauteed okra"
    ],
    "Baingan Bharta": [
        "baingan bharta", "roasted eggplant", "smoky brinjal",
        "eggplant mash", "begun bharta"
    ],
    "Aloo Sabzi": [
        "aloo sabzi", "potato curry", "jeera aloo", "sookha aloo",
        "potato dish"
    ],
    "Aloo Matar": [
        "aloo matar", "potato pea curry", "mutter aloo"
    ],
    "Jeera Aloo": [
        "jeera aloo", "cumin potato", "zeera aloo"
    ],
    "Karela Sabzi": [
        "karela sabzi", "bitter gourd fry", "stuffed karela"
    ],
    "Mixed Veg Curry": [
        "mixed veg", "veg curry", "mixed vegetable curry",
        "sabzi", "vegetable masala"
    ],
    "Lauki Sabzi": [
        "lauki sabzi", "bottle gourd curry", "dudhi sabzi"
    ],
    "Mushroom Masala": [
        "mushroom masala", "mushroom curry", "mushroom sabzi",
        "khumbi masala"
    ],
    "Green Chutney": [
        "green chutney", "mint chutney", "coriander chutney",
        "pudina chutney", "dhaniya chutney", "dip"
    ],
    "Tamarind Chutney": [
        "tamarind chutney", "imli chutney", "sweet chutney",
        "date chutney", "meethi chutney"
    ],
    "Pickle / Achar": [
        "pickle", "achar", "achaar", "mango pickle", "mixed pickle",
        "lime pickle", "nimbu achar"
    ],

    # ── Fruits ───────────────────────────────────────────────────────────────
    "Mango": ["mango", "aam", "alphonso", "kesar mango", "fresh mango"],
    "Banana": ["banana", "kela", "plantain"],
    "Apple": ["apple", "seb", "red apple", "green apple"],
    "Orange": ["orange", "santra", "narangi", "citrus"],
    "Papaya": ["papaya", "papita", "raw papaya"],
    "Guava": ["guava", "amrood", "peru"],
    "Grapes": ["grapes", "angoor", "black grapes", "green grapes"],
    "Watermelon": ["watermelon", "tarbooz", "tarbuja"],
    "Pineapple": ["pineapple", "ananas", "fresh pineapple"],
    "Pomegranate": ["pomegranate", "anar", "pomegranate seeds", "anardana"],
    "Coconut (Fresh)": [
        "coconut", "nariyal", "fresh coconut", "coconut flesh",
        "thengai", "grated coconut"
    ],
    "Lychee": ["lychee", "litchi", "lichi"],
    "Chikoo / Sapota": ["chikoo", "sapota", "sapodilla", "chiku"],
    "Amla / Indian Gooseberry": [
        "amla", "indian gooseberry", "gooseberry", "awla",
        "amalaki"
    ],

    # ── Meat, Fish & Poultry ─────────────────────────────────────────────────
    "Chicken Curry": [
        "chicken curry", "murgh curry", "chicken gravy",
        "chicken masala", "chicken sabzi"
    ],
    "Butter Chicken": [
        "butter chicken", "murgh makhani", "chicken makhani",
        "tikka masala", "murgh makhanwala"
    ],
    "Chicken Tikka Masala": [
        "chicken tikka masala", "tikka masala", "ctm",
        "british curry", "chicken tikka"
    ],
    "Tandoori Chicken": [
        "tandoori chicken", "roasted chicken", "tandoor chicken",
        "baked chicken", "grilled chicken"
    ],
    "Chicken Kebab": [
        "chicken kebab", "seekh kebab", "shami kebab",
        "reshmi kebab", "grilled kebab"
    ],
    "Mutton Curry": [
        "mutton curry", "lamb curry", "gosht curry",
        "mutton masala", "goat curry"
    ],
    "Keema Matar": [
        "keema matar", "minced meat peas", "kheema",
        "mince curry", "keema"
    ],
    "Fish Curry": [
        "fish curry", "macher jhol", "fish masala", "fish gravy",
        "fish dish"
    ],
    "Fish Fry": [
        "fish fry", "fried fish", "tawa fish", "fish cutlet"
    ],
    "Prawn Curry": [
        "prawn curry", "shrimp curry", "jhinga curry",
        "kolambi masala"
    ],
    "Prawn Masala": [
        "prawn masala", "shrimp masala", "jhinga masala",
        "goan prawn curry"
    ],
    "Liver Fry": [
        "liver fry", "kaleji", "chicken liver", "mutton liver"
    ],
    "Chicken Fried Rice": [
        "chicken fried rice", "indo chinese rice", "schezwan rice"
    ],
    "Chicken Pulao": [
        "chicken pulao", "murgh pulao", "chicken pilaf"
    ],
    "Boiled Chicken": [
        "boiled chicken", "plain chicken", "poached chicken",
        "steamed chicken"
    ],
    "Sardine / Mackerel Curry": [
        "sardine curry", "mackerel curry", "bangda curry",
        "mathi curry", "herring curry"
    ],
    "Crab Curry": [
        "crab curry", "kekda masala", "crab masala",
        "coastal crab curry"
    ],

    # ── Nuts & Seeds ─────────────────────────────────────────────────────────
    "Almonds": [
        "almonds", "badam", "raw almonds", "soaked almonds"
    ],
    "Cashew Nuts": [
        "cashew", "kaju", "cashew nuts", "roasted cashew"
    ],
    "Peanuts / Groundnuts": [
        "peanuts", "groundnuts", "mungfali", "moongphali",
        "roasted peanuts"
    ],
    "Walnuts": [
        "walnuts", "akhrot", "walnut halves"
    ],
    "Sesame Seeds": [
        "sesame", "til", "sesame seeds", "white sesame"
    ],
    "Flaxseeds": [
        "flaxseeds", "alsi", "linseed", "flax"
    ],
    "Sunflower Seeds": [
        "sunflower seeds", "surajmukhi ke beej"
    ],
    "Mixed Nuts": [
        "mixed nuts", "nuts mix", "trail mix", "dry fruits"
    ],

    # ── Oils & Fats ──────────────────────────────────────────────────────────
    "Ghee": [
        "ghee", "clarified butter", "desi ghee", "cow ghee"
    ],
    "Cooking Oil": [
        "oil", "cooking oil", "mustard oil", "sunflower oil",
        "refined oil", "vegetable oil"
    ],
    "Butter": [
        "butter", "makhan", "white butter", "salted butter"
    ],
    "Coconut Oil": [
        "coconut oil", "nariyal tel", "virgin coconut oil"
    ],

    # ── Sweets & Desserts ────────────────────────────────────────────────────
    "Gulab Jamun": [
        "gulab jamun", "milk solid sweet", "fried milk sweet",
        "khoya balls", "dessert balls"
    ],
    "Kheer / Rice Pudding": [
        "kheer", "rice pudding", "payasam", "rice kheer",
        "milk rice dessert"
    ],
    "Halwa": [
        "halwa", "suji halwa", "sooji halwa", "sheera",
        "semolina pudding", "aate ka halwa", "gajar halwa"
    ],
    "Ladoo": [
        "ladoo", "laddu", "besan ladoo", "motichoor ladoo",
        "round sweet"
    ],
    "Barfi / Burfi": [
        "barfi", "burfi", "milk cake", "kaju barfi", "milk fudge"
    ],
    "Jalebi": [
        "jalebi", "jilapi", "fried batter sweet", "orange sweet"
    ],
    "Rasgulla": [
        "rasgulla", "rasgola", "sponge rasgulla", "bengal sweet",
        "chenna ball"
    ],
    "Shrikhand": [
        "shrikhand", "strained yogurt sweet", "hung curd dessert"
    ],
    "Payasam": [
        "payasam", "kheer", "paysam", "south indian kheer",
        "semiya payasam"
    ],
    "Ice Cream": [
        "ice cream", "kulfi", "frozen dessert", "ice cream scoop"
    ],

    # ── Snacks & Street Food ─────────────────────────────────────────────────
    "Papad": [
        "papad", "poppadom", "poppadum", "papadum",
        "lentil cracker", "rice cracker", "crispy wafer"
    ],
    "Samosa": [
        "samosa", "samoosa", "fried pastry", "potato samosa",
        "veg samosa"
    ],
    "Pakora / Bhajiya": [
        "pakora", "pakoda", "bhajiya", "bhaji", "fritters",
        "onion pakora", "vegetable fritters"
    ],
    "Vada": [
        "vada", "wada", "medu vada", "dahi vada", "dal vada",
        "crispy lentil donut"
    ],
    "Murukku": [
        "murukku", "chakli", "spirals", "rice snack", "crunchy spiral"
    ],
    "Chakli": [
        "chakli", "murukku", "chivda", "crispy spiral snack"
    ],
    "Chivda / Chiwda": [
        "chivda", "chiwda", "poha chivda", "beaten rice snack",
        "namkeen mix"
    ],
    "Mixture / Bombay Mix": [
        "mixture", "bombay mix", "farsan", "namkeen", "spicy mix",
        "indian trail mix"
    ],

    # ── Beverages ────────────────────────────────────────────────────────────
    "Chai / Masala Tea": [
        "chai", "tea", "masala chai", "milk tea", "indian tea",
        "ginger tea", "adrak chai"
    ],
    "Filter Coffee": [
        "filter coffee", "south indian coffee", "kaapi",
        "coffee", "milk coffee"
    ],
    "Mango Lassi": [
        "mango lassi", "aam lassi", "mango smoothie",
        "mango yogurt drink"
    ],
    "Coconut Water": [
        "coconut water", "nariyal pani", "tender coconut",
        "green coconut water"
    ],
}

# ─── Auto-extend aliases with canonical name tokens ──────────────────────────
# Any food in the IFCT database that has no explicit alias entry
# gets its canonical name auto-added as its own "alias"
for _food_name in ALL_FOOD_NAMES:
    if _food_name not in FOOD_ALIASES:
        FOOD_ALIASES[_food_name] = []

# Build an inverted flat corpus for vectorization
# Each entry: (canonical_name, document_text)
_CORPUS: list[tuple[str, str]] = []
for canonical, aliases in FOOD_ALIASES.items():
    if canonical in IFCT_DATABASE:   # Only include foods in the database
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
    bigrams = [text[i:i+2] for i in range(len(text) - 1)
               if text[i] != " " and text[i+1] != " "]
    return words + bigrams


def _build_idf(corpus_docs: list[list[str]]) -> dict[str, float]:
    """Compute IDF weights from the corpus."""
    N = len(corpus_docs)
    df: Counter = Counter()
    for doc in corpus_docs:
        for token in set(doc):
            df[token] += 1
    return {token: math.log((N + 1) / (count + 1)) + 1
            for token, count in df.items()}


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

print(f"[SemanticMatcher] Indexed {len(_corpus_vectors)} foods from IFCT 2017 database")


# ─── Public API ───────────────────────────────────────────────────────────────

def match_food_semantic(
    query: str,
    top_k: int = 1,
    min_similarity: float = 0.05,
    fallback: str = "Paneer Butter Masala"
) -> tuple[str, float]:
    """
    Semantically matches a food name string to the closest entry in the
    full IFCT 2017 nutrition database using TF-IDF + character bigram
    cosine similarity.

    Args:
        query:          The food name returned by the VLM / detector.
        top_k:          How many candidates to return (default 1).
        min_similarity: Minimum cosine similarity to be considered a match.
                        Below this threshold, the fallback is returned.
        fallback:       Canonical name to return when no match found.

    Returns:
        (matched_canonical_name, similarity_score)
    """
    query_tokens = _tokenize(query)
    query_vector = _tf_idf_vector(query_tokens, _idf)

    scored: list[tuple[float, str]] = []
    for name, corpus_vec in _corpus_vectors:
        sim = _cosine_similarity(query_vector, corpus_vec)
        scored.append((sim, name))

    scored.sort(reverse=True)
    best_score, best_name = scored[0]

    print(f"[SemanticMatcher] '{query}' -> '{best_name}' (score={best_score:.3f})")

    if best_score < min_similarity:
        print(f"[SemanticMatcher] Score below threshold ({min_similarity}), "
              f"using fallback: '{fallback}'")
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
