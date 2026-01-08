import csv
import json
from datetime import datetime, timezone

INPUT = "sources/death_and_co_raw.csv"
OUTPUT = "catalog_deathandco.json"

OZ_TO_ML = 29.5735

def is_cocktail_header(row):
    return (
        row[2].isupper()
        and row[2].strip() != ""
        and row[5].strip() == ""
    )

def is_ingredient_row(row):
    return row[2].strip() != "" and row[5].strip() != ""

catalog = {
    "version": 1,
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "cocktails": []
}

current = None

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 6:
            continue

        # Cocktail name row
        if is_cocktail_header(row):
            if current:
                catalog["cocktails"].append(current)

            name = row[2].strip().title()

            current = {
                "id": f"deathandco:{name.lower().replace(' ', '-')}",
                "name": name,
                "creatorName": "Death & Co",
                "glass": None,
                "garnish": None,
                "instructions": "See Death & Co book",
                "story": None,
                "tags": [],
                "ingredients": []
            }
            continue

        # Ingredient rows
        if current and is_ingredient_row(row):
            ingredient = row[2].strip()
            try:
                oz = float(row[5])
                ml = round(oz * OZ_TO_ML, 1)
            except:
                ml = None

            current["ingredients"].append({
                "name": ingredient,
                "qty": ml,
                "unit": "ml" if ml else None
            })

# append last cocktail
if current:
    catalog["cocktails"].append(current)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {len(catalog['cocktails'])} Death & Co cocktails")
