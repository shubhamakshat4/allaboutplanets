# Rules Used by the Planetary Status Analyzer

A plain list of every rule this software applies, written so that an astrologer can read it and check it.

The application only calculates and organises. It never interprets, predicts, or judges a planet as good or bad. So the only thing that needs checking is whether these rules are stated correctly.

**How to use this document.** Read each rule. If one does not match what you follow, say so and it can be changed. The tag in brackets, for example `[DIGNITY_002]`, is the reference number for that rule — quote it when reporting a correction.

**Framework:** Parashari. Where *Brihat Parashara Hora Shastra* settles a value, that value is used. Where the classics differ, the disagreement is recorded in section 17 rather than being decided quietly.

---

## 1. What the software calculates from

| Setting | Value |
|---|---|
| Zodiac | Sidereal (Nirayana) |
| Ayanamsha | Lahiri by default; any of 21 may be chosen, and the one used is shown on every chart |
| Ephemeris | Swiss Ephemeris |
| Houses used for all rules | Whole sign (Rashi) counted from the Lagna sign |
| Bhava Chalita | Shown separately as information. No rule uses it. |
| Rahu and Ketu | Mean nodes |
| Birth time | Converted using the timezone in force at the place on the date of birth, so old daylight-saving rules are applied correctly |

The house frame matters. Every rule in this document — lordship, kendra and trikona, the yogas, Neecha Bhanga — counts houses as whole signs from the Lagna sign. `[HOUSE_001]`

---

## 2. The signs and their lords

| No. | Rashi | Sanskrit | Lord | Movable / Fixed / Dual | Odd or Even |
|---|---|---|---|---|---|
| 1 | Aries | Mesha | Mars | Movable | Odd |
| 2 | Taurus | Vrishabha | Venus | Fixed | Even |
| 3 | Gemini | Mithuna | Mercury | Dual | Odd |
| 4 | Cancer | Karka | Moon | Movable | Even |
| 5 | Leo | Simha | Sun | Fixed | Odd |
| 6 | Virgo | Kanya | Mercury | Dual | Even |
| 7 | Libra | Tula | Venus | Movable | Odd |
| 8 | Scorpio | Vrischika | Mars | Fixed | Even |
| 9 | Sagittarius | Dhanu | Jupiter | Dual | Odd |
| 10 | Capricorn | Makara | Saturn | Movable | Even |
| 11 | Aquarius | Kumbha | Saturn | Fixed | Odd |
| 12 | Pisces | Meena | Jupiter | Dual | Even |

Rahu and Ketu lord no sign. `[RK_001]`

---

## 3. Exaltation, debilitation, own sign and Mooltrikona

| Graha | Own sign(s) | Exalted at | Debilitated at | Mooltrikona |
|---|---|---|---|---|
| Sun | Leo | Aries 10° | Libra 10° | Leo 0°–20° |
| Moon | Cancer | Taurus 3° | Scorpio 3° | Taurus 4°–30° |
| Mars | Aries, Scorpio | Capricorn 28° | Cancer 28° | Aries 0°–12° |
| Mercury | Gemini, Virgo | Virgo 15° | Pisces 15° | Virgo 16°–20° |
| Jupiter | Sagittarius, Pisces | Cancer 5° | Capricorn 5° | Sagittarius 0°–10° |
| Venus | Taurus, Libra | Pisces 27° | Virgo 27° | Libra 0°–15° |
| Saturn | Capricorn, Aquarius | Libra 20° | Aries 20° | Aquarius 0°–20° |

The exaltation degree given is the deep exaltation point; the whole sign counts as the exaltation sign. `[DIGNITY_001]`

Mooltrikona ranges follow *Brihat Parashara Hora Shastra*, chapter 3. For the Moon and Mercury the Mooltrikona portion begins at the degree after the exaltation point — Taurus 4° and Virgo 16°. `[DIGNITY_002]`

A planet is reported as being in its Mooltrikona only when it is in the right sign **and** within the degrees shown.

Mercury in Virgo is both exalted and in its own sign. Both facts are reported; neither is suppressed.

Rahu and Ketu have no own sign and no Mooltrikona. `[RK_002]` `[RK_003]`

---

## 4. The houses

| Group | Houses |
|---|---|
| Kendra | 1, 4, 7, 10 |
| Trikona | 1, 5, 9 |
| Dusthana | 6, 8, 12 |
| Upachaya | 3, 6, 10, 11 |
| Maraka | 2, 7 |

The 1st house belongs to both Kendra and Trikona. `[FUNC_002]`

**Badhaka house**, decided by the Lagna sign: `[FUNC_003]`

