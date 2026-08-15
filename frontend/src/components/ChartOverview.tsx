import { useState } from 'react'
import type { Chart } from '@/types'
import { NorthIndianChart } from './NorthIndianChart'
import { PlanetTable } from './PlanetTable'
import { PlanetSelector } from './PlanetSelector'
import { Button } from '@/components/ui'
import { cn } from '@/lib/utils'

interface Props {
  chart: Chart
  onSelectPlanet: (planetId: number) => void
  selectedPlanet: number | null
}

export function ChartOverview({ chart, onSelectPlanet, selectedPlanet }: Props) {
  const { birth, settings } = chart
  const [showTable, setShowTable] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      {/* Birth details */}
      <section className="panel overflow-hidden">
        <div className="bg-gradient-to-r from-sun-400 via-orange-400 to-pink-400 px-6 py-5 text-white">
          <h1 className="font-display text-3xl font-bold leading-tight drop-shadow-sm">
            {birth.place_name.split(',')[0]}
          </h1>
          <p className="mt-1 text-[15px] font-bold text-white/95">
            {birth.date_label} · {birth.time_label}
          </p>
        </div>

        <dl className="grid grid-cols-2 gap-px bg-black/5 sm:grid-cols-4">
          {[
            ['Lagna', `${chart.lagna.signName} ${chart.lagna.degreeDms}`],
            ['Lagna lord', chart.lagna.lordName],
            ['Moon sign', moonSign(chart)],
            ['Place', birth.place_name],
          ].map(([label, value]) => (
            <div key={label} className="bg-white/85 px-4 py-3">
              <dt className="label">{label}</dt>
              <dd className="mt-0.5 truncate text-[15px] font-bold text-ink-800"
                  title={String(value)}>
                {value}
              </dd>
            </div>
          ))}
        </dl>
      </section>

      {/* Kundli */}
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section className="panel p-5">
          <h2 className="mb-3 font-display text-xl font-bold text-ink-800">
            Rashi chart
          </h2>
          <NorthIndianChart
            chart={chart}
            onSelectPlanet={onSelectPlanet}
            selectedPlanet={selectedPlanet}
          />
        </section>

        <section className="panel p-5">
          <h2 className="mb-3 font-display text-xl font-bold text-ink-800">
            Where each planet sits
          </h2>
          <ul className="space-y-1.5">
            {chart.planets.map((p) => (
              <li key={p.planet}>
                <button
                  type="button"
                  onClick={() => onSelectPlanet(p.planet)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-xl border border-transparent',
                    'px-3 py-2 text-left transition-colors hover:border-black/10 hover:bg-white',
                    selectedPlanet === p.planet && 'border-black/10 bg-white shadow-sm',
                  )}
                >
                  <span className="text-xl leading-none text-ink-600" aria-hidden>
                    {p.symbol}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-[15px] font-bold text-ink-800">
                      {p.planetName}
                    </span>
                    <span className="block text-[12.5px] text-ink-500">
                      {p.rashiName} · house {p.bhava} · {p.nakshatra}
                    </span>
                  </span>
                  <span className="shrink-0 font-mono text-[12px] tabular text-ink-400">
                    {p.degreeDms}
                  </span>
                  {p.retrograde && (
                    <span className="shrink-0 text-[12px] font-bold text-ink-400"
                          title="Retrograde">℞</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Choose a planet — the main call to action */}
      <section className="panel p-5 no-print">
        <h2 className="mb-1 text-center font-display text-2xl font-bold text-ink-800">
          Pick a planet to analyse
        </h2>
        <p className="mb-4 text-center text-[13.5px] text-ink-500">
          You will get its strengths, its challenges, and everything neutral —
          each point explained.
        </p>
        <PlanetSelector
          planets={chart.planets}
          selected={selectedPlanet}
          onSelect={onSelectPlanet}
          size="lg"
        />
      </section>

      {/* Optional extras, closed by default */}
      <div className="flex flex-wrap justify-center gap-2 no-print">
        <Button variant="soft" size="sm" onClick={() => setShowTable((v) => !v)}>
          {showTable ? 'Hide the full table' : 'Show the full table'}
        </Button>
        <Button variant="soft" size="sm" onClick={() => setShowSettings((v) => !v)}>
          {showSettings ? 'Hide chart settings' : 'Chart settings'}
        </Button>
      </div>

      {showTable && (
        <section className="panel animate-pop p-5">
          <h2 className="mb-3 font-display text-xl font-bold text-ink-800">
            All planets, side by side
          </h2>
          <PlanetTable
            chart={chart}
            onAnalyze={onSelectPlanet}
            selectedPlanet={selectedPlanet}
          />
        </section>
      )}

      {showSettings && (
        <section className="panel animate-pop p-5">
          <h2 className="mb-3 font-display text-xl font-bold text-ink-800">
            How this chart was calculated
          </h2>
          <dl className="grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
            {[
              ['Ayanamsha', settings.ayanamsha_mode],
              ['Ayanamsha value', settings.ayanamsha_value_dms],
              ['Zodiac', settings.zodiac_type],
              ['Houses', 'Whole sign from the Lagna'],
              ['Rahu & Ketu', settings.node_type],
              ['Timezone', `${birth.timezone ?? ''} ${birth.utc_offset_label}`.trim()],
              ['Latitude', birth.latitude_label],
              ['Longitude', birth.longitude_label],
            ].map(([label, value]) => (
              <div key={label}>
                <dt className="label">{label}</dt>
                <dd className="mt-0.5 text-[14px] font-semibold text-ink-700">{value}</dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      {chart.warnings.length > 0 && (
        <section className="panel border-hard-200 p-4">
          <ul className="list-inside list-disc space-y-1 text-[13px] text-hard-800">
            {chart.warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </section>
      )}
    </div>
  )
}

function moonSign(chart: Chart): string {
  const moon = chart.planets.find((p) => p.planet === 1)
  return moon ? `${moon.rashiName} · ${moon.nakshatra}` : '—'
}
