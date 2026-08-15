import type { PlanetRow } from '@/types'
import { cn, PLANET_THEME } from '@/lib/utils'

interface Props {
  planets: PlanetRow[]
  selected: number | null
  onSelect: (planetId: number) => void
  size?: 'sm' | 'lg'
}

export function PlanetSelector({ planets, selected, onSelect, size = 'sm' }: Props) {
  if (size === 'lg') {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {planets.map((planet) => {
          const theme = PLANET_THEME[planet.planet]
          const active = selected === planet.planet
          return (
            <button
              key={planet.planet}
              type="button"
              onClick={() => onSelect(planet.planet)}
              aria-pressed={active}
              className={cn(
                'group relative overflow-hidden rounded-xl2 border border-white/70 p-4 text-left',
                'shadow-card transition-all hover:-translate-y-0.5 hover:shadow-lift',
                active && 'ring-[3px] ring-offset-2 ring-offset-cream-50',
                active && theme.ring,
              )}
            >
              <span
                className={cn('absolute inset-0 bg-gradient-to-br opacity-90', theme.grad)}
                aria-hidden
              />
              <span className="relative block">
                <span className="flex items-start justify-between">
                  <span className="text-4xl leading-none text-white drop-shadow" aria-hidden>
                    {planet.symbol}
                  </span>
                  {planet.retrograde && (
                    <span
                      title="Retrograde"
                      className="rounded-full bg-white/30 px-2 py-0.5 text-[11px] font-bold text-white backdrop-blur"
                    >
                      ℞
                    </span>
                  )}
                </span>
                <span className="mt-3 block font-display text-xl font-bold text-white drop-shadow-sm">
                  {planet.planetName}
                </span>
                <span className="mt-0.5 block text-[12.5px] font-semibold text-white/90">
                  {planet.rashiName} · house {planet.bhava}
                </span>
              </span>
            </button>
          )
        })}
      </div>
    )
  }

  return (
    <div className="flex flex-wrap gap-2">
      {planets.map((planet) => {
        const theme = PLANET_THEME[planet.planet]
        const active = selected === planet.planet
        return (
          <button
            key={planet.planet}
            type="button"
            onClick={() => onSelect(planet.planet)}
            aria-pressed={active}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5',
              'text-[13px] font-bold shadow-sm transition-all active:scale-95',
              active
                ? cn(theme.chip, 'border-transparent shadow-card')
                : cn(theme.soft, 'hover:brightness-95'),
            )}
          >
            <span className="text-[15px] leading-none" aria-hidden>{planet.symbol}</span>
            {planet.planetName}
          </button>
        )
      })}
    </div>
  )
}
