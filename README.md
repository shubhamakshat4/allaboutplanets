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
cd backend && python -m pytest tests/ -q     # 376 tests
cd frontend && npm run typecheck
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
  planet_analyzer.py        Assembles Sections A–V for one planet.
  dignity_engine.py         Exaltation, debilitation, own sign, Mooltrikona, Vargottama
  relationship_engine.py    THE Panchadha Maitri engine — the only one in the codebase
  avastha_engine.py         Kumaradi and Chaitanyadi
  aspect_engine.py          Graha Drishti given and received
  conjunction_engine.py     Same-Rashi occupancy
  shadbala_engine.py        Six-fold strength, numbers only
  yoga_engine.py            The curated 22-yoga V1 set with per-condition evidence
  neecha_bhanga_engine.py   Six cancellation conditions, evaluated independently
  dispositor_engine.py      Dispositor chains with cycle detection
  rules/
    registry.py                          53 rules: ID, name, description, source, I/O
    planetary_rules.py                   Naming tables and structural constants
    maitri_rules.py                      MAITRI_001/002/003
    avastha_rules.py                     KUMARADI_001, CHAITANYADI_001
    functional_classification_rules.py   FUNC_001–FUNC_007
    neecha_bhanga_rules.py               NB_001–NB_006, NB_100
    yoga_rules.py                        YOGA_001–YOGA_022
```

Browse every registered rule at `GET /api/rules`, or in the UI's evidence panels.

---

## Rules

**[docs/RULES.md](docs/RULES.md) is the rule list, written for an astrologer to
read and verify.** Sixteen sections in plain language, with every table the
software actually uses — sign lords, dignities, the full friendship matrix,
aspects, combustion orbs, avastha bands, nakshatra lords, all 22 yogas — plus a
section recording every point where the classics disagree and which reading was
taken.

**[docs/RULES.pdf](docs/RULES.pdf)** is the same document typeset for reading
and printing — 24 A4 pages, each section starting on its own page with room in
the margins for notes, page numbers, and clickable bookmarks for all 19
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

Sections A–V, each collapsible, each with evidence panels:

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

376 tests over the deterministic engines:

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
- **API** — determinism, historical DST, error handling, and an audit asserting no
  interpretive phrase ("is strong", "will bring", "auspicious", …) appears anywhere in any
  chart or planet response
