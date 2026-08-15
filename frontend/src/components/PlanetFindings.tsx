import { useState } from 'react'
import { cn } from '@/lib/utils'

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

type SectionKey = keyof Pick<
  Findings,
  'favourable' | 'yogas' | 'challenging' | 'doshas' | 'interpretive' | 'neutral'
>

interface SectionSpec {
  key: SectionKey
  title: string
  subtitle: string
  emoji: string
  empty: string
  collapsed?: boolean
  dot: string
  ring: string
  head: string
  titleC: string
  subC: string
  bullet: string
  card: string
  btn: string
  panel: string
}

const SECTIONS: SectionSpec[] = [
  {
    key: 'favourable',
    title: 'Strengths',
    subtitle: 'Placements the classics count as favourable',
    emoji: '🌿',
    empty: 'Nothing in this group for this planet.',
    dot: 'bg-good-500', ring: 'ring-good-200',
    head: 'from-good-100 to-good-50',
    titleC: 'text-good-800', subC: 'text-good-700/80', bullet: 'text-good-600',
    card: 'border-good-200/80 bg-good-50/60 hover:bg-good-50',
    btn: 'text-good-700 hover:bg-good-100 border-good-300',
    panel: 'border-good-200 bg-white',
  },
  {
    key: 'yogas',
    title: 'Yogas formed',
    subtitle: 'Combinations this planet takes part in',
    emoji: '🌸',
    empty: 'This planet takes part in none of the yogas checked.',
    dot: 'bg-emerald-600', ring: 'ring-emerald-200',
    head: 'from-emerald-100 to-teal-50',
    titleC: 'text-emerald-900', subC: 'text-emerald-800/75', bullet: 'text-emerald-600',
    card: 'border-emerald-200/80 bg-emerald-50/60 hover:bg-emerald-50',
    btn: 'text-emerald-800 hover:bg-emerald-100 border-emerald-300',
    panel: 'border-emerald-200 bg-white',
  },
  {
    key: 'challenging',
    title: 'Challenges',
    subtitle: 'Placements the classics count as difficult',
    emoji: '🔥',
    empty: 'Nothing in this group for this planet.',
    dot: 'bg-hard-500', ring: 'ring-hard-200',
    head: 'from-hard-100 to-hard-50',
    titleC: 'text-hard-800', subC: 'text-hard-700/80', bullet: 'text-hard-500',
    card: 'border-hard-200/80 bg-hard-50/60 hover:bg-hard-50',
    btn: 'text-hard-700 hover:bg-hard-100 border-hard-300',
    panel: 'border-hard-200 bg-white',
  },
  {
    key: 'doshas',
    title: 'Doshas formed',
    subtitle: 'Afflictions this planet takes part in',
    emoji: '⚠️',
    empty: 'No dosha in the set checked involves this planet.',
    dot: 'bg-red-700', ring: 'ring-red-200',
    head: 'from-red-100 to-orange-50',
    titleC: 'text-red-900', subC: 'text-red-800/75', bullet: 'text-red-600',
    card: 'border-red-200/80 bg-red-50/60 hover:bg-red-50',
    btn: 'text-red-800 hover:bg-red-100 border-red-300',
    panel: 'border-red-200 bg-white',
  },
  {
    key: 'interpretive',
    title: 'Your call',
    subtitle: 'Points the classics leave open — the reason is under Explain',
    emoji: '🤔',
    empty: 'Nothing here needs your judgement for this planet.',
    dot: 'bg-pink-500', ring: 'ring-pink-200',
    head: 'from-pink-100 to-fuchsia-50',
    titleC: 'text-pink-800', subC: 'text-pink-700/80', bullet: 'text-pink-500',
    card: 'border-pink-200/80 bg-pink-50/60 hover:bg-pink-50',
    btn: 'text-pink-700 hover:bg-pink-100 border-pink-300',
    panel: 'border-pink-200 bg-white',
  },
  {
    key: 'neutral',
    title: 'Neutral & not applicable',
    subtitle: 'Checks that came out on neither side, or cannot apply',
    emoji: '⚖️',
    empty: 'Nothing in this group for this planet.',
    collapsed: true,
    dot: 'bg-amber-500', ring: 'ring-amber-200',
    head: 'from-amber-100 to-amber-50',
    titleC: 'text-amber-800', subC: 'text-amber-800/75', bullet: 'text-amber-500',
    card: 'border-amber-200/80 bg-amber-50/50 hover:bg-amber-50',
    btn: 'text-amber-800 hover:bg-amber-100 border-amber-300',
    panel: 'border-amber-200 bg-white',
  },
]

