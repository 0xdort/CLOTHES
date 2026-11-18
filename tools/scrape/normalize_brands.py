#!/usr/bin/env python3
"""Normalize raw scraped brand size tables (sources/brands/*_raw.json) into data/brands/<brand>.json.
Rules:
  - sizes normalized (XXL->2XL, XXXL->3XL); kids and womens items skipped (BAYC sizing is unisex/men's)
  - cm tables converted to inches
  - chest > 36in for an adult top is a full circumference -> halved to flat
  - rows with implausible values (flat chest <16 or 30-36 ambiguous, length outside 20-37) dropped
"""
import json, re, os
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SZ = {"XXL": "2XL", "XXXL": "3XL"}
CATS = [("half-zip", r"half[- ]?zip|quarter[- ]?zip|1/4 zip|1/2 zip"), ("zip-hoodie", r"zip[- ]?up hood|zip hood|full[- ]?zip hood"),
        ("hoodie", r"hood"), ("crewneck", r"crewneck|crew neck|sweatshirt|crew sweat"), ("rugby", r"rugby"),
        ("polo", r"polo"), ("long-sleeve", r"long ?sleeve|l/s|longsleeve"), ("tee", r"\btee\b|t-shirt|tshirt"),
        ("sweater", r"sweater|cardigan|knit"), ("shirt", r"oxford|shirt\b|overshirt|button"),
        ("jacket", r"jacket|coat|bomber|trucker|parka|anorak|windbreaker|varsity|blouson|chore|vest")]
def cat(title, typ):
    s = f"{title} {typ}".lower()
    for c, rx in CATS:
        if re.search(rx, s): return c
    return None
def norm(brand, rows, title_key, type_key=None, url=None):
    items = {}
    for r in rows:
        title = r[title_key]; typ = r.get(type_key, "") if type_key else ""
        if re.search(r"(?i)\bkids?\b|youth|toddler|baby|women|womens|wmns", f"{title} {typ}"): continue
        c = cat(title, typ)
        if not c: continue
        cm = r.get("unit") == "cm" or r.get("cm")
        sizes = {}
        for s, (ch, ln) in r["sizes"].items():
            s = SZ.get(s.upper(), s.upper())
            if cm: ch, ln = ch / 2.54, (ln / 2.54 if ln else None)
            if ch > 36: ch = ch / 2
            if ch < 16 or 30 < ch <= 36 or (ln and not 20 <= ln <= 37): continue
            sizes[s] = {"chest_flat": round(ch, 2), **({"length": round(ln, 2)} if ln else {})}
        if "M" not in sizes and "L" not in sizes: continue
        key = re.sub(r"\s+", " ", title.strip())
        items.setdefault(key, {"name": key, "category": c, "fit_note": r.get("fit"),
                               "url": (url + r["handle"]) if url and r.get("handle") else None, "sizes": sizes})
    out = {"brand": brand, "units": "in", "measurement_basis": {"chest_flat": "laid flat (circumference charts halved)", "length": "body length as published"},
           "items": list(items.values())}
    json.dump(out, open(f"{ROOT}/data/brands/{brand.lower().replace(' ', '-')}.json", "w"), indent=1)
    return len(out["items"])
R = lambda f: json.load(open(f"{ROOT}/sources/brands/{f}"))
print("Aime Leon Dore", norm("Aime Leon Dore", R("aimeleondore_raw.json"), "title", "type", "https://www.aimeleondore.com/products/"))
print("Stussy", norm("Stussy", R("stussy_raw.json"), "title", "type", "https://www.stussy.com/products/"))
print("Fear of God", norm("Fear of God", R("fearofgod_raw.json"), "name"))