| Lagna type | Badhaka house | Lagna signs |
|---|---|---|
| Movable | 11th | Aries, Cancer, Libra, Capricorn |
| Fixed | 9th | Taurus, Leo, Scorpio, Aquarius |
| Dual | 7th | Gemini, Virgo, Sagittarius, Pisces |

**Yoga Karaka.** A planet that lords a Kendra among the 4th, 7th or 10th **and** a Trikona among the 5th or 9th. Owning only the 1st house does not by itself make a planet a Yoga Karaka. `[FUNC_004]`

The software lists each house a planet owns and the group each house belongs to. It does not reduce this to a single verdict about the planet. `[FUNC_005]`

---

## 5. Benefic, malefic and neutral

Three separate questions, kept apart because the classics keep them apart. A graha can be a natural benefic and a functional malefic at the same time, and both are reported.

### What each graha is by nature `[NATURE_001]`

| Graha | Nature | Condition |
|---|---|---|
| Jupiter, Venus | Benefic | Always |
| Mars, Saturn, Rahu, Ketu | Malefic | Always |
| Sun | Malefic | Counted among the cruel grahas, a mild malefic |
| Moon | Benefic or Malefic | Benefic while bright, taken as 72°–288° from the Sun; malefic while dark |
| Mercury | Takes its company | Benefic with benefics, malefic with malefics, neutral when alone or when its sign holds both |

### What each house is by nature `[NATURE_002]`

| Houses | Counted as |
|---|---|
| 1, 2, 4, 5, 7, 9, 10, 11 | Auspicious |
| 6, 8, 12 | Difficult — the Dusthanas |
| 3 | Mixed — an Upachaya, but mildly difficult |

A natural malefic placed in an Upachaya house (3rd, 6th, 10th, 11th) is not counted a difficulty, since malefics are held to grow strong there. This is why a malefic in the 6th is treated differently from a malefic in the 8th or 12th. `[NATURE_003]`

### What a graha becomes for one Lagna `[NATURE_004]`

Decided by the houses it lords:

| Lords | Becomes |
|---|---|
| The 1st | Auspicious — the 1st is both Kendra and Trikona |
| The 5th or 9th | Auspicious — the Trikonas |
| The 3rd, 6th or 11th | Inauspicious — the Trishadaya |
| The 8th | Inauspicious, unless it also lords the Lagna |
| The 2nd or 12th | Neutral in itself |
| A Kendra (4th, 7th, 10th) | Kendradhipatya: a natural benefic loses its benefic power, a natural malefic turns auspicious |
| Both a Kendra and a Trikona | Yoga Karaka |

Where a graha holds both an auspicious and an inauspicious lordship, the Trikona lordship is taken to prevail.

This is why, for a Libra Lagna, Saturn lords the 4th and 5th and is the Yoga Karaka, while Jupiter lords the 3rd and 6th and is a functional malefic despite being the greatest natural benefic.

### Retrogression `[NATURE_005]`

| Case | Grouped as |
|---|---|
| A natural malefic, retrograde | Favourable |
| A natural benefic, retrograde | A difficulty |
| A natural benefic, direct | Favourable |
| A natural malefic, direct | Neutral |
| Sun or Moon | Does not apply — neither ever retrogrades |
| Rahu or Ketu | No distinction — they are always retrograde |

A retrograde graha stands near the earth and gains Cheshta Bala. The formulation followed here treats that gain as welcome in a malefic and unwelcome in a benefic.

### Company and aspect `[NATURE_006]`

A conjunction with, or an aspect received from, a natural benefic is grouped favourably; from a natural malefic, as a difficulty.

### How the groups are filled `[NATURE_007]` `[NATURE_008]` `[NATURE_009]` `[NATURE_010]`

Every graha is put through the same list of checks, so the same points appear for all nine. A check that cannot apply to a body still appears, saying so.

The findings are sorted into six groups:

| Group | Holds |
|---|---|
| Strengths | Placements the classics count as favourable |
| Yogas formed | Yogas this graha takes part in |
| Challenges | Placements the classics count as difficult |
| Doshas formed | Doshas this graha takes part in |
| Your call | Points the classics leave open. Kept apart from the neutral ones so a real disagreement is never mistaken for a routine 'does not apply'. The reason is given on the Explain panel. |
| Neutral & not applicable | Checks that came out on neither side, and checks that cannot bear on this graha at all. Each bullet says which of the two it is. |

The findings are never added up into a score or an overall judgement of the planet. The number beside each group is simply how many points fall in it.

These are the situations placed in **Your call**:

