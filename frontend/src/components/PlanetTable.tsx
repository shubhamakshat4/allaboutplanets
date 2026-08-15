import { useMemo, useState } from 'react'
import type { Chart, PlanetRow } from '@/types'
import {
  Badge, BoolBadge, Button, Table, TableWrap, Td, Th,
} from '@/components/ui'
import { cn } from '@/lib/utils'

type ColumnKey =
  | 'rashi' | 'degree' | 'bhava' | 'nakshatra' | 'pada' | 'nakshatraLord'
  | 'navamsha' | 'navamshaLord' | 'retrograde' | 'combust' | 'swarashi'
  | 'mooltrikona' | 'exalted' | 'debilitated' | 'vargottama'
  | 'kumaradi' | 'chaitanyadi' | 'housesOwned'

interface Column {
  key: ColumnKey
  label: string
  title?: string
  align?: 'left' | 'right' | 'center'
  render: (row: PlanetRow) => React.ReactNode
  mono?: boolean
}

const COLUMNS: Column[] = [
  { key: 'rashi', label: 'Rashi', render: (r) => r.rashiName },
  { key: 'degree', label: 'Degree', align: 'right', mono: true, render: (r) => r.degreeDms },
  { key: 'bhava', label: 'Bhava', align: 'right', mono: true, render: (r) => r.bhava,
    title: 'Whole-sign house counted from the Lagna' },
  { key: 'nakshatra', label: 'Nakshatra', render: (r) => r.nakshatra },
  { key: 'pada', label: 'Pada', align: 'right', mono: true, render: (r) => r.pada },
  { key: 'nakshatraLord', label: 'Nak. Lord', render: (r) => r.nakshatraLordName },
  { key: 'navamsha', label: 'Navamsha', render: (r) => r.navamsha },
  { key: 'navamshaLord', label: 'D9 Lord', render: (r) => r.navamshaLordName },
  { key: 'retrograde', label: 'Retro', align: 'center', render: (r) => <BoolBadge value={r.retrograde} /> },
  { key: 'combust', label: 'Combust', align: 'center', render: (r) => <BoolBadge value={r.combust} /> },
  { key: 'swarashi', label: 'Swarashi', align: 'center', render: (r) => <BoolBadge value={r.swarashi} /> },
  { key: 'mooltrikona', label: 'Mooltrikona', align: 'center', render: (r) => <BoolBadge value={r.mooltrikona} /> },
  { key: 'exalted', label: 'Exalted', align: 'center', render: (r) => <BoolBadge value={r.exalted} /> },
  { key: 'debilitated', label: 'Debilitated', align: 'center', render: (r) => <BoolBadge value={r.debilitated} /> },
  { key: 'vargottama', label: 'Vargottama', align: 'center', render: (r) => <BoolBadge value={r.vargottama} /> },
  { key: 'kumaradi', label: 'Kumaradi', render: (r) => r.kumaradi },
  { key: 'chaitanyadi', label: 'Chaitanyadi', render: (r) => r.chaitanyadi },
  { key: 'housesOwned', label: 'Owns', mono: true,
    render: (r) => (r.housesOwned.length ? r.housesOwned.join(', ') : '—'),
    title: 'Houses owned, counted from the Lagna' },
]

const DEFAULT_VISIBLE: ColumnKey[] = [
  'rashi', 'degree', 'bhava', 'nakshatra', 'pada', 'nakshatraLord',
  'navamsha', 'navamshaLord', 'retrograde', 'combust', 'swarashi',
  'mooltrikona', 'exalted', 'debilitated', 'vargottama', 'kumaradi', 'chaitanyadi',
]

interface Props {
  chart: Chart
  onAnalyze: (planetId: number) => void
  selectedPlanet?: number | null
}

export function PlanetTable({ chart, onAnalyze, selectedPlanet }: Props) {
  const [visible, setVisible] = useState<Set<ColumnKey>>(new Set(DEFAULT_VISIBLE))
  const [picker, setPicker] = useState(false)

  const columns = useMemo(() => COLUMNS.filter((c) => visible.has(c.key)), [visible])

  function toggle(key: ColumnKey) {
    setVisible((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3 no-print">
        <p className="text-[12px] text-ink-500">
          {columns.length} of {COLUMNS.length} columns shown. Scroll horizontally for more.
        </p>
        <Button size="sm" variant="outline" onClick={() => setPicker((p) => !p)}>
          {picker ? 'Hide columns' : 'Choose columns'}
        </Button>
      </div>

      {picker && (
        <div className="mb-4 flex flex-wrap gap-1.5 rounded-md border border-ink-200 bg-ink-50 p-3 no-print">
          {COLUMNS.map((column) => (
            <button
              key={column.key}
              type="button"
              onClick={() => toggle(column.key)}
              className={cn(
                'rounded border px-2 py-1 text-[11px] font-medium transition-colors',
                visible.has(column.key)
                  ? 'border-ink-800 bg-ink-800 text-white'
                  : 'border-ink-300 bg-white text-ink-600 hover:bg-ink-100',
              )}
            >
              {column.label}
            </button>
          ))}
        </div>
      )}

      <TableWrap>
        <Table className="min-w-[900px]">
          <thead>
            <tr>
              <Th className="sticky left-0 z-10 bg-white">Planet</Th>
              {columns.map((column) => (
                <Th key={column.key} align={column.align} title={column.title}>
                  {column.label}
                </Th>
              ))}
              <Th align="center" className="no-print">Analyze</Th>
            </tr>
          </thead>
          <tbody>
            {chart.planets.map((row) => (
              <tr
                key={row.planet}
                className={cn(
                  'transition-colors hover:bg-ink-50',
                  selectedPlanet === row.planet && 'bg-accent-50/70',
                )}
              >
                <Td className="sticky left-0 z-10 whitespace-nowrap bg-white">
                  <span className="flex items-center gap-2">
                    <span className="text-base leading-none text-ink-700" aria-hidden>
                      {row.symbol}
                    </span>
                    <span className="font-medium text-ink-900">{row.planetName}</span>
                  </span>
                </Td>
                {columns.map((column) => (
                  <Td key={column.key} align={column.align} mono={column.mono}>
                    {column.render(row)}
                  </Td>
                ))}
                <Td align="center" className="no-print">
                  <Button size="sm" variant="outline" onClick={() => onAnalyze(row.planet)}>
                    Analyze
                  </Button>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </TableWrap>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Badge>Bhava = whole sign from the Lagna</Badge>
        <Badge>Degrees are within the sign</Badge>
      </div>
    </div>
  )
}
