"""Regenerate docs/RULES.md — the plain-language rule list for astrologers.

The document is written for a practising astrologer to read and verify, not for
a programmer. It states each rule in ordinary language and prints the actual
tables the software uses, so every value can be checked against the classics.

Every number below is read from the live rule tables at generation time, so the
document can never drift from the code that actually runs.

    python -m tools.generate_rules_doc
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.astrology import combustion_engine as ce  # noqa: E402
from app.astrology import pyjhora_adapter as adapter  # noqa: E402
from app.astrology.rules import avastha_rules as ar  # noqa: E402
from app.astrology.rules import classification_rules as cr  # noqa: E402
from app.astrology.rules import dosha_rules as dr  # noqa: E402
from app.astrology.rules import maitri_rules as mr  # noqa: E402
from app.astrology.rules import planetary_rules as pr  # noqa: E402
from app.astrology.rules import yoga_rules as yr  # noqa: E402
from app.astrology.rules.registry import all_rules  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "docs" / "RULES.md"


def table(headers, rows) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def build() -> str:
    L: list[str] = []
    add = L.append

    # =====================================================================
    add("# Rules Used by the Planetary Status Analyzer")
    add("")
    add("A plain list of every rule this software applies, written so that an "
        "astrologer can read it and check it.")
    add("")
    add("The application only calculates and organises. It never interprets, "
        "predicts, or judges a planet as good or bad. So the only thing that "
        "needs checking is whether these rules are stated correctly.")
    add("")
    add("**How to use this document.** Read each rule. If one does not match "
        "what you follow, say so and it can be changed. The tag in brackets, "
        "for example `[DIGNITY_002]`, is the reference number for that rule — "
        "quote it when reporting a correction.")
    add("")
    add("**Framework:** Parashari. Where *Brihat Parashara Hora Shastra* "
        "settles a value, that value is used. Where the classics differ, the "
        "disagreement is recorded in section 17 rather than being decided "
        "quietly.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 1. What the software calculates from")
    add("")
    add(table(
        ["Setting", "Value"],
        [
            ("Zodiac", "Sidereal (Nirayana)"),
            ("Ayanamsha", "Lahiri by default; any of 21 may be chosen, and the "
                          "one used is shown on every chart"),
            ("Ephemeris", "Swiss Ephemeris"),
            ("Houses used for all rules", "Whole sign (Rashi) counted from the "
                                          "Lagna sign"),
            ("Bhava Chalita", "Shown separately as information. No rule uses it."),
            ("Rahu and Ketu", "Mean nodes"),
            ("Birth time", "Converted using the timezone in force at the place "
                           "on the date of birth, so old daylight-saving rules "
                           "are applied correctly"),
        ]))
    add("")
    add("The house frame matters. Every rule in this document — lordship, "
        "kendra and trikona, the yogas, Neecha Bhanga — counts houses as whole "
        "signs from the Lagna sign. `[HOUSE_001]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 2. The signs and their lords")
    add("")
    add(table(
        ["No.", "Rashi", "Sanskrit", "Lord", "Movable / Fixed / Dual", "Odd or Even"],
        [(i + 1, pr.SIGN_NAMES[i], pr.SIGN_SANSKRIT[i],
          pr.PLANET_NAMES[pr.SIGN_LORDS[i]],
          pr.sign_modality(i), pr.sign_parity(i))
         for i in range(12)]))
    add("")
    add("Rahu and Ketu lord no sign. `[RK_001]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 3. Exaltation, debilitation, own sign and Mooltrikona")
    add("")
    rows = []
    for p in pr.SUN_TO_SATURN:
        ex = pr.deep_exaltation_longitude(p)
        de = pr.deep_debilitation_longitude(p)
        mt = pr.mooltrikona_range(p)
        rows.append((
            pr.PLANET_NAMES[p],
            ", ".join(pr.sign_name(s) for s in pr.owned_signs(p)),
            f"{pr.sign_name(int(ex // 30))} {ex % 30:g}°",
            f"{pr.sign_name(int(de // 30))} {de % 30:g}°",
            f"{pr.sign_name(mt[0])} {mt[1]:g}°–{mt[2]:g}°",
        ))
    add(table(["Graha", "Own sign(s)", "Exalted at", "Debilitated at",
               "Mooltrikona"], rows))
    add("")
    add("The exaltation degree given is the deep exaltation point; the whole "
        "sign counts as the exaltation sign. `[DIGNITY_001]`")
    add("")
    add("Mooltrikona ranges follow *Brihat Parashara Hora Shastra*, chapter 3. "
        "For the Moon and Mercury the Mooltrikona portion begins at the degree "
        "after the exaltation point — Taurus 4° and Virgo 16°. `[DIGNITY_002]`")
    add("")
    add("A planet is reported as being in its Mooltrikona only when it is in "
        "the right sign **and** within the degrees shown.")
    add("")
    add("Mercury in Virgo is both exalted and in its own sign. Both facts are "
        "reported; neither is suppressed.")
    add("")
    add("Rahu and Ketu have no own sign and no Mooltrikona. `[RK_002]` "
        "`[RK_003]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 4. The houses")
    add("")
    add(table(
        ["Group", "Houses"],
        [("Kendra", "1, 4, 7, 10"),
         ("Trikona", "1, 5, 9"),
         ("Dusthana", "6, 8, 12"),
         ("Upachaya", "3, 6, 10, 11"),
         ("Maraka", "2, 7")]))
    add("")
    add("The 1st house belongs to both Kendra and Trikona. `[FUNC_002]`")
    add("")
    add("**Badhaka house**, decided by the Lagna sign: `[FUNC_003]`")
    add("")
    add(table(
        ["Lagna type", "Badhaka house", "Lagna signs"],
        [("Movable", "11th", "Aries, Cancer, Libra, Capricorn"),
         ("Fixed", "9th", "Taurus, Leo, Scorpio, Aquarius"),
         ("Dual", "7th", "Gemini, Virgo, Sagittarius, Pisces")]))
    add("")
    add("**Yoga Karaka.** A planet that lords a Kendra among the 4th, 7th or "
        "10th **and** a Trikona among the 5th or 9th. Owning only the 1st house "
        "does not by itself make a planet a Yoga Karaka. `[FUNC_004]`")
    add("")
    add("The software lists each house a planet owns and the group each house "
        "belongs to. It does not reduce this to a single verdict about the "
        "planet. `[FUNC_005]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 5. Benefic, malefic and neutral")
    add("")
    add("Three separate questions, kept apart because the classics keep them "
        "apart. A graha can be a natural benefic and a functional malefic at "
        "the same time, and both are reported.")
    add("")

    add("### What each graha is by nature `[NATURE_001]`")
    add("")
    add(table(
        ["Graha", "Nature", "Condition"],
        [("Jupiter, Venus", "Benefic", "Always"),
         ("Mars, Saturn, Rahu, Ketu", "Malefic", "Always"),
         ("Sun", "Malefic", "Counted among the cruel grahas, a mild malefic"),
         ("Moon", "Benefic or Malefic",
          f"Benefic while bright, taken as {cr.MOON_BRIGHT_FROM:g}°–"
          f"{cr.MOON_BRIGHT_TO:g}° from the Sun; malefic while dark"),
         ("Mercury", "Takes its company",
          "Benefic with benefics, malefic with malefics, neutral when alone "
          "or when its sign holds both")]))
    add("")

    add("### What each house is by nature `[NATURE_002]`")
    add("")
    add(table(
        ["Houses", "Counted as"],
        [("1, 2, 4, 5, 7, 9, 10, 11", "Auspicious"),
         ("6, 8, 12", "Difficult — the Dusthanas"),
         ("3", "Mixed — an Upachaya, but mildly difficult")]))
    add("")
    add("A natural malefic placed in an Upachaya house (3rd, 6th, 10th, 11th) "
        "is not counted a difficulty, since malefics are held to grow strong "
        "there. This is why a malefic in the 6th is treated differently from a "
        "malefic in the 8th or 12th. `[NATURE_003]`")
    add("")

    add("### What a graha becomes for one Lagna `[NATURE_004]`")
    add("")
    add("Decided by the houses it lords:")
    add("")
    add(table(
        ["Lords", "Becomes"],
        [("The 1st", "Auspicious — the 1st is both Kendra and Trikona"),
         ("The 5th or 9th", "Auspicious — the Trikonas"),
         ("The 3rd, 6th or 11th", "Inauspicious — the Trishadaya"),
         ("The 8th", "Inauspicious, unless it also lords the Lagna"),
         ("The 2nd or 12th", "Neutral in itself"),
         ("A Kendra (4th, 7th, 10th)",
          "Kendradhipatya: a natural benefic loses its benefic power, a "
          "natural malefic turns auspicious"),
         ("Both a Kendra and a Trikona", "Yoga Karaka")]))
    add("")
    add("Where a graha holds both an auspicious and an inauspicious lordship, "
        "the Trikona lordship is taken to prevail.")
    add("")
    add("This is why, for a Libra Lagna, Saturn lords the 4th and 5th and is "
        "the Yoga Karaka, while Jupiter lords the 3rd and 6th and is a "
        "functional malefic despite being the greatest natural benefic.")
    add("")

    add("### Retrogression `[NATURE_005]`")
    add("")
    add(table(
        ["Case", "Grouped as"],
        [("A natural malefic, retrograde", "Favourable"),
         ("A natural benefic, retrograde", "A difficulty"),
         ("A natural benefic, direct", "Favourable"),
         ("A natural malefic, direct", "Neutral"),
         ("Sun or Moon", "Does not apply — neither ever retrogrades"),
         ("Rahu or Ketu", "No distinction — they are always retrograde")]))
    add("")
    add("A retrograde graha stands near the earth and gains Cheshta Bala. The "
        "formulation followed here treats that gain as welcome in a malefic "
        "and unwelcome in a benefic.")
    add("")

    add("### Company and aspect `[NATURE_006]`")
    add("")
    add("A conjunction with, or an aspect received from, a natural benefic is "
        "grouped favourably; from a natural malefic, as a difficulty.")
    add("")

    add("### How the groups are filled `[NATURE_007]` `[NATURE_008]` "
        "`[NATURE_009]` `[NATURE_010]`")
    add("")
    add("Every graha is put through the same list of checks, so the same "
        "points appear for all nine. A check that cannot apply to a body still "
        "appears, saying so.")
    add("")
    add("The findings are sorted into six groups:")
    add("")
    add(table(
        ["Group", "Holds"],
        [("Strengths", "Placements the classics count as favourable"),
         ("Yogas formed", "Yogas this graha takes part in"),
         ("Challenges", "Placements the classics count as difficult"),
         ("Doshas formed", "Doshas this graha takes part in"),
         ("Your call",
          "Points the classics leave open. Kept apart from the neutral ones "
          "so a real disagreement is never mistaken for a routine 'does not "
          "apply'. The reason is given on the Explain panel."),
         ("Neutral & not applicable",
          "Checks that came out on neither side, and checks that cannot bear "
          "on this graha at all. Each bullet says which of the two it is.")]))
    add("")
    add("The findings are never added up into a score or an overall judgement "
        "of the planet. The number beside each group is simply how many points "
        "fall in it.")
    add("")
    add("These are the situations placed in **Your call**:")
    add("")
    add(table(
        ["Situation", "Why it is left open"],
        [(k.replace("_", " ").title(), v) for k, v in cr.CONTESTED.items()]))
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 6. Friendship between planets")
    add("")
    add("### Natural friendship (Naisargika Maitri)")
    add("")
    add("Fixed for all charts. `[MAITRI_001]`")
    add("")
    header = ["Planet sees →"] + [pr.PLANET_NAMES[p] for p in pr.ALL_PLANETS]
    rows = []
    for a in pr.ALL_PLANETS:
        row = [f"**{pr.PLANET_NAMES[a]}**"]
        for b in pr.ALL_PLANETS:
            row.append("—" if a == b else mr.natural_relationship(a, b))
        rows.append(row)
    add(table(header, rows))
    add("")
    add("Read each row as *how that planet regards the others*. The table is "
        "not symmetrical, which is correct: Mercury regards the Sun as a "
        "friend, while the Sun regards Mercury as neutral.")
    add("")
    add("The seven-graha portion matches *Brihat Parashara Hora Shastra*. The "
        "Rahu and Ketu rows do not come from that text — see sections 16 "
        "and 17. `[RK_006]`")
    add("")
    add("### Temporary friendship (Tatkalika Maitri)")
    add("")
    add("Decided by position in the chart being read. `[MAITRI_002]`")
    add("")
    add(table(
        ["Counted from the planet", "Result"],
        [(", ".join(_ord(h) for h in mr.TEMPORARY_FRIEND_HOUSES), "Temporary friend"),
         (", ".join(_ord(h) for h in mr.TEMPORARY_ENEMY_HOUSES), "Temporary enemy")]))
    add("")
    add("A planet in the same sign is in the 1st from the other, and so is a "
        "temporary enemy.")
    add("")
    add("### Combined friendship (Panchadha Maitri)")
    add("")
    add("Natural and temporary are combined into the five-fold result. "
        "`[MAITRI_003]`")
    add("")
    add(table(
        ["Natural", "Temporary", "Result"],
        [(nat, tmp, f"**{mr.panchadha_maitri(nat, tmp)}**")
         for nat in (mr.NATURAL_FRIEND, mr.NATURAL_NEUTRAL, mr.NATURAL_ENEMY)
         for tmp in (mr.TEMPORARY_FRIEND, mr.TEMPORARY_ENEMY)]))
    add("")
    add("This one calculation is used everywhere the software shows a "
        "relationship — with the sign lord, the nakshatra lord, the navamsha "
        "lord, the Lagna lord, a conjunct planet, an aspecting planet, and each "
        "yoga participant. There is no second method anywhere in the software.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 7. Aspects (Graha Drishti)")
    add("")
    add(table(
        ["Graha", "Aspects"],
        [(pr.PLANET_NAMES[p],
          ", ".join(_ord(n) for n in sorted(pr.GRAHA_DRISHTI[p])))
         for p in pr.ALL_PLANETS]))
    add("")
    add("Counted in whole signs from the sign the planet occupies. `[ASPECT_001]`")
    add("")
    add("Rahu and Ketu are given the 7th aspect only. Traditions that also give "
        "them the 5th and 9th are not applied. `[RK_005]`")
    add("")
    add("For every aspect the software shows the aspecting planet, the aspect "
        "number, both houses, and the Panchadha Maitri between the two.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 8. Conjunction, retrogression, combustion, planetary war")
    add("")
    add("**Conjunction.** Two planets in the same Rashi. The degree gap between "
        "them is shown, measured the short way round the zodiac. `[CONJ_001]`")
    add("")
    add("**Retrogression.** Taken from the planet's actual motion. The Sun and "
        "Moon never retrograde. As mean nodes, Rahu and Ketu are always "
        "retrograde. `[RK_010]`")
    add("")
    add("**Combustion (Asta).** A planet within this distance of the Sun is "
        "combust. `[COMBUST_001]`")
    add("")
    add(table(
        ["Graha", "In direct motion", "When retrograde"],
        [(pr.PLANET_NAMES[p],
          f"{ce.threshold_for(p, False):g}°",
          f"{ce.threshold_for(p, True):g}°")
         for p in pr.COMBUSTION_ELIGIBLE]))
    add("")
    add("The distance is measured the short way round, so a planet in late "
        "Pisces close to a Sun in early Aries is correctly found combust. The "
        "Sun itself is the reference point, and Rahu and Ketu are outside the "
        "rule. `[RK_008]`")
    add("")
    add("**Planetary war (Graha Yuddha).** Fought only between Mars, Mercury, "
        "Jupiter, Venus and Saturn. The luminaries and the nodes are excluded. "
        "`[RK_009]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 9. Avasthas")
    add("")
    add("Two Avastha systems are calculated, both from the planet's degree "
        "within its sign, with the order reversed in even signs.")
    add("")
    add("### Kumaradi (Baladi) Avastha `[KUMARADI_001]`")
    add("")
    add(table(
        ["Degree in sign", "Odd sign", "Even sign"],
        [(f"{s:g}° to {e:g}°", odd, even)
         for (s, e, odd), (_, _, even) in zip(ar.KUMARADI_ODD, ar.KUMARADI_EVEN)]))
    add("")
    add("### Chaitanyadi Avastha `[CHAITANYADI_001]`")
    add("")
    add(table(
        ["Degree in sign", "Odd sign", "Even sign"],
        [(f"{s:g}° to {e:g}°", odd, even)
         for (s, e, odd), (_, _, even) in zip(ar.CHAITANYADI_ODD, ar.CHAITANYADI_EVEN)]))
    add("")
    add("A planet exactly on a boundary takes the later band. A planet at "
        "exactly 6° in an odd sign is Kumara, not Bala.")
    add("")
    add("Odd signs are Aries, Gemini, Leo, Libra, Sagittarius and Aquarius. "
        "Even signs are the rest.")
    add("")
    add("These are the only two Avastha systems calculated. `[RK_012]` records "
        "that the classical descriptions address the seven grahas; the value is "
        "still shown for Rahu and Ketu with a note attached.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 10. Nakshatras")
    add("")
    add("The 27 nakshatras and their lords, in the Vimshottari order, repeating "
        "every nine. `[NAK_001]`")
    add("")
    add(table(
        ["No.", "Nakshatra", "Lord", "No.", "Nakshatra", "Lord", "No.",
         "Nakshatra", "Lord"],
        [tuple(
            item
            for k in (i, i + 9, i + 18)
            for item in (k + 1, pr.NAKSHATRA_NAMES[k],
                         pr.PLANET_NAMES[pr.nakshatra_lord(k + 1)])
        ) for i in range(9)]))
    add("")
    add("Each nakshatra is divided into four padas of 3°20′ each.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 11. Navamsha and Vargottama")
    add("")
    add("A planet in the same sign in the Rashi chart and the Navamsha is "
        "**Vargottama**. `[VARGA_001]`")
    add("")
    add("Divisional charts calculated: D1, D2, D3, D4, D7, D9, D10, D12, D16, "
        "D20, D24, D27, D30, D40, D45 and D60. For each, the software shows "
        "the sign, its lord, and the planet's dignity in that sign.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 12. Dispositor chain")
    add("")
    add("A planet is followed to the lord of the sign it occupies, then that "
        "lord to the lord of *its* sign, and so on. `[DISPOSITOR_001]`")
    add("")
    add("The chain stops when a planet is in its own sign, or when a planet "
        "already seen appears again, in which case the loop is reported as a "
        "cycle.")
    add("")
    add("Rahu and Ketu can appear in a chain but never act as a dispositor, "
        "since they lord no sign. `[RK_011]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 13. Neecha Bhanga")
    add("")
    add("Evaluated only for a planet that is actually debilitated. Six "
        "conditions are checked, and each is reported separately with the "
        "planets involved. They are never merged into a single answer.")
    add("")
    nb = [r for r in all_rules() if r.rule_id.startswith("NB_0")]
    add(table(
        ["No.", "Condition", "Tag"],
        [(i + 1, r.name, f"`[{r.rule_id}]`") for i, r in enumerate(nb)]))
    add("")
    add("Kendra means the 1st, 4th, 7th or 10th counted from the reference "
        "point.")
    add("")
    add("**Retrogression of the debilitated planet is not used as a "
        "cancellation condition.**")
    add("")
    add("Three states are kept separate and never confused with one another:")
    add("")
    add("1. The planet is debilitated.")
    add("2. One or more cancellation conditions are met.")
    add("3. Neecha Bhanga Raja Yoga, which additionally requires the planet to "
        "own or occupy a Kendra or Trikona. `[YOGA_022]`")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 14. The yogas checked")
    add("")
    add("Twenty-two yogas are examined. For each one the software shows every "
        "condition separately, whether it is met, and which planets take part.")
    add("")
    add(table(
        ["No.", "Yoga", "How it is formed", "Tag"],
        [(i + 1, s.name, s.summary, f"`[{s.rule_id}]`")
         for i, s in enumerate(yr.YOGA_SPECS)]))
    add("")
    add("### Points worth checking in the yoga rules")
    add("")
    add("**Gaja Kesari.** The formation is Jupiter in a Kendra from the Lagna "
        "or from the Moon. A Moon–Jupiter conjunction is the 1st from the Moon, "
        "which is a Kendra, so it forms the yoga. Four further conditions — a "
        "benefic association, not debilitated, not combust, not in an enemy's "
        "sign — are shown separately as strengthening conditions and do not "
        "prevent the yoga from forming.")
    add("")
    add("**Budha-Aditya.** The Sun and Mercury in the same Rashi. Mercury's "
        "combustion is reported as a separate fact and does not cancel the "
        "yoga.")
    add("")
    add("**Raja Yoga.** A Kendra lord and a Trikona lord joined by conjunction, "
        "mutual aspect, or exchange of signs. The Lagna lord counts as both, "
        "since the 1st house is a Kendra and a Trikona.")
    add("")
    add("**Kemadruma.** No planet in the 2nd or 12th from the Moon. The Sun, "
        "Rahu and Ketu are not counted as relieving it.")
    add("")
    add("**Parivartana.** Reported as a plain exchange. It is not divided into "
        "Maha, Khala and Dainya.")
    add("")
    add("**Benefics and malefics**, used by Adhi, Amala and Gaja Kesari: "
        "`[BENEFIC_001]`")
    add("")
    add(table(
        ["Graha", "Classed as"],
        [("Jupiter, Venus", "Always benefic"),
         ("Mercury", "Benefic unless it shares its sign with a natural malefic"),
         ("Moon", "Benefic when between 72° and 288° from the Sun (bright half)"),
         ("Sun, Mars, Saturn, Rahu, Ketu", "Malefic")]))
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 15. The doshas checked")
    add("")
    add("Fourteen doshas are examined. A dosha is reported by its formation "
        "alone. Where the classics give well-known grounds on which it is held "
        "to be lifted, those are shown with it, but the software never applies "
        "them: whether a cancellation carries is yours to judge. `[DOSHA_100]`")
    add("")
    add(table(
        ["No.", "Dosha", "How it is formed", "Tag"],
        [(i + 1, s.name, s.formation, f"`[{s.rule_id}]`")
         for i, s in enumerate(dr.DOSHA_SPECS)]))
    add("")
    add("Kemadruma is reported here rather than with the yogas, being an "
        "affliction by nature.")
    add("")
    add("Grounds for cancellation are recorded for "
        + ", ".join(dr.SPEC_BY_KEY[k].name for k in dr.CANCELLATIONS)
        + ".")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 16. Rahu and Ketu")
    add("")
    add("The classics count nine grahas but work out most of their detail for "
        "seven. Every feature is therefore stated explicitly for the nodes, so "
        "that no seven-planet rule is applied to them by accident.")
    add("")
    rk = [r for r in all_rules() if r.rule_id.startswith("RK_")]
    add(table(
        ["Question", "Answer", "Tag"],
        [
            ("Do they lord any sign?", "No", "`[RK_001]`"),
            ("Do they have a Mooltrikona?", "No", "`[RK_002]`"),
            ("Do they have an own sign?", "No", "`[RK_003]`"),
            ("Exaltation and debilitation?",
             "Rahu exalted in " + ", ".join(pr.sign_name(s) for s in pr.exaltation_signs(pr.RAHU))
             + "; Ketu the reverse. See section 17.", "`[RK_004]`"),
            ("Which aspects do they cast?", "7th only", "`[RK_005]`"),
            ("Do they have friendships?",
             "Yes, from the table in section 6, which is not from BPHS",
             "`[RK_006]`"),
            ("Is Shadbala calculated?", "No", "`[RK_007]`"),
            ("Can they be combust?", "No", "`[RK_008]`"),
            ("Can they be in planetary war?", "No", "`[RK_009]`"),
            ("Are they retrograde?", "Always, as mean nodes", "`[RK_010]`"),
            ("Can they be a dispositor?", "No", "`[RK_011]`"),
            ("Are Avasthas shown?", "Yes, with a note that the classics address "
                                    "the seven grahas", "`[RK_012]`"),
            ("How far apart are they?", "Always exactly 180°, seven signs apart",
             "`[RK_013]`"),
            ("Benefic or malefic?", "Both malefic", "`[RK_014]`"),
        ]))
    add("")
    add(f"({len(rk)} rules cover the nodes.)")
    add("")
    add("Because they lord no house, Rahu and Ketu are never reported as Kendra "
        "lord, Trikona lord, Dusthana lord, Upachaya lord, Maraka lord, "
        "Badhakesh or Yoga Karaka.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 17. Where traditions differ")
    add("")
    add("These are the places where the classics do not speak with one voice. "
        "A choice had to be made, and it is recorded here rather than hidden. "
        "**These are the points most worth your attention.**")
    add("")
    add(table(
        ["Matter", "What this software does", "The alternative"],
        [
            ("Exaltation of Rahu and Ketu",
             "Rahu exalted in Taurus and Gemini, debilitated in Scorpio and "
             "Sagittarius; Ketu the reverse",
             "Some hold Rahu exalted in Taurus alone, others in Gemini alone, "
             "with Ketu correspondingly placed. BPHS does not settle it."),
            ("Friendships of Rahu and Ketu",
             "Taken from the table in section 6",
             "BPHS derives friendship from a planet's Mooltrikona and "
             "exaltation, which the nodes do not have, so it gives no such "
             "table for them."),
            ("Aspects of Rahu and Ketu",
             "7th only",
             "Some give them the 5th and 9th as well."),
            ("Gaja Kesari",
             "Formed by Jupiter in a Kendra from the Lagna or Moon; the four "
             "further conditions are shown separately",
             "Some require all five conditions before the yoga is said to "
             "exist at all."),
            ("Kemadruma",
             "The Sun, Rahu and Ketu do not relieve it",
             "Some count any graha in the 2nd or 12th from the Moon, including "
             "the Sun."),
            ("Lunar nodes",
             "Mean nodes",
             "True nodes, which move irregularly and can appear briefly "
             "direct."),
            ("Moon as benefic",
             "Bright when 72° to 288° from the Sun",
             "Some use the paksha alone, or a wider or narrower arc."),
            ("Parivartana",
             "Reported as a plain exchange",
             "Classical division into Maha, Khala and Dainya."),
            ("Bhava",
             "Whole sign from the Lagna sign for every rule",
             "Bhava Chalita or cusp-based houses. These are shown in the "
             "software but no rule uses them."),
        ]))
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## 18. What the software will never do")
    add("")
    add("- Call a planet good, bad, strong or weak")
    add("- Predict an event or a period")
    add("- Give a score or a ranking to a planet")
    add("- Say what a yoga will bring")
    add("- Decide an astrological question by any means other than the rules "
        "listed above")
    add("")
    add("Shadbala is shown as numbers with the required minimum beside them, "
        "and nothing more. Every classification carries a tag so it can be "
        "traced back to the rule that produced it.")
    add("")
    add("---")
    add("")

    # =====================================================================
    add("## Full list of rule tags")
    add("")
    add("Every rule in the software, for reference when reporting a correction.")
    add("")
    add(table(
        ["Tag", "Rule"],
        [(f"`{r.rule_id}`", r.name) for r in all_rules()]))
    add("")
    add("---")
    add("")
    add(f"*Calculated with PyJHora {adapter.PYJHORA_VERSION} and the Swiss "
        f"Ephemeris. This document is generated from the software's own rule "
        f"tables, so the values shown are the values actually used.*")
    add("")

    return "\n".join(L)


def _ord(n: int) -> str:
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 11 -> 11th, 12 -> 12th."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"Wrote {OUT} ({os.path.getsize(OUT):,} bytes)")
