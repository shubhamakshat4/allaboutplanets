"""Central registry of every deterministic rule used by this application.

Nothing in this project may derive an astrological classification without a Rule
that is declared here. Each rule carries an ID, name, description, source and a
description of its inputs/outputs, so that any value shown in the UI can be
traced back to the rule that produced it.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    description: str
    source: str
    inputs: List[str] = field(default_factory=list)
    calculation: str = ""
    output: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


_REGISTRY: Dict[str, Rule] = {}


def register(rule: Rule) -> Rule:
    if rule.rule_id in _REGISTRY:
        raise ValueError(f"Duplicate rule id: {rule.rule_id}")
    _REGISTRY[rule.rule_id] = rule
    return rule


def get_rule(rule_id: str) -> Rule:
    return _REGISTRY[rule_id]


def all_rules() -> List[Rule]:
    return sorted(_REGISTRY.values(), key=lambda r: r.rule_id)


# ---------------------------------------------------------------------------
# Source labels. Used verbatim in API responses so the UI can show provenance.
# ---------------------------------------------------------------------------
SRC_PYJHORA = "PyJHora"
SRC_CUSTOM = "Custom Rule Engine"
SRC_SUPPLIED = "Custom Rule Engine (supplied rule material)"


# ---------------------------------------------------------------------------
# Time / configuration / geography
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="TIME_001",
    name="Birth instant resolution",
    description=(
        "Local civil birth time is converted to a UTC offset using the IANA "
        "timezone of the birth place evaluated AT the birth instant, so that "
        "historical daylight-saving and zone changes are honoured. The resulting "
        "offset is handed to PyJHora as the Place timezone."
    ),
    source=SRC_CUSTOM,
    inputs=["date", "time", "IANA timezone or explicit UTC offset"],
    calculation="zoneinfo.ZoneInfo(tz).utcoffset(naive_local_datetime) -> hours",
    output="UTC offset in hours; Julian Day via utils.julian_day_number",
))

register(Rule(
    rule_id="CONFIG_001",
    name="Ayanamsha and zodiac configuration",
    description=(
        "The ayanamsha mode is set explicitly on every calculation rather than "
        "relying on the PyJHora package default (which is TRUE_PUSHYA in 4.8.7). "
        "The mode used is stored with the chart and displayed."
    ),
    source=SRC_CUSTOM,
    inputs=["ayanamsha mode name"],
    calculation="drik.set_ayanamsa_mode(mode) before every chart calculation",
    output="Sidereal positions under the named ayanamsha",
))

register(Rule(
    rule_id="GEO_001",
    name="Place resolution",
    description=(
        "Latitude, longitude and IANA timezone for a named place. PyJHora's "
        "bundled place database is not distributed with the wheel, so resolution "
        "uses an external geocoder with full manual override. Never guessed."
    ),
    source=SRC_CUSTOM,
    inputs=["place query"],
    calculation="Geocoder lookup, then timezonefinder for the IANA zone",
    output="latitude, longitude, timezone name, UTC offset",
))

register(Rule(
    rule_id="HOUSE_001",
    name="Whole-sign Bhava",
    description=(
        "Bhava of a planet counted as whole signs from the Lagna sign. This is "
        "the house frame used by every classical rule in this application "
        "(lordship, kendra/trikona, yogas, Neecha Bhanga). Bhava Chalita from "
        "PyJHora is reported separately and never substituted for this."
    ),
    source=SRC_CUSTOM,
    inputs=["planet sign index", "lagna sign index"],
    calculation="((planet_sign - lagna_sign) mod 12) + 1",
    output="Bhava number 1-12",
))

register(Rule(
    rule_id="NAK_001",
    name="Nakshatra lord",
    description="Lord of a nakshatra by the Vimshottari sequence, repeating every 9 nakshatras.",
    source=SRC_CUSTOM,
    inputs=["nakshatra index 1-27"],
    calculation="VIMSHOTTARI_ORDER[(nakshatra_index - 1) mod 9]",
    output="Planet id of the nakshatra lord",
))

# ---------------------------------------------------------------------------
# Dignity
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="DIGNITY_001",
    name="Rashi dignity",
    description=(
        "Exalted / Debilitated / Own sign / Friend's sign / Neutral sign / "
        "Enemy's sign for a planet in a sign, decoded from PyJHora's dignity "
        "table const.house_strengths_of_planets."
    ),
    source=SRC_PYJHORA,
    inputs=["planet id", "sign index"],
    calculation="const.house_strengths_of_planets[planet][sign] -> "
                "{5:Own, 4:Exalted, 3:Friend, 2:Neutral, 1:Enemy, 0:Debilitated}",
    output="One dignity classification plus the independent booleans",
))

register(Rule(
    rule_id="DIGNITY_002",
    name="Mooltrikona",
    description=(
        "Whether a planet occupies its Mooltrikona sign AND its Mooltrikona "
        "degree range. Defined for Sun..Saturn only in the selected rule set; "
        "Rahu and Ketu report 'Not defined in selected rule set'."
    ),
    source=SRC_PYJHORA,
    inputs=["planet id", "sign index", "degree within sign"],
    calculation="const.moola_trikona_range_of_planets[planet] = (sign, start_deg, end_deg); "
                "sign matches AND start <= degree < end",
    output="Yes / No / Not defined in selected rule set",
))

register(Rule(
    rule_id="COMBUST_001",
    name="Combustion (Asta)",
    description=(
        "A planet within the classical orb of the Sun is combust. Orbs, measured "
        "from the Sun: Moon 12, Mars 17, Mercury 14 (12 retrograde), Jupiter 11, "
        "Venus 10 (8 retrograde), Saturn 15 degrees. Separation is the shorter "
        "arc, so a pair straddling 0 Aries is handled. The Sun is the reference "
        "and Rahu/Ketu are outside the rule (see RK_008). "
        "Evaluated by this engine rather than by PyJHora 4.8.7, which indexes "
        "its orb table one position out for every planet (the Moon wrapping to "
        "Saturn's orb) and compares raw longitudes. PyJHora's verdict is "
        "reported beside ours."
    ),
    source=SRC_SUPPLIED,
    inputs=["planet longitude", "Sun longitude", "retrograde status"],
    calculation="shorter_arc(planet, Sun) <= orb(planet, retrograde)",
    output="Combust Yes/No, with the separation and orb shown",
))

register(Rule(
    rule_id="VARGA_001",
    name="Vargottama",
    description="A planet occupying the same sign in D1 and D9.",
    source=SRC_SUPPLIED,
    inputs=["D1 sign", "D9 sign"],
    calculation="D1_sign == D9_sign",
    output="Yes / No",
))

# ---------------------------------------------------------------------------
# Relationships (Maitri)
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="MAITRI_001",
    name="Natural (permanent) relationship",
    description=(
        "Natural friendship between two planets, read from PyJHora's "
        "const.planet_relations table. The table defines all 9 bodies including "
        "Rahu and Ketu; any undefined pair is reported as such rather than guessed."
    ),
    source=SRC_PYJHORA,
    inputs=["planet A id", "planet B id"],
    calculation="const.planet_relations[A][B] -> {3:Friend, 2:Neutral, 1:Enemy}",
    output="Friend / Neutral / Enemy / Not defined in selected rule set",
))

register(Rule(
    rule_id="MAITRI_002",
    name="Temporary relationship",
    description=(
        "Planets occupying the 2nd, 3rd, 4th, 10th, 11th or 12th sign from a "
        "planet are its temporary friends. Planets in the 1st, 5th, 6th, 7th, "
        "8th or 9th sign from it are its temporary enemies."
    ),
    source=SRC_PYJHORA,
    inputs=["sign of planet A", "sign of planet B"],
    calculation="offset = (sign_B - sign_A) mod 12; "
                "offset in const.temporary_friend_raasi_positions [1,2,3,9,10,11] -> Friend; "
                "offset in const.temporary_enemy_raasi_positions [0,4,5,6,7,8] -> Enemy",
    output="Friend / Enemy",
))

register(Rule(
    rule_id="MAITRI_003",
    name="Panchadha Maitri (five-fold compound relationship)",
    description=(
        "Combination of the natural and temporary relationship into the five-fold "
        "compound relationship. This is the single relationship engine used "
        "everywhere in the application."
    ),
    source=SRC_SUPPLIED,
    inputs=["natural relationship", "temporary relationship"],
    calculation=(
        "Friend  + Friend = Ati Mitra; "
        "Neutral + Friend = Mitra; "
        "Friend  + Enemy  = Sama; "
        "Enemy   + Friend = Sama; "
        "Neutral + Enemy  = Shatru; "
        "Enemy   + Enemy  = Ati Shatru"
    ),
    output="Ati Mitra / Mitra / Sama / Shatru / Ati Shatru",
))

# ---------------------------------------------------------------------------
# Functional classification
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="FUNC_001",
    name="House ownership",
    description="Houses owned by a planet, from the signs it lords, counted from Lagna.",
    source=SRC_PYJHORA,
    inputs=["planet id", "lagna sign"],
    calculation="For each sign S where const._house_owners_list[S] == planet: "
                "house = ((S - lagna_sign) mod 12) + 1",
    output="List of house numbers",
))

register(Rule(
    rule_id="FUNC_002",
    name="Kendra / Trikona / Dusthana / Upachaya / Maraka house categories",
    description="Standard Parashari house category sets.",
    source=SRC_SUPPLIED,
    inputs=["house number"],
    calculation="Kendra {1,4,7,10}; Trikona {1,5,9}; Dusthana {6,8,12}; "
                "Upachaya {3,6,10,11}; Maraka {2,7}",
    output="Set of categories the house belongs to",
))

register(Rule(
    rule_id="FUNC_003",
    name="Badhaka house and Badhakesh",
    description=(
        "Badhaka house determined by the modality of the Lagna sign; the lord of "
        "that house is the Badhakesh."
    ),
    source=SRC_SUPPLIED,
    inputs=["lagna sign"],
    calculation="Movable Lagna -> 11th; Fixed Lagna -> 9th; Dual Lagna -> 7th",
    output="Badhaka house number and its lord",
))

register(Rule(
    rule_id="FUNC_004",
    name="Yoga Karaka",
    description=(
        "A planet that simultaneously owns at least one Kendra house (other than "
        "the 1st alone) and at least one Trikona house."
    ),
    source=SRC_SUPPLIED,
    inputs=["houses owned"],
    calculation="owns a house in {4,7,10} AND owns a house in {5,9}",
    output="Yes / No",
))

register(Rule(
    rule_id="FUNC_005",
    name="Functional classification summary",
    description=(
        "The set of lordship roles a planet holds. Presented as independent "
        "components; the application does not reduce them to a benefic/malefic "
        "verdict."
    ),
    source=SRC_SUPPLIED,
    inputs=["houses owned", "lagna sign"],
    calculation="Union of FUNC_002, FUNC_003, FUNC_004 evaluated per owned house",
    output="Kendra Lord, Trikona Lord, Dusthana Lord, Upachaya Lord, Maraka Lord, "
           "Badhakesh, Yoga Karaka flags",
))

register(Rule(
    rule_id="FUNC_006",
    name="Sign modality",
    description="Movable (Chara), Fixed (Sthira) or Dual (Dwiswabhava) sign.",
    source=SRC_PYJHORA,
    inputs=["sign index"],
    calculation="const.movable_signs / const.fixed_signs / const.dual_signs",
    output="Movable / Fixed / Dual",
))

register(Rule(
    rule_id="FUNC_007",
    name="Sign parity",
    description="Odd (Oja) or Even (Yugma) sign.",
    source=SRC_PYJHORA,
    inputs=["sign index"],
    calculation="const.odd_signs / const.even_signs (0-based indices)",
    output="Odd / Even",
))

# ---------------------------------------------------------------------------
# Avasthas
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="KUMARADI_001",
    name="Kumaradi Avastha",
    description=(
        "Five-fold avastha from the degree of the planet within its sign, with "
        "the order reversed for even signs."
    ),
    source=SRC_SUPPLIED,
    inputs=["degree within sign", "sign parity"],
    calculation=(
        "Odd sign:  0-6 Bala, 6-12 Kumara, 12-18 Yuva, 18-24 Vriddha, 24-30 Mrita. "
        "Even sign: 0-6 Mrita, 6-12 Vriddha, 12-18 Yuva, 18-24 Kumara, 24-30 Bala. "
        "Bands are lower-inclusive, upper-exclusive."
    ),
    output="Bala / Kumara / Yuva / Vriddha / Mrita",
))

register(Rule(
    rule_id="CHAITANYADI_001",
    name="Chaitanyadi Avastha",
    description=(
        "Three-fold avastha from the degree of the planet within its sign, with "
        "the order reversed for even signs."
    ),
    source=SRC_SUPPLIED,
    inputs=["degree within sign", "sign parity"],
    calculation=(
        "Odd sign:  0-10 Jagrut, 10-20 Swapna, 20-30 Sushupta. "
        "Even sign: 0-10 Sushupta, 10-20 Swapna, 20-30 Jagrut. "
        "Bands are lower-inclusive, upper-exclusive."
    ),
    output="Jagrut / Swapna / Sushupta",
))

# ---------------------------------------------------------------------------
# Interactions
# ---------------------------------------------------------------------------
register(Rule(
    rule_id="CONJ_001",
    name="Conjunction",
    description="Two planets occupying the same Rashi in D1.",
    source=SRC_SUPPLIED,
    inputs=["sign of planet A", "sign of planet B"],
    calculation="sign_A == sign_B; separation = |absolute_longitude_A - absolute_longitude_B| "
                "reduced to the shorter arc",
    output="Conjunction record with degree separation",
))

register(Rule(
    rule_id="ASPECT_001",
    name="Graha Drishti ordinal",
    description=(
        "The ordinal number of an aspect (4th, 7th, 9th ...) derived from the "
        "signs involved. Which aspects exist at all comes from PyJHora."
    ),
    source=SRC_CUSTOM,
    inputs=["source sign", "target sign"],
    calculation="((target_sign - source_sign) mod 12) + 1",
    output="Aspect ordinal 1-12",
))

register(Rule(
    rule_id="DISPOSITOR_001",
    name="Dispositor chain",
    description=(
        "Chain formed by repeatedly moving from a planet to the lord of the sign "
        "it occupies, terminating on a self-dispositor or a detected cycle."
    ),
    source=SRC_SUPPLIED,
    inputs=["planet positions", "sign lords"],
    calculation="X -> lord(sign_of(X)); stop when lord == X (self) or a planet repeats (cycle)",
    output="Ordered chain, termination reason, cycle members",
))

register(Rule(
    rule_id="BENEFIC_001",
    name="Natural benefic / malefic classification",
    description=(
        "Jupiter and Venus are natural benefics. Mercury is a benefic when it "
        "does not share its sign with any natural malefic. The Moon is a benefic "
        "when its elongation from the Sun lies between 72 and 288 degrees "
        "(waxing/bright). Sun, Mars, Saturn, Rahu and Ketu are natural malefics."
    ),
    source=SRC_SUPPLIED,
    inputs=["planet id", "chart positions"],
    calculation="See description; evaluated once per chart and reused by every yoga",
    output="Benefic / Malefic with the reason recorded",
))

# ---------------------------------------------------------------------------
# Neecha Bhanga
# ---------------------------------------------------------------------------
_NB = [
    ("NB_001", "Debilitation-sign lord in Kendra from Lagna",
     "The lord of the sign in which the planet is debilitated occupies a Kendra "
     "(1, 4, 7, 10) counted from the Lagna."),
    ("NB_002", "Debilitation-sign lord in Kendra from Moon",
     "The lord of the sign in which the planet is debilitated occupies a Kendra "
     "counted from the Moon."),
    ("NB_003", "Exaltation-sign lord in Kendra from Lagna",
     "The lord of the sign in which the planet would be exalted occupies a Kendra "
     "counted from the Lagna."),
    ("NB_004", "Exaltation-sign lord in Kendra from Moon",
     "The lord of the sign in which the planet would be exalted occupies a Kendra "
     "counted from the Moon."),
    ("NB_005", "Association with a cancellation lord",
     "The debilitated planet is conjunct with, or in mutual Graha Drishti with, "
     "the lord of its debilitation sign or the lord of its exaltation sign."),
    ("NB_006", "Debilitation lord and exaltation lord in mutual Kendras",
     "The lord of the debilitation sign and the lord of the exaltation sign "
     "occupy Kendras from each other (1, 4, 7 or 10 signs apart)."),
]
for _id, _name, _desc in _NB:
    register(Rule(
        rule_id=_id, name=_name, description=_desc, source=SRC_SUPPLIED,
        inputs=["debilitated planet", "chart positions", "lagna sign", "moon sign"],
        calculation=_desc,
        output="Satisfied / Not satisfied, with the participating planets recorded",
    ))

register(Rule(
    rule_id="NB_100",
    name="Neecha Bhanga (cancellation) summary",
    description=(
        "Count of satisfied conditions NB_001..NB_006. Reported as a count and a "
        "per-condition breakdown. Retrograde motion is deliberately NOT used as a "
        "cancellation condition in V1."
    ),
    source=SRC_SUPPLIED,
    inputs=["NB_001..NB_006 results"],
    calculation="Number of conditions evaluating to Satisfied",
    output="Integer count plus the individual condition results",
))

# ---------------------------------------------------------------------------
# Benefic / malefic classification
# ---------------------------------------------------------------------------
_NATURE = [
    ("NATURE_001", "Natural benefic, malefic or neutral",
     "Jupiter and Venus are natural benefics in every chart. Mars, Saturn, "
     "Rahu and Ketu are natural malefics, and the Sun is counted among the "
     "cruel grahas as a mild malefic. The Moon is benefic while bright, taken "
     "as an elongation from the Sun between 72 and 288 degrees, and malefic "
     "while dark. Mercury takes the nature of the company it keeps: benefic "
     "with benefics, malefic with malefics, and neutral when alone or when "
     "its sign holds both.",
     "Benefic / Malefic / Neutral, with the reason recorded"),
    ("NATURE_002", "Nature of each house",
     "The Trikonas (1, 5, 9) and Kendras (1, 4, 7, 10) are auspicious, as are "
     "the 2nd and 11th. The Dusthanas (6, 8, 12) are the difficult houses. The "
     "3rd is an Upachaya but is counted mildly difficult.",
     "Auspicious / Difficult / Mixed"),
    ("NATURE_003", "Grouping of a planet's house placement",
     "A placement in an auspicious house is grouped favourably and one in a "
     "Dusthana as a difficulty. A natural malefic placed in an Upachaya house "
     "(3rd, 6th, 10th, 11th) is grouped favourably instead, since malefics are "
     "held to grow strong in the Upachayas.",
     "The group the placement bullet falls into"),
    ("NATURE_004", "Functional nature for a given Lagna",
     "Decided by the houses a planet lords. The Lagna lord is auspicious, the "
     "1st being both Kendra and Trikona. Lords of the 5th and 9th are "
     "auspicious. Lords of the 3rd, 6th and 11th, the Trishadaya, are "
     "inauspicious, as is the 8th lord unless it also lords the Lagna. Lords "
     "of the 2nd and 12th are neutral in themselves. By Kendradhipatya a "
     "natural benefic lording a Kendra (4th, 7th, 10th) loses its benefic "
     "power while a natural malefic doing so turns auspicious. A planet "
     "lording both a Kendra and a Trikona is a Yoga Karaka. Where a planet "
     "holds both an auspicious and an inauspicious lordship, the Trikona "
     "lordship prevails.",
     "Benefic / Malefic / Neutral for that Lagna, with every reason listed"),
    ("NATURE_005", "Grouping of retrogression",
     "A retrograde graha stands near the earth and gains Cheshta Bala. "
     "Retrogression in a natural malefic is grouped favourably; in a natural "
     "benefic it is grouped as the less welcome case. The Sun and Moon never "
     "retrograde and the nodes always do, so for those four the question "
     "carries no distinction and is left neutral.",
     "The group the retrogression bullet falls into"),
    ("NATURE_006", "Grouping of company and aspect",
     "A conjunction with, or an aspect received from, a natural benefic is "
     "grouped favourably; from a natural malefic, as a difficulty; from a "
     "graha whose nature resolves neutral, neutrally.",
     "The group each conjunction and aspect bullet falls into"),
    ("NATURE_007", "The fixed catalogue of checks",
     "Every planet is put through the same catalogue of checks, so the same "
     "bullets appear for all nine grahas. A check that cannot apply to a body "
     "still produces its bullet, stating that it does not apply, and is "
     "grouped neutral.",
     "One bullet per check for every planet"),
    ("NATURE_009", "Points left to the astrologer",
     "The yellow group holds three different kinds of point, and each bullet "
     "says which it is. 'Does not apply' means the check cannot bear on that "
     "body at all. 'Neutral' means the rule ran and came out on neither side. "
     "'Your call' means the classics genuinely differ, or two rules pull "
     "against each other, and the software will not decide for you. The "
     "situations treated as open are: the exaltation of Rahu and Ketu, which "
     "the classics do not fix; a graha holding both an auspicious and an "
     "inauspicious lordship; a natural malefic lording both a Kendra and a "
     "Maraka house; the combustion of Mercury, which is common and widely "
     "discounted; conjunction with or aspect from a node, since nodes are held "
     "to take the character of their associations; a Neecha Bhanga where only "
     "some conditions are met; and Vargottama in a debilitated graha. Each "
     "carries its reason on the Explain panel.",
     "Yellow, with the kind and the reason shown"),
    ("NATURE_008", "No aggregate verdict",
     "The findings are never combined into a score, a rating or an overall "
     "judgement of the planet. The count shown against each group is simply "
     "how many facts fall in it.",
     "Three groups of independent facts"),
]
for _id, _name, _desc, _out in _NATURE:
    register(Rule(
        rule_id=_id, name=_name, description=_desc, source=SRC_SUPPLIED,
        inputs=["planet", "chart positions", "lagna sign"],
        calculation=_desc, output=_out,
    ))


# ---------------------------------------------------------------------------
# Rahu and Ketu
#
# Brihat Parashara Hora Shastra counts nine grahas but develops most of its
# quantitative apparatus for the seven. Each feature below therefore states
# explicitly whether it applies to the nodes, so that no seven-planet rule is
# ever extended to them by default and nothing is guessed.
# ---------------------------------------------------------------------------
_RAHU_KETU = [
    ("RK_001", "Rahu and Ketu hold no sign lordship",
     "The twelve signs are lorded by the Sun through Saturn only. Rahu and Ketu "
     "own no sign, therefore they own no house and hold no functional "
     "classification derived from house ownership: not Kendra lord, Trikona "
     "lord, Dusthana lord, Upachaya lord, Maraka lord, Badhakesh or Yoga Karaka. "
     "A tradition assigning Rahu co-lordship of Aquarius and Ketu co-lordship of "
     "Scorpio exists and is recorded in PyJHora, but it is not part of the "
     "Parashari lordship scheme used here and is not applied.",
     "Houses owned: empty. Lordship roles: all No."),
    ("RK_002", "Rahu and Ketu have no Mooltrikona",
     "BPHS assigns Mooltrikona signs and degree ranges to the seven grahas only.",
     "Not defined in selected rule set."),
    ("RK_003", "Rahu and Ketu have no Swarashi",
     "Own-sign status follows from lordship, which the nodes do not hold (RK_001).",
     "Not defined in selected rule set."),
    ("RK_004", "Rahu and Ketu exaltation and debilitation",
     "BPHS does not place Rahu and Ketu in the main exaltation table. The rule "
     "set applied here takes Rahu as exalted in Taurus and Gemini and debilitated "
     "in Scorpio and Sagittarius, with Ketu the reverse. Other well-attested "
     "traditions give Rahu exaltation in Taurus alone, or in Gemini alone, with "
     "Ketu correspondingly in Scorpio or Sagittarius. The value is labelled with "
     "its source wherever it is shown, and no deep-exaltation degree is claimed.",
     "Exaltation and debilitation signs, labelled with their source."),
    ("RK_005", "Rahu and Ketu Graha Drishti",
     "The nodes cast the 7th Graha Drishti only in the rule set applied here. "
     "Traditions giving them the 5th and 9th aspects as well are not applied. "
     "They receive Graha Drishti from other planets normally.",
     "7th aspect only, with the restriction stated."),
    ("RK_006", "Rahu and Ketu natural relationships",
     "BPHS derives natural friendship from a graha's Mooltrikona and exaltation "
     "signs, a derivation the nodes cannot enter since they have neither in the "
     "classical scheme. The relationship table applied here does define all nine "
     "bodies, so Panchadha Maitri is computed for the nodes and labelled with its "
     "source. Temporary relationship is purely positional and applies to them "
     "without qualification.",
     "Natural, temporary and Panchadha Maitri, source-labelled."),
    ("RK_007", "Rahu and Ketu are outside Shadbala",
     "The six-fold strength framework is defined for the Sun through Saturn. No "
     "Shadbala component is calculated for the nodes.",
     "Not available."),
    ("RK_008", "Rahu and Ketu are outside combustion",
     "Combustion applies to the Moon through Saturn. The nodes are shadow points "
     "with no disc to be eclipsed by the Sun's proximity.",
     "Not applicable."),
    ("RK_009", "Rahu and Ketu are outside Graha Yuddha",
     "Planetary war is fought between the five star planets, Mars, Mercury, "
     "Jupiter, Venus and Saturn. The luminaries and the nodes are excluded.",
     "Not applicable."),
    ("RK_010", "Rahu and Ketu are always retrograde as mean nodes",
     "With the mean-node calculation used here the nodes move uniformly "
     "backwards, so they are reported retrograde in every chart. True-node "
     "calculations can show them stationary or briefly direct.",
     "Retrograde, with the node type stated."),
    ("RK_011", "Rahu and Ketu never act as dispositors",
     "A dispositor is the lord of the occupied sign. Since the nodes lord no "
     "sign (RK_001), they can appear in a dispositor chain as a member but never "
     "as the lord that the chain steps to.",
     "May start or appear in a chain; never terminate one as a self-dispositor."),
    ("RK_012", "Avastha applicability to Rahu and Ketu",
     "Kumaradi and Chaitanyadi Avastha are stated as degree bands by sign parity "
     "without an explicit restriction on the bodies they cover, while the "
     "classical descriptions address the seven grahas. The value is computed for "
     "the nodes by the same band rule and carries a note recording that the "
     "classical scope is the seven grahas.",
     "Computed, with an applicability note attached."),
    ("RK_013", "Rahu and Ketu are always in opposition",
     "The nodes are the two intersections of the lunar orbit with the ecliptic "
     "and are therefore exactly 180 degrees apart, occupying signs seven apart. "
     "They are never conjunct with each other.",
     "Ketu longitude equals Rahu longitude plus 180 degrees."),
    ("RK_014", "Rahu and Ketu as natural malefics",
     "Both nodes are classified natural malefics under rule BENEFIC_001, so "
     "neither can satisfy a benefic-association condition in any yoga, and "
     "either occupying a sign with Mercury renders Mercury malefic.",
     "Malefic."),
]
for _id, _name, _desc, _out in _RAHU_KETU:
    register(Rule(
        rule_id=_id, name=_name, description=_desc, source=SRC_SUPPLIED,
        inputs=["planet id", "chart positions"],
        calculation=_desc,
        output=_out,
    ))


# ---------------------------------------------------------------------------
# Doshas
#
# A dosha is reported by its formation alone. Where the classics give
# well-known grounds for cancellation those are shown with the finding, but the
# software does not decide whether a cancellation carries.
# ---------------------------------------------------------------------------
from .dosha_rules import DOSHA_SPECS as _DOSHA_SPECS  # noqa: E402

for _spec in _DOSHA_SPECS:
    register(Rule(
        rule_id=_spec.rule_id, name=_spec.name, description=_spec.formation,
        source=SRC_SUPPLIED,
        inputs=["chart positions", "house lords", "lagna sign"],
        calculation=_spec.formation,
        output="Present / Not present, with the participating grahas, the "
               "evidence, and any classical grounds for cancellation",
    ))

register(Rule(
    rule_id="DOSHA_100",
    name="How doshas are reported",
    description=(
        "Only doshas that actually form, and that the selected planet takes "
        "part in, are listed on that planet's page. Kemadruma is reported here "
        "rather than with the yogas, being an affliction by nature. Grounds on "
        "which the classics hold a dosha to be lifted are shown with it, but "
        "are never applied automatically: whether a cancellation carries is "
        "left to the astrologer."
    ),
    source=SRC_SUPPLIED,
    inputs=["dosha results", "selected planet"],
    calculation="Filter to doshas where present is true and the planet is a participant",
    output="The doshas involving that planet",
))


# ---------------------------------------------------------------------------
# Yogas
# ---------------------------------------------------------------------------
_YOGAS = [
    ("YOGA_001", "Raja Yoga",
     "A Kendra lord and a Trikona lord associate by conjunction, mutual Graha "
     "Drishti, or sign exchange (Parivartana). The Lagna lord qualifies as both, "
     "since the 1st house is a Kendra and a Trikona."),
    ("YOGA_002", "Dharma-Karmadhipati Yoga",
     "The 9th lord and the 10th lord associate by conjunction, mutual Graha "
     "Drishti, or sign exchange."),
    ("YOGA_003", "Ruchaka Yoga",
     "Mars occupies Aries, Scorpio or Capricorn AND occupies a Kendra (1, 4, 7, 10) "
     "from the Lagna."),
    ("YOGA_004", "Bhadra Yoga",
     "Mercury occupies Gemini or Virgo AND occupies a Kendra from the Lagna."),
    ("YOGA_005", "Hamsa Yoga",
     "Jupiter occupies Sagittarius, Pisces or Cancer AND occupies a Kendra from the Lagna."),
    ("YOGA_006", "Malavya Yoga",
     "Venus occupies Taurus, Libra or Pisces AND occupies a Kendra from the Lagna."),
    ("YOGA_007", "Sasa Yoga",
     "Saturn occupies Capricorn, Aquarius or Libra AND occupies a Kendra from the Lagna."),
    ("YOGA_008", "Gaja Kesari Yoga",
     "Core formation: Jupiter occupies a Kendra (1, 4, 7, 10) from the Lagna or from "
     "the Moon. A Moon-Jupiter conjunction is the 1st from the Moon and therefore "
     "forms it. Four strengthening conditions are evaluated and reported separately "
     "and do not affect the formation status: Jupiter conjunct with or in mutual "
     "Graha Drishti with a natural benefic; Jupiter not debilitated; Jupiter not "
     "combust; Jupiter not in an enemy's sign. Classical sources differ on whether "
     "these govern the formation of the yoga or only the extent of its results, so "
     "the two sets are kept distinct rather than merged into one verdict."),
    ("YOGA_009", "Budha-Aditya Yoga",
     "The Sun and Mercury occupy the same Rashi. Mercury's combustion is reported "
     "as a separate independent fact and does not negate the formation."),
    ("YOGA_010", "Chandra-Mangala Yoga",
     "The Moon and Mars occupy the same Rashi. Mutual-aspect variants are not part of V1."),
    ("YOGA_011", "Guru-Mangala Yoga",
     "Jupiter and Mars occupy the same Rashi."),
    ("YOGA_012", "Adhi Yoga",
     "Natural benefics (BENEFIC_001) occupy the 6th, 7th and/or 8th signs counted "
     "from the Moon. Formation requires at least one such benefic; the occupancy of "
     "each of the three positions is reported individually."),
    ("YOGA_013", "Amala Yoga",
     "A natural benefic (BENEFIC_001) occupies the 10th sign counted from the Lagna "
     "or the 10th sign counted from the Moon."),
    ("YOGA_014", "Harsha Yoga",
     "The lord of the 6th house occupies the 6th, 8th or 12th house."),
    ("YOGA_015", "Sarala Yoga",
     "The lord of the 8th house occupies the 6th, 8th or 12th house."),
    ("YOGA_016", "Vimala Yoga",
     "The lord of the 12th house occupies the 6th, 8th or 12th house."),
    ("YOGA_017", "Dhana Yoga",
     "Two or more of the lords of the 2nd, 5th, 9th and 11th houses associate by "
     "conjunction, mutual Graha Drishti or sign exchange, and at least one "
     "participant is the 2nd lord or the 11th lord."),
    ("YOGA_018", "Lakshmi Yoga",
     "The Lagna lord occupies a Kendra or Trikona house, and the 9th lord occupies "
     "its own sign, its Mooltrikona sign, or its exaltation sign while placed in a "
     "Kendra or Trikona house. Each condition is reported individually."),
    ("YOGA_019", "Saraswati Yoga",
     "Jupiter, Venus and Mercury each occupy the 2nd house, a Kendra (1, 4, 7, 10) "
     "or a Trikona (1, 5, 9) from the Lagna, and Jupiter additionally occupies its "
     "own sign, its Mooltrikona sign, its exaltation sign or a friend's sign."),
    ("YOGA_020", "Kemadruma Yoga",
     "No planet other than the Sun, Rahu and Ketu occupies the 2nd or the 12th sign "
     "counted from the Moon. The exclusion of the Sun and the nodes is the "
     "conventional formulation used consistently here."),
    ("YOGA_021", "Parivartana Yoga",
     "Planet A occupies a sign owned by planet B while planet B occupies a sign "
     "owned by planet A. Maha/Khala/Dainya subclassification is not part of V1."),
    ("YOGA_022", "Neecha Bhanga Raja Yoga",
     "A debilitated planet whose Neecha Bhanga condition count (NB_100) is at least "
     "one, AND which either owns or occupies a Kendra or Trikona house. Debilitation, "
     "Neecha Bhanga and Neecha Bhanga Raja Yoga are kept as three distinct states."),
]
for _id, _name, _desc in _YOGAS:
    register(Rule(
        rule_id=_id, name=_name, description=_desc, source=SRC_SUPPLIED,
        inputs=["chart positions", "house lords", "Graha Drishti", "dignity"],
        calculation=_desc,
        output="Present / Not Present with participants and per-condition evidence",
    ))
