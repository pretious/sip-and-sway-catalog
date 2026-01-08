import csv
import json
import re
from pathlib import Path

SRC = Path("sources/death_and_co_raw.csv")
OUT = Path("catalog_deathandco.json")

def norm(s):
    return s.strip().title()

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
        if cocktail_name == "" or cocktail_name.isupper() and ingredient == "":
            continue

        # New cocktail detected
        if current is None or cocktail_name != current["name"]:
            if current:
                current["instructions"] = " ".join(instructions_buf).strip()
                if garnish:
                    current["garnish"] = garnish
                cocktails.append(current)

            current = {
                "id": cocktail_name.lower().replace(" ", "-"),
                "name": norm(cocktail_name),
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
            current["ingredients"].append({
                "name": norm(ingredient),
                "qty": float(qty) if qty not in ("", "remainder") else None,
                "unit": "oz" if qty not in ("", "remainder") else None
            })

        # Instruction / garnish text
        if "GARNISH:" in text.upper():
            garnish = text.replace("GARNISH:", "").strip()
        elif text:
            instructions_buf.append(text)

# flush last cocktail
if current:
    current["instructions"] = " ".join(instructions_buf).strip()
    if garnish:
        current["garnish"] = garnish
    cocktails.append(current)

output = {
    "version": 1,
    "generatedAt": None,
    "cocktails": cocktails
}

OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")

print(f"✅ Converted {len(cocktails)} Death & Co cocktails → {OUT.name}")