| Situation | Why it is left open |
|---|---|
| Node Dignity | The classics do not place Rahu and Ketu in the exaltation table. The sign used here is one tradition among several: some give Rahu exaltation in Taurus alone, others in Gemini, with Ketu placed correspondingly. Whether to read this as a strength is yours to decide. |
| Mixed Lordship | This graha holds lordships that pull in opposite directions. The rule followed here lets the Trikona lordship prevail, but many astrologers weigh the difficult lordship more heavily, and the Kendradhipatya treatment of a Kendra lord is itself read differently by different schools. |
| Maraka And Kendra | This graha lords a Kendra, which turns a natural malefic auspicious by Kendradhipatya, and also a Maraka house. The two pull against each other and the classics do not settle which prevails. |
| Mercury Combustion | Mercury never travels far from the Sun and is combust in a great many charts. Many astrologers hold Mercury's combustion to be far less telling than that of the other grahas, especially where Budha-Aditya is formed. |
| Node Association | Rahu and Ketu are widely held to take on the character of the graha they join, of their dispositor, or of the house they occupy. Reading an association with a node purely as a difficulty is only one view. |
| Partial Neecha Bhanga | Some of the cancelling conditions are met and some are not. How far a partial Neecha Bhanga lifts the debilitation is one of the most argued points in the classics, and the count alone does not settle it. |
| Vargottama Debilitated | The graha is Vargottama while debilitated. One reading is that Vargottama steadies it; another is that holding the same sign in both charts deepens the debilitation. |
| Retrograde School | Schools differ on retrogression. Some hold that a retrograde graha is simply strengthened, some that it gives the results of the previous sign, and some that it acts contrary to its usual nature. |

---

## 6. Friendship between planets

### Natural friendship (Naisargika Maitri)

Fixed for all charts. `[MAITRI_001]`

| Planet sees → | Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn | Rahu | Ketu |
|---|---|---|---|---|---|---|---|---|---|
| **Sun** | — | Friend | Friend | Neutral | Friend | Enemy | Enemy | Enemy | Neutral |
| **Moon** | Friend | — | Neutral | Friend | Neutral | Neutral | Neutral | Neutral | Neutral |
| **Mars** | Friend | Friend | — | Enemy | Friend | Neutral | Neutral | Neutral | Neutral |
| **Mercury** | Friend | Enemy | Neutral | — | Neutral | Friend | Neutral | Neutral | Enemy |
| **Jupiter** | Friend | Friend | Friend | Enemy | — | Enemy | Neutral | Enemy | Neutral |
| **Venus** | Enemy | Enemy | Neutral | Friend | Neutral | — | Friend | Friend | Neutral |
| **Saturn** | Enemy | Enemy | Enemy | Friend | Neutral | Friend | — | Friend | Enemy |
| **Rahu** | Enemy | Enemy | Enemy | Neutral | Neutral | Friend | Friend | — | Neutral |
| **Ketu** | Friend | Neutral | Friend | Neutral | Neutral | Enemy | Enemy | Neutral | — |

Read each row as *how that planet regards the others*. The table is not symmetrical, which is correct: Mercury regards the Sun as a friend, while the Sun regards Mercury as neutral.

The seven-graha portion matches *Brihat Parashara Hora Shastra*. The Rahu and Ketu rows do not come from that text — see sections 16 and 17. `[RK_006]`

### Temporary friendship (Tatkalika Maitri)

Decided by position in the chart being read. `[MAITRI_002]`

| Counted from the planet | Result |
|---|---|
| 2nd, 3rd, 4th, 10th, 11th, 12th | Temporary friend |
| 1st, 5th, 6th, 7th, 8th, 9th | Temporary enemy |

A planet in the same sign is in the 1st from the other, and so is a temporary enemy.

### Combined friendship (Panchadha Maitri)

Natural and temporary are combined into the five-fold result. `[MAITRI_003]`

| Natural | Temporary | Result |
|---|---|---|
| Friend | Friend | **Ati Mitra** |
| Friend | Enemy | **Sama** |
| Neutral | Friend | **Mitra** |
| Neutral | Enemy | **Shatru** |
| Enemy | Friend | **Sama** |
| Enemy | Enemy | **Ati Shatru** |

This one calculation is used everywhere the software shows a relationship — with the sign lord, the nakshatra lord, the navamsha lord, the Lagna lord, a conjunct planet, an aspecting planet, and each yoga participant. There is no second method anywhere in the software.

---

## 7. Aspects (Graha Drishti)

| Graha | Aspects |
|---|---|
| Sun | 7th |
| Moon | 7th |
| Mars | 4th, 7th, 8th |
| Mercury | 7th |
| Jupiter | 5th, 7th, 9th |
| Venus | 7th |
| Saturn | 3rd, 7th, 10th |
| Rahu | 7th |
| Ketu | 7th |

