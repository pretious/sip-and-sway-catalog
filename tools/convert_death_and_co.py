import csv
import json
from pathlib import Path

SRC = Path("sources/death_and_co_raw.csv")
OUT = Path("catalog_deathandco.json")

def norm(s: str) -> str:
    return s.strip().title()

def parse_qty(qty: str):
    q = qty.strip()
    q_lower = q.lower()
    if q_lower in ("", "remainder", "as needed", "to top"):
        return None
    try:
        return float(q)
    except ValueError:
        return None

cocktails = []
current = None
instructions_buf = []
garnish = None

with SRC.open(newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        if len(row) < 6:
            continue

        cocktail_name = row[2].strip()
        ingredient = row[3].strip()
        qty = row[5].strip()
        text = row[6].strip() if len(row) > 6 else ""

        # Skip section headers & empty rows
        # (section headers have ALL CAPS cocktail_name and empty ingredient)
        if cocktail_name == "" or (cocktail_name.isupper() and ingredient == ""):
            continue

        # New cocktail detected (compare to raw cocktail_name stored in current["name"])
        if current is None or cocktail_name != current["name"]:
            if current:
                current["instructions"] = " ".join(instructions_buf).strip()
                if garnish:
                    current["garnish"] = garnish
                cocktails.append(current)

            current = {
                "id": cocktail_name.lower().replace(" ", "-"),
                "name": cocktail_name,                 # keep raw for boundary detection
                "displayName": norm(cocktail_name),    # nice title-cased name for UI
                "glass": None,
                "garnish": None,
                "instructions": "",
                "story": None,
                "tags": ["death-and-co"],
                "ingredients": []
            }

            instructions_buf = []
            garnish = None

        # Ingredient row
        if ingredient:
            qv = parse_qty(qty)

            # If qty is non-numeric (e.g. "8 sprigs"), preserve it in the name
            display_ingredient = norm(ingredient) if qv is not None else norm(f"{ingredient} ({qty})")

            current["ingredients"].append({
                "name": display_ingredient,
                "qty": qv,
                "unit": "oz" if qv is not None else None
            })

        # Instruction / garnish text
        if "GARNISH:" in text.upper():
            garnish = text.replace("GARNISH:", "", 1).strip()
        elif text:
            instructions_buf.append(text)

# flush last cocktail
if current:
    current["instructions"] = " ".join(instructions_buf).strip()
    if garnish:
        current["garnish"] = garnish
    cocktails.append(current)

# Convert to your CatalogDTO-ish shape:
# - rename displayName -> name
# - drop internal "name" used for parsing boundaries
final_cocktails = []
for c in cocktails:
    final_cocktails.append({
        "id": c["id"],
        "name": c["displayName"],
        "creatorName": "Death & Co",
        "glass": c["glass"],
        "garnish": c["garnish"],
        "instructions": c["instructions"],
        "story": c["story"],
        "tags": c["tags"],
        "ingredients": c["ingredients"]
    })

output = {
    "version": 1,
    "generatedAt": None,
    "cocktails": final_cocktails
}

OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"✅ Converted {len(final_cocktails)} Death & Co cocktails → {OUT.name}")
