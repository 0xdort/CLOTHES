#!/usr/bin/env python3
"""Bundle data/ into site/data.js for the static site."""
import json, glob, os, statistics as st, collections, re
ROOT = os.path.join(os.path.dirname(__file__), "..")
FAM = {"tee": "tee", "long-sleeve": "long-sleeve", "rugby": "long-sleeve", "polo": "shirt", "shirt": "shirt",
       "hoodie": "fleece", "zip-hoodie": "fleece", "crewneck": "fleece", "half-zip": "fleece", "sweater": "fleece", "jacket": "jacket"}
BASE_BRAND = [("Gildan", "Gildan"), ("Comfort Colors", "Comfort Colors"), ("Bella", "Bella+Canvas"), ("Los Angeles", "LA Apparel"),
              ("Champion", "Champion"), ("Carhartt", "Carhartt"), ("Nike", "Nike"), ("Polo", "Polo Ralph Lauren"), ("Levi", "Levi's")]
catalog = []
for p in sorted(glob.glob(f"{ROOT}/data/baselines/*.json")):
    d = json.load(open(p)); b = next(v for k, v in BASE_BRAND if d["name"].startswith(k))
    catalog.append(dict(brand=b, name=d["name"], cat=d["category"], sizes=d["sizes"], src="official spec sheet"))
for p in sorted(glob.glob(f"{ROOT}/data/brands/*.json")):
    d = json.load(open(p))
    for it in d["items"]:
        catalog.append(dict(brand=d["brand"].replace("Aime", "Aimé").replace("Stussy", "Stüssy").replace("Fear of God", "Fear of God / Essentials"),
                            name=it["name"], cat=it["category"], sizes=it["sizes"], src="brand size guide"))
bayc = []
for p in sorted(glob.glob(f"{ROOT}/data/items/*.json")):
    d = json.load(open(p))
    if "items" in d:  # anchor drop vintage one-offs -> catalog only
        for it in d["items"]:
            catalog.append(dict(brand="BAYC vintage", name=it["handle"].replace("-", " ").title(), cat="tee", sizes={it["size"]: it}, src="store listing"))
        continue
    if d["category"].startswith("kids"): continue
    bayc.append(dict(id=d["id"], name=d["name"], drop=d.get("drop"), released=d.get("released"), cat=d["category"],
                     chart=d.get("chart_type", "garment"), sizes=d.get("sizes", {}), label_shift=d.get("label_shift"),
                     source=d.get("source", {}).get("type"), post=d.get("source", {}).get("post"), store=d.get("store_url"),
                     tolerance=d.get("source", {}).get("tolerance_in"), traps=d.get("traps", [])))
    if d.get("chart_type", "garment") == "garment" and d.get("sizes"):
        catalog.append(dict(brand="BAYC", name=d["name"], cat=d["category"], sizes=d["sizes"], src="official chart"))
bayc.sort(key=lambda x: x["released"] or "", reverse=True)
# reference stats: brand -> cat -> size -> median chest/length
stats = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
for c in catalog:
    if c["brand"].startswith("BAYC"): continue
    for s, m in c["sizes"].items():
        stats[c["brand"]][c["cat"]][s].append((m["chest_flat"], m.get("length")))
refs = {}
for b, cats in stats.items():
    refs[b] = {}
    for cat, sizes in cats.items():
        refs[b][cat] = {s: dict(chest=round(st.median(v[0] for v in vals), 2),
                                length=round(st.median([v[1] for v in vals if v[1]]), 2) if any(v[1] for v in vals) else None,
                                n=len(vals)) for s, vals in sizes.items()}
# family offsets at size M across all catalogs (how much bigger each family is cut than a tee)
# median per brand first, then across brands, so one big catalog (e.g. oversized FOG) can't skew it
fb = collections.defaultdict(lambda: collections.defaultdict(list))
for c in catalog:
    m = c["sizes"].get("M")
    if m and not c["brand"].startswith("BAYC"): fb[FAM.get(c["cat"], c["cat"])][c["brand"]].append(m["chest_flat"])
offsets = {f: round(st.median(st.median(v) for v in bs.values()), 2) for f, bs in fb.items()}
out = dict(bayc=bayc, catalog=catalog, refs=refs, famMedianM=offsets, family=FAM, built=__import__("datetime").date.today().isoformat())
os.makedirs(f"{ROOT}/site", exist_ok=True)
open(f"{ROOT}/site/data.js", "w").write("window.FITDATA=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False) + ";")
print(len(bayc), "bayc items,", len(catalog), "catalog items,", {b: len(v) for b, v in refs.items()}, offsets)
