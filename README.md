# Planetary Status Analyzer

A calculation and research tool for Vedic astrology. Enter birth details, generate the
chart with PyJHora, then select any of the nine grahas to see a complete, structured,
factual breakdown of that planet's calculated status.

**It calculates, organises and displays. It does not interpret or predict.**

No output anywhere in this application says a planet is good, bad, strong or weak, or
what any configuration will cause. Every classification is a rule-based fact carrying a
rule ID and a source, and every derived value has a "How calculated?" panel showing the
inputs and the rule that produced it. The astrologer does the interpreting.

---

## Running it

Two processes. Backend first.

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Health check: <http://127.0.0.1:8000/health> · API docs: <http://127.0.0.1:8000/docs>

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` to the backend on port 8000.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -q

cd ../frontend && npm run typecheck
```

`requirements.txt` holds only what the running application needs.
`requirements-dev.txt` adds the test suite and the tools that regenerate the
rule documents.

---

## Deploying

The application serves its own built frontend, so a single container hosts
everything on one origin. A `Dockerfile` and a Render blueprint are included.

### Render

1. Push to GitHub.
2. Render → **New** → **Blueprint** → pick the repository. `render.yaml` sets
   the runtime, the health check and auto-deploy.

   Or **New → Web Service** → Runtime **Docker**, health check path `/health`.
3. After the first deploy, open `/health`. It reports the PyJHora version and
   `frontend_bundled`. If that is `false`, the UI did not reach the image.

Nothing needs configuring: there are no API keys, and no environment variables
beyond the `PORT` Render provides.

### Notes on the image

* PyJHora declares PyQt6 for its desktop UI module, which this application
  never imports. It is installed with `--no-deps` and its real runtime needs
  are listed explicitly, keeping roughly 100 MB of Qt out of the image.
* The build fails rather than the deploy if `frontend/dist/index.html` is
  missing after the frontend stage.
* Generated charts are held in memory. On a free instance that sleeps, the
  cache is lost on wake, but the frontend re-sends the birth details and
  rebuilds the identical chart, so a sleeping instance is invisible apart from
  the cold start.

### Running the container locally

```bash
docker build -t planetary-status-analyzer .
docker run --rm -p 8000:8000 planetary-status-analyzer
```

---

## Architecture

```
React + Vite + TypeScript + Tailwind
        ↓  REST
FastAPI  (app/api/routes.py)
        ↓
Chart Calculation Service   (astrology/chart_calculator.py)
        ↓
PyJHora Adapter             (astrology/pyjhora_adapter.py)   ← the only module importing jhora
        ↓
Planetary Fact Engines      (dignity, relationship, avastha, aspect, conjunction,
                             shadbala, yoga, neecha_bhanga, dispositor)
        ↓
Planet Analysis API         (astrology/planet_analyzer.py)
        ↓
React UI
```

No astrology logic lives in the frontend. It renders structured objects and nothing more.

### Layout

```
backend/app/astrology/
  pyjhora_adapter.py        Sole boundary to PyJHora. Nothing else imports jhora.
  chart_calculator.py       Builds the ChartContext every engine consumes.
  planet_analyzer.py        Assembles the full reference view for one planet.
  dignity_engine.py         Exaltation, debilitation, own sign, Mooltrikona, Vargottama
  relationship_engine.py    THE Panchadha Maitri engine — the only one in the codebase
  avastha_engine.py         Kumaradi and Chaitanyadi
  aspect_engine.py          Graha Drishti given and received
  conjunction_engine.py     Same-Rashi occupancy
  shadbala_engine.py        Six-fold strength, numbers only
  yoga_engine.py            The curated 22-yoga V1 set with per-condition evidence
  neecha_bhanga_engine.py   Six cancellation conditions, evaluated independently
  dispositor_engine.py      Dispositor chains with cycle detection
  combustion_engine.py      Classical orbs, shorter-arc separation
  dosha_engine.py           The curated 14-dosha set
  planet_findings.py        Sorts every fact into the six groups the UI shows
  rules/
    registry.py                          93 rules: ID, name, description, source, I/O
    planetary_rules.py                   Naming tables and structural constants
    classification_rules.py              NATURE_001–NATURE_010
    maitri_rules.py                      MAITRI_001/002/003
    avastha_rules.py                     KUMARADI_001, CHAITANYADI_001
    functional_classification_rules.py   FUNC_001–FUNC_007
    neecha_bhanga_rules.py               NB_001–NB_006, NB_100
    yoga_rules.py                        YOGA_001–YOGA_022
    dosha_rules.py                       DOSHA_001–DOSHA_014
```

