# FEATURE → PyJHora FUNCTION → OUR CUSTOM LOGIC → SOURCE/RULE

Inspected package: **PyJHora 4.8.7** (`jhora`), Swiss Ephemeris via **pyswisseph 2.10.3.2**.
Verified empirically by executing each function before integration (see `backend/tests/`).

Every entry below was confirmed against the *installed* source. No function in this
project calls a PyJHora API that is not listed here.

---

## Legend

| Column | Meaning |
|---|---|
| **PyJHora function** | The real, verified API used |
| **Our logic** | What our own deterministic engine adds on top |
| **Rule ID** | Identifier in `backend/app/astrology/rules/` when we own the rule |

---

## 1. Time, place & configuration

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Julian Day from date+time | `utils.julian_day_number(Date, (h,m,s))` | We convert local civil time → offset via IANA tz (`zoneinfo`) so historical DST is correct, then hand a float-hour tuple to PyJHora | `TIME_001` |
| Place struct | `drik.Place(name, lat, lon, tz_offset_hours)` | Geocoding is ours (PyJHora's bundled `geonames_places_5k.db` is **not shipped** with the wheel — verified `FileNotFoundError`) | `GEO_001` |
| Ayanamsha selection | `drik.set_ayanamsa_mode(mode)`; 21 modes in `const.available_ayanamsa_modes` | We pin the mode explicitly per request and store it on the chart. PyJHora's package default is `TRUE_PUSHYA`; **we never rely on it** — our default is `LAHIRI`, always echoed to the user | `CONFIG_001` |
| Ayanamsha value | `drik.get_ayanamsa_value(jd)` | passthrough | PyJHora |

## 2. Positions

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Rasi (D1) chart | `charts.rasi_chart(jd, place)` → `[['L',(sign,deg)],[0,(sign,deg)],…]` index 0=Lagna, 1..9 = Sun..Ketu | Reshape into typed records | PyJHora |
| Divisional charts | `charts.divisional_chart(jd, place, divisional_chart_factor=D)` | We request D1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60 with PyJHora's *standard* chart methods | PyJHora |
| Ascendant | `drik.ascendant(jd, place)` | passthrough (already inside `rasi_chart`) | PyJHora |
| Nakshatra + Pada | `drik.nakshatra_pada(longitude)` → `[nak 1-27, pada 1-4, remainder]` | Map index → name; nakshatra lord from Vimshottari order | `NAK_001` |
| Bhava (whole sign) | — | **Ours.** `((planet_sign − lagna_sign) mod 12) + 1`. This is the house frame used by *all* classical Parashari rules in this app | `HOUSE_001` |
| Bhava (Bhava Chalita) | `charts.bhava_houses(jd, place)` and `charts.bhava_chart(jd, place)` | Displayed **alongside** whole-sign, never mixed into rule evaluation | PyJHora (`const.bhaava_madhya_method=1`, KN Rao / Parashari cusp−15,cusp,cusp+15) |

> **Methodology note (surfaced in the UI):** whole-sign bhava drives every rule
> (lordship, kendra/trikona, yogas, Neecha Bhanga). Bhava Chalita is shown as an
> independent fact. The two are never silently interchanged.

## 3. Planetary state

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Retrograde | `drik.planets_in_retrograde(jd, place)` — true speed sign from Swiss Ephemeris (`longi[3] < 0`) | We use **this** one, not `charts.planets_in_retrograde()`. PyJHora's own docstring says the `charts` variant is a longitude-band approximation for dhasa/yoga code and directs you here "for accurate results" | PyJHora |
| Speed / motion detail | `drik.planets_speed_info(jd, place)` → `{p: (lon, lat, speed_long, …)}` | Report daily motion in °/day and direct/retrograde | PyJHora |
| Stationary | `drik.planets_in_stationary(jd, place)` | passthrough | PyJHora |
| Combustion | `charts.planets_in_combustion(planet_positions)` | passthrough. Thresholds exposed to the UI from `const.combustion_range_of_planets_from_sun` and `…_while_in_retrogade` | PyJHora |
| Planetary war | `drik.planets_in_graha_yudh(jd, place)` → `[(p1,p2,category)]` | Category names 0=Bhed, 1=Ullekh, 2=Apsavya, 3=Anshumard. Eligible bodies are Mars, Mercury, Jupiter, Venus, Saturn only → everything else reports **"Not applicable"** | PyJHora |

## 4. Aspects (Drishti)

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Graha Drishti | `house.graha_drishti_from_chart(h_to_p)` → `(arp, ahp, app)` = aspected rasis / houses / planets | We invert `app` to build *received* aspects, and derive the aspect ordinal as `((target_sign − source_sign) mod 12) + 1` | PyJHora + `ASPECT_001` |
| Special aspects | `const.graha_drishti` = `{Mars:[4,7,8], Jupiter:[5,7,9], Saturn:[3,7,10], all others:[7]}` | Read from the library, never hard-coded by us | PyJHora |

> Rahu/Ketu are given the 7th drishti only by this rule set. Surfaced as a
> methodology note rather than silently assumed.

## 5. Relationships

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Natural (permanent) Maitri | `const.planet_relations` (9×9, incl. Rahu/Ketu; 3=Friend, 2=Neutral, 1=Enemy, 5=self) | Read table, map to names | `MAITRI_001` |
| Temporary Maitri | `const.temporary_friend_raasi_positions` = offsets `[1,2,3,9,10,11]`; enemies `[0,4,5,6,7,8]` | Our engine computes it per pair (2,3,4,10,11,12 from the planet = friend; 1,5,6,7,8,9 = enemy) | `MAITRI_002` |
| Panchadha Maitri | `house._get_compound_relationships_of_planets(h_to_p)` exists and uses the identical combination table | **Ours** (`MAITRI_003`) so every pair carries its own evidence; cross-checked against PyJHora's function in `test_relationship_engine.py` | `MAITRI_003` |
| Sign lords | `const._house_owners_list` = `[Mars,Venus,Mercury,Moon,Sun,Mercury,Venus,Mars,Jupiter,Saturn,Saturn,Jupiter]` | Read table | PyJHora |

## 6. Dignity

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Exalted / Debilitated / Own / Friend / Neutral / Enemy sign | `const.house_strengths_of_planets` (9×12; 5=Owner, 4=Exalted, 3=Friend, 2=Neutral, 1=Enemy, 0=Debilitated) | Decode per planet+sign | `DIGNITY_001` |
| Deep exaltation degrees | `const.planet_deep_exaltation_longitudes` (Sun..Saturn) | Report exact degree of deep exaltation/debilitation | PyJHora |
| Mooltrikona | `const.moola_trikona_range_of_planets` — **Sun..Saturn only** | Range check on degree-in-sign. Rahu/Ketu → *"Not defined in selected rule set"* | `DIGNITY_002` |
| Vargottama | — | **Ours.** D1 sign == D9 sign | `VARGA_001` |

> Rahu/Ketu exaltation rows exist in `const.house_strengths_of_planets` (Rahu exalted
> Taurus/Gemini, debilitated Scorpio/Sagittarius; Ketu the reverse). This is one
> tradition among several, so it is labelled with its source in the UI, and Rahu/Ketu
> own no sign in the lordship table used for houses.

## 7. Shadbala

| Feature | PyJHora function | Our logic | Rule ID / Source |
|---|---|---|---|
| Full Shadbala | `strength.shad_bala(jd, place)` → `[sthana, kaala, dig, cheshta, naisargika, drik, total_virupa, total_rupa, ratio_vs_required]`, each a 7-list (Sun..Saturn) | Reshape only | PyJHora |
| Sthana components | `strength._uchcha_bala`, `_sapthavargaja_bala1`, `_ojayugama_bala`, `_kendra_bala`, `_dreshkon_bala` | Called individually for the breakdown the spec requires | PyJHora (private API, pinned to 4.8.7) |
| Kala components | `_nathonnath_bala`, `_paksha_bala`, `_tribhaga_bala`, `_abdadhipathi`, `_masadhipathi`, `_vaaradhipathi`, `_hora_bala`, `_ayana_bala`, `_yuddha_bala` | Called individually | PyJHora (private API) |
| Drik Bala contributions | `strength.planet_aspect_relationship_table(planet_positions)` (9×9 virupa matrix) | Show which planet contributed what to Drik Bala | PyJHora |
| Required Shadbala | `const.shad_bala_factors` = `[5,6,5,7,6.5,5.5,5]` rupas | Displayed as the required minimum. **No verdict text.** | PyJHora |

> Shadbala is defined for Sun..Saturn only. Rahu/Ketu → *"Not available"*.

## 8. Yogas

PyJHora ships `horoscope/chart/yoga.py` (90+ yogas) and `raja_yoga.py`. The spec asks for a
**curated 22-yoga V1 set with per-condition evidence**, which those modules do not expose
(they return booleans/name lists). Therefore the yoga engine is **ours**, built strictly on
PyJHora-derived primitives (positions, lordships, drishti from `house.graha_drishti_from_chart`,
dignity from `const.house_strengths_of_planets`).

Rule IDs `YOGA_001` … `YOGA_022` in `rules/yoga_rules.py`, each carrying source,
inputs, conditions and evidence.

## 9. Ours entirely (no PyJHora equivalent)

| Feature | Rule ID |
|---|---|
| Kumaradi Avastha | `KUMARADI_001` |
| Chaitanyadi Avastha | `CHAITANYADI_001` |
| Functional classification (Kendra/Trikona/Dusthana/Upachaya/Maraka/Badhaka/Yogakaraka) | `FUNC_001`…`FUNC_007` |
| Dispositor chain + cycle detection | `DISPOSITOR_001` |
| Neecha Bhanga conditions 1–6 | `NB_001`…`NB_006` |
| Benefic/malefic classification | `BENEFIC_001` |
| Conjunction detection | `CONJ_001` |

## 10. Deliberately NOT used

| PyJHora API | Why |
|---|---|
| `charts.planets_in_retrograde(pp)` | Approximation; library directs to `drik` version |
| `horoscope.chart.yoga` / `raja_yoga` | Returns verdicts without per-condition evidence; spec requires a curated, auditable 22-yoga set |
| `horoscope.prediction.*` | Generates predictions — forbidden by the product philosophy |
| `horoscope.dhasa.*` | Out of V1 scope |
| `place_db.get_place` / `search_places_*` | Backing SQLite DB is absent from the distributed wheel (verified) |
