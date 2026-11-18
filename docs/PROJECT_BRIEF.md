# BAYC Merch Fit Reference: Project Brief for Review

> **For the reviewer:** this covers the problem, what has been built and learned so far, and the plan for the website.
> We'd like a second opinion on **function** (does the core flow solve the problem?), **design/UX** (is it easy to use?),
> and **aesthetic** (does it feel right for this community?). The questions we most want answered are at the end.

---

## 1. The problem

Bored Ape Yacht Club (BAYC) members buy merch online with **no try-on and no exchanges**. Sizing varies a lot from drop to drop:

- Collabs are made by different factories around the world, and every drop fits differently.
- A member's **Small** BAYC x BMW "Bimmer Club" jacket fit like a normal **L**. It's officially "an oversized mechanics jacket".
- The same member needed an **XL** in the BAYC x McBess denim jacket.
- Size charts are published only *sometimes*. They appear only as images in X/Twitter posts, never as text on the store.
- If you order wrong, the only recourse is reselling on the club's p2p marketplace, which is slow and hard.

**Goal:** a reference site where a member can see what a BAYC item **"FITS LIKE"** in garments they already own or can
try on. For example: *"Saladeen Rugby M ≈ Gildan long sleeve M ≈ Aimé Leon Dore rugby XS. 2 sizes smaller than a Polo rugby."*

## 2. Key insight

**Compare garment measurements, not size labels.** The meaning of "M" varies by about 6 inches across brands. Every item
is stored as flat garment measurements in inches: **chest laid flat (pit to pit)** is the main comparison, and **body
length** is second. Matching runs on those numbers.

## 3. What we found (the data reality)

- **Official BAYC store** (Shopify; the product feed is public): no size charts on the pages. It only has fit words like "boxy" or
  "14oz oversized fleece". The only real measurements are on one-off vintage tees (e.g. *23" chest flat, 32" long*).
- **Official charts exist only as images on X.** A full scrape of public posts found **5 charts**: Saladeen Rugby,
  Regatta Crewneck, Regatta Half Zip, Regatta Kids Crewneck, and Wotherspoon Surf Tee. Older drops (BAPE S1/S2, Bimmer
  jacket, McBess) have no surviving public chart.
