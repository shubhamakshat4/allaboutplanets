import { useState } from 'react'
import type { Chart, PlanetAnalysis } from '@/types'
import { Button, Input, Section } from '@/components/ui'
import {
  AvasthaSection, DignitySection, LagnaSection, LordshipSection,
  NakshatraSection, NavamshaSection, PositionSection, RashiLordSection,
} from './sections/PositionSections'
import {
  AspectsGivenSection, AspectsReceivedSection, CombustionSection,
  ConjunctionSection, PlanetaryWarSection, RelationshipProfileSection,
  RetrogradeSection,
} from './sections/StateSections'
import {
  DispositorSection, DivisionalSection, NeechaBhangaSection, ShadbalaSection,
} from './sections/StrengthSections'
import { AllYogasSection, YogaParticipationSection } from './sections/YogaSections'

/**
 * The complete reference view. Kept out of the way behind a toggle so the
 * everyday reading stays simple, but nothing is discarded.
 */
const SECTIONS = [
  { id: 'position', title: 'Position', subtitle: 'Sign, degree, house, nakshatra, navamsha' },
  { id: 'dignity', title: 'Dignity', subtitle: 'Exaltation, own sign, Mooltrikona and the rest' },
  { id: 'rashi-lord', title: 'Its sign lord', subtitle: 'Relationship with the lord of its sign' },
  { id: 'lordship', title: 'Houses it lords', subtitle: 'And what group each house belongs to' },
  { id: 'lagna', title: 'Relation to the Lagna', subtitle: 'Lagna lord, placement and aspect' },
  { id: 'nakshatra', title: 'Nakshatra', subtitle: 'Its lord and where that lord stands' },
  { id: 'navamsha', title: 'Navamsha', subtitle: 'D9 sign, its lord, and Vargottama' },
  { id: 'avastha', title: 'Avasthas', subtitle: 'Kumaradi and Chaitanyadi with the bands shown' },
  { id: 'retrograde', title: 'Motion', subtitle: 'Direct or retrograde' },
  { id: 'combustion', title: 'Combustion', subtitle: 'Distance from the Sun and the orb' },
  { id: 'war', title: 'Planetary war', subtitle: 'Graha Yuddha' },
  { id: 'conjunctions', title: 'Conjunctions', subtitle: 'Planets sharing its sign' },
  { id: 'aspects-received', title: 'Aspects received', subtitle: 'Who looks at this planet' },
  { id: 'aspects-given', title: 'Aspects given', subtitle: 'Which houses and planets it looks at' },
  { id: 'relationships', title: 'All relationships', subtitle: 'Against every other planet' },
  { id: 'shadbala', title: 'Shadbala', subtitle: 'The six strengths, in figures' },
  { id: 'vargas', title: 'Divisional charts', subtitle: 'D1 through D60' },
  { id: 'dispositor', title: 'Dispositor chain', subtitle: 'Sign lord to sign lord' },
  { id: 'neecha-bhanga', title: 'Neecha Bhanga', subtitle: 'The six cancellation conditions' },
  { id: 'yoga-participation', title: 'Its yogas', subtitle: 'Yogas this planet takes part in' },
  { id: 'all-yogas', title: 'All yogas in the chart', subtitle: 'All 22 checks' },
] as const

export function DetailedView({
  analysis, chart,
}: { analysis: PlanetAnalysis; chart: Chart }) {
  const [filter, setFilter] = useState('')
  const [presentOnly, setPresentOnly] = useState(false)
  const [open, setOpen] = useState<Set<string>>(new Set(['position']))

  const toggle = (id: string) =>
    setOpen((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  return (
    <div className="animate-pop space-y-3">
      <div className="panel flex flex-wrap items-center gap-3 p-3 no-print">
        <Input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Search within the detail…"
          className="min-w-[200px] flex-1"
          aria-label="Search the detail"
        />
        <label className="flex select-none items-center gap-2 text-[13px] font-semibold text-ink-600">
          <input
            type="checkbox"
            checked={presentOnly}
            onChange={(e) => setPresentOnly(e.target.checked)}
            className="h-4 w-4 rounded border-ink-400"
          />
          Only yogas present
        </label>
        <Button size="sm" variant="soft"
          onClick={() => setOpen(new Set(SECTIONS.map((s) => s.id)))}>
          Open all
        </Button>
        <Button size="sm" variant="soft" onClick={() => setOpen(new Set())}>
          Close all
        </Button>
      </div>

      {SECTIONS.map((section) => (
        <Section
          key={section.id}
          id={section.id}
          title={section.title}
          subtitle={section.subtitle}
          open={open.has(section.id)}
          onToggle={toggle}
          count={count(section.id, analysis)}
        >
          {render(section.id, analysis, chart, filter, presentOnly)}
        </Section>
      ))}
    </div>
  )
}

function count(id: string, a: PlanetAnalysis): number | undefined {
  switch (id) {
    case 'conjunctions': return a.conjunctions.length
    case 'aspects-received': return a.aspectsReceived.length
    case 'aspects-given': return a.aspectsGiven.planets.length
    case 'relationships': return a.relationships.length
    case 'vargas': return a.divisionalPositions.length
    case 'yoga-participation': return a.yogaParticipation.length
    case 'all-yogas': return a.allYogas.length
    default: return undefined
  }
}

function render(
  id: string, a: PlanetAnalysis, chart: Chart,
  filter: string, presentOnly: boolean,
) {
  switch (id) {
    case 'position': return <PositionSection a={a} />
    case 'dignity': return <DignitySection a={a} />
    case 'rashi-lord': return <RashiLordSection a={a} />
    case 'lordship': return <LordshipSection a={a} />
    case 'lagna': return <LagnaSection a={a} />
    case 'nakshatra': return <NakshatraSection a={a} />
    case 'navamsha': return <NavamshaSection a={a} />
    case 'avastha': return <AvasthaSection a={a} />
    case 'retrograde': return <RetrogradeSection a={a} />
    case 'combustion': return <CombustionSection a={a} />
    case 'war': return <PlanetaryWarSection a={a} />
    case 'conjunctions': return <ConjunctionSection a={a} filter={filter} />
    case 'aspects-received': return <AspectsReceivedSection a={a} filter={filter} />
    case 'aspects-given': return <AspectsGivenSection a={a} filter={filter} />
    case 'relationships': return <RelationshipProfileSection a={a} filter={filter} />
    case 'shadbala': return <ShadbalaSection a={a} />
    case 'vargas': return <DivisionalSection a={a} />
    case 'dispositor': return <DispositorSection a={a} />
    case 'neecha-bhanga': return <NeechaBhangaSection a={a} />
    case 'yoga-participation':
      return <YogaParticipationSection a={a} filter={filter} presentOnly={presentOnly} />
    case 'all-yogas':
      return <AllYogasSection yogas={chart.yogas} selectedPlanet={a.planet} filter={filter} />
    default: return null
  }
}
