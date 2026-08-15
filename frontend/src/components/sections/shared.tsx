import type { ReactNode } from 'react'
import type { Condition, Relationship } from '@/types'
import { Badge, Evidence, StatusPill } from '@/components/ui'
import { cn, maitriTone } from '@/lib/utils'

/** Panchadha Maitri chip with the underlying natural + temporary pair on hover. */
export function MaitriChip({
  relationship, showParts = false,
}: { relationship: Relationship; showParts?: boolean }) {
  const value = relationship.panchadhaMaitri
  const tooltip =
    value === 'Self'
      ? 'A planet is not related to itself under this rule set.'
      : `Natural: ${relationship.naturalRelationship} · Temporary: ${relationship.temporaryRelationship}`

  return (
    <span className="inline-flex items-center gap-1.5">
      <Badge className={cn('border', maitriTone(value))} title={tooltip}>
        {value}
      </Badge>
      {showParts && value !== 'Self' && (
        <span className="text-[11px] text-ink-500">
          {relationship.naturalRelationship} + {relationship.temporaryRelationship}
        </span>
      )}
    </span>
  )
}

/** The full evidence trail behind one Panchadha Maitri result. */
export function MaitriEvidence({ relationship }: { relationship: Relationship }) {
  const e = relationship.evidence as Record<string, string | number>
  return (
    <Evidence rule="MAITRI_003" source="Custom Rule Engine + PyJHora tables">
      {e.naturalRule && <p>{String(e.naturalRule)}</p>}
      {e.temporaryRule && <p>{String(e.temporaryRule)}</p>}
      {e.combination && (
        <p className="font-medium text-ink-900">{String(e.combination)}</p>
      )}
      {e.note && <p className="italic">{String(e.note)}</p>}
    </Evidence>
  )
}

/** A single relationship rendered as a compact three-part row. */
export function RelationshipTriple({ relationship }: { relationship: Relationship }) {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5">
      <LabeledValue label="Natural" value={relationship.naturalRelationship} />
      <LabeledValue label="Temporary" value={relationship.temporaryRelationship} />
      <span className="flex items-center gap-1.5">
        <span className="label">Panchadha</span>
        <MaitriChip relationship={relationship} />
      </span>
    </div>
  )
}

export function LabeledValue({ label, value }: { label: string; value: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="label">{label}</span>
      <span className="text-sm text-ink-900">{value}</span>
    </span>
  )
}

/** Renders a list of rule conditions with individual status and evidence. */
export function ConditionList({ conditions }: { conditions: Condition[] }) {
  return (
    <ol className="space-y-2.5">
      {conditions.map((condition, index) => (
        <li
          key={index}
          className="rounded-md border border-ink-200 bg-ink-50/60 px-3 py-2.5"
        >
          <div className="flex flex-wrap items-start justify-between gap-2">
            <p className="min-w-0 flex-1 text-[13px] font-medium leading-snug text-ink-900">
              {(condition as any).number !== undefined && (
                <span className="mr-1.5 font-mono text-[11px] text-ink-400">
                  Condition {(condition as any).number}
                </span>
              )}
              {condition.title}
            </p>
            <StatusPill status={condition.status} />
          </div>
          {(condition as any).statement && (
            <p className="mt-1 text-[12px] italic leading-relaxed text-ink-500">
              {(condition as any).statement}
            </p>
          )}
          <p className="mt-1.5 text-[12px] leading-relaxed text-ink-700">
            {condition.evidence}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {(condition as any).group && (
              <Badge
                className={
                  (condition as any).group === 'Core formation'
                    ? 'border-ink-800 bg-white text-ink-800'
                    : 'border-ink-200 bg-white text-ink-500'
                }
                title={
                  (condition as any).group === 'Core formation'
                    ? 'This condition determines whether the yoga is formed.'
                    : 'Reported independently. It does not affect the formation status.'
                }
              >
                {(condition as any).group}
              </Badge>
            )}
            {(condition as any).ruleId && (
              <Badge>Rule: {(condition as any).ruleId}</Badge>
            )}
          </div>
        </li>
      ))}
    </ol>
  )
}

/** A neutral horizontal bar for a numeric magnitude. Carries no verdict. */
export function ValueBar({
  value, max, className,
}: { value: number; max: number; className?: string }) {
  const pct = max > 0 ? Math.min(100, Math.max(0, (Math.abs(value) / max) * 100)) : 0
  const negative = value < 0
  return (
    <span
      className={cn('inline-block h-1.5 w-full min-w-[48px] rounded-full bg-ink-100', className)}
      role="presentation"
    >
      <span
        className={cn('block h-full rounded-full', negative ? 'bg-ink-400' : 'bg-ink-700')}
        style={{ width: `${pct}%` }}
      />
    </span>
  )
}

export function SourceBadges({ sources }: { sources?: Record<string, any> | null }) {
  if (!sources) return null
  const entries: { source?: string; rule?: string | null }[] =
    'source' in sources ? [sources as any] : Object.values(sources)
  const seen = new Set<string>()
  const badges: ReactNode[] = []
  entries.forEach((entry, index) => {
    const key = `${entry.source}|${entry.rule}`
    if (!entry.source || seen.has(key)) return
    seen.add(key)
    badges.push(
      <Badge key={index}>
        {entry.source}
        {entry.rule ? ` · ${entry.rule}` : ''}
      </Badge>,
    )
  })
  if (badges.length === 0) return null
  return <div className="mt-3 flex flex-wrap gap-1.5">{badges}</div>
}