- **The charts are inconsistent, even within one drop:**
  - The Regatta Crewneck and Saladeen Rugby use the **same template and the same label** ("Chest 1" down from armhole").
    The Crewneck's numbers are flat (22–29); the Saladeen's are full circumference (38–46).
  - The Surf Tee chart says **"WAIST"**, but its footnote says to measure your **chest**. It's a chart of the wearer's body, not the garment.
  - The Regatta **Half Zip runs about 2 sizes smaller** than the Regatta **Crewneck** from the same drop: Crewneck M = Half Zip XL, both 24".

### Headline comparison: median flat chest of a size M (inches)

| Type | BAYC | Basics (Gildan/Champion/Carhartt) | Stüssy | Aimé Leon Dore | Fear of God |
|---|---|---|---|---|---|
| Tee | – | 20 | 21.5 | 21.5 | 26.2 |
| Rugby | **20** (Saladeen) | 22.5 (Polo RL) | 22.8 | 22.2 | – |
| Crewneck | 24 (Regatta) | 23.4 | 24.8 | 22.8 | 26.5 |
| Half zip | **21.8** (Regatta) | – | 23 | 22.7 | 28.8 |
| Hoodie | – | 23.1 | 23.5 | 22.5 | 26.5 |
| Jacket | – | 23.5 | 25 | 24 | 26.8 |

## 4. What exists today (repo: `0xdort/CLOTHES`, branch `claude/sweet-turing-ni7o36`)

```
data/
  items/       6 BAYC items with official charts (+ Anchor Drop vintage one-offs)
  baselines/   23 everyday garments from official spec sheets (Gildan, Comfort Colors, Bella+Canvas,
               LA Apparel, Champion, Carhartt, Nike Club Fleece, Polo RL rugby, Levi's Trucker)
  brands/      521 items from Stüssy, Aimé Leon Dore, Fear of God/Essentials (scraped size guides)
  fit-notes.json   official fit notes + member reports where no chart exists (Bimmer, McBess)
sources/
  charts/      original chart images + index of the X posts they came from
  brands/      raw scraped tables (pre-normalization)
tools/
  fits_like.py            CLI matcher
  scrape/                 scrapers + normalizer (cm→in, circumference→flat, sanity filters)
```

### Data shape (per item)
```json
{
  "id": "regatta-half-zip", "name": "BAYC Regatta Half Zip", "drop": "Manifest 002: Regatta",
  "category": "half-zip", "units": "in",
  "source": { "type": "official_chart", "file": "sources/charts/regatta-half-zip.jpg", "post": "https://x.com/...", "tolerance_in": 1 },
  "sizes": { "M": { "chest_flat": 21.75, "length": 29.5 }, "L": { "chest_flat": 22.75, "length": 30.5 } }
}
```
Body-only charts are marked `"chart_type": "body"` and are not used in garment-to-garment matching.

### Matching logic (current)
- `score = |Δchest_flat| × 1.0 + |Δlength| × 0.35`. For each other item, take its best-scoring size.
- Results are grouped into **same type** first (garment families: tee / long-sleeve+rugby / fleece = hoodie+crew+half-zip+sweater /
  shirt+polo / jacket), then **other types**. At most 2 results per brand, so one big catalog can't fill the list.
- Each result reads like: `L  Stussy: Basic LS Tee  [long-sleeve]  chest 0.5" roomier, 1" shorter`.
- Sleeves are ignored for now, because brands measure them differently (from the shoulder vs. from center back).

## 5. The plan: the website

### Core flows
1. **"What size do I get?"** (the main flow)
   - The user sets a **reference fit**: something they own that fits well, e.g. *Stüssy hoodie, M*. Or they enter their own flat measurement.
   - Every BAYC item then shows **"Your size: L"**, with a confidence note and the difference ("1" roomier than your Stüssy M").
2. **Item page** (one BAYC drop item)
   - The chart, cleaned up and in one consistent format.
   - A **size ladder**: a horizontal chart of chest widths, with this item's sizes next to familiar garments
     (Gildan, Champion, Stüssy, Essentials) so you can see where each size falls.
   - "FITS LIKE" matches per size.
   - Warnings: "this chart is body sizes", "measured all the way around", "chart says ±1"".
3. **Paste a new chart**
   - When a new drop announces its chart, anyone types the numbers into a grid (sizes × chest/length) and gets instant matches.
   - Later, it could read the numbers from a screenshot automatically.
4. **Contribute** (later)
   - Members submit a flat measurement of an item they own: size, chest, length, an optional photo, and fit feedback ("runs big/small").
   - This is the only way to cover old drops like Bimmer, McBess and BAPE.
5. **Browse**
   - Drops listed by date.
   - A "how big is a Medium" comparison across brands (the table above, made interactive).

### Build approach (proposed)
- A **static site** first: all data is bundled JSON (≈0.5 MB), and matching runs in the browser. Fast, free to host, no accounts.
- The reference fit is saved in the browser so it's remembered on the next visit.
- Contributions need a small shared database later. Submissions are reviewed before they count; they are not trusted automatically.
- Mobile first: most people will check this on a phone, mid-drop, from a link in Discord or X.

### Aesthetic direction (proposed, very open to critique)
- **Nautical / yacht-club clubhouse.** The recent official charts use a tall condensed serif headline ("SIZING CHART"),
  deep navy, cream, and signal-flag pennant accents. The site would echo that mood so it feels native to the community.
- Feel: a **members' tailor card** or a **regatta results board**. Clean tables, big readable numbers, measurements as the hero.
- Light and dark modes. Measurement numbers in a tabular/monospaced figure style so the columns line up.
- **Must be clearly unofficial / fan-made.** No BAYC logos, ape artwork or trademarks used as our branding. Our own name,
  with a "not affiliated with Yuga Labs" note. We link to official posts and the store; we don't imitate them.

## 6. Known limitations / risks
- **Very little BAYC data:** only 5 public charts. The site is only as good as the member contributions it gets.
- **Measurements aren't everything:** fabric weight, stretch, shoulder drop, shrinkage after washing, and personal
  preference all matter. Two garments with the same chest can still fit differently.
- **Scraped brand data was parsed automatically** from 900+ tables, with sanity filters. A few odd values may remain.
- **Blocked sources:** Uniqlo, Levi's, J.Crew, North Face and Carhartt refused automated access. Kith and Rowing Blazers need one more host allowed.
- **Possible confusion:** charts mix measurement methods (flat vs. all the way around, garment vs. body). We normalize, but the UI has to
  explain this simply.

## 7. Questions for the reviewer
1. **Function:** Is a "reference fit" (pick something you own) the right main input, or should it lead with body
   measurements, or with "paste a chart"? What would *you* reach for mid-drop?
2. **Trust:** How should we show confidence and caveats (±1" tolerance, chest-only matching, fabric differences)
   without burying the answer?
3. **Size ladder:** Is a horizontal chest-width chart the clearest way to show "where this size falls"? Better ideas?
4. **Aesthetic:** Does the nautical / clubhouse direction fit, and how do we keep it community-native while staying
   clearly unofficial?
5. **Contributions:** What's the lowest-friction way to get members to measure their old merch (Bimmer, McBess,
   BAPE)? Incentives, flow, photo verification?
6. **Matching:** Should matching also use shoulder width and fit intent ("I like it boxy" vs. "I like it trim")?
   Is `chest + 0.35 × length` a reasonable starting score?
7. **Anything we're missing** that would make an ape trust this enough to order based on it?

---

## 8. Review round 1: decisions and what v1 does

The first reviewer's notes were adopted almost entirely. Status of each:

| Reviewer suggestion | Status in v1 (`site/`) |
|---|---|
| Main flow is 3 taps (brand → item type → size), saved for next visit | ✅ Saved on the device; the home screen then shows your size on every drop |
| "I'll measure a shirt" as a backup, with a diagram | ✅ Pit-to-pit + length inputs with an SVG how-to |
| "Paste a chart" for power users | ✅ Its own page; spots all-the-way-around numbers and halves them |
| One big answer: "Get the L" + High/Medium/Guess + reason in plain words | ✅ Big signal-flag size tag + stitched confidence badge + one-line reason |
| Show where the data came from on every item | ✅ Official chart / member reports only, with links to the original post and the store |
| "In between sizes? M if trim, L if boxy" | ✅ Shown when you fall between two sizes |
| Flag known traps loudly | ✅ "⚑ Heads up" boxes (Half Zip 2 sizes small, body-size chart, measured all the way around) |
| Silhouette overlay instead of bars; ruler second | ✅ Your reference as a dashed outline under the BAYC item; ruler below |
| Shareable result | ✅ v1 copies a text line; image card still to do |
| Clubhouse look: cream paper, navy ink, condensed serif headlines, mono numbers, tape dividers, signal-flag size tags, stitched badges, no anchors or crests | ✅ |
| Dark mode as "night regatta" | ✅ |
| Ape voice in the copy | ✅ "Measure twice, ape once", "Don't get rugged by a size chart" |
| Warn when even the largest size is too small (found while testing) | ✅ "Even the biggest size is trimmer than what you're used to" |
| Quick member input ("I bought M, it fits like my ___, runs small/true/big") | ⏳ Next: needs a small shared database |
| Detailed member input (flat-lay photo, reviewer approval) | ⏳ |
| Credit with ape number/ENS, Tailor badge, leaderboard, wallet signature against spam | ⏳ |
| Member votes nudge the result by up to ½ size (shown when they do) | ⏳ Needs member input first |
| Shoulder width in matching (light weight, only when both have it) | ⏳ Only 1 BAYC chart and few comps have shoulder so far |
| "Don't buy blind" page for each new drop, posted the day its chart drops | ⏳ The paste page is the start of this |
| Swap board tied to the p2p marketplace | ⏳ |
| Shrinkage notes | ⏳ Comes with member input |
| Unblock Rowing Blazers | ⏳ Needs one more allowed host (their size-chart service) |

### How the v1 recommendation works
1. **Your reference:** we take the median measurement of your brand's items in your type and size. For example, "Stüssy hoodie M" means the
   median of 21 Stüssy hoodies in M (23½" pit to pit).
2. **Different garment types:** if the BAYC item is a different family from your reference (e.g. a rugby vs. your hoodie), we use your
   brand's own items in that family. If the brand has none, we adjust using how much bigger or smaller that family is typically cut
   (median across brands, so oversized Fear of God can't skew it).
3. **Picking the size:** the BAYC size with the lowest `|Δchest| + 0.35 × |Δlength|`.
4. **Confidence:**
   - **High:** a direct comparison, built from 2 or more of your brand's items, with the chest within ¾".
   - **Medium:** we had to convert from a different garment type, the reference is a single item, or the chest is more than ¾" off.
   - **Guess:** the chest is more than 1¾" off, the chart is body sizes, or there's no chart and only member reports.

### Screenshots (`docs/screenshots/`)
- `01` phone, first visit · `02` setup (3 taps) · `03` home with your sizes · `04`/`05` Half Zip answer and full page
- `06` desktop Saladeen Rugby with a Fear of God reference: shows the "even the biggest size is trimmer" warning
- `07` "How big is a Medium?" · `08` paste-a-chart result · `09` phone dark mode

### Questions for round 2
1. On the phone answer screen (`04`), is the flag + "Get the L" + reason enough above the fold, or should the first warning move up too?
2. The silhouette uses a simple long-sleeve/tee outline for everything. Is it worth drawing separate hoodie, half-zip and jacket shapes?
3. The confidence rules above: too strict, or too generous?
4. What should the shareable image card look like?
