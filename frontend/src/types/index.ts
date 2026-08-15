/** Types mirroring the backend's structured analysis objects. */

export interface SourceRef {
  source?: string
  rule?: string | null
  methodology?: string
}

export interface Relationship {
  planetA: number
  planetAName: string
  planetB: number
  planetBName: string
  naturalRelationship: string
  temporaryRelationship: string
  panchadhaMaitri: string
  panchadhaExplanation?: string
  evidence: Record<string, unknown>
  sources: Record<string, SourceRef>
}

export interface Conjunction {
  planetA: number
  planetAName: string
  planetB: number
  planetBName: string
  rashi: number
  rashiName: string
  sameRashi: boolean
  sameBhava: boolean
  bhavaA: number
  bhavaB: number
  degreeADms: string
  degreeBDms: string
  separation: number
  separationDms: string
  relationship: Relationship
  evidence: string
  sources: SourceRef
}

export interface AspectRecord {
  sourcePlanet: number
  sourcePlanetName: string
  targetPlanet: number
  targetPlanetName: string
  aspectType: string
  aspectOrdinal: number
  sourceHouse: number
  targetHouse: number
  targetSignName?: string
  relationship: Relationship
  evidence: string
  sources: SourceRef
}

export interface AspectedHouse {
  targetSign: number
  targetSignName: string
  targetHouse: number
  targetHouseLordName: string
  aspectType: string
  aspectOrdinal: number
  occupyingPlanets: { planet: number; planetName: string }[]
  evidence: string
}

export interface AspectsGiven {
  houses: AspectedHouse[]
  planets: AspectRecord[]
  drishtiSet: number[]
  drishtiSetText: string
  nodeNote: string | null
  sources: SourceRef
}

export interface Condition {
  title: string
  satisfied: boolean | null
  status: string
  evidence: string
}

export interface YogaParticipant {
  planet: number
  planetName: string
  role: string
  sign: number
  signName: string
  bhava: number
  housesOwned: number[]
}

export interface Yoga {
  key: string
  name: string
  ruleId: string
  summary: string
  present: boolean
  status: string
  participants: YogaParticipant[]
  conditions: Condition[]
  associationType: string | null
  evidence: string | null
  instances: Record<string, any>[]
  sources: SourceRef
  [k: string]: unknown
}

export interface YogaParticipationRow {
  key: string
  name: string
  ruleId: string
  status: string
  present: boolean
  role: string
  otherParticipants: { planet: number; planetName: string }[]
  conditions: Condition[]
  instances: Record<string, any>[]
  evidence: string | null
  associationType: string | null
  sources: SourceRef
}

export interface NeechaBhangaCondition extends Condition {
  number: number
  ruleId: string
  statement: string
  participants: { planet: number; planetName: string }[]
}

export interface PlanetRow {
  planet: number
  planetName: string
  symbol: string
  rashi: number
  rashiName: string
  degree: number
  degreeDms: string
  absoluteLongitudeDms: string
  bhava: number
  bhavaChalita: number | null
  nakshatra: string
  pada: number
  nakshatraLordName: string
  navamsha: string
  navamshaLordName: string
  retrograde: boolean
  combust: boolean | string
  swarashi: boolean | string
  mooltrikona: boolean | string
  exalted: boolean
  debilitated: boolean
  signRelationship: string
  vargottama: boolean | string
  kumaradi: string
  chaitanyadi: string
  housesOwned: number[]
}

export interface HouseRow {
  house: number
  sign: number
  signName: string
  signSanskrit: string
  lord: number
  lordName: string
  planets: {
    planet: number
    planetName: string
    symbol: string
    degreeDms: string
    retrograde: boolean
    combust: boolean
  }[]
  hasLagna: boolean
}

export interface CalculationSettings {
  engine: string
  pyjhora_version: string
  ephemeris: string
  zodiac_type: string
  ayanamsha_mode: string
  ayanamsha_value: number
  ayanamsha_value_dms: string
  house_system_for_rules: string
  house_system_secondary: string
  node_type: string
  julian_day: number
}

export interface ResolvedBirth {
  date_label: string
  time_label: string
  place_name: string
  latitude: number
  longitude: number
  latitude_label: string
  longitude_label: string
  timezone: string | null
  utc_offset_hours: number
  utc_offset_label: string
  timezone_source: string
}

export interface Chart {
  chart_id: string
  birth: ResolvedBirth
  settings: CalculationSettings
  lagna: {
    sign: number
    signName: string
    signSanskrit: string
    degree: number
    degreeDms: string
    lord: number
    lordName: string
    modality: string
    nakshatra: string
    pada: number
    nakshatraLordName: string
  }
  planets: PlanetRow[]
  houses: HouseRow[]
  bhava_chalita: {
    house: number
    sign: number
    start: number
    cusp: number
    end: number
    occupants: number[]
    has_lagna: boolean
  }[]
  yogas: Yoga[]
  warnings: string[]
}

export interface Finding {
  key: string
  category: 'favourable' | 'challenging' | 'neutral'
  text: string
  explanation: string
  detail: { label: string; value: string }[]
  openKind?: 'not_applicable' | 'neutral' | 'interpretive' | null
  openLabel?: string | null
}

export interface Findings {
  favourable: Finding[]
  challenging: Finding[]
  yogas: Finding[]
  doshas: Finding[]
  neutral: Finding[]
  interpretive: Finding[]
  counts: Record<string, number>
  note: string
}

export interface PlanetAnalysis {
  planet: number
  planetName: string
  summary: Record<string, any>
  findings: Findings
  position: Record<string, any>
  dignity: Record<string, any>
  rashiLordRelationship: Record<string, any>
  lordship: Record<string, any>
  lagnaRelationship: Record<string, any>
  nakshatraRelationship: Record<string, any>
  navamshaRelationship: Record<string, any>
  avastha: { kumaradi: Record<string, any>; chaitanyadi: Record<string, any> }
  retrograde: Record<string, any>
  combustion: Record<string, any>
  planetaryWar: Record<string, any>
  conjunctions: Conjunction[]
  aspectsReceived: AspectRecord[]
  aspectsGiven: AspectsGiven
  relationships: Relationship[]
  shadbala: Record<string, any>
  divisionalPositions: Record<string, any>[]
  dispositorChain: Record<string, any>
  neechaBhanga: Record<string, any>
  yogaParticipation: YogaParticipationRow[]
  allYogas: {
    key: string
    name: string
    ruleId: string
    status: string
    present: boolean
    participants: YogaParticipant[]
  }[]
}

export interface PlaceResult {
  name: string
  display_name: string
  country: string | null
  admin1: string | null
  latitude: number
  longitude: number
  timezone: string | null
  source: string
}

export interface Meta {
  pyjhora_version: string
  ephemeris: string
  ayanamsha_modes: { value: string; label: string }[]
  default_ayanamsha: string
  planets: { id: number; name: string; sanskrit: string; symbol: string }[]
  varga_factors: { factor: number; name: string }[]
  pyjhora_yoga_module: { module: string; used: boolean; reason: string }
}

export interface BirthRequest {
  year: number
  month: number
  day: number
  hour: number
  minute: number
  second: number
  place_name: string
  latitude: number
  longitude: number
  timezone?: string | null
  utc_offset_hours?: number | null
  ayanamsha_mode: string
}