Counted in whole signs from the sign the planet occupies. `[ASPECT_001]`

Rahu and Ketu are given the 7th aspect only. Traditions that also give them the 5th and 9th are not applied. `[RK_005]`

For every aspect the software shows the aspecting planet, the aspect number, both houses, and the Panchadha Maitri between the two.

---

## 8. Conjunction, retrogression, combustion, planetary war

**Conjunction.** Two planets in the same Rashi. The degree gap between them is shown, measured the short way round the zodiac. `[CONJ_001]`

**Retrogression.** Taken from the planet's actual motion. The Sun and Moon never retrograde. As mean nodes, Rahu and Ketu are always retrograde. `[RK_010]`

**Combustion (Asta).** A planet within this distance of the Sun is combust. `[COMBUST_001]`

| Graha | In direct motion | When retrograde |
|---|---|---|
| Moon | 12° | 12° |
| Mars | 17° | 17° |
| Mercury | 14° | 12° |
| Jupiter | 11° | 11° |
| Venus | 10° | 8° |
| Saturn | 15° | 15° |

The distance is measured the short way round, so a planet in late Pisces close to a Sun in early Aries is correctly found combust. The Sun itself is the reference point, and Rahu and Ketu are outside the rule. `[RK_008]`

**Planetary war (Graha Yuddha).** Fought only between Mars, Mercury, Jupiter, Venus and Saturn. The luminaries and the nodes are excluded. `[RK_009]`

---

## 9. Avasthas

Two Avastha systems are calculated, both from the planet's degree within its sign, with the order reversed in even signs.

### Kumaradi (Baladi) Avastha `[KUMARADI_001]`

| Degree in sign | Odd sign | Even sign |
|---|---|---|
| 0° to 6° | Bala | Mrita |
| 6° to 12° | Kumara | Vriddha |
| 12° to 18° | Yuva | Yuva |
| 18° to 24° | Vriddha | Kumara |
| 24° to 30° | Mrita | Bala |

### Chaitanyadi Avastha `[CHAITANYADI_001]`

| Degree in sign | Odd sign | Even sign |
|---|---|---|
| 0° to 10° | Jagrut | Sushupta |
| 10° to 20° | Swapna | Swapna |
| 20° to 30° | Sushupta | Jagrut |

A planet exactly on a boundary takes the later band. A planet at exactly 6° in an odd sign is Kumara, not Bala.

Odd signs are Aries, Gemini, Leo, Libra, Sagittarius and Aquarius. Even signs are the rest.

These are the only two Avastha systems calculated. `[RK_012]` records that the classical descriptions address the seven grahas; the value is still shown for Rahu and Ketu with a note attached.

---

## 10. Nakshatras

The 27 nakshatras and their lords, in the Vimshottari order, repeating every nine. `[NAK_001]`

| No. | Nakshatra | Lord | No. | Nakshatra | Lord | No. | Nakshatra | Lord |
|---|---|---|---|---|---|---|---|---|
| 1 | Ashwini | Ketu | 10 | Magha | Ketu | 19 | Mula | Ketu |
| 2 | Bharani | Venus | 11 | Purva Phalguni | Venus | 20 | Purva Ashadha | Venus |
| 3 | Krittika | Sun | 12 | Uttara Phalguni | Sun | 21 | Uttara Ashadha | Sun |
| 4 | Rohini | Moon | 13 | Hasta | Moon | 22 | Shravana | Moon |
| 5 | Mrigashira | Mars | 14 | Chitra | Mars | 23 | Dhanishta | Mars |
| 6 | Ardra | Rahu | 15 | Swati | Rahu | 24 | Shatabhisha | Rahu |
| 7 | Punarvasu | Jupiter | 16 | Vishakha | Jupiter | 25 | Purva Bhadrapada | Jupiter |
| 8 | Pushya | Saturn | 17 | Anuradha | Saturn | 26 | Uttara Bhadrapada | Saturn |
| 9 | Ashlesha | Mercury | 18 | Jyeshtha | Mercury | 27 | Revati | Mercury |

Each nakshatra is divided into four padas of 3°20′ each.

---

## 11. Navamsha and Vargottama

A planet in the same sign in the Rashi chart and the Navamsha is **Vargottama**. `[VARGA_001]`

Divisional charts calculated: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45 and D60. For each, the software shows the sign, its lord, and the planet's dignity in that sign.

---

## 12. Dispositor chain

