import type { Chart } from '@/types'
import { cn } from '@/lib/utils'

/** Ink colour per graha, so each planet is recognisable in the kundli. */
const PLANET_INK: Record<number, string> = {
  0: '#ea580c', 1: '#0891b2', 2: '#e11d48', 3: '#059669', 4: '#b45309',
  5: '#c026d3', 6: '#6d28d9', 7: '#7c3aed', 8: '#78716c',
}

/**
 * Traditional North Indian (diamond) kundli.
 *
 * The frame is a square with both diagonals plus the rhombus joining the
 * midpoints of the sides, giving twelve bhava cells. House 1 is the upper
 * central diamond and the houses run anticlockwise.
 */

const CELLS: { house: number; points: string; cx: number; cy: number }[] = [
  { house: 1, points: '50,0 75,25 50,50 25,25', cx: 50, cy: 24 },
  { house: 2, points: '0,0 50,0 25,25', cx: 25, cy: 10 },
  { house: 3, points: '0,0 25,25 0,50', cx: 10, cy: 25 },
  { house: 4, points: '0,50 25,25 50,50 25,75', cx: 25, cy: 50 },
  { house: 5, points: '0,50 25,75 0,100', cx: 10, cy: 75 },
  { house: 6, points: '0,100 25,75 50,100', cx: 25, cy: 90 },
  { house: 7, points: '50,100 25,75 50,50 75,75', cx: 50, cy: 76 },
  { house: 8, points: '50,100 75,75 100,100', cx: 75, cy: 90 },
  { house: 9, points: '100,100 75,75 100,50', cx: 90, cy: 75 },
  { house: 10, points: '100,50 75,75 50,50 75,25', cx: 75, cy: 50 },
  { house: 11, points: '100,50 75,25 100,0', cx: 90, cy: 25 },
  { house: 12, points: '100,0 75,25 50,0', cx: 75, cy: 10 },
]

interface Props {
  chart: Chart
  onSelectPlanet?: (planetId: number) => void
  selectedPlanet?: number | null
  className?: string
}

export function NorthIndianChart({
  chart, onSelectPlanet, selectedPlanet, className,
}: Props) {
  const byHouse = new Map(chart.houses.map((h) => [h.house, h]))

  return (
    <figure className={cn('w-full', className)}>
      <svg
        viewBox="-3 -3 106 106"
        className="w-full select-none"
        role="img"
        aria-label={`North Indian rashi chart. Lagna in ${chart.lagna.signName}.`}
      >
        {/* Frame */}
        <defs>
          <linearGradient id="kundliBg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#fff8ea" />
            <stop offset="50%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#f2f5ff" />
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="100" height="100" rx="1.5"
          fill="url(#kundliBg)" stroke="#d97706" strokeWidth="0.9" />
        <line x1="0" y1="0" x2="100" y2="100" stroke="#e9a23b" strokeWidth="0.45" />
        <line x1="100" y1="0" x2="0" y2="100" stroke="#e9a23b" strokeWidth="0.45" />
        <polygon points="50,0 100,50 50,100 0,50"
          fill="none" stroke="#e9a23b" strokeWidth="0.45" />

        {CELLS.map(({ house, points, cx, cy }) => {
          const data = byHouse.get(house)
          if (!data) return null

          const planets = data.planets
          // Cells at the corners are triangles and hold fewer rows comfortably.
          const isNarrow = [2, 3, 5, 6, 8, 9, 11, 12].includes(house)
          const lineHeight = planets.length > 3 ? 3.4 : 4
          const startY = cy - ((planets.length - 1) * lineHeight) / 2 + 1.2

          return (
            <g key={house}>
              <polygon
                points={points}
                fill={house === 1 ? 'rgba(249,191,36,.18)' : 'transparent'}
              />

              {/* Sign number in the corner of each cell. */}
              <text
                x={cx} y={isNarrow ? cy - 5.5 : cy - 9}
                textAnchor="middle"
                fill="#b9b2a0" className="font-sans"
                style={{ fontSize: '3.1px', fontWeight: 500 }}
              >
                {data.sign + 1}
              </text>

              {house === 1 && (
                <text
                  x={cx} y={cy - 13.5} textAnchor="middle"
                  fill="#d97706" className="font-sans"
                  style={{ fontSize: '3.2px', fontWeight: 700, letterSpacing: '0.3px' }}
                >
                  LAGNA
                </text>
              )}

              {planets.map((p, index) => {
                const isSelected = selectedPlanet === p.planet
                return (
                  <text
                    key={p.planet}
                    x={cx}
                    y={startY + index * lineHeight}
                    textAnchor="middle"
                    onClick={() => onSelectPlanet?.(p.planet)}
                    className={cn('font-sans', onSelectPlanet && 'cursor-pointer')}
                    fill={isSelected ? '#b45309' : PLANET_INK[p.planet]}
                    style={{ fontSize: '3.7px', fontWeight: isSelected ? 800 : 700 }}
                  >
                    {p.planetName.slice(0, 2)}
                    {p.retrograde && (
                      <tspan fill="#8a8578" style={{ fontSize: '2.6px' }}>
                        {' '}℞
                      </tspan>
                    )}
                    {p.combust && (
                      <tspan fill="#8a8578" style={{ fontSize: '2.6px' }}>
                        {' '}c
                      </tspan>
                    )}
                  </text>
                )
              })}
            </g>
          )
        })}
      </svg>

      <figcaption className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-ink-400">
        <span>Small numbers are the Rashi (1 = Aries).</span>
        <span><span className="font-bold text-ink-600">℞</span> retrograde</span>
        <span><span className="font-bold text-ink-600">c</span> combust</span>
      </figcaption>
    </figure>
  )
}
