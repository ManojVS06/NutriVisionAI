"""One-shot SQLite migration: adds quality_score, detection_method, confidence columns."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutrivision.db")
print("DB path:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# --- meals table ---
cursor.execute("PRAGMA table_info(meals)")
meals_cols = [row[1] for row in cursor.fetchall()]
print("Existing meals columns:", meals_cols)

if "quality_score" not in meals_cols:
    cursor.execute("ALTER TABLE meals ADD COLUMN quality_score REAL DEFAULT 100.0")
    print("  + Added meals.quality_score")
if "detection_method" not in meals_cols:
    cursor.execute("ALTER TABLE meals ADD COLUMN detection_method TEXT DEFAULT 'gemini_vision'")
    print("  + Added meals.detection_method")

# --- food_items table ---
cursor.execute("PRAGMA table_info(food_items)")
fi_cols = [row[1] for row in cursor.fetchall()]
print("Existing food_items columns:", fi_cols)

if "confidence" not in fi_cols:
    cursor.execute("ALTER TABLE food_items ADD COLUMN confidence REAL DEFAULT 1.0")
    print("  + Added food_items.confidence")
if "detection_method" not in fi_cols:
    cursor.execute("ALTER TABLE food_items ADD COLUMN detection_method TEXT DEFAULT 'gemini_vision'")
    print("  + Added food_items.detection_method")

conn.commit()
conn.close()
print("\nMigration complete.")