export function PlanetFindings({ findings }: { findings: Findings }) {
  return (
    <div className="space-y-5">
      {SECTIONS.map((section) => (
        <Section
          key={section.key}
          section={section}
          items={findings[section.key] ?? []}
        />
      ))}

      <p className="px-1 text-center text-[12px] leading-relaxed text-ink-400">
        {findings.note}
      </p>
    </div>
  )
}

function Section({
  section, items,
}: { section: SectionSpec; items: Finding[] }) {
  const collapsible = Boolean(section.collapsed)
  const [open, setOpen] = useState(!collapsible)

  return (
    <section className={cn('panel overflow-hidden ring-1', section.ring)}>
      <header
        className={cn(
          'flex w-full items-center gap-3 bg-gradient-to-r px-5 py-3.5 text-left',
          section.head,
          collapsible && 'cursor-pointer',
        )}
        role={collapsible ? 'button' : undefined}
        tabIndex={collapsible ? 0 : undefined}
        aria-expanded={collapsible ? open : undefined}
        onClick={collapsible ? () => setOpen((o) => !o) : undefined}
        onKeyDown={
          collapsible
            ? (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  setOpen((o) => !o)
                }
              }
            : undefined
        }
      >
        <span className="text-2xl leading-none" aria-hidden>{section.emoji}</span>
        <div className="min-w-0 flex-1">
          <h3 className={cn('font-display text-lg font-bold leading-tight',
                            section.titleC)}>
            {section.title}
          </h3>
          <p className={cn('text-[12px] leading-snug', section.subC)}>
            {section.subtitle}
          </p>
        </div>
        <span
          className={cn(
            'grid h-8 min-w-8 place-items-center rounded-full px-2.5',
            'font-display text-base font-bold text-white shadow-sm',
            items.length === 0 ? 'bg-ink-300' : section.dot,
          )}
        >
          {items.length}
        </span>
        {collapsible && (
          <span
            className={cn('text-lg font-bold transition-transform', section.titleC,
                          open && 'rotate-90')}
            aria-hidden
          >
            ›
          </span>
        )}
      </header>

      <div className={cn('print-open p-3 sm:p-4', open ? 'block' : 'hidden')}>
        {items.length === 0 ? (
          <p className="py-5 text-center text-sm text-ink-400">{section.empty}</p>
        ) : (
          <ul className="space-y-2">
            {items.map((item) => (
              <Item key={item.key} item={item} section={section} />
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}

function Item({ item, section }: { item: Finding; section: SectionSpec }) {
  const [open, setOpen] = useState(false)
  // The pink section is entirely 'your call', so the pill would just repeat
  // the heading. It is only useful inside the yellow group.
  const showPill = section.key === 'neutral' && Boolean(item.openLabel)

  return (
    <li
      className={cn('rounded-2xl border transition-colors print-avoid-break',
                    section.card)}
    >
      <div className="flex items-start gap-3 px-4 py-3">
        <span className={cn('mt-[3px] text-lg leading-none', section.bullet)} aria-hidden>
          •
        </span>

        <p className="min-w-0 flex-1 text-[15px] font-semibold leading-snug text-ink-800">
          {item.text}
          {showPill && (
            <span
              className={cn(
                'ml-2 inline-block whitespace-nowrap rounded-full border px-2 py-[1px]',
                'align-middle text-[10.5px] font-bold uppercase tracking-wide',
                'border-amber-200 bg-white text-amber-700',
              )}
            >
              {item.openLabel}
            </span>
          )}
        </p>

        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          className={cn(
            'no-print shrink-0 rounded-full border bg-white/80 px-3 py-1',
            'text-[12px] font-bold transition-colors',
            section.btn,
          )}
        >
          {open ? 'Hide' : 'Explain'}
        </button>
      </div>

      <div className={cn('print-open px-4 pb-4', open ? 'block' : 'hidden')}>
        <div className={cn('animate-pop rounded-2xl border px-4 py-3 shadow-sm',
                           section.panel)}>
          <p className="text-[13.5px] leading-relaxed text-ink-700">
            {item.explanation}
          </p>

          {item.detail.length > 0 && (
            <dl className="mt-3 grid gap-x-6 gap-y-1.5 border-t border-black/5 pt-3 sm:grid-cols-2">
              {item.detail.map((row, index) => (
                <div key={index} className="flex items-baseline justify-between gap-3">
                  <dt className="text-[12px] text-ink-500">{row.label}</dt>
                  <dd className="text-[12.5px] font-semibold tabular text-ink-800">
                    {row.value}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </div>
    </li>
  )
}
