# BAYC Merch Fit Reference

Goal: a reference for how every BAYC / Yuga merch drop actually fits, so members can type in a new size chart and see
"FITS LIKE <size> in <past item>".

Approach: compare garment **measurements** (flat chest, length, shoulder, sleeve, in inches), not size labels.

- `data/items/` – one JSON per item, measurements per size (`chest_flat` is the primary comparison key)
- `data/fit-notes.json` – official fit notes and member reports where no chart exists yet
- `sources/charts/` – original size chart images