A planet is followed to the lord of the sign it occupies, then that lord to the lord of *its* sign, and so on. `[DISPOSITOR_001]`

The chain stops when a planet is in its own sign, or when a planet already seen appears again, in which case the loop is reported as a cycle.

Rahu and Ketu can appear in a chain but never act as a dispositor, since they lord no sign. `[RK_011]`

---

## 13. Neecha Bhanga

Evaluated only for a planet that is actually debilitated. Six conditions are checked, and each is reported separately with the planets involved. They are never merged into a single answer.

| No. | Condition | Tag |
|---|---|---|
| 1 | Debilitation-sign lord in Kendra from Lagna | `[NB_001]` |
| 2 | Debilitation-sign lord in Kendra from Moon | `[NB_002]` |
| 3 | Exaltation-sign lord in Kendra from Lagna | `[NB_003]` |
| 4 | Exaltation-sign lord in Kendra from Moon | `[NB_004]` |
| 5 | Association with a cancellation lord | `[NB_005]` |
| 6 | Debilitation lord and exaltation lord in mutual Kendras | `[NB_006]` |

Kendra means the 1st, 4th, 7th or 10th counted from the reference point.

**Retrogression of the debilitated planet is not used as a cancellation condition.**

Three states are kept separate and never confused with one another:

1. The planet is debilitated.
2. One or more cancellation conditions are met.
3. Neecha Bhanga Raja Yoga, which additionally requires the planet to own or occupy a Kendra or Trikona. `[YOGA_022]`

---

## 14. The yogas checked

Twenty-two yogas are examined. For each one the software shows every condition separately, whether it is met, and which planets take part.

| No. | Yoga | How it is formed | Tag |
|---|---|---|---|
| 1 | Raja Yoga | Kendra lord and Trikona lord associate by conjunction, mutual Graha Drishti or sign exchange. | `[YOGA_001]` |
| 2 | Dharma-Karmadhipati Yoga | 9th lord and 10th lord associate by conjunction, mutual Graha Drishti or sign exchange. | `[YOGA_002]` |
| 3 | Ruchaka Yoga | Mars in Aries, Scorpio or Capricorn and in a Kendra from Lagna. | `[YOGA_003]` |
| 4 | Bhadra Yoga | Mercury in Gemini or Virgo and in a Kendra from Lagna. | `[YOGA_004]` |
| 5 | Hamsa Yoga | Jupiter in Sagittarius, Pisces or Cancer and in a Kendra from Lagna. | `[YOGA_005]` |
| 6 | Malavya Yoga | Venus in Taurus, Libra or Pisces and in a Kendra from Lagna. | `[YOGA_006]` |
| 7 | Sasa Yoga | Saturn in Capricorn, Aquarius or Libra and in a Kendra from Lagna. | `[YOGA_007]` |
| 8 | Gaja Kesari Yoga | Jupiter in a Kendra from Lagna or Moon, with a qualifying benefic association, not debilitated, not combust, not in an enemy sign. | `[YOGA_008]` |
| 9 | Budha-Aditya Yoga | Sun and Mercury in the same Rashi. | `[YOGA_009]` |
| 10 | Chandra-Mangala Yoga | Moon and Mars in the same Rashi. | `[YOGA_010]` |
| 11 | Guru-Mangala Yoga | Jupiter and Mars in the same Rashi. | `[YOGA_011]` |
| 12 | Adhi Yoga | Natural benefics occupy the 6th, 7th and/or 8th from the Moon. | `[YOGA_012]` |
| 13 | Amala Yoga | A natural benefic occupies the 10th from Lagna or the 10th from the Moon. | `[YOGA_013]` |
| 14 | Harsha Yoga | The 6th lord occupies the 6th, 8th or 12th house. | `[YOGA_014]` |
| 15 | Sarala Yoga | The 8th lord occupies the 6th, 8th or 12th house. | `[YOGA_015]` |
| 16 | Vimala Yoga | The 12th lord occupies the 6th, 8th or 12th house. | `[YOGA_016]` |
| 17 | Dhana Yoga | Lords of the 2nd, 5th, 9th and 11th associate, with the 2nd or 11th lord among the participants. | `[YOGA_017]` |
| 18 | Lakshmi Yoga | Lagna lord in a Kendra or Trikona, and the 9th lord in own, Mooltrikona or exaltation sign while in a Kendra or Trikona. | `[YOGA_018]` |
| 19 | Saraswati Yoga | Jupiter, Venus and Mercury each in the 2nd, a Kendra or a Trikona, with Jupiter additionally in own, Mooltrikona, exaltation or friend's sign. | `[YOGA_019]` |
| 20 | Kemadruma Yoga | No qualifying planet in the 2nd or 12th from the Moon. | `[YOGA_020]` |
| 21 | Parivartana Yoga | Two planets occupy each other's owned signs. | `[YOGA_021]` |
| 22 | Neecha Bhanga Raja Yoga | A debilitated planet with at least one satisfied Neecha Bhanga condition that also owns or occupies a Kendra or Trikona. | `[YOGA_022]` |

