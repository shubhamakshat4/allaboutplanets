/**
 * Rule review form for the Planetary Status Analyzer.
 *
 * GENERATED FILE - do not edit by hand.
 * Regenerate with:  python -m tools.generate_review_form
 *
 * How to use
 * ----------
 *  1. Open https://script.google.com and start a new project.
 *  2. Replace the contents of Code.gs with this file.
 *  3. Run buildReviewForm(). Approve the permissions it asks for; it needs to
 *     create a form and a spreadsheet on your account.
 *  4. The execution log prints two links: one to edit the form, one to send to
 *     the astrologer.
 *
 * Each rule becomes a required multiple-choice question and an optional
 * comment box. Responses collect in a linked Google Sheet, one row per
 * submission, so several reviewers can be compared side by side.
 */

var FORM_TITLE = "Planetary Status Analyzer - rule review";
var FORM_DESCRIPTION = "Every rule this software applies, one at a time, for you to confirm or\ncorrect.\n\nThere are 93 rules across 12 sections. Each shows\nexactly what the software does. Mark it correct, or say what it should\ndo instead. A citation is welcome but not required.\n\nThe full reference with all the tables is in RULES.pdf. Nothing here\ninterprets a chart or predicts anything; these are only the rules used\nto derive the facts.";
var VERDICTS = [
  "Correct as stated",
  "Correct, but the wording could be clearer",
  "Needs a change",
  "Not sure / skip"
];
var SECTIONS = [
  {
    "title": "Time, place and configuration",
    "blurb": "How the birth moment and the chart settings are resolved.",
    "rules": [
      {
        "id": "CONFIG_001",
        "name": "Ayanamsha and zodiac configuration",
        "statement": "The ayanamsha mode is set explicitly on every calculation rather than relying on the PyJHora package default (which is TRUE_PUSHYA in 4.8.7). The mode used is stored with the chart and displayed.   [Result: Sidereal positions under the named ayanamsha]"
      },
      {
        "id": "GEO_001",
        "name": "Place resolution",
        "statement": "Latitude, longitude and IANA timezone for a named place. PyJHora's bundled place database is not distributed with the wheel, so resolution uses an external geocoder with full manual override. Never guessed.   [Result: latitude, longitude, timezone name, UTC offset]"
      },
      {
        "id": "TIME_001",
        "name": "Birth instant resolution",
        "statement": "Local civil birth time is converted to a UTC offset using the IANA timezone of the birth place evaluated AT the birth instant, so that historical daylight-saving and zone changes are honoured. The resulting offset is handed to PyJHora as the Place timezone.   [Result: UTC offset in hours; Julian Day via utils.julian_day_number]"
      }
    ]
  },
  {
    "title": "Houses and Nakshatras",
    "blurb": "Which house frame is used, and how nakshatra lords are assigned.",
    "rules": [
      {
        "id": "HOUSE_001",
        "name": "Whole-sign Bhava",
        "statement": "Bhava of a planet counted as whole signs from the Lagna sign. This is the house frame used by every classical rule in this application (lordship, kendra/trikona, yogas, Neecha Bhanga). Bhava Chalita from PyJHora is reported separately and never substituted for this.   [Result: Bhava number 1-12]"
      },
      {
        "id": "NAK_001",
        "name": "Nakshatra lord",
        "statement": "Lord of a nakshatra by the Vimshottari sequence, repeating every 9 nakshatras.   [Result: Planet id of the nakshatra lord]"
      }
    ]
  },
  {
    "title": "Dignity",
    "blurb": "Exaltation, debilitation, own sign, Mooltrikona, Vargottama, combustion.",
    "rules": [
      {
        "id": "COMBUST_001",
        "name": "Combustion (Asta)",
        "statement": "A planet within the classical orb of the Sun is combust. Orbs, measured from the Sun: Moon 12, Mars 17, Mercury 14 (12 retrograde), Jupiter 11, Venus 10 (8 retrograde), Saturn 15 degrees. Separation is the shorter arc, so a pair straddling 0 Aries is handled. The Sun is the reference and Rahu/Ketu are outside the rule (see RK_008). Evaluated by this engine rather than by PyJHora 4.8.7, which indexes its orb table one position out for every planet (the Moon wrapping to Saturn's orb) and compares raw longitudes. PyJHora's verdict is reported beside ours.   [Result: Combust Yes/No, with the separation and orb shown]"
      },
      {
        "id": "DIGNITY_001",
        "name": "Rashi dignity",
        "statement": "Exalted / Debilitated / Own sign / Friend's sign / Neutral sign / Enemy's sign for a planet in a sign, decoded from PyJHora's dignity table const.house_strengths_of_planets.   [Result: One dignity classification plus the independent booleans]"
      },
      {
        "id": "DIGNITY_002",
        "name": "Mooltrikona",
        "statement": "Whether a planet occupies its Mooltrikona sign AND its Mooltrikona degree range. Defined for Sun..Saturn only in the selected rule set; Rahu and Ketu report 'Not defined in selected rule set'.   [Result: Yes / No / Not defined in selected rule set]"
      },
      {
        "id": "VARGA_001",
        "name": "Vargottama",
        "statement": "A planet occupying the same sign in D1 and D9.   [Result: Yes / No]"
      }
    ]
  },
  {
    "title": "Benefic, malefic and neutral",
    "blurb": "What each graha and each house is counted as, and how a graha's functional nature is decided for a given Lagna.",
    "rules": [
      {
        "id": "NATURE_001",
        "name": "Natural benefic, malefic or neutral",
        "statement": "Jupiter and Venus are natural benefics in every chart. Mars, Saturn, Rahu and Ketu are natural malefics, and the Sun is counted among the cruel grahas as a mild malefic. The Moon is benefic while bright, taken as an elongation from the Sun between 72 and 288 degrees, and malefic while dark. Mercury takes the nature of the company it keeps: benefic with benefics, malefic with malefics, and neutral when alone or when its sign holds both.   [Result: Benefic / Malefic / Neutral, with the reason recorded]"
      },
      {
        "id": "NATURE_002",
        "name": "Nature of each house",
        "statement": "The Trikonas (1, 5, 9) and Kendras (1, 4, 7, 10) are auspicious, as are the 2nd and 11th. The Dusthanas (6, 8, 12) are the difficult houses. The 3rd is an Upachaya but is counted mildly difficult.   [Result: Auspicious / Difficult / Mixed]"
      },
      {
        "id": "NATURE_003",
        "name": "Grouping of a planet's house placement",
        "statement": "A placement in an auspicious house is grouped favourably and one in a Dusthana as a difficulty. A natural malefic placed in an Upachaya house (3rd, 6th, 10th, 11th) is grouped favourably instead, since malefics are held to grow strong in the Upachayas.   [Result: The group the placement bullet falls into]"
      },
      {
        "id": "NATURE_004",
        "name": "Functional nature for a given Lagna",
        "statement": "Decided by the houses a planet lords. The Lagna lord is auspicious, the 1st being both Kendra and Trikona. Lords of the 5th and 9th are auspicious. Lords of the 3rd, 6th and 11th, the Trishadaya, are inauspicious, as is the 8th lord unless it also lords the Lagna. Lords of the 2nd and 12th are neutral in themselves. By Kendradhipatya a natural benefic lording a Kendra (4th, 7th, 10th) loses its benefic power while a natural malefic doing so turns auspicious. A planet lording both a Kendra and a Trikona is a Yoga Karaka. Where a planet holds both an auspicious and an inauspicious lordship, the Trikona lordship prevails.   [Result: Benefic / Malefic / Neutral for that Lagna, with every reason listed]"
      },
      {
        "id": "NATURE_005",
        "name": "Grouping of retrogression",
        "statement": "A retrograde graha stands near the earth and gains Cheshta Bala. Retrogression in a natural malefic is grouped favourably; in a natural benefic it is grouped as the less welcome case. The Sun and Moon never retrograde and the nodes always do, so for those four the question carries no distinction and is left neutral.   [Result: The group the retrogression bullet falls into]"
      },
      {
        "id": "NATURE_006",
        "name": "Grouping of company and aspect",
        "statement": "A conjunction with, or an aspect received from, a natural benefic is grouped favourably; from a natural malefic, as a difficulty; from a graha whose nature resolves neutral, neutrally.   [Result: The group each conjunction and aspect bullet falls into]"
      },
      {
        "id": "NATURE_007",
        "name": "The fixed catalogue of checks",
        "statement": "Every planet is put through the same catalogue of checks, so the same bullets appear for all nine grahas. A check that cannot apply to a body still produces its bullet, stating that it does not apply, and is grouped neutral.   [Result: One bullet per check for every planet]"
      },
      {
        "id": "NATURE_008",
        "name": "No aggregate verdict",
        "statement": "The findings are never combined into a score, a rating or an overall judgement of the planet. The count shown against each group is simply how many facts fall in it.   [Result: Three groups of independent facts]"
      },
      {
        "id": "NATURE_009",
        "name": "Points left to the astrologer",
        "statement": "Points the classics leave open are shown in a group of their own rather than mixed in with the neutral ones, so a genuine disagreement is never mistaken for a routine 'does not apply'. A point is placed there when the classics genuinely differ, or when two rules pull against each other, and the software will not decide for you. The situations treated as open are: the exaltation of Rahu and Ketu, which the classics do not fix; a graha holding both an auspicious and an inauspicious lordship; a natural malefic lording both a Kendra and a Maraka house; the combustion of Mercury, which is common and widely discounted; conjunction with or aspect from a node, since nodes are held to take the character of their associations; a Neecha Bhanga where only some conditions are met; and Vargottama in a debilitated graha. Each carries its reason on the Explain panel.   [Result: Its own group, with the reason shown on the Explain panel]"
      },
      {
        "id": "NATURE_010",
        "name": "The six groups a finding can fall into",
        "statement": "Findings are sorted into six groups. Strengths holds placements the classics count as favourable, and Challenges those they count as difficult. Yogas and doshas are pulled out into groups of their own so they can be read without hunting, yogas carrying the favourable colour and doshas the difficult one. Points the classics leave open form their own group. What remains is neutral or not applicable, and each of those bullets says which of the two it is.   [Result: Six groups: strengths, yogas, challenges, doshas, open points, neutral]"
      }
    ]
  },
  {
    "title": "Friendship between planets",
    "blurb": "Natural, temporary and the combined Panchadha Maitri.",
    "rules": [
      {
        "id": "MAITRI_001",
        "name": "Natural (permanent) relationship",
        "statement": "Natural friendship between two planets, read from PyJHora's const.planet_relations table. The table defines all 9 bodies including Rahu and Ketu; any undefined pair is reported as such rather than guessed.   [Result: Friend / Neutral / Enemy / Not defined in selected rule set]"
      },
      {
        "id": "MAITRI_002",
        "name": "Temporary relationship",
        "statement": "Planets occupying the 2nd, 3rd, 4th, 10th, 11th or 12th sign from a planet are its temporary friends. Planets in the 1st, 5th, 6th, 7th, 8th or 9th sign from it are its temporary enemies.   [Result: Friend / Enemy]"
      },
      {
        "id": "MAITRI_003",
        "name": "Panchadha Maitri (five-fold compound relationship)",
        "statement": "Combination of the natural and temporary relationship into the five-fold compound relationship. This is the single relationship engine used everywhere in the application.   [Result: Ati Mitra / Mitra / Sama / Shatru / Ati Shatru]"
      }
    ]
  },
  {
    "title": "Functional classification",
    "blurb": "Kendra, Trikona, Dusthana, Upachaya, Maraka, Badhaka, Yoga Karaka.",
    "rules": [
      {
        "id": "FUNC_001",
        "name": "House ownership",
        "statement": "Houses owned by a planet, from the signs it lords, counted from Lagna.   [Result: List of house numbers]"
      },
      {
        "id": "FUNC_002",
        "name": "Kendra / Trikona / Dusthana / Upachaya / Maraka house categories",
        "statement": "Standard Parashari house category sets.   [Result: Set of categories the house belongs to]"
      },
      {
        "id": "FUNC_003",
        "name": "Badhaka house and Badhakesh",
        "statement": "Badhaka house determined by the modality of the Lagna sign; the lord of that house is the Badhakesh.   [Result: Badhaka house number and its lord]"
      },
      {
        "id": "FUNC_004",
        "name": "Yoga Karaka",
        "statement": "A planet that simultaneously owns at least one Kendra house (other than the 1st alone) and at least one Trikona house.   [Result: Yes / No]"
      },
      {
        "id": "FUNC_005",
        "name": "Functional classification summary",
        "statement": "The set of lordship roles a planet holds. Presented as independent components; the application does not reduce them to a benefic/malefic verdict.   [Result: Kendra Lord, Trikona Lord, Dusthana Lord, Upachaya Lord, Maraka Lord, Badhakesh, Yoga Karaka flags]"
      },
      {
        "id": "FUNC_006",
        "name": "Sign modality",
        "statement": "Movable (Chara), Fixed (Sthira) or Dual (Dwiswabhava) sign.   [Result: Movable / Fixed / Dual]"
      },
      {
        "id": "FUNC_007",
        "name": "Sign parity",
        "statement": "Odd (Oja) or Even (Yugma) sign.   [Result: Odd / Even]"
      }
    ]
  },
  {
    "title": "Avasthas",
    "blurb": "The Kumaradi and Chaitanyadi degree bands.",
    "rules": [
      {
        "id": "CHAITANYADI_001",
        "name": "Chaitanyadi Avastha",
        "statement": "Three-fold avastha from the degree of the planet within its sign, with the order reversed for even signs.   [Result: Jagrut / Swapna / Sushupta]"
      },
      {
        "id": "KUMARADI_001",
        "name": "Kumaradi Avastha",
        "statement": "Five-fold avastha from the degree of the planet within its sign, with the order reversed for even signs.   [Result: Bala / Kumara / Yuva / Vriddha / Mrita]"
      }
    ]
  },
  {
    "title": "Aspects, conjunction and structure",
    "blurb": "Graha Drishti, same-sign conjunction, dispositor chains.",
    "rules": [
      {
        "id": "ASPECT_001",
        "name": "Graha Drishti ordinal",
        "statement": "The ordinal number of an aspect (4th, 7th, 9th ...) derived from the signs involved. Which aspects exist at all comes from PyJHora.   [Result: Aspect ordinal 1-12]"
      },
      {
        "id": "BENEFIC_001",
        "name": "Natural benefic / malefic classification",
        "statement": "Jupiter and Venus are natural benefics. Mercury is a benefic when it does not share its sign with any natural malefic. The Moon is a benefic when its elongation from the Sun lies between 72 and 288 degrees (waxing/bright). Sun, Mars, Saturn, Rahu and Ketu are natural malefics.   [Result: Benefic / Malefic with the reason recorded]"
      },
      {
        "id": "CONJ_001",
        "name": "Conjunction",
        "statement": "Two planets occupying the same Rashi in D1.   [Result: Conjunction record with degree separation]"
      },
      {
        "id": "DISPOSITOR_001",
        "name": "Dispositor chain",
        "statement": "Chain formed by repeatedly moving from a planet to the lord of the sign it occupies, terminating on a self-dispositor or a detected cycle.   [Result: Ordered chain, termination reason, cycle members]"
      }
    ]
  },
  {
    "title": "Neecha Bhanga",
    "blurb": "The six conditions under which a debilitation is held to be cancelled.",
    "rules": [
      {
        "id": "NB_001",
        "name": "Debilitation-sign lord in Kendra from Lagna",
        "statement": "The lord of the sign in which the planet is debilitated occupies a Kendra (1, 4, 7, 10) counted from the Lagna.   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_002",
        "name": "Debilitation-sign lord in Kendra from Moon",
        "statement": "The lord of the sign in which the planet is debilitated occupies a Kendra counted from the Moon.   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_003",
        "name": "Exaltation-sign lord in Kendra from Lagna",
        "statement": "The lord of the sign in which the planet would be exalted occupies a Kendra counted from the Lagna.   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_004",
        "name": "Exaltation-sign lord in Kendra from Moon",
        "statement": "The lord of the sign in which the planet would be exalted occupies a Kendra counted from the Moon.   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_005",
        "name": "Association with a cancellation lord",
        "statement": "The debilitated planet is conjunct with, or in mutual Graha Drishti with, the lord of its debilitation sign or the lord of its exaltation sign.   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_006",
        "name": "Debilitation lord and exaltation lord in mutual Kendras",
        "statement": "The lord of the debilitation sign and the lord of the exaltation sign occupy Kendras from each other (1, 4, 7 or 10 signs apart).   [Result: Satisfied / Not satisfied, with the participating planets recorded]"
      },
      {
        "id": "NB_100",
        "name": "Neecha Bhanga (cancellation) summary",
        "statement": "Count of satisfied conditions NB_001..NB_006. Reported as a count and a per-condition breakdown. Retrograde motion is deliberately NOT used as a cancellation condition in V1.   [Result: Integer count plus the individual condition results]"
      }
    ]
  },
  {
    "title": "Rahu and Ketu",
    "blurb": "Every point where the nodes are treated differently from the seven.",
    "rules": [
      {
        "id": "RK_001",
        "name": "Rahu and Ketu hold no sign lordship",
        "statement": "The twelve signs are lorded by the Sun through Saturn only. Rahu and Ketu own no sign, therefore they own no house and hold no functional classification derived from house ownership: not Kendra lord, Trikona lord, Dusthana lord, Upachaya lord, Maraka lord, Badhakesh or Yoga Karaka. A tradition assigning Rahu co-lordship of Aquarius and Ketu co-lordship of Scorpio exists and is recorded in PyJHora, but it is not part of the Parashari lordship scheme used here and is not applied.   [Result: Houses owned: empty. Lordship roles: all No.]"
      },
      {
        "id": "RK_002",
        "name": "Rahu and Ketu have no Mooltrikona",
        "statement": "BPHS assigns Mooltrikona signs and degree ranges to the seven grahas only.   [Result: Not defined in selected rule set.]"
      },
      {
        "id": "RK_003",
        "name": "Rahu and Ketu have no Swarashi",
        "statement": "Own-sign status follows from lordship, which the nodes do not hold (RK_001).   [Result: Not defined in selected rule set.]"
      },
      {
        "id": "RK_004",
        "name": "Rahu and Ketu exaltation and debilitation",
        "statement": "BPHS does not place Rahu and Ketu in the main exaltation table. The rule set applied here takes Rahu as exalted in Taurus and Gemini and debilitated in Scorpio and Sagittarius, with Ketu the reverse. Other well-attested traditions give Rahu exaltation in Taurus alone, or in Gemini alone, with Ketu correspondingly in Scorpio or Sagittarius. The value is labelled with its source wherever it is shown, and no deep-exaltation degree is claimed.   [Result: Exaltation and debilitation signs, labelled with their source.]"
      },
      {
        "id": "RK_005",
        "name": "Rahu and Ketu Graha Drishti",
        "statement": "The nodes cast the 7th Graha Drishti only in the rule set applied here. Traditions giving them the 5th and 9th aspects as well are not applied. They receive Graha Drishti from other planets normally.   [Result: 7th aspect only, with the restriction stated.]"
      },
      {
        "id": "RK_006",
        "name": "Rahu and Ketu natural relationships",
        "statement": "BPHS derives natural friendship from a graha's Mooltrikona and exaltation signs, a derivation the nodes cannot enter since they have neither in the classical scheme. The relationship table applied here does define all nine bodies, so Panchadha Maitri is computed for the nodes and labelled with its source. Temporary relationship is purely positional and applies to them without qualification.   [Result: Natural, temporary and Panchadha Maitri, source-labelled.]"
      },
      {
        "id": "RK_007",
        "name": "Rahu and Ketu are outside Shadbala",
        "statement": "The six-fold strength framework is defined for the Sun through Saturn. No Shadbala component is calculated for the nodes.   [Result: Not available.]"
      },
      {
        "id": "RK_008",
        "name": "Rahu and Ketu are outside combustion",
        "statement": "Combustion applies to the Moon through Saturn. The nodes are shadow points with no disc to be eclipsed by the Sun's proximity.   [Result: Not applicable.]"
      },
      {
        "id": "RK_009",
        "name": "Rahu and Ketu are outside Graha Yuddha",
        "statement": "Planetary war is fought between the five star planets, Mars, Mercury, Jupiter, Venus and Saturn. The luminaries and the nodes are excluded.   [Result: Not applicable.]"
      },
      {
        "id": "RK_010",
        "name": "Rahu and Ketu are always retrograde as mean nodes",
        "statement": "With the mean-node calculation used here the nodes move uniformly backwards, so they are reported retrograde in every chart. True-node calculations can show them stationary or briefly direct.   [Result: Retrograde, with the node type stated.]"
      },
      {
        "id": "RK_011",
        "name": "Rahu and Ketu never act as dispositors",
        "statement": "A dispositor is the lord of the occupied sign. Since the nodes lord no sign (RK_001), they can appear in a dispositor chain as a member but never as the lord that the chain steps to.   [Result: May start or appear in a chain; never terminate one as a self-dispositor.]"
      },
      {
        "id": "RK_012",
        "name": "Avastha applicability to Rahu and Ketu",
        "statement": "Kumaradi and Chaitanyadi Avastha are stated as degree bands by sign parity without an explicit restriction on the bodies they cover, while the classical descriptions address the seven grahas. The value is computed for the nodes by the same band rule and carries a note recording that the classical scope is the seven grahas.   [Result: Computed, with an applicability note attached.]"
      },
      {
        "id": "RK_013",
        "name": "Rahu and Ketu are always in opposition",
        "statement": "The nodes are the two intersections of the lunar orbit with the ecliptic and are therefore exactly 180 degrees apart, occupying signs seven apart. They are never conjunct with each other.   [Result: Ketu longitude equals Rahu longitude plus 180 degrees.]"
      },
      {
        "id": "RK_014",
        "name": "Rahu and Ketu as natural malefics",
        "statement": "Both nodes are classified natural malefics under rule BENEFIC_001, so neither can satisfy a benefic-association condition in any yoga, and either occupying a sign with Mercury renders Mercury malefic.   [Result: Malefic.]"
      }
    ]
  },
  {
    "title": "Yogas",
    "blurb": "The 22 yogas checked.",
    "rules": [
      {
        "id": "YOGA_001",
        "name": "Raja Yoga",
        "statement": "A Kendra lord and a Trikona lord associate by conjunction, mutual Graha Drishti, or sign exchange (Parivartana). The Lagna lord qualifies as both, since the 1st house is a Kendra and a Trikona.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_002",
        "name": "Dharma-Karmadhipati Yoga",
        "statement": "The 9th lord and the 10th lord associate by conjunction, mutual Graha Drishti, or sign exchange.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_003",
        "name": "Ruchaka Yoga",
        "statement": "Mars occupies Aries, Scorpio or Capricorn AND occupies a Kendra (1, 4, 7, 10) from the Lagna.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_004",
        "name": "Bhadra Yoga",
        "statement": "Mercury occupies Gemini or Virgo AND occupies a Kendra from the Lagna.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_005",
        "name": "Hamsa Yoga",
        "statement": "Jupiter occupies Sagittarius, Pisces or Cancer AND occupies a Kendra from the Lagna.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_006",
        "name": "Malavya Yoga",
        "statement": "Venus occupies Taurus, Libra or Pisces AND occupies a Kendra from the Lagna.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_007",
        "name": "Sasa Yoga",
        "statement": "Saturn occupies Capricorn, Aquarius or Libra AND occupies a Kendra from the Lagna.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_008",
        "name": "Gaja Kesari Yoga",
        "statement": "Core formation: Jupiter occupies a Kendra (1, 4, 7, 10) from the Lagna or from the Moon. A Moon-Jupiter conjunction is the 1st from the Moon and therefore forms it. Four strengthening conditions are evaluated and reported separately and do not affect the formation status: Jupiter conjunct with or in mutual Graha Drishti with a natural benefic; Jupiter not debilitated; Jupiter not combust; Jupiter not in an enemy's sign. Classical sources differ on whether these govern the formation of the yoga or only the extent of its results, so the two sets are kept distinct rather than merged into one verdict.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_009",
        "name": "Budha-Aditya Yoga",
        "statement": "The Sun and Mercury occupy the same Rashi. Mercury's combustion is reported as a separate independent fact and does not negate the formation.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_010",
        "name": "Chandra-Mangala Yoga",
        "statement": "The Moon and Mars occupy the same Rashi. Mutual-aspect variants are not part of V1.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_011",
        "name": "Guru-Mangala Yoga",
        "statement": "Jupiter and Mars occupy the same Rashi.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_012",
        "name": "Adhi Yoga",
        "statement": "Natural benefics (BENEFIC_001) occupy the 6th, 7th and/or 8th signs counted from the Moon. Formation requires at least one such benefic; the occupancy of each of the three positions is reported individually.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_013",
        "name": "Amala Yoga",
        "statement": "A natural benefic (BENEFIC_001) occupies the 10th sign counted from the Lagna or the 10th sign counted from the Moon.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_014",
        "name": "Harsha Yoga",
        "statement": "The lord of the 6th house occupies the 6th, 8th or 12th house.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_015",
        "name": "Sarala Yoga",
        "statement": "The lord of the 8th house occupies the 6th, 8th or 12th house.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_016",
        "name": "Vimala Yoga",
        "statement": "The lord of the 12th house occupies the 6th, 8th or 12th house.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_017",
        "name": "Dhana Yoga",
        "statement": "Two or more of the lords of the 2nd, 5th, 9th and 11th houses associate by conjunction, mutual Graha Drishti or sign exchange, and at least one participant is the 2nd lord or the 11th lord.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_018",
        "name": "Lakshmi Yoga",
        "statement": "The Lagna lord occupies a Kendra or Trikona house, and the 9th lord occupies its own sign, its Mooltrikona sign, or its exaltation sign while placed in a Kendra or Trikona house. Each condition is reported individually.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_019",
        "name": "Saraswati Yoga",
        "statement": "Jupiter, Venus and Mercury each occupy the 2nd house, a Kendra (1, 4, 7, 10) or a Trikona (1, 5, 9) from the Lagna, and Jupiter additionally occupies its own sign, its Mooltrikona sign, its exaltation sign or a friend's sign.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_020",
        "name": "Kemadruma Yoga",
        "statement": "No planet other than the Sun, Rahu and Ketu occupies the 2nd or the 12th sign counted from the Moon. The exclusion of the Sun and the nodes is the conventional formulation used consistently here.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_021",
        "name": "Parivartana Yoga",
        "statement": "Planet A occupies a sign owned by planet B while planet B occupies a sign owned by planet A. Maha/Khala/Dainya subclassification is not part of V1.   [Result: Present / Not Present with participants and per-condition evidence]"
      },
      {
        "id": "YOGA_022",
        "name": "Neecha Bhanga Raja Yoga",
        "statement": "A debilitated planet whose Neecha Bhanga condition count (NB_100) is at least one, AND which either owns or occupies a Kendra or Trikona house. Debilitation, Neecha Bhanga and Neecha Bhanga Raja Yoga are kept as three distinct states.   [Result: Present / Not Present with participants and per-condition evidence]"
      }
    ]
  },
  {
    "title": "Doshas",
    "blurb": "The 14 doshas checked.",
    "rules": [
      {
        "id": "DOSHA_001",
        "name": "Mangal Dosha (Kuja Dosha)",
        "statement": "Mars occupies the 1st, 2nd, 4th, 7th, 8th or 12th house, counted from the Lagna, the Moon or Venus.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_002",
        "name": "Kaal Sarpa Dosha",
        "statement": "All seven grahas from the Sun to Saturn lie within the arc running from Rahu to Ketu.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_003",
        "name": "Guru Chandal Dosha",
        "statement": "Jupiter shares its sign with Rahu or Ketu.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_004",
        "name": "Angarak Dosha",
        "statement": "Mars shares its sign with Rahu or Ketu.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_005",
        "name": "Grahan Dosha",
        "statement": "The Sun or the Moon shares its sign with Rahu or Ketu.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_006",
        "name": "Shrapit Dosha",
        "statement": "Saturn shares its sign with Rahu.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_007",
        "name": "Vish Dosha (Punarphoo)",
        "statement": "The Moon shares its sign with Saturn.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_008",
        "name": "Kemadruma Dosha",
        "statement": "No graha other than the Sun and the nodes occupies the 2nd or the 12th sign from the Moon.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_009",
        "name": "Sakata Dosha",
        "statement": "The Moon occupies the 6th, 8th or 12th sign counted from Jupiter.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_010",
        "name": "Papakartari Dosha",
        "statement": "A graha stands hemmed, with a natural malefic in both the 2nd and the 12th sign from it.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_011",
        "name": "Kendradhipatya Dosha",
        "statement": "A natural benefic lords a Kendra, the 4th, 7th or 10th house.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_012",
        "name": "Daridra Dosha",
        "statement": "The lord of the 11th house occupies the 6th, 8th or 12th house.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_013",
        "name": "Amavasya Dosha",
        "statement": "The Sun and the Moon stand within 12 degrees of each other, the birth falling close to the new moon.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_014",
        "name": "Pitru Dosha",
        "statement": "Rahu or Ketu occupies the 9th house, or the lord of the 9th occupies the 6th, 8th or 12th.   [Result: Present / Not present, with the participating grahas, the evidence, and any classical grounds for cancellation]"
      },
      {
        "id": "DOSHA_100",
        "name": "How doshas are reported",
        "statement": "Only doshas that actually form, and that the selected planet takes part in, are listed on that planet's page. Kemadruma is reported here rather than with the yogas, being an affliction by nature. Grounds on which the classics hold a dosha to be lifted are shown with it, but are never applied automatically: whether a cancellation carries is left to the astrologer.   [Result: The doshas involving that planet]"
      }
    ]
  }
];

