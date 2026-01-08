import csv
import json
from datetime import datetime, timezone

INPUT = "sources/death_and_co_raw.csv"
OUTPUT = "catalog_deathandco.json"

OZ_TO_ML = 29.5735

def is_cocktail_header(row):
    # this file is weird; cocktail names appear as ALL CAPS in column 3,
    # and quantity column is blank on those rows
    return (
        len(row) >= 6
        and row[2].strip() != ""
        and row[2].strip() == row[2].strip().upper()
        and row[5].strip() == ""
    )

def is_ingredient_row(row):
    # ingredient name in column 3, quantity in column 6
    return (
        len(row) >= 6
        and row[2].strip() != ""
        and row[5].strip() != ""
    )

def make_id(name: str) -> str:
    slug = (
        name.lower()
            .strip()
            .replace("&", "and")
            .replace("/", "-")
            .replace("’", "")
            .replace("'", "")
    )
    while "  " in slug:
        slug = slug.replace("  ", " ")
    slug = slug.replace(" ", "-")
    return f"deathandco:{slug}"

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

        # Cocktail header row
        if is_cocktail_header(row):
            if current:
                catalog["cocktails"].append(current)

            raw_name = row[2].strip()
            # title-case for display, but keep stable id based on title-cased name
            name = raw_name.title()

            current = {
                "id": make_id(name),
                "name": name,
                "creatorName": "Death & Co",
                "glass": None,
                "garnish": None,
                "instructions": "See Death & Co source",
                "story": None,
                "tags": [],
                "ingredients": []
            }
            continue

        # Ingredient row
        if current and is_ingredient_row(row):
            ing_name = row[2].strip()

            qty_ml = None
            try:
                oz = float(row[5].strip())
                qty_ml = round(oz * OZ_TO_ML, 1)
            except:
                qty_ml = None

            current["ingredients"].append({
                "name": ing_name,
                "qty": qty_ml,
                "unit": "ml" if qty_ml is not None else None
            })

# Append last cocktail
if current:
    catalog["cocktails"].append(current)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {len(catalog['cocktails'])} Death & Co cocktails → {OUTPUT}")