Browse every registered rule at `GET /api/rules`, or in the UI's evidence panels.

---

## Rules

**[docs/RULES.md](docs/RULES.md) is the rule list, written for an astrologer to
read and verify.** Eighteen sections in plain language, with every table the
software actually uses — sign lords, dignities, the full friendship matrix,
aspects, combustion orbs, avastha bands, nakshatra lords, the 22 yogas and the
14 doshas — plus a section recording every point where the classics disagree and
which reading was taken.

**[docs/RULES.pdf](docs/RULES.pdf)** is the same document typeset for reading
and printing — 29 A4 pages, each section starting on its own page with room in
the margins for notes, page numbers, and clickable bookmarks for all 21
sections.

Both are generated from the live rule tables, and a test fails if the Markdown
drifts from the code, so they always describe what actually runs:

```bash
cd backend
python -m tools.generate_rules_doc    # rules → docs/RULES.md
python -m tools.generate_rules_pdf    # docs/RULES.md → docs/RULES.pdf (+ .html)
```

The PDF step renders through headless Chrome or Edge, then stamps page numbers
and bookmarks with PyMuPDF. If no browser is found it stops and tells you to
print the generated HTML yourself.

Each rule carries a tag such as `[DIGNITY_002]`. The same tags appear in the
application's evidence panels and at `GET /api/rules`, so any value on screen
can be traced back to the rule that produced it.

### Getting the rules reviewed

**[docs/review-form.gs](docs/review-form.gs)** builds a Google Form that walks
an astrologer through every rule one at a time. Each becomes a required
multiple-choice question with the rule stated in full, followed by an optional
box for what should change instead. Responses collect in a linked Sheet, so
several reviewers can be compared side by side.

```bash
cd backend
python -m tools.generate_review_form    # rules -> docs/review-form.gs
```

Paste the result into a new project at <https://script.google.com>, run
`buildReviewForm`, and the execution log prints the edit link, the share link
and the responses sheet. A test fails if the form drifts from the rules, so it
always asks about every rule that exists.

## Methodology, stated plainly

`docs/PYJHORA_MAPPING.md` maps every feature to the exact PyJHora function behind it.
The library was inspected and executed before any integration code was written; no
invented APIs are called. The decisions worth knowing up front:

| Decision | What we do and why |
|---|---|
| **Ayanamsha** | Set explicitly on every calculation. PyJHora 4.8.7 defaults to `TRUE_PUSHYA`; we never rely on that. Default is `LAHIRI`, and the mode in force is stored with the chart and shown on screen. |
| **Houses** | All classical rules use **whole-sign bhava** counted from the Lagna sign. PyJHora's Bhava Chalita is displayed alongside as an independent fact and is never substituted into rule evaluation. |
| **Timezone** | The UTC offset is evaluated *at the birth instant* via the IANA zone, so historical daylight-saving is correct (a July 1980 London birth resolves to UTC+1, not UTC+0). If no timezone or offset is given, the request is rejected — nothing is assumed. |
| **Retrograde** | From `drik.planets_in_retrograde`, which uses true Swiss Ephemeris speed. PyJHora's own docstring names this the accurate source over the positional approximation in `charts`. |
| **Combustion** | PyJHora's verdict is authoritative and is never overridden. The distance and the threshold are shown next to it so the calculation is visible. |
| **Exaltation** | Derived from `const.planet_deep_exaltation_longitudes`, not the dignity table. The table stores one code per cell, so it records Mercury in Virgo as *Own Sign* only — which would silently hide Mercury's exaltation. Both facts are now reported. |
| **Rahu / Ketu** | Handled explicitly per feature, never by blindly applying seven-planet rules. They own no sign, so Swarashi, Mooltrikona and house lordship report **"Not defined in selected rule set"**. Shadbala reports **"Not available"**. Graha Yuddha and combustion report **"Not applicable"**. Their natural relationships *are* defined by the selected rule set and are used, with the source labelled. |
| **Yogas** | PyJHora ships 90+ yogas but returns names without per-condition evidence, so the curated 22-yoga V1 set is evaluated by our own engine on PyJHora-derived primitives. Every yoga reports each condition separately with its evidence. |
| **Neecha Bhanga** | Six conditions, each evaluated and reported independently — never merged into one boolean. Retrograde motion is deliberately *not* a cancellation condition in V1. Debilitation, Neecha Bhanga and Neecha Bhanga Raja Yoga are kept as three distinct states. |
| **Geocoding** | PyJHora's bundled place database is not shipped with the wheel (verified: `FileNotFoundError`), so place lookup uses the Open-Meteo geocoding API. Latitude, longitude and timezone are always manually overridable, and a lookup failure is reported as a failure. |