### Points worth checking in the yoga rules

**Gaja Kesari.** The formation is Jupiter in a Kendra from the Lagna or from the Moon. A Moon–Jupiter conjunction is the 1st from the Moon, which is a Kendra, so it forms the yoga. Four further conditions — a benefic association, not debilitated, not combust, not in an enemy's sign — are shown separately as strengthening conditions and do not prevent the yoga from forming.

**Budha-Aditya.** The Sun and Mercury in the same Rashi. Mercury's combustion is reported as a separate fact and does not cancel the yoga.

**Raja Yoga.** A Kendra lord and a Trikona lord joined by conjunction, mutual aspect, or exchange of signs. The Lagna lord counts as both, since the 1st house is a Kendra and a Trikona.

**Kemadruma.** No planet in the 2nd or 12th from the Moon. The Sun, Rahu and Ketu are not counted as relieving it.

**Parivartana.** Reported as a plain exchange. It is not divided into Maha, Khala and Dainya.

**Benefics and malefics**, used by Adhi, Amala and Gaja Kesari: `[BENEFIC_001]`

| Graha | Classed as |
|---|---|
| Jupiter, Venus | Always benefic |
| Mercury | Benefic unless it shares its sign with a natural malefic |
| Moon | Benefic when between 72° and 288° from the Sun (bright half) |
| Sun, Mars, Saturn, Rahu, Ketu | Malefic |

---

## 15. The doshas checked

Fourteen doshas are examined. A dosha is reported by its formation alone. Where the classics give well-known grounds on which it is held to be lifted, those are shown with it, but the software never applies them: whether a cancellation carries is yours to judge. `[DOSHA_100]`

| No. | Dosha | How it is formed | Tag |
|---|---|---|---|
| 1 | Mangal Dosha (Kuja Dosha) | Mars occupies the 1st, 2nd, 4th, 7th, 8th or 12th house, counted from the Lagna, the Moon or Venus. | `[DOSHA_001]` |
| 2 | Kaal Sarpa Dosha | All seven grahas from the Sun to Saturn lie within the arc running from Rahu to Ketu. | `[DOSHA_002]` |
| 3 | Guru Chandal Dosha | Jupiter shares its sign with Rahu or Ketu. | `[DOSHA_003]` |
| 4 | Angarak Dosha | Mars shares its sign with Rahu or Ketu. | `[DOSHA_004]` |
| 5 | Grahan Dosha | The Sun or the Moon shares its sign with Rahu or Ketu. | `[DOSHA_005]` |
| 6 | Shrapit Dosha | Saturn shares its sign with Rahu. | `[DOSHA_006]` |
| 7 | Vish Dosha (Punarphoo) | The Moon shares its sign with Saturn. | `[DOSHA_007]` |
| 8 | Kemadruma Dosha | No graha other than the Sun and the nodes occupies the 2nd or the 12th sign from the Moon. | `[DOSHA_008]` |
| 9 | Sakata Dosha | The Moon occupies the 6th, 8th or 12th sign counted from Jupiter. | `[DOSHA_009]` |
| 10 | Papakartari Dosha | A graha stands hemmed, with a natural malefic in both the 2nd and the 12th sign from it. | `[DOSHA_010]` |
| 11 | Kendradhipatya Dosha | A natural benefic lords a Kendra, the 4th, 7th or 10th house. | `[DOSHA_011]` |
| 12 | Daridra Dosha | The lord of the 11th house occupies the 6th, 8th or 12th house. | `[DOSHA_012]` |
| 13 | Amavasya Dosha | The Sun and the Moon stand within 12 degrees of each other, the birth falling close to the new moon. | `[DOSHA_013]` |
| 14 | Pitru Dosha | Rahu or Ketu occupies the 9th house, or the lord of the 9th occupies the 6th, 8th or 12th. | `[DOSHA_014]` |

Kemadruma is reported here rather than with the yogas, being an affliction by nature.

Grounds for cancellation are recorded for Mangal Dosha (Kuja Dosha), Kaal Sarpa Dosha, Guru Chandal Dosha, Kemadruma Dosha, Papakartari Dosha, Kendradhipatya Dosha, Amavasya Dosha, Pitru Dosha.

---

## 16. Rahu and Ketu

