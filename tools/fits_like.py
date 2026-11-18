#!/usr/bin/env python3
"""Usage: python3 tools/fits_like.py <item.json> [more.json ...]
Prints, for each size of the given item(s), the closest size in every other known item (by flat chest, then length)."""
import json, sys, glob, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "data")

def load(path):
    d = json.load(open(path))
    out = []
    if "sizes" in d:
        out.append((d["id"], d["name"], d.get("category", ""), d["sizes"]))
    for it in d.get("items", []):  # one-of-one listings (e.g. vintage drops)
        out.append((it["handle"], it["handle"], d.get("category", ""), {it["size"]: it}))
    return out

def known():
    items = []
    for p in sorted(glob.glob(f"{ROOT}/items/*.json") + glob.glob(f"{ROOT}/baselines/*.json")):
        items += [(p, *x) for x in load(p)]
    return items

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
            for sc, oname, ocat, osize, om in sorted(matches)[:6]:
                dc = m["chest_flat"] - om["chest_flat"]
                dl = (m.get("length", 0) - om.get("length", 0)) if "length" in om and "length" in m else None
                tag = "same" if abs(dc) < 0.5 else (f"{abs(dc):g}\" {'roomier' if dc>0 else 'tighter'}")
                lt = "" if dl is None else f", {abs(dl):g}\" {'longer' if dl>0 else 'shorter'}" if abs(dl) >= 0.5 else ", same length"
                print(f"     {osize:>4} {oname[:48]:48} [{ocat}]  chest {tag}{lt}")

if __name__ == "__main__":
    main(sys.argv[1:] or sys.exit(__doc__))
