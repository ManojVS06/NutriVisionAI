"""
NutriVision AI — IFCT (Indian Food Composition Tables) Database

Based on:
- Indian Food Composition Tables 2017, National Institute of Nutrition, India
- USDA FoodData Central (for non-Indian items)

Each entry contains per 100g nutritional values.
"""

from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# IFCT Nutrition Database
# Format: food_name → {nutrient: value_per_100g}
# Nutrients: calories(kcal), protein(g), carbs(g), fat(g), fiber(g),
#            sugar(g), sodium(mg), calcium(mg), iron(mg), potassium(mg),
#            vitamin_c(mg), vitamin_a(mcg), folate(mcg), zinc(mg)
# ─────────────────────────────────────────────────────────────────────────────

IFCT_DATABASE: dict[str, dict] = {

    # ─────────────────── Grains & Rice ───────────────────
    "basmati rice": {
        "calories": 130, "protein": 2.4, "carbs": 28.0, "fat": 0.2,
        "fiber": 0.3, "sugar": 0.0, "sodium": 1, "calcium": 5,
        "iron": 0.2, "potassium": 35, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 3, "zinc": 0.5, "category": "grain",
        "aliases": ["steamed rice", "white rice", "rice", "cooked rice"],
        "region": "pan-india"
    },
    "brown rice": {
        "calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9,
        "fiber": 1.8, "sugar": 0.4, "sodium": 5, "calcium": 10,
        "iron": 0.5, "potassium": 79, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 4, "zinc": 0.6, "category": "grain",
        "aliases": ["brown rice cooked"],
        "region": "pan-india"
    },
    "roti": {
        "calories": 297, "protein": 8.5, "carbs": 60.0, "fat": 3.7,
        "fiber": 2.7, "sugar": 0.5, "sodium": 492, "calcium": 24,
        "iron": 2.1, "potassium": 150, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 15, "zinc": 0.9, "category": "bread",
        "aliases": ["chapati", "phulka", "wheat roti", "atta roti"],
        "region": "north-india"
    },
    "paratha": {
        "calories": 326, "protein": 7.2, "carbs": 52.0, "fat": 10.8,
        "fiber": 2.4, "sugar": 0.8, "sodium": 520, "calcium": 22,
        "iron": 1.9, "potassium": 130, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 14, "zinc": 0.8, "category": "bread",
        "aliases": ["plain paratha", "lachha paratha"],
        "region": "north-india"
    },
    "aloo paratha": {
        "calories": 267, "protein": 6.1, "carbs": 43.5, "fat": 8.0,
        "fiber": 3.0, "sugar": 1.2, "sodium": 480, "calcium": 26,
        "iron": 1.8, "potassium": 220, "vitamin_c": 8, "vitamin_a": 2,
        "folate": 18, "zinc": 0.7, "category": "bread",
        "aliases": ["potato paratha"],
        "region": "north-india"
    },
    "puri": {
        "calories": 340, "protein": 7.8, "carbs": 50.0, "fat": 12.5,
        "fiber": 1.8, "sugar": 0.4, "sodium": 380, "calcium": 18,
        "iron": 1.7, "potassium": 115, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 11, "zinc": 0.7, "category": "bread",
        "aliases": ["poori"],
        "region": "north-india"
    },
    "naan": {
        "calories": 317, "protein": 9.0, "carbs": 57.0, "fat": 7.0,
        "fiber": 2.1, "sugar": 2.0, "sodium": 640, "calcium": 40,
        "iron": 2.2, "potassium": 140, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 20, "zinc": 0.9, "category": "bread",
        "aliases": ["butter naan", "tandoori naan"],
        "region": "north-india"
    },
    "idli": {
        "calories": 58, "protein": 2.0, "carbs": 12.0, "fat": 0.2,
        "fiber": 0.5, "sugar": 0.1, "sodium": 165, "calcium": 12,
        "iron": 0.4, "potassium": 45, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 8, "zinc": 0.3, "category": "south-indian",
        "aliases": ["steamed idli", "rice idli"],
        "region": "south-india"
    },
    "dosa": {
        "calories": 133, "protein": 4.0, "carbs": 24.0, "fat": 2.8,
        "fiber": 0.8, "sugar": 0.3, "sodium": 385, "calcium": 18,
        "iron": 0.6, "potassium": 80, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 12, "zinc": 0.4, "category": "south-indian",
        "aliases": ["plain dosa", "sada dosa", "rice dosa"],
        "region": "south-india"
    },
    "masala dosa": {
        "calories": 168, "protein": 4.8, "carbs": 27.5, "fat": 5.2,
        "fiber": 2.1, "sugar": 1.0, "sodium": 420, "calcium": 28,
        "iron": 1.0, "potassium": 185, "vitamin_c": 10, "vitamin_a": 5,
        "folate": 18, "zinc": 0.6, "category": "south-indian",
        "aliases": [],
        "region": "south-india"
    },
    "upma": {
        "calories": 148, "protein": 3.5, "carbs": 25.0, "fat": 4.5,
        "fiber": 1.8, "sugar": 0.8, "sodium": 340, "calcium": 15,
        "iron": 0.8, "potassium": 120, "vitamin_c": 4, "vitamin_a": 15,
        "folate": 10, "zinc": 0.5, "category": "south-indian",
        "aliases": ["semolina upma", "rava upma"],
        "region": "south-india"
    },
    "poha": {
        "calories": 130, "protein": 2.8, "carbs": 27.5, "fat": 1.5,
        "fiber": 1.2, "sugar": 1.0, "sodium": 280, "calcium": 12,
        "iron": 1.5, "potassium": 90, "vitamin_c": 6, "vitamin_a": 8,
        "folate": 9, "zinc": 0.4, "category": "snack",
        "aliases": ["flattened rice", "beaten rice"],
        "region": "west-india"
    },

    # ─────────────────── Lentils & Legumes ───────────────────
    "dal tadka": {
        "calories": 90, "protein": 5.1, "carbs": 14.5, "fat": 2.0,
        "fiber": 3.0, "sugar": 0.5, "sodium": 280, "calcium": 28,
        "iron": 1.8, "potassium": 210, "vitamin_c": 1, "vitamin_a": 12,
        "folate": 35, "zinc": 0.6, "category": "lentil",
        "aliases": ["tadka dal", "yellow dal", "arhar dal"],
        "region": "north-india"
    },
    "dal makhani": {
        "calories": 132, "protein": 6.5, "carbs": 14.0, "fat": 6.0,
        "fiber": 3.5, "sugar": 0.8, "sodium": 380, "calcium": 45,
        "iron": 2.2, "potassium": 280, "vitamin_c": 2, "vitamin_a": 25,
        "folate": 40, "zinc": 0.9, "category": "lentil",
        "aliases": ["black dal", "makhani dal", "kali dal"],
        "region": "north-india"
    },
    "rajma": {
        "calories": 127, "protein": 8.7, "carbs": 22.0, "fat": 0.5,
        "fiber": 6.4, "sugar": 0.3, "sodium": 310, "calcium": 50,
        "iron": 3.0, "potassium": 400, "vitamin_c": 2, "vitamin_a": 5,
        "folate": 62, "zinc": 1.4, "category": "legume",
        "aliases": ["kidney beans curry", "rajma chawal"],
        "region": "north-india"
    },
    "chana masala": {
        "calories": 118, "protein": 7.2, "carbs": 18.0, "fat": 3.0,
        "fiber": 5.0, "sugar": 2.5, "sodium": 350, "calcium": 48,
        "iron": 2.8, "potassium": 360, "vitamin_c": 8, "vitamin_a": 18,
        "folate": 55, "zinc": 1.2, "category": "legume",
        "aliases": ["chole", "chickpea curry", "chhole masala"],
        "region": "north-india"
    },
    "sambar": {
        "calories": 55, "protein": 2.8, "carbs": 8.5, "fat": 1.5,
        "fiber": 2.8, "sugar": 2.0, "sodium": 420, "calcium": 35,
        "iron": 1.5, "potassium": 220, "vitamin_c": 15, "vitamin_a": 40,
        "folate": 28, "zinc": 0.5, "category": "lentil-soup",
        "aliases": ["south indian sambar"],
        "region": "south-india"
    },
    "moong dal": {
        "calories": 104, "protein": 7.0, "carbs": 17.5, "fat": 0.4,
        "fiber": 2.5, "sugar": 1.0, "sodium": 250, "calcium": 30,
        "iron": 1.6, "potassium": 195, "vitamin_c": 1, "vitamin_a": 5,
        "folate": 42, "zinc": 0.7, "category": "lentil",
        "aliases": ["green gram dal", "yellow moong"],
        "region": "pan-india"
    },

    # ─────────────────── Vegetables ───────────────────
    "aloo sabzi": {
        "calories": 97, "protein": 1.8, "carbs": 18.0, "fat": 2.8,
        "fiber": 2.0, "sugar": 1.5, "sodium": 290, "calcium": 12,
        "iron": 0.8, "potassium": 340, "vitamin_c": 16, "vitamin_a": 3,
        "folate": 15, "zinc": 0.4, "category": "vegetable",
        "aliases": ["potato sabzi", "aloo curry", "dum aloo"],
        "region": "pan-india"
    },
    "palak paneer": {
        "calories": 154, "protein": 8.0, "carbs": 8.5, "fat": 10.5,
        "fiber": 2.2, "sugar": 1.5, "sodium": 340, "calcium": 220,
        "iron": 2.5, "potassium": 295, "vitamin_c": 20, "vitamin_a": 150,
        "folate": 50, "zinc": 1.0, "category": "vegetable",
        "aliases": ["spinach paneer", "saag paneer"],
        "region": "north-india"
    },
    "paneer butter masala": {
        "calories": 198, "protein": 9.5, "carbs": 8.0, "fat": 15.0,
        "fiber": 1.5, "sugar": 4.5, "sodium": 420, "calcium": 230,
        "iron": 1.2, "potassium": 270, "vitamin_c": 12, "vitamin_a": 85,
        "folate": 18, "zinc": 0.9, "category": "vegetable",
        "aliases": ["paneer makhani", "butter paneer"],
        "region": "north-india"
    },
    "mixed vegetable": {
        "calories": 62, "protein": 2.5, "carbs": 9.5, "fat": 1.8,
        "fiber": 3.5, "sugar": 3.0, "sodium": 250, "calcium": 45,
        "iron": 1.2, "potassium": 310, "vitamin_c": 22, "vitamin_a": 65,
        "folate": 30, "zinc": 0.5, "category": "vegetable",
        "aliases": ["mix veg", "sabzi"],
        "region": "pan-india"
    },
    "bhindi masala": {
        "calories": 75, "protein": 2.0, "carbs": 9.5, "fat": 3.2,
        "fiber": 3.8, "sugar": 1.5, "sodium": 280, "calcium": 78,
        "iron": 0.7, "potassium": 295, "vitamin_c": 18, "vitamin_a": 36,
        "folate": 46, "zinc": 0.4, "category": "vegetable",
        "aliases": ["okra masala", "ladies finger curry"],
        "region": "pan-india"
    },
    "baingan bharta": {
        "calories": 68, "protein": 1.8, "carbs": 9.0, "fat": 3.0,
        "fiber": 3.5, "sugar": 3.5, "sodium": 310, "calcium": 25,
        "iron": 0.6, "potassium": 280, "vitamin_c": 8, "vitamin_a": 12,
        "folate": 18, "zinc": 0.3, "category": "vegetable",
        "aliases": ["eggplant curry", "baigan bharta"],
        "region": "north-india"
    },

    # ─────────────────── Non-Vegetarian ───────────────────
    "chicken curry": {
        "calories": 175, "protein": 22.0, "carbs": 5.0, "fat": 8.0,
        "fiber": 1.0, "sugar": 1.5, "sodium": 420, "calcium": 25,
        "iron": 1.5, "potassium": 340, "vitamin_c": 5, "vitamin_a": 20,
        "folate": 12, "zinc": 2.2, "category": "non-veg",
        "aliases": ["murgh curry", "chicken gravy"],
        "region": "pan-india"
    },
    "butter chicken": {
        "calories": 210, "protein": 20.0, "carbs": 8.5, "fat": 11.5,
        "fiber": 1.2, "sugar": 4.0, "sodium": 480, "calcium": 35,
        "iron": 1.4, "potassium": 320, "vitamin_c": 8, "vitamin_a": 55,
        "folate": 15, "zinc": 2.0, "category": "non-veg",
        "aliases": ["murgh makhani", "chicken makhani"],
        "region": "north-india"
    },
    "chicken biryani": {
        "calories": 192, "protein": 13.5, "carbs": 26.0, "fat": 4.5,
        "fiber": 1.5, "sugar": 0.8, "sodium": 510, "calcium": 28,
        "iron": 1.8, "potassium": 270, "vitamin_c": 4, "vitamin_a": 22,
        "folate": 20, "zinc": 1.8, "category": "non-veg",
        "aliases": ["biryani chicken", "hyderabadi biryani"],
        "region": "pan-india"
    },
    "fish curry": {
        "calories": 165, "protein": 20.5, "carbs": 5.5, "fat": 7.0,
        "fiber": 1.0, "sugar": 1.0, "sodium": 380, "calcium": 45,
        "iron": 1.2, "potassium": 360, "vitamin_c": 6, "vitamin_a": 35,
        "folate": 18, "zinc": 1.5, "category": "non-veg",
        "aliases": ["machli curry", "fish masala"],
        "region": "coastal-india"
    },
    "egg curry": {
        "calories": 148, "protein": 10.5, "carbs": 6.0, "fat": 9.5,
        "fiber": 1.2, "sugar": 2.0, "sodium": 360, "calcium": 55,
        "iron": 1.8, "potassium": 220, "vitamin_c": 5, "vitamin_a": 55,
        "folate": 25, "zinc": 1.2, "category": "non-veg",
        "aliases": ["anda curry", "egg masala"],
        "region": "pan-india"
    },
    "boiled eggs": {
        "calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 10.6,
        "fiber": 0, "sugar": 1.1, "sodium": 124, "calcium": 50,
        "iron": 1.8, "potassium": 126, "vitamin_c": 0, "vitamin_a": 149,
        "folate": 44, "zinc": 1.3, "category": "non-veg",
        "aliases": ["boiled egg", "hard boiled egg", "egg"],
        "region": "pan-india"
    },

    # ─────────────────── Rice Dishes ───────────────────
    "veg biryani": {
        "calories": 155, "protein": 4.5, "carbs": 28.0, "fat": 3.8,
        "fiber": 2.8, "sugar": 1.5, "sodium": 460, "calcium": 35,
        "iron": 1.5, "potassium": 220, "vitamin_c": 6, "vitamin_a": 30,
        "folate": 22, "zinc": 0.9, "category": "rice",
        "aliases": ["vegetable biryani", "veg dum biryani"],
        "region": "pan-india"
    },
    "pulao": {
        "calories": 148, "protein": 3.5, "carbs": 27.5, "fat": 3.2,
        "fiber": 1.8, "sugar": 1.0, "sodium": 380, "calcium": 18,
        "iron": 0.8, "potassium": 140, "vitamin_c": 3, "vitamin_a": 15,
        "folate": 15, "zinc": 0.6, "category": "rice",
        "aliases": ["veg pulao", "vegetable pulao"],
        "region": "pan-india"
    },
    "curd rice": {
        "calories": 102, "protein": 3.8, "carbs": 19.0, "fat": 1.8,
        "fiber": 0.4, "sugar": 2.5, "sodium": 210, "calcium": 85,
        "iron": 0.3, "potassium": 120, "vitamin_c": 0, "vitamin_a": 8,
        "folate": 8, "zinc": 0.5, "category": "rice",
        "aliases": ["thayir sadam", "yogurt rice"],
        "region": "south-india"
    },
    "lemon rice": {
        "calories": 145, "protein": 2.8, "carbs": 27.0, "fat": 3.5,
        "fiber": 1.0, "sugar": 0.5, "sodium": 310, "calcium": 12,
        "iron": 0.5, "potassium": 95, "vitamin_c": 12, "vitamin_a": 5,
        "folate": 10, "zinc": 0.4, "category": "rice",
        "aliases": ["chitranna"],
        "region": "south-india"
    },

    # ─────────────────── Dairy ───────────────────
    "curd": {
        "calories": 61, "protein": 3.4, "carbs": 4.7, "fat": 3.3,
        "fiber": 0, "sugar": 4.7, "sodium": 46, "calcium": 110,
        "iron": 0.1, "potassium": 155, "vitamin_c": 0, "vitamin_a": 18,
        "folate": 11, "zinc": 0.5, "category": "dairy",
        "aliases": ["yogurt", "dahi", "plain curd", "lassi"],
        "region": "pan-india"
    },
    "paneer": {
        "calories": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8,
        "fiber": 0, "sugar": 1.2, "sodium": 30, "calcium": 480,
        "iron": 0.3, "potassium": 79, "vitamin_c": 0, "vitamin_a": 80,
        "folate": 8, "zinc": 1.8, "category": "dairy",
        "aliases": ["cottage cheese", "fresh paneer"],
        "region": "pan-india"
    },
    "raita": {
        "calories": 45, "protein": 2.5, "carbs": 5.0, "fat": 1.5,
        "fiber": 0.5, "sugar": 3.8, "sodium": 220, "calcium": 90,
        "iron": 0.2, "potassium": 140, "vitamin_c": 3, "vitamin_a": 15,
        "folate": 8, "zinc": 0.4, "category": "dairy",
        "aliases": ["cucumber raita", "boondi raita", "vegetable raita"],
        "region": "pan-india"
    },
    "buttermilk": {
        "calories": 40, "protein": 3.3, "carbs": 4.8, "fat": 0.9,
        "fiber": 0, "sugar": 4.8, "sodium": 105, "calcium": 115,
        "iron": 0.1, "potassium": 151, "vitamin_c": 0, "vitamin_a": 7,
        "folate": 5, "zinc": 0.4, "category": "dairy",
        "aliases": ["chaas", "lassi", "mattha"],
        "region": "pan-india"
    },

    # ─────────────────── Snacks ───────────────────
    "samosa": {
        "calories": 262, "protein": 4.5, "carbs": 33.0, "fat": 12.5,
        "fiber": 2.8, "sugar": 1.5, "sodium": 420, "calcium": 25,
        "iron": 1.4, "potassium": 280, "vitamin_c": 8, "vitamin_a": 5,
        "folate": 18, "zinc": 0.6, "category": "snack",
        "aliases": ["aloo samosa", "potato samosa"],
        "region": "north-india"
    },
    "pakora": {
        "calories": 258, "protein": 6.5, "carbs": 26.5, "fat": 14.0,
        "fiber": 2.0, "sugar": 0.8, "sodium": 380, "calcium": 65,
        "iron": 2.0, "potassium": 190, "vitamin_c": 5, "vitamin_a": 12,
        "folate": 22, "zinc": 0.8, "category": "snack",
        "aliases": ["bhajiya", "vegetable pakora", "onion pakora"],
        "region": "pan-india"
    },
    "pav bhaji": {
        "calories": 178, "protein": 5.5, "carbs": 28.5, "fat": 5.5,
        "fiber": 5.0, "sugar": 4.0, "sodium": 540, "calcium": 50,
        "iron": 2.5, "potassium": 380, "vitamin_c": 35, "vitamin_a": 55,
        "folate": 38, "zinc": 0.9, "category": "snack",
        "aliases": ["bhaji pav"],
        "region": "west-india"
    },
    "vada pav": {
        "calories": 285, "protein": 6.8, "carbs": 42.0, "fat": 10.5,
        "fiber": 3.2, "sugar": 2.5, "sodium": 580, "calcium": 42,
        "iron": 1.8, "potassium": 310, "vitamin_c": 12, "vitamin_a": 8,
        "folate": 25, "zinc": 0.8, "category": "snack",
        "aliases": ["batata vada pav"],
        "region": "west-india"
    },
    "dhokla": {
        "calories": 160, "protein": 5.0, "carbs": 25.0, "fat": 4.5,
        "fiber": 1.5, "sugar": 3.0, "sodium": 380, "calcium": 35,
        "iron": 1.0, "potassium": 145, "vitamin_c": 2, "vitamin_a": 5,
        "folate": 20, "zinc": 0.5, "category": "snack",
        "aliases": ["khaman dhokla", "steamed dhokla"],
        "region": "west-india"
    },

    # ─────────────────── Salads & Sides ───────────────────
    "green salad": {
        "calories": 20, "protein": 1.5, "carbs": 3.5, "fat": 0.2,
        "fiber": 2.0, "sugar": 1.5, "sodium": 15, "calcium": 40,
        "iron": 0.8, "potassium": 220, "vitamin_c": 25, "vitamin_a": 85,
        "folate": 45, "zinc": 0.3, "category": "salad",
        "aliases": ["garden salad", "mixed salad", "vegetable salad"],
        "region": "pan-india"
    },
    "kachumber salad": {
        "calories": 28, "protein": 1.0, "carbs": 5.0, "fat": 0.3,
        "fiber": 1.8, "sugar": 2.5, "sodium": 120, "calcium": 28,
        "iron": 0.5, "potassium": 190, "vitamin_c": 18, "vitamin_a": 30,
        "folate": 22, "zinc": 0.2, "category": "salad",
        "aliases": ["cucumber tomato salad", "indian salad"],
        "region": "pan-india"
    },
    "pickle": {
        "calories": 65, "protein": 0.8, "carbs": 6.5, "fat": 4.0,
        "fiber": 2.5, "sugar": 0.5, "sodium": 1850, "calcium": 22,
        "iron": 0.8, "potassium": 95, "vitamin_c": 2, "vitamin_a": 8,
        "folate": 5, "zinc": 0.2, "category": "condiment",
        "aliases": ["achar", "mango pickle", "lime pickle"],
        "region": "pan-india"
    },
    "papad": {
        "calories": 354, "protein": 18.0, "carbs": 52.0, "fat": 7.5,
        "fiber": 6.0, "sugar": 0.3, "sodium": 1250, "calcium": 48,
        "iron": 3.5, "potassium": 350, "vitamin_c": 0, "vitamin_a": 0,
        "folate": 38, "zinc": 1.5, "category": "condiment",
        "aliases": ["pappad", "roasted papad"],
        "region": "pan-india"
    },
    "chutney": {
        "calories": 42, "protein": 1.2, "carbs": 7.0, "fat": 1.2,
        "fiber": 1.5, "sugar": 3.5, "sodium": 280, "calcium": 30,
        "iron": 0.8, "potassium": 140, "vitamin_c": 12, "vitamin_a": 25,
        "folate": 15, "zinc": 0.2, "category": "condiment",
        "aliases": ["coconut chutney", "mint chutney", "tamarind chutney"],
        "region": "pan-india"
    },

    # ─────────────────── Sweets & Desserts ───────────────────
    "kheer": {
        "calories": 162, "protein": 4.8, "carbs": 28.0, "fat": 4.0,
        "fiber": 0.2, "sugar": 22.0, "sodium": 65, "calcium": 145,
        "iron": 0.3, "potassium": 180, "vitamin_c": 0, "vitamin_a": 40,
        "folate": 6, "zinc": 0.6, "category": "dessert",
        "aliases": ["rice kheer", "rice pudding", "chawal ki kheer"],
        "region": "pan-india"
    },
    "gulab jamun": {
        "calories": 357, "protein": 5.5, "carbs": 55.0, "fat": 13.5,
        "fiber": 0.5, "sugar": 42.0, "sodium": 120, "calcium": 80,
        "iron": 0.8, "potassium": 110, "vitamin_c": 0, "vitamin_a": 25,
        "folate": 5, "zinc": 0.5, "category": "dessert",
        "aliases": ["gulabjamun"],
        "region": "pan-india"
    },
    "halwa": {
        "calories": 295, "protein": 4.5, "carbs": 40.0, "fat": 13.0,
        "fiber": 1.5, "sugar": 28.0, "sodium": 85, "calcium": 35,
        "iron": 1.2, "potassium": 120, "vitamin_c": 0, "vitamin_a": 30,
        "folate": 8, "zinc": 0.5, "category": "dessert",
        "aliases": ["sooji halwa", "atta halwa", "gajar halwa"],
        "region": "pan-india"
    },

    # ─────────────────── Beverages ───────────────────
    "chai": {
        "calories": 60, "protein": 1.5, "carbs": 8.5, "fat": 2.0,
        "fiber": 0, "sugar": 7.5, "sodium": 30, "calcium": 60,
        "iron": 0.1, "potassium": 85, "vitamin_c": 0, "vitamin_a": 12,
        "folate": 2, "zinc": 0.1, "category": "beverage",
        "aliases": ["masala chai", "tea", "milk tea", "indian tea"],
        "region": "pan-india"
    },
    "lassi": {
        "calories": 68, "protein": 2.8, "carbs": 9.5, "fat": 2.2,
        "fiber": 0, "sugar": 9.0, "sodium": 55, "calcium": 95,
        "iron": 0.1, "potassium": 130, "vitamin_c": 0, "vitamin_a": 15,
        "folate": 5, "zinc": 0.4, "category": "beverage",
        "aliases": ["sweet lassi", "punjabi lassi", "mango lassi"],
        "region": "north-india"
    },

    # ─────────────────── Fruits ───────────────────
    "mango": {
        "calories": 60, "protein": 0.8, "carbs": 15.0, "fat": 0.4,
        "fiber": 1.6, "sugar": 13.7, "sodium": 1, "calcium": 11,
        "iron": 0.2, "potassium": 168, "vitamin_c": 36, "vitamin_a": 54,
        "folate": 14, "zinc": 0.1, "category": "fruit",
        "aliases": ["alphonso mango", "mango slice"],
        "region": "pan-india"
    },
    "banana": {
        "calories": 89, "protein": 1.1, "carbs": 23.0, "fat": 0.3,
        "fiber": 2.6, "sugar": 12.2, "sodium": 1, "calcium": 5,
        "iron": 0.3, "potassium": 358, "vitamin_c": 8, "vitamin_a": 3,
        "folate": 20, "zinc": 0.2, "category": "fruit",
        "aliases": ["ripe banana"],
        "region": "pan-india"
    },
}


