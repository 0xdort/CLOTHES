#!/usr/bin/env python3
"""Usage: python3 tools/fits_like.py <item.json> [more.json ...]
Prints, for each size of the given item(s), the closest size in every other known item (by flat chest, then length)."""
import json, sys, glob, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "data")

def load(path):
    d = json.load(open(path))
    out = []
    if d.get("chart_type") == "body":
        return out  # wearer measurements only; not comparable garment-to-garment
    if "sizes" in d:
        out.append((d["id"], d["name"], d.get("category", ""), d["sizes"]))
    for it in d.get("items", []):
        if "sizes" in it:  # brand catalogs: data/brands/*.json
            name = f'{d["brand"]}: {it["name"]}'
            out.append((name, name, it["category"], it["sizes"]))
        else:  # one-of-one listings (e.g. vintage drops)
            out.append((it["handle"], it["handle"], d.get("category", ""), {it["size"]: it}))
    return out

def known():
    items = []
    for p in sorted(glob.glob(f"{ROOT}/items/*.json") + glob.glob(f"{ROOT}/baselines/*.json") + glob.glob(f"{ROOT}/brands/*.json")):
        items += [(p, *x) for x in load(p)]
    return items

# Garment families: "fits like" is most meaningful within the same family.
FAMILY = {
    "tee": "tee", "long-sleeve": "long-sleeve", "rugby": "long-sleeve", "oxford": "shirt", "polo": "shirt", "sweater": "fleece",
    "kids-crewneck": "kids", "hoodie": "fleece", "zip-hoodie": "fleece", "crewneck": "fleece", "half-zip": "fleece",
    "jacket": "jacket",
}
fam = lambda c: FAMILY.get(c, c)

def score(a, b):
    s = abs(a["chest_flat"] - b["chest_flat"]) * 1.0
    if "length" in a and "length" in b:
        s += abs(a["length"] - b["length"]) * 0.35
    return s

def main(paths):
    targets = [x for p in paths for x in load(p)]
    others = known()
    for tid, tname, tcat, tsizes in targets:
        print(f"\n=== {tname}")
        for size, m in tsizes.items():
            print(f"\n  {size}: {m['chest_flat']}\" chest flat, {m.get('length','?')}\" long  FITS LIKE:")
            matches = []
            for _, oid, oname, ocat, osizes in others:
                if oid == tid:
                    continue
                best = min(osizes.items(), key=lambda kv: score(m, kv[1]))
                matches.append((score(m, best[1]), oname, ocat, best[0], best[1]))
            def diverse(xs, n):  # at most 2 picks per brand so one catalog can't crowd out the rest
                seen, out = {}, []
                for x in xs:
                    b = x[1].split(":")[0] if ":" in x[1] else x[1]
                    if seen.get(b, 0) < 2:
                        seen[b] = seen.get(b, 0) + 1; out.append(x)
                    if len(out) == n: break
                return out
            same = diverse([x for x in sorted(matches) if fam(x[2]) == fam(tcat)], 6)
            other = diverse([x for x in sorted(matches) if fam(x[2]) != fam(tcat)], 3)
            for label, group in (("same type", same), ("other types", other)):
              if not group: continue
              print(f"     -- {label}")
              for sc, oname, ocat, osize, om in group:
                dc = m["chest_flat"] - om["chest_flat"]
                dl = (m.get("length", 0) - om.get("length", 0)) if "length" in om and "length" in m else None
                tag = "same" if abs(dc) < 0.5 else (f"{abs(dc):g}\" {'roomier' if dc>0 else 'tighter'}")
                lt = "" if dl is None else f", {abs(dl):g}\" {'longer' if dl>0 else 'shorter'}" if abs(dl) >= 0.5 else ", same length"
                print(f"     {osize:>4} {oname[:60]:60} [{ocat}]  chest {tag}{lt}")

if __name__ == "__main__":
    main(sys.argv[1:] or sys.exit(__doc__))
