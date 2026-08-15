import { useEffect, useState } from 'react'
import { api, ApiError } from '@/api/client'
import type { Chart, PlanetAnalysis } from '@/types'
import { PlanetFindings, type Findings } from './PlanetFindings'
import { PlanetSelector } from './PlanetSelector'
import { DetailedView } from './DetailedView'
import { Button, ErrorBox, Spinner } from '@/components/ui'
import { cn, PLANET_THEME } from '@/lib/utils'

interface Props {
  chart: Chart
  planetId: number
  onSelectPlanet: (planetId: number) => void
  onBack: () => void
}

export function PlanetAnalysisView({
  chart, planetId, onSelectPlanet, onBack,
}: Props) {
  const [analysis, setAnalysis] = useState<PlanetAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDetail, setShowDetail] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    setAnalysis(null)
    setShowDetail(false)
    api
      .getPlanetAnalysis(chart.chart_id, planetId)
      .then((r) => { if (!cancelled) setAnalysis(r) })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : 'Could not load this planet.')
        }
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [chart.chart_id, planetId])

  useEffect(() => { window.scrollTo({ top: 0, behavior: 'smooth' }) }, [planetId])

  if (loading) return <Spinner label="Reading the chart…" />
  if (error) return <ErrorBox>{error}</ErrorBox>
  if (!analysis) return null

  const s = analysis.summary
  const theme = PLANET_THEME[planetId]
  const findings = analysis.findings as unknown as Findings

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <div className="no-print">
        <PlanetSelector
          planets={chart.planets}
          selected={planetId}
          onSelect={onSelectPlanet}
        />
      </div>

      {/* Hero */}
      <section className="panel overflow-hidden">
        <div className={cn('bg-gradient-to-r px-6 py-6 text-white', theme.grad)}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <span className="text-6xl leading-none drop-shadow" aria-hidden>
                {s.symbol}
              </span>
              <div>
                <h1 className="font-display text-4xl font-bold leading-none drop-shadow-sm">
                  {analysis.planetName}
                </h1>
                <p className="mt-1.5 text-[15px] font-bold text-white/95">
                  {s.rashi} · {ordinal(s.bhava)} house
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 no-print">
              <Button size="sm" variant="glass" onClick={onBack}>← Chart</Button>
              <Button size="sm" variant="glass" onClick={() => window.print()}>
                Print
              </Button>
            </div>
          </div>
        </div>

        {/* Each fact sits with its lord and the relationship to that lord, so
            the strip stays short while carrying what is read most often. */}
        <dl className="grid grid-cols-2 gap-px bg-black/5 sm:grid-cols-3 lg:grid-cols-5">
          <Fact label="Sign" value={s.rashi} lord={s.rashiLord} selfNote="own sign" />
          <Fact
            label="House"
            value={ordinal(s.bhava)}
            sub={(s.bhavaCategories as string[]).join(' · ') || undefined}
          />
          <Fact
            label="Lords"
            value={
              (s.housesOwned as number[]).length
                ? (s.housesOwned as number[]).map(ordinal).join(', ')
                : '—'
            }
            sub={
              (s.housesOwnedSigns as string[]).length
                ? (s.housesOwnedSigns as string[]).join(' · ')
                : 'no sign lordship'
            }
          />
          <Fact label="Degree" value={s.degreeDms} />
          <Fact
            label="Nakshatra"
            value={`${s.nakshatra} · ${s.pada}`}
            lord={s.nakshatraLord}
            selfNote="own nakshatra"
          />
        </dl>
      </section>

      {/* The three groups — the heart of the page */}
      <PlanetFindings findings={findings} />

      {/* Everything else, tucked away */}
      <div className="no-print pt-1 text-center">
        <Button variant="soft" onClick={() => setShowDetail((v) => !v)}>
          {showDetail ? 'Hide the full detail' : 'Show the full detail'}
        </Button>
        <p className="mt-2 text-[12px] text-ink-400">
          Positions, aspects, divisional charts, Shadbala figures and every yoga.
        </p>
      </div>

      {showDetail && <DetailedView analysis={analysis} chart={chart} />}
    </div>
  )
}

interface LordPair {
  lord: string
  maitri: string | null
  isSelf: boolean
}

/** One tile in the header strip: a fact, optionally with its lord and the
 *  Panchadha Maitri towards that lord. */
function Fact({
  label, value, sub, lord, selfNote,
}: {
  label: string
  value: string
  sub?: string
  lord?: LordPair
  selfNote?: string
}) {
  return (
    <div className="min-w-0 bg-white/85 px-4 py-3">
      <dt className="label">{label}</dt>
      <dd className="mt-0.5 truncate text-[15px] font-bold text-ink-800" title={value}>
        {value}
      </dd>

      {lord && (
        <p className="mt-1 flex flex-wrap items-center gap-1.5">
          <span className="text-[12px] text-ink-500">{lord.lord}</span>
          {lord.isSelf ? (
            <span className="text-[11px] italic text-ink-400">{selfNote}</span>
          ) : (
            <span
              className={cn(
                'rounded-full border px-1.5 py-[1px] text-[10.5px] font-bold',
                maitriTone(lord.maitri),
              )}
            >
              {lord.maitri}
            </span>
          )}
        </p>
      )}

      {sub && !lord && (
        <p className="mt-1 truncate text-[12px] text-ink-500" title={sub}>{sub}</p>
      )}
    </div>
  )
}

/** Panchadha Maitri, coloured to match the group its bullet falls into. */
function maitriTone(maitri: string | null): string {
  switch (maitri) {
    case 'Ati Mitra':
    case 'Mitra':
      return 'border-good-300 bg-good-50 text-good-800'
    case 'Shatru':
    case 'Ati Shatru':
      return 'border-hard-300 bg-hard-50 text-hard-800'
    case 'Sama':
      return 'border-amber-300 bg-amber-50 text-amber-800'
    default:
      return 'border-black/10 bg-white text-ink-500'
  }
}

function ordinal(n: number): string {
  if (n % 100 >= 10 && n % 100 <= 20) return `${n}th`
  return `${n}${({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] ?? 'th'}`
}