function buildReviewForm() {
  var form = FormApp.create(FORM_TITLE)
      .setDescription(FORM_DESCRIPTION)
      .setProgressBar(true)
      .setAllowResponseEdits(true)
      .setShowLinkToRespondAgain(false);

  form.addTextItem()
      .setTitle('Your name')
      .setHelpText('So a follow-up question can reach the right person.')
      .setRequired(true);

  form.addParagraphTextItem()
      .setTitle('Which tradition or lineage do you follow?')
      .setHelpText('Useful context where the classics differ. Optional.')
      .setRequired(false);

  var total = 0;
  for (var s = 0; s < SECTIONS.length; s++) {
    var section = SECTIONS[s];

    form.addPageBreakItem()
        .setTitle(section.title)
        .setHelpText(section.blurb + '  (' + section.rules.length +
                     (section.rules.length === 1 ? ' rule)' : ' rules)'));

    for (var r = 0; r < section.rules.length; r++) {
      var rule = section.rules[r];
      total++;

      form.addMultipleChoiceItem()
          .setTitle(rule.id + ' - ' + rule.name)
          .setHelpText(rule.statement)
          .setChoiceValues(VERDICTS)
          .setRequired(true);

      form.addParagraphTextItem()
          .setTitle(rule.id + ' - what should change?')
          .setHelpText('Only if you marked it above. A source or citation helps.')
          .setRequired(false);
    }
  }

  form.addPageBreakItem()
      .setTitle('Anything else')
      .setHelpText('Rules that are missing, or anything the form did not ask.');

  form.addParagraphTextItem()
      .setTitle('Rules you would add or remove')
      .setRequired(false);

  form.addParagraphTextItem()
      .setTitle('Any other comment')
      .setRequired(false);

  var sheet = SpreadsheetApp.create(FORM_TITLE + ' - responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  Logger.log('Rules in the form : ' + total);
  Logger.log('Edit the form     : ' + form.getEditUrl());
  Logger.log('Send this link    : ' + form.getPublishedUrl());
  Logger.log('Responses sheet   : ' + sheet.getUrl());
  return form.getPublishedUrl();
}