The classics count nine grahas but work out most of their detail for seven. Every feature is therefore stated explicitly for the nodes, so that no seven-planet rule is applied to them by accident.

| Question | Answer | Tag |
|---|---|---|
| Do they lord any sign? | No | `[RK_001]` |
| Do they have a Mooltrikona? | No | `[RK_002]` |
| Do they have an own sign? | No | `[RK_003]` |
| Exaltation and debilitation? | Rahu exalted in Taurus, Gemini; Ketu the reverse. See section 17. | `[RK_004]` |
| Which aspects do they cast? | 7th only | `[RK_005]` |
| Do they have friendships? | Yes, from the table in section 6, which is not from BPHS | `[RK_006]` |
| Is Shadbala calculated? | No | `[RK_007]` |
| Can they be combust? | No | `[RK_008]` |
| Can they be in planetary war? | No | `[RK_009]` |
| Are they retrograde? | Always, as mean nodes | `[RK_010]` |
| Can they be a dispositor? | No | `[RK_011]` |
| Are Avasthas shown? | Yes, with a note that the classics address the seven grahas | `[RK_012]` |
| How far apart are they? | Always exactly 180°, seven signs apart | `[RK_013]` |
| Benefic or malefic? | Both malefic | `[RK_014]` |

(14 rules cover the nodes.)

Because they lord no house, Rahu and Ketu are never reported as Kendra lord, Trikona lord, Dusthana lord, Upachaya lord, Maraka lord, Badhakesh or Yoga Karaka.

---

## 17. Where traditions differ

These are the places where the classics do not speak with one voice. A choice had to be made, and it is recorded here rather than hidden. **These are the points most worth your attention.**

| Matter | What this software does | The alternative |
|---|---|---|
| Exaltation of Rahu and Ketu | Rahu exalted in Taurus and Gemini, debilitated in Scorpio and Sagittarius; Ketu the reverse | Some hold Rahu exalted in Taurus alone, others in Gemini alone, with Ketu correspondingly placed. BPHS does not settle it. |
| Friendships of Rahu and Ketu | Taken from the table in section 6 | BPHS derives friendship from a planet's Mooltrikona and exaltation, which the nodes do not have, so it gives no such table for them. |
| Aspects of Rahu and Ketu | 7th only | Some give them the 5th and 9th as well. |
| Gaja Kesari | Formed by Jupiter in a Kendra from the Lagna or Moon; the four further conditions are shown separately | Some require all five conditions before the yoga is said to exist at all. |
| Kemadruma | The Sun, Rahu and Ketu do not relieve it | Some count any graha in the 2nd or 12th from the Moon, including the Sun. |
| Lunar nodes | Mean nodes | True nodes, which move irregularly and can appear briefly direct. |
| Moon as benefic | Bright when 72° to 288° from the Sun | Some use the paksha alone, or a wider or narrower arc. |
| Parivartana | Reported as a plain exchange | Classical division into Maha, Khala and Dainya. |
| Bhava | Whole sign from the Lagna sign for every rule | Bhava Chalita or cusp-based houses. These are shown in the software but no rule uses them. |

---

## 18. What the software will never do

- Call a planet good, bad, strong or weak
- Predict an event or a period
- Give a score or a ranking to a planet
- Say what a yoga will bring
- Decide an astrological question by any means other than the rules listed above

Shadbala is shown as numbers with the required minimum beside them, and nothing more. Every classification carries a tag so it can be traced back to the rule that produced it.

---

## Full list of rule tags

Every rule in the software, for reference when reporting a correction.

