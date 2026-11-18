# BAYC Merch Fit Reference

Goal: a reference for how every BAYC / Yuga merch drop actually fits, so members can type in a new size chart and see
"FITS LIKE <size> in <past item>".

Approach: compare garment **measurements** (flat chest, length, shoulder, sleeve, in inches), not size labels.

- `data/items/` – one JSON per item, measurements per size (`chest_flat` is the primary comparison key)
- `data/fit-notes.json` – official fit notes and member reports where no chart exists yet
- `sources/charts/` – original size chart images
- `data/baselines/` – widely available everyday garments (Gildan 5000, Comfort Colors 1717, Bella+Canvas 3001,
  LA Apparel 1801, Champion Reverse Weave, Carhartt Detroit) from official spec sheets, used as reference points
  until we have charts for more BAYC drops

## Try it

    python3 tools/fits_like.py data/items/king-saladeen-rugby.json
- `data/brands/` – 520+ items from Stussy, Aime Leon Dore and Fear of God/Essentials (scraped size guides,
  normalized to flat inches). `data/brands/README.md` compares how big a size M is per brand and garment type.
- `tools/scrape/` – the scrapers and the normalizer (`normalize_brands.py`) that turns raw tables into `data/brands/`