def search_food(query: str, threshold: float = 0.6) -> Optional[tuple[str, dict]]:
    """
    Search for a food item in the IFCT database.
    Uses alias matching and fuzzy search.

    Args:
        query: Food name to search for
        threshold: Minimum match score (0-1)

    Returns:
        Tuple of (canonical_name, nutrition_data) or None if not found
    """
    query_lower = query.lower().strip()

    # Exact match
    if query_lower in IFCT_DATABASE:
        return query_lower, IFCT_DATABASE[query_lower]

    # Alias match
    for food_name, data in IFCT_DATABASE.items():
        aliases = data.get("aliases", [])
        if query_lower in [a.lower() for a in aliases]:
            return food_name, data

    # Partial match (any word from query matches food name)
    query_words = set(query_lower.split())
    best_match = None
    best_score = 0.0

    for food_name, data in IFCT_DATABASE.items():
        food_words = set(food_name.lower().split())
        aliases = [a.lower() for a in data.get("aliases", [])]

        # Score by word overlap
        overlap = len(query_words & food_words)
        if overlap > 0:
            score = overlap / max(len(query_words), len(food_words))
            if score > best_score:
                best_score = score
                best_match = (food_name, data)

        # Check aliases
        for alias in aliases:
            alias_words = set(alias.split())
            overlap = len(query_words & alias_words)
            if overlap > 0:
                score = overlap / max(len(query_words), len(alias_words))
                if score > best_score:
                    best_score = score
                    best_match = (food_name, data)

    if best_match and best_score >= threshold:
        return best_match

    return None


def get_all_food_names() -> list[str]:
    """Return all canonical food names in the database."""
    return list(IFCT_DATABASE.keys())


def get_foods_by_category(category: str) -> dict:
    """Return all foods in a given category."""
    return {
        name: data for name, data in IFCT_DATABASE.items()
        if data.get("category") == category
    }


def get_foods_by_region(region: str) -> dict:
    """Return all foods from a given regional cuisine."""
    return {
        name: data for name, data in IFCT_DATABASE.items()
        if data.get("region") == region or data.get("region") == "pan-india"
    }
