"""
NutriVisionAI — Full IFCT 2017 Database
Indian Food Composition Tables (National Institute of Nutrition, ICMR)

Coverage: 156 food items across 12 food groups
Source: IFCT 2017, NIN Hyderabad + USDA supplement for dishes
All values are per 100g of the EDIBLE/PREPARED portion.

Extra field "density" (g/cm³) is custom-added for volume→weight estimation
in the depth-based portion estimation pipeline (not from IFCT).

Groups:
  Cereals & Millets      — 28 items
  Pulses & Legumes       — 18 items
  Dairy & Eggs           — 12 items
  Vegetables (Raw)       — 18 items
  Vegetables (Cooked)    — 14 items
  Fruits                 — 14 items
  Meat, Fish & Poultry   — 18 items
  Nuts & Seeds           — 8 items
  Oils & Fats            — 4 items
  Sweets & Desserts      — 10 items
  Snacks & Street Food   — 8 items
  Beverages              — 4 items
  Total: 158 items
"""

# ─── Schema per entry ────────────────────────────────────────────────────────
# density        : float   — g/cm³  (custom, for 3D portion estimation)
# calories_100g  : float   — kcal / 100g
# protein_100g   : float   — g / 100g
# carbs_100g     : float   — g / 100g
# fat_100g       : float   — g / 100g
# fiber_100g     : float   — g / 100g
# sodium_100g    : float   — mg / 100g
# sugar_100g     : float   — g / 100g
# category       : str     — food group label
# ─────────────────────────────────────────────────────────────────────────────

