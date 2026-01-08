import csv
import json
from collections import defaultdict
from datetime import datetime, timezone

INPUT = "sources/death_and_co_raw.csv"
OUTPUT = "catalog.json"

OZ_TO_ML = 29.5735

def norm(s):
    return (s or "").strip()

def header_lookup(fieldnames):
    # map lowercase header -> actual header
    return {h.strip().lower(): h for h in fieldnames if h}

def pick_header(hmap, candidates):
    for c in candidates:
        key = c.strip().lower()
        if key in hmap:
            return hmap[key]
    return None

def get(row, h):
    if not h:
        return None
    return row.get(h)

def to_float(s):
    s = norm(s)
    if not s:
        return None
    try:
        return float(s)
    except:
        return None

def make_id(name: str) -> str:
    slug = (
        name.lower()
            .strip()
            .replace("&", "and")
            .replace("/", "-")
            .replace("’", "")
            .replace("'", "")
    )
    # keep it simple
    while "  " in slug:
        slug = slug.replace("  ", " ")
    slug = slug.replace(" ", "-")
    return f"deathandco:{slug}"

cocktails_by_id = defaultdict(lambda: {"ingredients": []})

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames:
        raise RuntimeError("CSV has no headers (fieldnames is empty).")

    hmap = header_lookup(reader.fieldnames)

    # Try common header variants
    H_DRINK = pick_header(hmap, ["drink", "cocktail", "cocktail_name", "name"])
    H_ING   = pick_header(hmap, ["ingredient", "ingredient_name"])
    H_AMT   = pick_header(hmap, ["amount", "qty", "quantity"])
    H_UNIT  = pick_header(hmap, ["unit", "units"])
    H_GLASS = pick_header(hmap, ["glass", "glassware"])
    H_GARN  = pick_header(hmap, ["garnish"])
    H_PREP  = pick_header(hmap, ["preparation", "instructions", "method", "direction", "directions"])

    if not H_DRINK or not H_ING:
        raise RuntimeError(
            "Could not find required headers. "
            f"Found headers: {reader.fieldnames}\n"
            f"Detected drink header: {H_DRINK}, ingredient header: {H_ING}"
        )

    for row in reader:
        drink_name = norm(get(row, H_DRINK))
        if not drink_name:
            continue

        cid = make_id(drink_name)
        c = cocktails_by_id[cid]

        # set once (but safe to overwrite with same values)
        c["id"] = cid
        c["name"] = drink_name
        c["creatorName"] = "Death & Co"

        glass = norm(get(row, H_GLASS))
        c["glass"] = glass.lower() if glass else None

        garnish = norm(get(row, H_GARN))
        c["garnish"] = garnish if garnish else None

        prep = norm(get(row, H_PREP))
        c["instructions"] = prep if prep else "—"

        c["story"] = None
        c["tags"] = []

        ing_name = norm(get(row, H_ING))
        if not ing_name:
            continue

        amt = to_float(get(row, H_AMT)) if H_AMT else None
        unit = norm(get(row, H_UNIT)) if H_UNIT else ""

        # If unit is ounces (or missing), convert to ml if we have a number
        qty_out = None
        unit_out = None

        if amt is not None:
            u = unit.lower()
            if u in ["oz", "ounce", "ounces", "fl oz", "floz", "fl. oz"] or u == "":
                qty_out = round(amt * OZ_TO_ML, 1)
                unit_out = "ml"
            else:
                qty_out = round(amt, 2)
                unit_out = unit

        c["ingredients"].append({
            "name": ing_name,
            "qty": qty_out,
            "unit": unit_out
        })

catalog = {
    "version": 1,
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "cocktails": list(cocktails_by_id.values())
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(catalog['cocktails'])} cocktails to {OUTPUT}")