Where a rule is ambiguous across traditions, the choice is isolated in a rule file,
labelled in the UI, and documented — never silently picked.

---

## What you get per planet

Every graha runs the same fixed catalogue of checks, and the findings are sorted
into six groups: **strengths**, **yogas formed**, **challenges**, **doshas
formed**, **your call** for points the classics leave open, and **neutral or not
applicable**. Each bullet has an Explain panel. A check that cannot apply to a
body still appears and says so.

Behind a single toggle sits the full reference view, each section collapsible
and evidenced:

**Position & dignity** — longitude, Rashi, Rashi lord, Bhava, Nakshatra, Pada, Nakshatra
lord, Navamsha, Navamsha lord · exaltation, debilitation, Swarashi, Mooltrikona,
friend/neutral/enemy sign as independent facts

**Lordship** — houses owned, each classified Kendra/Trikona/Dusthana/Upachaya/Maraka/
Badhaka, plus Yoga Karaka and the full functional classification component-by-component

**Relationships** — Panchadha Maitri with the Rashi lord, Nakshatra lord, Navamsha lord,
Lagnesh, every conjunct planet, every aspecting planet, every aspected planet, every yoga
participant, and a complete profile against all eight other planets. One engine produces
all of them.

**State** — retrograde, combustion, Graha Yuddha, Kumaradi and Chaitanyadi Avastha with
the degree band shown

**Interactions** — conjunctions with degree separation · Drishti received · Drishti given
to both houses and planets

**Strength** — Shadbala with all five Sthana components, all nine Kala components, Dig,
Cheshta, Naisargika and Drik Bala, contributing aspects, totals in Virupas and Rupas, and
the required minimum. Numbers only, no verdict.

**Structural** — D1 through D60 · dispositor chain with cycle detection · Neecha Bhanga

**Yogas** — which of the 22 this planet takes part in, its role, the other participants,
and per-condition evidence · plus all 22 checks for the whole chart

Search and filter work across sections ("show only Shatru", "only planets aspecting
Jupiter", "only yogas that are present"). Export produces a print-optimised PDF with every
section and evidence panel forced open; raw structured data downloads as JSON.

---

## Test coverage

683 tests over the deterministic engines:

- **Avastha boundaries** — 5°59'59" / 6°00' / 11°59'59" / 12°00' / 17°59'59" / 18°00' /
  23°59'59" / 24°00', and 9°59'59" / 10°00' / 19°59'59" / 20°00', in both odd and even signs
- **Panchadha Maitri** — the full combination table, every offset 0–11, and a
  cross-check proving our independent implementation agrees with PyJHora's own compound
  matrix on all 72 ordered pairs across four separate charts
- **Dignity** — exaltation, debilitation, own signs, Mooltrikona ranges and their
  inclusive/exclusive boundaries
- **Functional classification** — every category, Badhaka by modality for all 12 Lagnas,
  Yoga Karaka including the classical results derived rather than hard-coded
- **Interactions** — conjunction symmetry, aspect given/received consistency, special
  aspect sets per planet, dispositor termination across seven charts
- **Yogas** — all 22 evaluated, present/absent consistency with their own conditions,
  participation matching the full yoga list, verified across six charts
- **Doshas** — all 14 evaluated against five charts, each checked against the
  positions it claims to read
- **Classification** — the classical Yoga Karakas derived rather than hard-coded,
  Kendradhipatya both ways, Moon and Mercury conditional nature at their boundaries
- **Documents** — `docs/RULES.md`, `RULES.pdf` and `RULES.html` are all checked
  against the live rules, so a stale document fails the build
- **API** — determinism, historical DST, error handling, and an audit asserting no
  outcome or verdict phrase ("will bring", "is strong", "overall score", …) reaches
  any chart or planet response