IFCT_DATABASE: dict[str, dict] = {

    # =========================================================================
    # CEREALS & MILLETS (28)
    # =========================================================================

    # Rice varieties
    "Cooked White Rice": {
        "density": 0.82, "calories_100g": 130, "protein_100g": 2.7,
        "carbs_100g": 28.0, "fat_100g": 0.3, "fiber_100g": 0.4,
        "sodium_100g": 1.0, "sugar_100g": 0.1, "category": "Cereals"
    },
    "Cooked Brown Rice": {
        "density": 0.85, "calories_100g": 123, "protein_100g": 2.6,
        "carbs_100g": 25.6, "fat_100g": 0.9, "fiber_100g": 1.8,
        "sodium_100g": 2.0, "sugar_100g": 0.3, "category": "Cereals"
    },
    "Cooked Parboiled Rice": {
        "density": 0.84, "calories_100g": 126, "protein_100g": 2.8,
        "carbs_100g": 27.0, "fat_100g": 0.3, "fiber_100g": 0.5,
        "sodium_100g": 2.0, "sugar_100g": 0.1, "category": "Cereals"
    },
    "Jeera Rice": {
        "density": 0.82, "calories_100g": 142, "protein_100g": 2.8,
        "carbs_100g": 26.0, "fat_100g": 3.2, "fiber_100g": 0.5,
        "sodium_100g": 120.0, "sugar_100g": 0.2, "category": "Cereals"
    },
    "Lemon Rice": {
        "density": 0.82, "calories_100g": 148, "protein_100g": 2.9,
        "carbs_100g": 27.0, "fat_100g": 3.8, "fiber_100g": 0.6,
        "sodium_100g": 140.0, "sugar_100g": 0.5, "category": "Cereals"
    },
    "Curd Rice": {
        "density": 0.88, "calories_100g": 110, "protein_100g": 3.8,
        "carbs_100g": 16.0, "fat_100g": 3.2, "fiber_100g": 0.3,
        "sodium_100g": 90.0, "sugar_100g": 2.0, "category": "Cereals"
    },
    "Khichdi": {
        "density": 0.90, "calories_100g": 118, "protein_100g": 4.5,
        "carbs_100g": 20.0, "fat_100g": 2.5, "fiber_100g": 1.5,
        "sodium_100g": 180.0, "sugar_100g": 0.4, "category": "Cereals"
    },
    "Chicken Biryani": {
        "density": 0.90, "calories_100g": 163, "protein_100g": 10.5,
        "carbs_100g": 22.0, "fat_100g": 5.6, "fiber_100g": 1.6,
        "sodium_100g": 310.0, "sugar_100g": 0.8, "category": "Cereals"
    },
    "Veg Biryani": {
        "density": 0.88, "calories_100g": 148, "protein_100g": 3.8,
        "carbs_100g": 24.0, "fat_100g": 4.8, "fiber_100g": 2.0,
        "sodium_100g": 280.0, "sugar_100g": 1.0, "category": "Cereals"
    },
    "Mutton Biryani": {
        "density": 0.92, "calories_100g": 185, "protein_100g": 12.0,
        "carbs_100g": 20.0, "fat_100g": 7.0, "fiber_100g": 1.2,
        "sodium_100g": 340.0, "sugar_100g": 0.6, "category": "Cereals"
    },
    "Fried Rice": {
        "density": 0.85, "calories_100g": 168, "protein_100g": 4.5,
        "carbs_100g": 25.0, "fat_100g": 5.5, "fiber_100g": 1.0,
        "sodium_100g": 480.0, "sugar_100g": 1.2, "category": "Cereals"
    },

    # Wheat & Breads
    "Roti / Chapati": {
        "density": 0.60, "calories_100g": 264, "protein_100g": 8.0,
        "carbs_100g": 48.0, "fat_100g": 3.0, "fiber_100g": 7.0,
        "sodium_100g": 5.0, "sugar_100g": 0.4, "category": "Cereals"
    },
    "Naan": {
        "density": 0.55, "calories_100g": 310, "protein_100g": 9.0,
        "carbs_100g": 54.0, "fat_100g": 6.5, "fiber_100g": 2.0,
        "sodium_100g": 400.0, "sugar_100g": 3.0, "category": "Cereals"
    },
    "Paratha": {
        "density": 0.58, "calories_100g": 326, "protein_100g": 7.0,
        "carbs_100g": 44.0, "fat_100g": 14.0, "fiber_100g": 3.0,
        "sodium_100g": 290.0, "sugar_100g": 1.0, "category": "Cereals"
    },
    "Aloo Paratha": {
        "density": 0.62, "calories_100g": 292, "protein_100g": 6.5,
        "carbs_100g": 42.0, "fat_100g": 11.0, "fiber_100g": 3.5,
        "sodium_100g": 320.0, "sugar_100g": 0.8, "category": "Cereals"
    },
    "Puri": {
        "density": 0.40, "calories_100g": 350, "protein_100g": 6.5,
        "carbs_100g": 42.0, "fat_100g": 18.0, "fiber_100g": 2.5,
        "sodium_100g": 310.0, "sugar_100g": 1.2, "category": "Cereals"
    },
    "Bhatura": {
        "density": 0.38, "calories_100g": 370, "protein_100g": 7.5,
        "carbs_100g": 44.0, "fat_100g": 19.0, "fiber_100g": 2.0,
        "sodium_100g": 340.0, "sugar_100g": 1.0, "category": "Cereals"
    },

    # South Indian
    "Idli": {
        "density": 0.65, "calories_100g": 120, "protein_100g": 6.0,
        "carbs_100g": 28.0, "fat_100g": 0.5, "fiber_100g": 1.5,
        "sodium_100g": 180.0, "sugar_100g": 0.2, "category": "Cereals"
    },
    "Dosa": {
        "density": 0.50, "calories_100g": 168, "protein_100g": 4.0,
        "carbs_100g": 28.0, "fat_100g": 4.5, "fiber_100g": 1.0,
        "sodium_100g": 200.0, "sugar_100g": 0.5, "category": "Cereals"
    },
    "Masala Dosa": {
        "density": 0.55, "calories_100g": 190, "protein_100g": 4.5,
        "carbs_100g": 30.0, "fat_100g": 6.0, "fiber_100g": 1.5,
        "sodium_100g": 220.0, "sugar_100g": 0.6, "category": "Cereals"
    },
    "Uttapam": {
        "density": 0.62, "calories_100g": 175, "protein_100g": 5.0,
        "carbs_100g": 28.0, "fat_100g": 5.0, "fiber_100g": 2.0,
        "sodium_100g": 230.0, "sugar_100g": 1.0, "category": "Cereals"
    },
    "Appam": {
        "density": 0.52, "calories_100g": 155, "protein_100g": 3.5,
        "carbs_100g": 28.0, "fat_100g": 3.5, "fiber_100g": 0.8,
        "sodium_100g": 160.0, "sugar_100g": 1.0, "category": "Cereals"
    },
    "Upma": {
        "density": 0.75, "calories_100g": 135, "protein_100g": 3.5,
        "carbs_100g": 18.0, "fat_100g": 5.5, "fiber_100g": 1.8,
        "sodium_100g": 250.0, "sugar_100g": 0.4, "category": "Cereals"
    },
    "Poha": {
        "density": 0.60, "calories_100g": 130, "protein_100g": 2.8,
        "carbs_100g": 22.0, "fat_100g": 3.8, "fiber_100g": 1.5,
        "sodium_100g": 210.0, "sugar_100g": 0.5, "category": "Cereals"
    },

    # Millets
    "Bajra Roti": {
        "density": 0.58, "calories_100g": 255, "protein_100g": 7.5,
        "carbs_100g": 46.0, "fat_100g": 4.0, "fiber_100g": 8.5,
        "sodium_100g": 10.0, "sugar_100g": 0.3, "category": "Cereals"
    },
    "Ragi / Finger Millet Porridge": {
        "density": 0.85, "calories_100g": 108, "protein_100g": 3.2,
        "carbs_100g": 22.0, "fat_100g": 0.8, "fiber_100g": 2.0,
        "sodium_100g": 15.0, "sugar_100g": 1.0, "category": "Cereals"
    },
    "Jowar Roti": {
        "density": 0.58, "calories_100g": 249, "protein_100g": 7.0,
        "carbs_100g": 46.0, "fat_100g": 3.5, "fiber_100g": 7.5,
        "sodium_100g": 8.0, "sugar_100g": 0.3, "category": "Cereals"
    },
    "Pesarattu": {
        "density": 0.55, "calories_100g": 145, "protein_100g": 8.5,
        "carbs_100g": 22.0, "fat_100g": 2.5, "fiber_100g": 2.5,
        "sodium_100g": 190.0, "sugar_100g": 0.4, "category": "Cereals"
    },
    "Dhokla": {
        "density": 0.55, "calories_100g": 142, "protein_100g": 5.5,
        "carbs_100g": 22.0, "fat_100g": 3.8, "fiber_100g": 1.5,
        "sodium_100g": 350.0, "sugar_100g": 1.5, "category": "Cereals"
    },

    # =========================================================================
    # PULSES & LEGUMES (18)
    # =========================================================================

    "Yellow Dal Tadka": {
        "density": 1.00, "calories_100g": 86, "protein_100g": 5.0,
        "carbs_100g": 12.0, "fat_100g": 2.2, "fiber_100g": 3.0,
        "sodium_100g": 280.0, "sugar_100g": 0.5, "category": "Pulses"
    },
    "Dal Makhani": {
        "density": 1.05, "calories_100g": 120, "protein_100g": 5.5,
        "carbs_100g": 12.0, "fat_100g": 5.5, "fiber_100g": 3.5,
        "sodium_100g": 320.0, "sugar_100g": 1.0, "category": "Pulses"
    },
    "Moong Dal": {
        "density": 1.00, "calories_100g": 92, "protein_100g": 6.8,
        "carbs_100g": 13.5, "fat_100g": 0.6, "fiber_100g": 2.8,
        "sodium_100g": 160.0, "sugar_100g": 0.8, "category": "Pulses"
    },
    "Masoor Dal": {
        "density": 1.00, "calories_100g": 88, "protein_100g": 6.0,
        "carbs_100g": 13.0, "fat_100g": 0.5, "fiber_100g": 3.2,
        "sodium_100g": 200.0, "sugar_100g": 0.6, "category": "Pulses"
    },
    "Urad Dal": {
        "density": 1.02, "calories_100g": 105, "protein_100g": 7.5,
        "carbs_100g": 15.0, "fat_100g": 0.8, "fiber_100g": 3.5,
        "sodium_100g": 220.0, "sugar_100g": 0.5, "category": "Pulses"
    },
    "Chana Dal": {
        "density": 1.02, "calories_100g": 164, "protein_100g": 8.0,
        "carbs_100g": 25.0, "fat_100g": 2.5, "fiber_100g": 5.0,
        "sodium_100g": 200.0, "sugar_100g": 1.0, "category": "Pulses"
    },
    "Rajma": {
        "density": 1.00, "calories_100g": 110, "protein_100g": 6.5,
        "carbs_100g": 16.0, "fat_100g": 2.0, "fiber_100g": 5.0,
        "sodium_100g": 310.0, "sugar_100g": 0.8, "category": "Pulses"
    },
    "Chole / Chana Masala": {
        "density": 1.00, "calories_100g": 125, "protein_100g": 7.0,
        "carbs_100g": 18.0, "fat_100g": 3.0, "fiber_100g": 5.0,
        "sodium_100g": 340.0, "sugar_100g": 1.5, "category": "Pulses"
    },
    "Sambar": {
        "density": 1.00, "calories_100g": 55, "protein_100g": 2.5,
        "carbs_100g": 8.5, "fat_100g": 1.2, "fiber_100g": 2.0,
        "sodium_100g": 320.0, "sugar_100g": 1.1, "category": "Pulses"
    },
    "Rasam": {
        "density": 1.00, "calories_100g": 30, "protein_100g": 1.0,
        "carbs_100g": 5.0, "fat_100g": 0.5, "fiber_100g": 0.5,
        "sodium_100g": 380.0, "sugar_100g": 0.5, "category": "Pulses"
    },
    "Pav Bhaji": {
        "density": 0.92, "calories_100g": 165, "protein_100g": 4.5,
        "carbs_100g": 22.0, "fat_100g": 7.0, "fiber_100g": 3.5,
        "sodium_100g": 420.0, "sugar_100g": 2.5, "category": "Pulses"
    },
    "Kadhi": {
        "density": 1.02, "calories_100g": 80, "protein_100g": 3.0,
        "carbs_100g": 8.0, "fat_100g": 4.0, "fiber_100g": 0.5,
        "sodium_100g": 290.0, "sugar_100g": 2.0, "category": "Pulses"
    },
    "Dal Fry": {
        "density": 1.00, "calories_100g": 98, "protein_100g": 5.5,
        "carbs_100g": 13.0, "fat_100g": 3.0, "fiber_100g": 3.0,
        "sodium_100g": 300.0, "sugar_100g": 0.6, "category": "Pulses"
    },
    "Lobia / Black Eyed Pea Curry": {
        "density": 1.00, "calories_100g": 115, "protein_100g": 6.8,
        "carbs_100g": 16.0, "fat_100g": 2.5, "fiber_100g": 4.5,
        "sodium_100g": 290.0, "sugar_100g": 1.0, "category": "Pulses"
    },
    "Sprouts Salad": {
        "density": 0.75, "calories_100g": 50, "protein_100g": 4.5,
        "carbs_100g": 7.0, "fat_100g": 0.5, "fiber_100g": 2.5,
        "sodium_100g": 20.0, "sugar_100g": 1.5, "category": "Pulses"
    },
    "Moong Dal Chilla": {
        "density": 0.65, "calories_100g": 148, "protein_100g": 9.0,
        "carbs_100g": 20.0, "fat_100g": 3.5, "fiber_100g": 2.5,
        "sodium_100g": 220.0, "sugar_100g": 0.5, "category": "Pulses"
    },
    "Cooked Black Chickpeas": {
        "density": 1.00, "calories_100g": 120, "protein_100g": 7.5,
        "carbs_100g": 17.0, "fat_100g": 2.0, "fiber_100g": 5.5,
        "sodium_100g": 250.0, "sugar_100g": 1.0, "category": "Pulses"
    },
    "Matar Paneer": {
        "density": 1.02, "calories_100g": 190, "protein_100g": 8.5,
        "carbs_100g": 10.0, "fat_100g": 13.0, "fiber_100g": 2.0,
        "sodium_100g": 320.0, "sugar_100g": 2.0, "category": "Pulses"
    },

    # =========================================================================
    # DAIRY & EGGS (12)
    # =========================================================================

    "Paneer Butter Masala": {
        "density": 1.05, "calories_100g": 229, "protein_100g": 9.2,
        "carbs_100g": 6.8, "fat_100g": 18.5, "fiber_100g": 0.8,
        "sodium_100g": 340.0, "sugar_100g": 3.2, "category": "Dairy"
    },
    "Shahi Paneer": {
        "density": 1.05, "calories_100g": 245, "protein_100g": 10.0,
        "carbs_100g": 8.0, "fat_100g": 19.0, "fiber_100g": 0.5,
        "sodium_100g": 350.0, "sugar_100g": 3.5, "category": "Dairy"
    },
    "Palak Paneer": {
        "density": 1.02, "calories_100g": 175, "protein_100g": 9.5,
        "carbs_100g": 6.0, "fat_100g": 13.0, "fiber_100g": 2.5,
        "sodium_100g": 310.0, "sugar_100g": 1.5, "category": "Dairy"
    },
    "Kadai Paneer": {
        "density": 1.04, "calories_100g": 220, "protein_100g": 10.0,
        "carbs_100g": 7.0, "fat_100g": 17.0, "fiber_100g": 1.5,
        "sodium_100g": 360.0, "sugar_100g": 2.5, "category": "Dairy"
    },
    "Matar Paneer": {
        "density": 1.02, "calories_100g": 190, "protein_100g": 8.5,
        "carbs_100g": 10.0, "fat_100g": 13.0, "fiber_100g": 2.0,
        "sodium_100g": 320.0, "sugar_100g": 2.0, "category": "Dairy"
    },
    "Curd / Raita": {
        "density": 1.03, "calories_100g": 60, "protein_100g": 3.5,
        "carbs_100g": 4.0, "fat_100g": 3.3, "fiber_100g": 0.0,
        "sodium_100g": 45.0, "sugar_100g": 4.0, "category": "Dairy"
    },
    "Lassi": {
        "density": 1.03, "calories_100g": 72, "protein_100g": 3.0,
        "carbs_100g": 10.0, "fat_100g": 2.5, "fiber_100g": 0.0,
        "sodium_100g": 50.0, "sugar_100g": 8.0, "category": "Dairy"
    },
    "Paneer (Raw)": {
        "density": 1.10, "calories_100g": 296, "protein_100g": 18.3,
        "carbs_100g": 1.2, "fat_100g": 24.0, "fiber_100g": 0.0,
        "sodium_100g": 28.0, "sugar_100g": 1.2, "category": "Dairy"
    },
    "Boiled Egg": {
        "density": 1.10, "calories_100g": 155, "protein_100g": 13.0,
        "carbs_100g": 1.1, "fat_100g": 11.0, "fiber_100g": 0.0,
        "sodium_100g": 124.0, "sugar_100g": 1.1, "category": "Dairy"
    },
    "Egg Curry": {
        "density": 1.00, "calories_100g": 145, "protein_100g": 10.0,
        "carbs_100g": 5.0, "fat_100g": 10.0, "fiber_100g": 0.8,
        "sodium_100g": 330.0, "sugar_100g": 1.2, "category": "Dairy"
    },
    "Omelette": {
        "density": 0.95, "calories_100g": 175, "protein_100g": 12.0,
        "carbs_100g": 2.0, "fat_100g": 13.5, "fiber_100g": 0.2,
        "sodium_100g": 340.0, "sugar_100g": 0.5, "category": "Dairy"
    },
    "Egg Bhurji / Scrambled Egg": {
        "density": 0.90, "calories_100g": 168, "protein_100g": 11.5,
        "carbs_100g": 3.0, "fat_100g": 12.5, "fiber_100g": 0.4,
        "sodium_100g": 380.0, "sugar_100g": 1.0, "category": "Dairy"
    },

    # =========================================================================
    # RAW VEGETABLES (18)
    # =========================================================================

    "Tomato": {
        "density": 0.62, "calories_100g": 18, "protein_100g": 0.9,
        "carbs_100g": 3.9, "fat_100g": 0.2, "fiber_100g": 1.2,
        "sodium_100g": 5.0, "sugar_100g": 2.6, "category": "Vegetables"
    },
    "Onion": {
        "density": 0.72, "calories_100g": 40, "protein_100g": 1.1,
        "carbs_100g": 9.3, "fat_100g": 0.1, "fiber_100g": 1.7,
        "sodium_100g": 4.0, "sugar_100g": 4.2, "category": "Vegetables"
    },
    "Potato": {
        "density": 1.05, "calories_100g": 77, "protein_100g": 2.0,
        "carbs_100g": 17.0, "fat_100g": 0.1, "fiber_100g": 2.2,
        "sodium_100g": 6.0, "sugar_100g": 0.8, "category": "Vegetables"
    },
    "Carrot": {
        "density": 0.68, "calories_100g": 41, "protein_100g": 0.9,
        "carbs_100g": 9.6, "fat_100g": 0.2, "fiber_100g": 2.8,
        "sodium_100g": 69.0, "sugar_100g": 4.7, "category": "Vegetables"
    },
    "Spinach / Palak": {
        "density": 0.35, "calories_100g": 23, "protein_100g": 2.9,
        "carbs_100g": 3.6, "fat_100g": 0.4, "fiber_100g": 2.2,
        "sodium_100g": 79.0, "sugar_100g": 0.4, "category": "Vegetables"
    },
    "Cauliflower / Gobi": {
        "density": 0.55, "calories_100g": 25, "protein_100g": 2.0,
        "carbs_100g": 5.0, "fat_100g": 0.3, "fiber_100g": 2.0,
        "sodium_100g": 30.0, "sugar_100g": 1.9, "category": "Vegetables"
    },
    "Lady Finger / Bhindi": {
        "density": 0.55, "calories_100g": 33, "protein_100g": 1.9,
        "carbs_100g": 7.5, "fat_100g": 0.2, "fiber_100g": 3.2,
        "sodium_100g": 7.0, "sugar_100g": 1.5, "category": "Vegetables"
    },
    "Brinjal / Baingan": {
        "density": 0.60, "calories_100g": 25, "protein_100g": 1.0,
        "carbs_100g": 5.9, "fat_100g": 0.2, "fiber_100g": 3.0,
        "sodium_100g": 2.0, "sugar_100g": 2.4, "category": "Vegetables"
    },
    "Cucumber": {
        "density": 0.62, "calories_100g": 16, "protein_100g": 0.7,
        "carbs_100g": 3.6, "fat_100g": 0.1, "fiber_100g": 0.5,
        "sodium_100g": 2.0, "sugar_100g": 1.7, "category": "Vegetables"
    },
    "Capsicum / Bell Pepper": {
        "density": 0.62, "calories_100g": 26, "protein_100g": 1.0,
        "carbs_100g": 6.0, "fat_100g": 0.3, "fiber_100g": 2.1,
        "sodium_100g": 4.0, "sugar_100g": 2.4, "category": "Vegetables"
    },
    "Bitter Gourd / Karela": {
        "density": 0.58, "calories_100g": 17, "protein_100g": 1.0,
        "carbs_100g": 3.7, "fat_100g": 0.2, "fiber_100g": 2.8,
        "sodium_100g": 5.0, "sugar_100g": 0.5, "category": "Vegetables"
    },
    "Radish / Mooli": {
        "density": 0.58, "calories_100g": 16, "protein_100g": 0.7,
        "carbs_100g": 3.4, "fat_100g": 0.1, "fiber_100g": 1.6,
        "sodium_100g": 39.0, "sugar_100g": 1.9, "category": "Vegetables"
    },
    "Bottle Gourd / Lauki": {
        "density": 0.60, "calories_100g": 15, "protein_100g": 0.6,
        "carbs_100g": 3.5, "fat_100g": 0.1, "fiber_100g": 0.5,
        "sodium_100g": 2.0, "sugar_100g": 1.5, "category": "Vegetables"
    },
    "Drumstick / Moringa": {
        "density": 0.45, "calories_100g": 37, "protein_100g": 2.1,
        "carbs_100g": 8.5, "fat_100g": 0.2, "fiber_100g": 3.2,
        "sodium_100g": 42.0, "sugar_100g": 0.5, "category": "Vegetables"
    },
    "Green Peas": {
        "density": 0.70, "calories_100g": 81, "protein_100g": 5.4,
        "carbs_100g": 14.5, "fat_100g": 0.4, "fiber_100g": 5.1,
        "sodium_100g": 5.0, "sugar_100g": 5.7, "category": "Vegetables"
    },
    "Mushroom": {
        "density": 0.55, "calories_100g": 22, "protein_100g": 3.1,
        "carbs_100g": 3.3, "fat_100g": 0.3, "fiber_100g": 1.0,
        "sodium_100g": 5.0, "sugar_100g": 2.0, "category": "Vegetables"
    },
    "Corn / Maize": {
        "density": 0.80, "calories_100g": 86, "protein_100g": 3.3,
        "carbs_100g": 18.7, "fat_100g": 1.4, "fiber_100g": 2.0,
        "sodium_100g": 15.0, "sugar_100g": 3.2, "category": "Vegetables"
    },
    "Sweet Potato": {
        "density": 0.98, "calories_100g": 86, "protein_100g": 1.6,
        "carbs_100g": 20.0, "fat_100g": 0.1, "fiber_100g": 3.0,
        "sodium_100g": 55.0, "sugar_100g": 4.2, "category": "Vegetables"
    },

    # =========================================================================
    # COOKED VEGETABLE DISHES (14)
    # =========================================================================

    "Mixed Vegetable Salad": {
        "density": 0.30, "calories_100g": 25, "protein_100g": 1.2,
        "carbs_100g": 4.5, "fat_100g": 0.2, "fiber_100g": 2.5,
        "sodium_100g": 10.0, "sugar_100g": 2.0, "category": "Vegetables"
    },
    "Aloo Gobi": {
        "density": 0.85, "calories_100g": 100, "protein_100g": 2.5,
        "carbs_100g": 12.0, "fat_100g": 5.0, "fiber_100g": 2.5,
        "sodium_100g": 260.0, "sugar_100g": 1.0, "category": "Vegetables"
    },
    "Bhindi / Okra Fry": {
        "density": 0.70, "calories_100g": 90, "protein_100g": 2.0,
        "carbs_100g": 8.0, "fat_100g": 6.0, "fiber_100g": 3.0,
        "sodium_100g": 190.0, "sugar_100g": 0.5, "category": "Vegetables"
    },
    "Baingan Bharta": {
        "density": 0.85, "calories_100g": 80, "protein_100g": 1.8,
        "carbs_100g": 7.0, "fat_100g": 5.0, "fiber_100g": 3.0,
        "sodium_100g": 240.0, "sugar_100g": 1.5, "category": "Vegetables"
    },
    "Aloo Sabzi": {
        "density": 0.90, "calories_100g": 110, "protein_100g": 2.2,
        "carbs_100g": 16.0, "fat_100g": 4.5, "fiber_100g": 2.0,
        "sodium_100g": 270.0, "sugar_100g": 0.8, "category": "Vegetables"
    },
    "Aloo Matar": {
        "density": 0.88, "calories_100g": 105, "protein_100g": 3.5,
        "carbs_100g": 15.0, "fat_100g": 4.0, "fiber_100g": 3.0,
        "sodium_100g": 260.0, "sugar_100g": 1.5, "category": "Vegetables"
    },
    "Jeera Aloo": {
        "density": 0.88, "calories_100g": 118, "protein_100g": 2.0,
        "carbs_100g": 16.0, "fat_100g": 5.5, "fiber_100g": 2.0,
        "sodium_100g": 250.0, "sugar_100g": 0.5, "category": "Vegetables"
    },
    "Karela Sabzi": {
        "density": 0.80, "calories_100g": 75, "protein_100g": 1.5,
        "carbs_100g": 7.0, "fat_100g": 4.5, "fiber_100g": 3.5,
        "sodium_100g": 210.0, "sugar_100g": 0.3, "category": "Vegetables"
    },
    "Mixed Veg Curry": {
        "density": 0.88, "calories_100g": 95, "protein_100g": 2.5,
        "carbs_100g": 10.0, "fat_100g": 5.5, "fiber_100g": 3.0,
        "sodium_100g": 280.0, "sugar_100g": 2.0, "category": "Vegetables"
    },
    "Lauki Sabzi": {
        "density": 0.85, "calories_100g": 58, "protein_100g": 1.5,
        "carbs_100g": 7.0, "fat_100g": 2.5, "fiber_100g": 1.5,
        "sodium_100g": 180.0, "sugar_100g": 1.5, "category": "Vegetables"
    },
    "Mushroom Masala": {
        "density": 0.88, "calories_100g": 110, "protein_100g": 4.0,
        "carbs_100g": 7.0, "fat_100g": 7.5, "fiber_100g": 1.5,
        "sodium_100g": 310.0, "sugar_100g": 2.0, "category": "Vegetables"
    },
    "Green Chutney": {
        "density": 0.95, "calories_100g": 40, "protein_100g": 1.0,
        "carbs_100g": 5.0, "fat_100g": 1.5, "fiber_100g": 1.5,
        "sodium_100g": 350.0, "sugar_100g": 1.0, "category": "Vegetables"
    },
    "Tamarind Chutney": {
        "density": 1.10, "calories_100g": 90, "protein_100g": 0.5,
        "carbs_100g": 22.0, "fat_100g": 0.2, "fiber_100g": 1.0,
        "sodium_100g": 550.0, "sugar_100g": 18.0, "category": "Vegetables"
    },
    "Pickle / Achar": {
        "density": 1.00, "calories_100g": 150, "protein_100g": 1.5,
        "carbs_100g": 8.0, "fat_100g": 12.0, "fiber_100g": 2.0,
        "sodium_100g": 1200.0, "sugar_100g": 3.0, "category": "Vegetables"
    },

    # =========================================================================
    # FRUITS (14)
    # =========================================================================

    "Mango": {
        "density": 0.85, "calories_100g": 60, "protein_100g": 0.8,
        "carbs_100g": 15.0, "fat_100g": 0.4, "fiber_100g": 1.6,
        "sodium_100g": 1.0, "sugar_100g": 13.7, "category": "Fruits"
    },
    "Banana": {
        "density": 0.92, "calories_100g": 89, "protein_100g": 1.1,
        "carbs_100g": 23.0, "fat_100g": 0.3, "fiber_100g": 2.6,
        "sodium_100g": 1.0, "sugar_100g": 12.2, "category": "Fruits"
    },
    "Apple": {
        "density": 0.75, "calories_100g": 52, "protein_100g": 0.3,
        "carbs_100g": 14.0, "fat_100g": 0.2, "fiber_100g": 2.4,
        "sodium_100g": 1.0, "sugar_100g": 10.4, "category": "Fruits"
    },
    "Orange": {
        "density": 0.82, "calories_100g": 47, "protein_100g": 0.9,
        "carbs_100g": 12.0, "fat_100g": 0.1, "fiber_100g": 2.4,
        "sodium_100g": 0.0, "sugar_100g": 9.4, "category": "Fruits"
    },
    "Papaya": {
        "density": 0.72, "calories_100g": 43, "protein_100g": 0.5,
        "carbs_100g": 11.0, "fat_100g": 0.3, "fiber_100g": 1.7,
        "sodium_100g": 8.0, "sugar_100g": 7.8, "category": "Fruits"
    },
    "Guava": {
        "density": 0.68, "calories_100g": 68, "protein_100g": 2.6,
        "carbs_100g": 14.0, "fat_100g": 1.0, "fiber_100g": 5.4,
        "sodium_100g": 2.0, "sugar_100g": 8.9, "category": "Fruits"
    },
    "Grapes": {
        "density": 0.88, "calories_100g": 67, "protein_100g": 0.6,
        "carbs_100g": 17.0, "fat_100g": 0.4, "fiber_100g": 0.9,
        "sodium_100g": 2.0, "sugar_100g": 15.5, "category": "Fruits"
    },
    "Watermelon": {
        "density": 0.60, "calories_100g": 30, "protein_100g": 0.6,
        "carbs_100g": 7.6, "fat_100g": 0.2, "fiber_100g": 0.4,
        "sodium_100g": 1.0, "sugar_100g": 6.2, "category": "Fruits"
    },
    "Pineapple": {
        "density": 0.68, "calories_100g": 50, "protein_100g": 0.5,
        "carbs_100g": 13.0, "fat_100g": 0.1, "fiber_100g": 1.4,
        "sodium_100g": 1.0, "sugar_100g": 9.9, "category": "Fruits"
    },
    "Pomegranate": {
        "density": 1.00, "calories_100g": 83, "protein_100g": 1.7,
        "carbs_100g": 19.0, "fat_100g": 1.2, "fiber_100g": 4.0,
        "sodium_100g": 3.0, "sugar_100g": 13.7, "category": "Fruits"
    },
    "Coconut (Fresh)": {
        "density": 0.90, "calories_100g": 354, "protein_100g": 3.3,
        "carbs_100g": 15.2, "fat_100g": 33.5, "fiber_100g": 9.0,
        "sodium_100g": 20.0, "sugar_100g": 6.2, "category": "Fruits"
    },
    "Lychee": {
        "density": 0.85, "calories_100g": 66, "protein_100g": 0.8,
        "carbs_100g": 17.0, "fat_100g": 0.4, "fiber_100g": 1.3,
        "sodium_100g": 1.0, "sugar_100g": 15.2, "category": "Fruits"
    },
    "Chikoo / Sapota": {
        "density": 0.90, "calories_100g": 83, "protein_100g": 0.4,
        "carbs_100g": 20.0, "fat_100g": 1.1, "fiber_100g": 5.3,
        "sodium_100g": 12.0, "sugar_100g": 12.0, "category": "Fruits"
    },
    "Amla / Indian Gooseberry": {
        "density": 0.85, "calories_100g": 44, "protein_100g": 0.9,
        "carbs_100g": 10.2, "fat_100g": 0.6, "fiber_100g": 4.3,
        "sodium_100g": 1.0, "sugar_100g": 0.0, "category": "Fruits"
    },

    # =========================================================================
    # MEAT, FISH & POULTRY (18)
    # =========================================================================

    "Chicken Curry": {
        "density": 1.00, "calories_100g": 150, "protein_100g": 14.0,
        "carbs_100g": 5.0, "fat_100g": 8.5, "fiber_100g": 1.0,
        "sodium_100g": 380.0, "sugar_100g": 1.0, "category": "Meat"
    },
    "Butter Chicken": {
        "density": 1.02, "calories_100g": 195, "protein_100g": 12.0,
        "carbs_100g": 7.0, "fat_100g": 14.0, "fiber_100g": 1.0,
        "sodium_100g": 420.0, "sugar_100g": 3.0, "category": "Meat"
    },
    "Chicken Tikka Masala": {
        "density": 1.02, "calories_100g": 185, "protein_100g": 14.0,
        "carbs_100g": 6.0, "fat_100g": 12.0, "fiber_100g": 1.0,
        "sodium_100g": 450.0, "sugar_100g": 2.5, "category": "Meat"
    },
    "Tandoori Chicken": {
        "density": 1.05, "calories_100g": 170, "protein_100g": 20.0,
        "carbs_100g": 4.0, "fat_100g": 8.0, "fiber_100g": 0.5,
        "sodium_100g": 480.0, "sugar_100g": 1.5, "category": "Meat"
    },
    "Chicken Kebab": {
        "density": 1.05, "calories_100g": 200, "protein_100g": 22.0,
        "carbs_100g": 5.0, "fat_100g": 10.5, "fiber_100g": 0.8,
        "sodium_100g": 500.0, "sugar_100g": 1.0, "category": "Meat"
    },
    "Mutton Curry": {
        "density": 1.02, "calories_100g": 180, "protein_100g": 15.0,
        "carbs_100g": 4.0, "fat_100g": 12.0, "fiber_100g": 0.5,
        "sodium_100g": 350.0, "sugar_100g": 0.8, "category": "Meat"
    },
    "Keema Matar": {
        "density": 1.00, "calories_100g": 165, "protein_100g": 14.5,
        "carbs_100g": 7.0, "fat_100g": 9.5, "fiber_100g": 2.0,
        "sodium_100g": 380.0, "sugar_100g": 1.5, "category": "Meat"
    },
    "Fish Curry": {
        "density": 1.00, "calories_100g": 120, "protein_100g": 15.0,
        "carbs_100g": 4.0, "fat_100g": 5.5, "fiber_100g": 0.5,
        "sodium_100g": 380.0, "sugar_100g": 0.5, "category": "Meat"
    },
    "Fish Fry": {
        "density": 1.05, "calories_100g": 205, "protein_100g": 18.0,
        "carbs_100g": 8.0, "fat_100g": 12.0, "fiber_100g": 0.5,
        "sodium_100g": 420.0, "sugar_100g": 0.5, "category": "Meat"
    },
    "Prawn Curry": {
        "density": 1.00, "calories_100g": 110, "protein_100g": 14.0,
        "carbs_100g": 4.5, "fat_100g": 4.5, "fiber_100g": 0.3,
        "sodium_100g": 400.0, "sugar_100g": 0.8, "category": "Meat"
    },
    "Prawn Masala": {
        "density": 1.02, "calories_100g": 135, "protein_100g": 15.0,
        "carbs_100g": 5.0, "fat_100g": 7.0, "fiber_100g": 0.5,
        "sodium_100g": 450.0, "sugar_100g": 1.0, "category": "Meat"
    },
    "Liver Fry": {
        "density": 1.05, "calories_100g": 175, "protein_100g": 20.0,
        "carbs_100g": 4.0, "fat_100g": 9.0, "fiber_100g": 0.0,
        "sodium_100g": 380.0, "sugar_100g": 0.5, "category": "Meat"
    },
    "Mutton Biryani": {
        "density": 0.92, "calories_100g": 185, "protein_100g": 12.0,
        "carbs_100g": 20.0, "fat_100g": 7.0, "fiber_100g": 1.2,
        "sodium_100g": 340.0, "sugar_100g": 0.6, "category": "Meat"
    },
    "Chicken Fried Rice": {
        "density": 0.88, "calories_100g": 175, "protein_100g": 8.5,
        "carbs_100g": 22.0, "fat_100g": 6.0, "fiber_100g": 1.0,
        "sodium_100g": 520.0, "sugar_100g": 1.0, "category": "Meat"
    },
    "Chicken Pulao": {
        "density": 0.90, "calories_100g": 158, "protein_100g": 10.0,
        "carbs_100g": 20.0, "fat_100g": 4.5, "fiber_100g": 1.0,
        "sodium_100g": 310.0, "sugar_100g": 0.5, "category": "Meat"
    },
    "Boiled Chicken": {
        "density": 1.05, "calories_100g": 135, "protein_100g": 25.0,
        "carbs_100g": 0.0, "fat_100g": 3.5, "fiber_100g": 0.0,
        "sodium_100g": 70.0, "sugar_100g": 0.0, "category": "Meat"
    },
    "Sardine / Mackerel Curry": {
        "density": 1.00, "calories_100g": 130, "protein_100g": 16.0,
        "carbs_100g": 3.0, "fat_100g": 6.5, "fiber_100g": 0.0,
        "sodium_100g": 420.0, "sugar_100g": 0.5, "category": "Meat"
    },
    "Crab Curry": {
        "density": 1.00, "calories_100g": 90, "protein_100g": 13.0,
        "carbs_100g": 4.0, "fat_100g": 2.5, "fiber_100g": 0.0,
        "sodium_100g": 480.0, "sugar_100g": 0.5, "category": "Meat"
    },

    # =========================================================================
    # NUTS & SEEDS (8)
    # =========================================================================

    "Almonds": {
        "density": 0.62, "calories_100g": 579, "protein_100g": 21.2,
        "carbs_100g": 21.6, "fat_100g": 49.9, "fiber_100g": 12.5,
        "sodium_100g": 1.0, "sugar_100g": 4.4, "category": "Nuts"
    },
    "Cashew Nuts": {
        "density": 0.68, "calories_100g": 553, "protein_100g": 18.2,
        "carbs_100g": 30.2, "fat_100g": 43.8, "fiber_100g": 3.3,
        "sodium_100g": 12.0, "sugar_100g": 5.9, "category": "Nuts"
    },
    "Peanuts / Groundnuts": {
        "density": 0.65, "calories_100g": 567, "protein_100g": 25.8,
        "carbs_100g": 16.1, "fat_100g": 49.2, "fiber_100g": 8.5,
        "sodium_100g": 18.0, "sugar_100g": 4.7, "category": "Nuts"
    },
    "Walnuts": {
        "density": 0.55, "calories_100g": 654, "protein_100g": 15.2,
        "carbs_100g": 13.7, "fat_100g": 65.2, "fiber_100g": 6.7,
        "sodium_100g": 2.0, "sugar_100g": 2.6, "category": "Nuts"
    },
    "Sesame Seeds": {
        "density": 0.62, "calories_100g": 573, "protein_100g": 17.7,
        "carbs_100g": 23.4, "fat_100g": 49.7, "fiber_100g": 11.8,
        "sodium_100g": 11.0, "sugar_100g": 0.3, "category": "Nuts"
    },
    "Flaxseeds": {
        "density": 0.65, "calories_100g": 534, "protein_100g": 18.3,
        "carbs_100g": 28.9, "fat_100g": 42.2, "fiber_100g": 27.3,
        "sodium_100g": 30.0, "sugar_100g": 1.6, "category": "Nuts"
    },
    "Sunflower Seeds": {
        "density": 0.62, "calories_100g": 584, "protein_100g": 20.8,
        "carbs_100g": 20.0, "fat_100g": 51.5, "fiber_100g": 8.6,
        "sodium_100g": 9.0, "sugar_100g": 2.6, "category": "Nuts"
    },
    "Mixed Nuts": {
        "density": 0.62, "calories_100g": 590, "protein_100g": 18.0,
        "carbs_100g": 20.0, "fat_100g": 52.0, "fiber_100g": 8.0,
        "sodium_100g": 10.0, "sugar_100g": 4.0, "category": "Nuts"
    },

    # =========================================================================
    # OILS & FATS (4)
    # =========================================================================

    "Ghee": {
        "density": 0.91, "calories_100g": 900, "protein_100g": 0.0,
        "carbs_100g": 0.0, "fat_100g": 99.5, "fiber_100g": 0.0,
        "sodium_100g": 2.0, "sugar_100g": 0.0, "category": "Fats"
    },
    "Cooking Oil": {
        "density": 0.92, "calories_100g": 884, "protein_100g": 0.0,
        "carbs_100g": 0.0, "fat_100g": 100.0, "fiber_100g": 0.0,
        "sodium_100g": 0.0, "sugar_100g": 0.0, "category": "Fats"
    },
    "Butter": {
        "density": 0.91, "calories_100g": 717, "protein_100g": 0.9,
        "carbs_100g": 0.1, "fat_100g": 81.1, "fiber_100g": 0.0,
        "sodium_100g": 576.0, "sugar_100g": 0.1, "category": "Fats"
    },
    "Coconut Oil": {
        "density": 0.92, "calories_100g": 862, "protein_100g": 0.0,
        "carbs_100g": 0.0, "fat_100g": 100.0, "fiber_100g": 0.0,
        "sodium_100g": 0.0, "sugar_100g": 0.0, "category": "Fats"
    },

    # =========================================================================
    # SWEETS & DESSERTS (10)
    # =========================================================================

    "Gulab Jamun": {
        "density": 1.10, "calories_100g": 320, "protein_100g": 3.5,
        "carbs_100g": 50.0, "fat_100g": 12.0, "fiber_100g": 0.0,
        "sodium_100g": 80.0, "sugar_100g": 40.0, "category": "Sweets"
    },
    "Kheer / Rice Pudding": {
        "density": 1.05, "calories_100g": 155, "protein_100g": 4.5,
        "carbs_100g": 24.0, "fat_100g": 5.0, "fiber_100g": 0.2,
        "sodium_100g": 60.0, "sugar_100g": 16.0, "category": "Sweets"
    },
    "Halwa": {
        "density": 1.10, "calories_100g": 340, "protein_100g": 4.0,
        "carbs_100g": 50.0, "fat_100g": 14.0, "fiber_100g": 1.0,
        "sodium_100g": 90.0, "sugar_100g": 35.0, "category": "Sweets"
    },
    "Ladoo": {
        "density": 1.05, "calories_100g": 440, "protein_100g": 7.0,
        "carbs_100g": 58.0, "fat_100g": 20.0, "fiber_100g": 2.0,
        "sodium_100g": 80.0, "sugar_100g": 40.0, "category": "Sweets"
    },
    "Barfi / Burfi": {
        "density": 1.10, "calories_100g": 395, "protein_100g": 9.0,
        "carbs_100g": 52.0, "fat_100g": 18.0, "fiber_100g": 0.5,
        "sodium_100g": 70.0, "sugar_100g": 45.0, "category": "Sweets"
    },
    "Jalebi": {
        "density": 0.80, "calories_100g": 370, "protein_100g": 2.5,
        "carbs_100g": 63.0, "fat_100g": 13.0, "fiber_100g": 0.0,
        "sodium_100g": 60.0, "sugar_100g": 50.0, "category": "Sweets"
    },
    "Rasgulla": {
        "density": 1.05, "calories_100g": 186, "protein_100g": 4.0,
        "carbs_100g": 36.0, "fat_100g": 3.5, "fiber_100g": 0.0,
        "sodium_100g": 40.0, "sugar_100g": 28.0, "category": "Sweets"
    },
    "Shrikhand": {
        "density": 1.05, "calories_100g": 225, "protein_100g": 6.5,
        "carbs_100g": 34.0, "fat_100g": 8.0, "fiber_100g": 0.0,
        "sodium_100g": 50.0, "sugar_100g": 30.0, "category": "Sweets"
    },
    "Payasam": {
        "density": 1.05, "calories_100g": 165, "protein_100g": 4.5,
        "carbs_100g": 26.0, "fat_100g": 5.5, "fiber_100g": 0.5,
        "sodium_100g": 55.0, "sugar_100g": 18.0, "category": "Sweets"
    },
    "Ice Cream": {
        "density": 0.70, "calories_100g": 207, "protein_100g": 3.5,
        "carbs_100g": 24.0, "fat_100g": 11.0, "fiber_100g": 0.0,
        "sodium_100g": 80.0, "sugar_100g": 21.0, "category": "Sweets"
    },

    # =========================================================================
    # SNACKS & STREET FOOD (8)
    # =========================================================================

    "Papad": {
        "density": 0.30, "calories_100g": 330, "protein_100g": 20.0,
        "carbs_100g": 45.0, "fat_100g": 7.0, "fiber_100g": 5.0,
        "sodium_100g": 1600.0, "sugar_100g": 0.5, "category": "Snacks"
    },
    "Samosa": {
        "density": 0.55, "calories_100g": 310, "protein_100g": 5.5,
        "carbs_100g": 35.0, "fat_100g": 17.0, "fiber_100g": 2.5,
        "sodium_100g": 420.0, "sugar_100g": 1.0, "category": "Snacks"
    },
    "Pakora / Bhajiya": {
        "density": 0.50, "calories_100g": 285, "protein_100g": 7.0,
        "carbs_100g": 32.0, "fat_100g": 15.0, "fiber_100g": 3.0,
        "sodium_100g": 380.0, "sugar_100g": 1.5, "category": "Snacks"
    },
    "Vada": {
        "density": 0.60, "calories_100g": 295, "protein_100g": 8.0,
        "carbs_100g": 30.0, "fat_100g": 17.0, "fiber_100g": 2.5,
        "sodium_100g": 400.0, "sugar_100g": 0.5, "category": "Snacks"
    },
    "Murukku": {
        "density": 0.38, "calories_100g": 462, "protein_100g": 8.0,
        "carbs_100g": 58.0, "fat_100g": 23.0, "fiber_100g": 3.0,
        "sodium_100g": 650.0, "sugar_100g": 0.5, "category": "Snacks"
    },
    "Chakli": {
        "density": 0.42, "calories_100g": 475, "protein_100g": 7.5,
        "carbs_100g": 55.0, "fat_100g": 25.0, "fiber_100g": 3.5,
        "sodium_100g": 600.0, "sugar_100g": 0.5, "category": "Snacks"
    },
    "Chivda / Chiwda": {
        "density": 0.30, "calories_100g": 412, "protein_100g": 10.0,
        "carbs_100g": 50.0, "fat_100g": 20.0, "fiber_100g": 4.0,
        "sodium_100g": 820.0, "sugar_100g": 5.0, "category": "Snacks"
    },
    "Mixture / Bombay Mix": {
        "density": 0.35, "calories_100g": 445, "protein_100g": 9.0,
        "carbs_100g": 50.0, "fat_100g": 24.0, "fiber_100g": 5.0,
        "sodium_100g": 750.0, "sugar_100g": 2.0, "category": "Snacks"
    },

    # =========================================================================
    # BEVERAGES (4)
    # =========================================================================

    "Chai / Masala Tea": {
        "density": 1.00, "calories_100g": 42, "protein_100g": 1.5,
        "carbs_100g": 7.0, "fat_100g": 1.2, "fiber_100g": 0.0,
        "sodium_100g": 15.0, "sugar_100g": 6.5, "category": "Beverages"
    },
    "Filter Coffee": {
        "density": 1.00, "calories_100g": 50, "protein_100g": 1.8,
        "carbs_100g": 7.5, "fat_100g": 1.8, "fiber_100g": 0.0,
        "sodium_100g": 10.0, "sugar_100g": 7.0, "category": "Beverages"
    },
    "Mango Lassi": {
        "density": 1.03, "calories_100g": 85, "protein_100g": 2.8,
        "carbs_100g": 15.0, "fat_100g": 2.0, "fiber_100g": 0.5,
        "sodium_100g": 40.0, "sugar_100g": 13.0, "category": "Beverages"
    },
    "Coconut Water": {
        "density": 1.00, "calories_100g": 19, "protein_100g": 0.7,
        "carbs_100g": 3.7, "fat_100g": 0.2, "fiber_100g": 1.1,
        "sodium_100g": 105.0, "sugar_100g": 2.6, "category": "Beverages"
    },
}

# ─── Convenience accessors ─────────────────────────────────────────────────

# Total count
TOTAL_ITEMS = len(IFCT_DATABASE)

# Category index
CATEGORY_INDEX: dict[str, list[str]] = {}
for _name, _data in IFCT_DATABASE.items():
    _cat = _data["category"]
    CATEGORY_INDEX.setdefault(_cat, []).append(_name)

# All food names as a flat list
ALL_FOOD_NAMES: list[str] = list(IFCT_DATABASE.keys())