| Tag | Rule |
|---|---|
| `ASPECT_001` | Graha Drishti ordinal |
| `BENEFIC_001` | Natural benefic / malefic classification |
| `CHAITANYADI_001` | Chaitanyadi Avastha |
| `COMBUST_001` | Combustion (Asta) |
| `CONFIG_001` | Ayanamsha and zodiac configuration |
| `CONJ_001` | Conjunction |
| `DIGNITY_001` | Rashi dignity |
| `DIGNITY_002` | Mooltrikona |
| `DISPOSITOR_001` | Dispositor chain |
| `DOSHA_001` | Mangal Dosha (Kuja Dosha) |
| `DOSHA_002` | Kaal Sarpa Dosha |
| `DOSHA_003` | Guru Chandal Dosha |
| `DOSHA_004` | Angarak Dosha |
| `DOSHA_005` | Grahan Dosha |
| `DOSHA_006` | Shrapit Dosha |
| `DOSHA_007` | Vish Dosha (Punarphoo) |
| `DOSHA_008` | Kemadruma Dosha |
| `DOSHA_009` | Sakata Dosha |
| `DOSHA_010` | Papakartari Dosha |
| `DOSHA_011` | Kendradhipatya Dosha |
| `DOSHA_012` | Daridra Dosha |
| `DOSHA_013` | Amavasya Dosha |
| `DOSHA_014` | Pitru Dosha |
| `DOSHA_100` | How doshas are reported |
| `FUNC_001` | House ownership |
| `FUNC_002` | Kendra / Trikona / Dusthana / Upachaya / Maraka house categories |
| `FUNC_003` | Badhaka house and Badhakesh |
| `FUNC_004` | Yoga Karaka |
| `FUNC_005` | Functional classification summary |
| `FUNC_006` | Sign modality |
| `FUNC_007` | Sign parity |
| `GEO_001` | Place resolution |
| `HOUSE_001` | Whole-sign Bhava |
| `KUMARADI_001` | Kumaradi Avastha |
| `MAITRI_001` | Natural (permanent) relationship |
| `MAITRI_002` | Temporary relationship |
| `MAITRI_003` | Panchadha Maitri (five-fold compound relationship) |
| `NAK_001` | Nakshatra lord |
| `NATURE_001` | Natural benefic, malefic or neutral |
| `NATURE_002` | Nature of each house |
| `NATURE_003` | Grouping of a planet's house placement |
| `NATURE_004` | Functional nature for a given Lagna |
| `NATURE_005` | Grouping of retrogression |
| `NATURE_006` | Grouping of company and aspect |
| `NATURE_007` | The fixed catalogue of checks |
| `NATURE_008` | No aggregate verdict |
| `NATURE_009` | Points left to the astrologer |
| `NATURE_010` | The six groups a finding can fall into |
| `NB_001` | Debilitation-sign lord in Kendra from Lagna |
| `NB_002` | Debilitation-sign lord in Kendra from Moon |
| `NB_003` | Exaltation-sign lord in Kendra from Lagna |
| `NB_004` | Exaltation-sign lord in Kendra from Moon |
| `NB_005` | Association with a cancellation lord |
| `NB_006` | Debilitation lord and exaltation lord in mutual Kendras |
| `NB_100` | Neecha Bhanga (cancellation) summary |
| `RK_001` | Rahu and Ketu hold no sign lordship |
| `RK_002` | Rahu and Ketu have no Mooltrikona |
| `RK_003` | Rahu and Ketu have no Swarashi |
| `RK_004` | Rahu and Ketu exaltation and debilitation |
| `RK_005` | Rahu and Ketu Graha Drishti |
| `RK_006` | Rahu and Ketu natural relationships |
| `RK_007` | Rahu and Ketu are outside Shadbala |
| `RK_008` | Rahu and Ketu are outside combustion |
| `RK_009` | Rahu and Ketu are outside Graha Yuddha |
| `RK_010` | Rahu and Ketu are always retrograde as mean nodes |
| `RK_011` | Rahu and Ketu never act as dispositors |
| `RK_012` | Avastha applicability to Rahu and Ketu |
| `RK_013` | Rahu and Ketu are always in opposition |
| `RK_014` | Rahu and Ketu as natural malefics |
| `TIME_001` | Birth instant resolution |
| `VARGA_001` | Vargottama |
| `YOGA_001` | Raja Yoga |
| `YOGA_002` | Dharma-Karmadhipati Yoga |
| `YOGA_003` | Ruchaka Yoga |
| `YOGA_004` | Bhadra Yoga |
| `YOGA_005` | Hamsa Yoga |
| `YOGA_006` | Malavya Yoga |
| `YOGA_007` | Sasa Yoga |
| `YOGA_008` | Gaja Kesari Yoga |
| `YOGA_009` | Budha-Aditya Yoga |
| `YOGA_010` | Chandra-Mangala Yoga |
| `YOGA_011` | Guru-Mangala Yoga |
| `YOGA_012` | Adhi Yoga |
| `YOGA_013` | Amala Yoga |
| `YOGA_014` | Harsha Yoga |
| `YOGA_015` | Sarala Yoga |
| `YOGA_016` | Vimala Yoga |
| `YOGA_017` | Dhana Yoga |
| `YOGA_018` | Lakshmi Yoga |
| `YOGA_019` | Saraswati Yoga |
| `YOGA_020` | Kemadruma Yoga |
| `YOGA_021` | Parivartana Yoga |
| `YOGA_022` | Neecha Bhanga Raja Yoga |

---

*Calculated with PyJHora 4.8.7 and the Swiss Ephemeris. This document is generated from the software's own rule tables, so the values shown are the values actually used.*
