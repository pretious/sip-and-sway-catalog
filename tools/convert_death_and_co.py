import csv
import json
from collections import defaultdict
from datetime import date


INPUT = "sources/death_and_co_raw.csv"
OUTPUT = "catalog.json"

OZ_TO_ML = 29.5735

def norm(s):
    return s.strip()

cocktails = defaultdict(lambda: {
    "ingredients": []
})

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = norm(row["drink"])

        cid = "deathandco:" + name.lower().replace(" ", "-")

        c = cocktails[cid]
        c["id"] = cid
        c["name"] = name
        c["creatorName"] = "Death & Co"
        c["glass"] = row["glass"].lower() if row["glass"] else None
        c["garnish"] = row["garnish"] or None
        c["instructions"] = row["preparation"].strip()
        c["story"] = None
        c["tags"] = []

        qty = None
        if row["amount"]:
            try:
                qty = float(row["amount"]) * OZ_TO_ML
            except:
                qty = None

        unit = "ml" if qty else None

        c["ingredients"].append({
            "name": row["ingredient"],
            "qty": round(qty, 1) if qty else None,
            "unit": unit
        })

catalog = {
    "version": 1,
    "generatedAt": date.today().isoformat(),
    "cocktails": list(cocktails.values())
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(catalog['cocktails'])} cocktails")
