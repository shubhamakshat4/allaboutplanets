import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const NOT_DEFINED = 'Not defined in selected rule set'
export const NOT_AVAILABLE = 'Not available'
export const NOT_APPLICABLE = 'Not applicable'

/** Renders booleans as Yes/No while passing through the explicit "not …" strings. */
export function yesNo(value: boolean | string | null | undefined): string {
  if (value === true) return 'Yes'
  if (value === false) return 'No'
  if (value === null || value === undefined) return NOT_AVAILABLE
  return String(value)
}

export function isUnknown(value: unknown): boolean {
  return value === NOT_DEFINED || value === NOT_AVAILABLE || value === NOT_APPLICABLE
}

export function ordinal(n: number): string {
  const mod100 = n % 100
  if (mod100 >= 10 && mod100 <= 20) return `${n}th`
  const suffix = { 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] ?? 'th'
  return `${n}${suffix}`
}

/** Colour band per Panchadha Maitri value. Neutral, not evaluative — the palette
 *  distinguishes categories so tables scan quickly; it implies no judgement. */
export function maitriTone(value: string): string {
  switch (value) {
    case 'Ati Mitra':
      return 'bg-emerald-50 text-emerald-800 border-emerald-200'
    case 'Mitra':
      return 'bg-teal-50 text-teal-800 border-teal-200'
    case 'Sama':
      return 'bg-ink-100 text-ink-700 border-ink-200'
    case 'Shatru':
      return 'bg-amber-50 text-amber-800 border-amber-200'
    case 'Ati Shatru':
      return 'bg-rose-50 text-rose-800 border-rose-200'
    default:
      return 'bg-ink-50 text-ink-500 border-ink-200'
  }
}

export function debounce<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let timer: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

export const PLANET_GLYPHS: Record<number, string> = {
  0: '☉', 1: '☽', 2: '♂', 3: '☿', 4: '♃', 5: '♀', 6: '♄', 7: '☊', 8: '☋',
}

/** Traditional colour associated with each graha, used to give every planet
 *  its own identity across the app. */
export interface PlanetTheme {
  grad: string      // header gradient
  chip: string      // selected pill
  soft: string      // unselected pill / tint
  text: string      // accent text
  ring: string
}

export const PLANET_THEME: Record<number, PlanetTheme> = {
  0: { grad: 'from-amber-400 to-orange-500', chip: 'bg-orange-500 text-white',
       soft: 'bg-orange-50 text-orange-700 border-orange-200',
       text: 'text-orange-600', ring: 'ring-orange-200' },
  1: { grad: 'from-sky-300 to-cyan-400', chip: 'bg-cyan-500 text-white',
       soft: 'bg-cyan-50 text-cyan-700 border-cyan-200',
       text: 'text-cyan-600', ring: 'ring-cyan-200' },
  2: { grad: 'from-red-400 to-rose-600', chip: 'bg-rose-600 text-white',
       soft: 'bg-rose-50 text-rose-700 border-rose-200',
       text: 'text-rose-600', ring: 'ring-rose-200' },
  3: { grad: 'from-emerald-400 to-teal-500', chip: 'bg-emerald-600 text-white',
       soft: 'bg-emerald-50 text-emerald-700 border-emerald-200',
       text: 'text-emerald-600', ring: 'ring-emerald-200' },
  4: { grad: 'from-yellow-400 to-amber-500', chip: 'bg-amber-500 text-white',
       soft: 'bg-amber-50 text-amber-800 border-amber-200',
       text: 'text-amber-600', ring: 'ring-amber-200' },
  5: { grad: 'from-pink-300 to-fuchsia-400', chip: 'bg-fuchsia-500 text-white',
       soft: 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200',
       text: 'text-fuchsia-600', ring: 'ring-fuchsia-200' },
  6: { grad: 'from-indigo-500 to-violet-700', chip: 'bg-violet-700 text-white',
       soft: 'bg-violet-50 text-violet-700 border-violet-200',
       text: 'text-violet-600', ring: 'ring-violet-200' },
  7: { grad: 'from-purple-400 to-slate-600', chip: 'bg-purple-600 text-white',
       soft: 'bg-purple-50 text-purple-700 border-purple-200',
       text: 'text-purple-600', ring: 'ring-purple-200' },
  8: { grad: 'from-stone-400 to-amber-700', chip: 'bg-stone-600 text-white',
       soft: 'bg-stone-100 text-stone-700 border-stone-300',
       text: 'text-stone-600', ring: 'ring-stone-200' },
}

export const PLANET_NAMES: Record<number, string> = {
  0: 'Sun', 1: 'Moon', 2: 'Mars', 3: 'Mercury', 4: 'Jupiter',
  5: 'Venus', 6: 'Saturn', 7: 'Rahu', 8: 'Ketu',
}

export const SIGN_ABBR = [
  'Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi',
]

export function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
