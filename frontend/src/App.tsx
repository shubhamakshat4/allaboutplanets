import { useCallback, useEffect, useState } from 'react'
import { api, ApiError, forgetBirthRequest } from '@/api/client'
import type { Chart, Meta } from '@/types'
import { BirthForm } from '@/components/BirthForm'
import { ChartOverview } from '@/components/ChartOverview'
import { PlanetAnalysisView } from '@/components/PlanetAnalysisView'
import { Button, ErrorBox, Spinner } from '@/components/ui'

const STORAGE_KEY = 'psa.lastChartId'

type View = 'form' | 'chart' | 'planet'

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [chart, setChart] = useState<Chart | null>(null)
  const [planetId, setPlanetId] = useState<number | null>(null)
  const [view, setView] = useState<View>('form')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => { api.meta().then(setMeta).catch(() => setMeta(null)) }, [])

  const loadChart = useCallback(async (chartId: string, goTo: View = 'chart') => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.getChart(chartId)
      setChart(result)
      setView(goTo)
      window.localStorage.setItem(STORAGE_KEY, result.chart_id)
    } catch (e) {
      window.localStorage.removeItem(STORAGE_KEY)
      if (e instanceof ApiError && e.status === 404) {
        setError('That chart could not be restored. Please enter the birth details again.')
        setView('form')
      } else {
        setError(e instanceof ApiError ? e.message : 'The chart could not be loaded.')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (saved) void loadChart(saved)
  }, [loadChart])

  function reset() {
    window.localStorage.removeItem(STORAGE_KEY)
    forgetBirthRequest()
    setChart(null)
    setPlanetId(null)
    setError(null)
    setView('form')
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-black/5 bg-cream-50/80 backdrop-blur-md no-print">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-3">
          <button
            onClick={() => setView(chart ? 'chart' : 'form')}
            className="flex items-center gap-2.5 text-left"
          >
            <span
              className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-sun-400 to-orange-500 text-lg shadow-card"
              aria-hidden
            >
              ✨
            </span>
            <span>
              <span className="block font-display text-lg font-bold leading-none text-ink-800">
                Planet Insights
              </span>
              <span className="hidden text-[11px] font-semibold text-ink-400 sm:block">
                Vedic chart, planet by planet
              </span>
            </span>
          </button>

          <div className="ml-auto flex items-center gap-2">
            {chart && view === 'planet' && (
              <Button size="sm" variant="soft" onClick={() => setView('chart')}>
                ← Chart
              </Button>
            )}
            {chart && (
              <Button size="sm" variant="ghost" onClick={reset}>New chart</Button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        {error && <div className="mb-5"><ErrorBox>{error}</ErrorBox></div>}

        {loading && <Spinner label="Loading the chart…" />}

        {!loading && view === 'form' && (
          <BirthForm meta={meta} onGenerated={(id) => loadChart(id, 'chart')} />
        )}

        {!loading && view === 'chart' && chart && (
          <ChartOverview
            chart={chart}
            onSelectPlanet={(id) => { setPlanetId(id); setView('planet') }}
            selectedPlanet={planetId}
          />
        )}

        {!loading && view === 'planet' && chart && planetId !== null && (
          <PlanetAnalysisView
            chart={chart}
            planetId={planetId}
            onSelectPlanet={setPlanetId}
            onBack={() => setView('chart')}
          />
        )}
      </main>

      <footer className="pb-8 text-center text-[11.5px] text-ink-400 no-print">
        Calculated facts only. Nothing here is a prediction.
      </footer>
    </div>
  )
}
