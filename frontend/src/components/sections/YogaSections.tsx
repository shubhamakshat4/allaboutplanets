import { useState } from 'react'
import type { PlanetAnalysis, Yoga, YogaParticipationRow } from '@/types'
import {
  Badge, Button, Empty, StatusPill, Table, TableWrap, Td, Th,
} from '@/components/ui'
import { ConditionList, MaitriChip } from './shared'
import { cn } from '@/lib/utils'

/* --- SECTION 10: yogas involving the selected planet ---------------------- */
export function YogaParticipationSection({
  a, filter, presentOnly,
}: { a: PlanetAnalysis; filter: string; presentOnly: boolean }) {
  const [openKey, setOpenKey] = useState<string | null>(null)

  const rows = a.yogaParticipation.filter((row) => {
    if (presentOnly && !row.present) return false
    const q = filter.trim().toLowerCase()
    if (!q) return true
    return [
      row.name, row.role, row.status,
      ...row.otherParticipants.map((p) => p.planetName),
    ].some((value) => value.toLowerCase().includes(q))
  })

  if (a.yogaParticipation.length === 0) {
    return <Empty>{a.planetName} takes part in none of the 22 V1 yoga definitions.</Empty>
  }
  if (rows.length === 0) return <Empty>No yoga matches the current filter.</Empty>

  return (
    <div className="space-y-3">
      <TableWrap>
        <Table className="min-w-[720px]">
          <thead>
            <tr>
              <Th>Yoga</Th>
              <Th>Status</Th>
              <Th>{a.planetName}'s role</Th>
              <Th>Other participants</Th>
              <Th align="center" className="no-print">Evidence</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key} className="hover:bg-ink-50">
                <Td className="font-medium">
                  {row.name}
                  <span className="ml-2 font-mono text-[10px] text-ink-400">{row.ruleId}</span>
                </Td>
                <Td><StatusPill status={row.status} /></Td>
                <Td>{row.role}</Td>
                <Td>
                  {row.otherParticipants.length === 0
                    ? <span className="text-ink-300">—</span>
                    : row.otherParticipants.map((p) => p.planetName).join(', ')}
                </Td>
                <Td align="center" className="no-print">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setOpenKey(openKey === row.key ? null : row.key)}
                  >
                    {openKey === row.key ? 'Hide' : 'View'}
                  </Button>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </TableWrap>

      {rows.map((row) => (
        <div
          key={`ev-${row.key}`}
          className={cn(
            'print-expand rounded-md border border-ink-200 p-4',
            openKey === row.key ? 'block' : 'hidden',
          )}
        >
          <YogaEvidence row={row} />
        </div>
      ))}
    </div>
  )
}

function YogaEvidence({ row }: { row: YogaParticipationRow }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h4 className="font-serif text-sm font-semibold text-ink-900">{row.name}</h4>
        <div className="flex items-center gap-2">
          <StatusPill status={row.status} />
          <Badge>{row.ruleId}</Badge>
        </div>
      </div>

      {row.associationType && (
        <p className="text-[13px] text-ink-700">
          <span className="label mr-2">Association</span>{row.associationType}
        </p>
      )}
      {row.evidence && <p className="text-[13px] text-ink-700">{row.evidence}</p>}

      <FormationSummary yoga={row as unknown as Record<string, unknown>} />
      <ConditionList conditions={row.conditions} />

      {row.instances.length > 0 && (
        <div className="space-y-2">
          <p className="label">Detected instances</p>
          {row.instances.map((instance, index) => (
            <YogaInstance key={index} instance={instance} />
          ))}
        </div>
      )}
    </div>
  )
}

/** Shown for yogas that separate a core formation from strengthening conditions. */
function FormationSummary({ yoga }: { yoga: Record<string, unknown> }) {
  const total = yoga.strengtheningConditionsTotal as number | undefined
  if (typeof total !== 'number') return null
  const met = yoga.strengtheningConditionsSatisfied as number
  const core = yoga.coreFormation as boolean

  return (
    <div className="rounded-md border border-ink-200 bg-ink-50/60 px-3 py-2.5">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5">
        <span className="flex items-center gap-1.5">
          <span className="label">Core formation</span>
          <StatusPill status={core ? 'Present' : 'Not Present'} />
        </span>
        <span className="flex items-center gap-1.5">
          <span className="label">Strengthening conditions</span>
          <span className="font-mono text-[13px] tabular text-ink-900">
            {met} of {total} satisfied
          </span>
        </span>
      </div>
      {typeof yoga.note === 'string' && (
        <p className="mt-2 border-t border-ink-200 pt-2 text-[12px] leading-relaxed text-ink-600">
          {yoga.note}
        </p>
      )}
    </div>
  )
}

function YogaInstance({ instance }: { instance: Record<string, any> }) {
  const skip = new Set([
    'participants', 'participantNames', 'relationship', 'conditions',
    'neechaBhangaConditions',
  ])

  return (
    <div className="rounded-md border border-ink-200 bg-ink-50/60 px-3 py-2.5">
      <dl className="grid gap-x-5 gap-y-1.5 sm:grid-cols-2">
        {Object.entries(instance)
          .filter(([key, value]) =>
            !skip.has(key) && value !== null && value !== undefined && value !== '')
          .map(([key, value]) => (
            <div key={key} className="min-w-0">
              <dt className="label">{humanise(key)}</dt>
              <dd className="text-[13px] leading-snug text-ink-800">{render(value)}</dd>
            </div>
          ))}
      </dl>
      {instance.relationship && (
        <div className="mt-2 border-t border-ink-200 pt-2">
          <MaitriChip relationship={instance.relationship} showParts />
        </div>
      )}
      {Array.isArray(instance.conditions) && instance.conditions.length > 0 && (
        <div className="mt-3">
          <ConditionList conditions={instance.conditions} />
        </div>
      )}
    </div>
  )
}

/* --- SECTION 11: all 22 yoga checks -------------------------------------- */
export function AllYogasSection({
  yogas, selectedPlanet, filter,
}: { yogas: Yoga[]; selectedPlanet: number; filter: string }) {
  const [openKey, setOpenKey] = useState<string | null>(null)

  const rows = yogas.filter((yoga) => {
    const q = filter.trim().toLowerCase()
    if (!q) return true
    return [yoga.name, yoga.status, yoga.summary,
      ...yoga.participants.map((p) => p.planetName)]
      .some((value) => value.toLowerCase().includes(q))
  })

  const presentCount = yogas.filter((y) => y.present).length

  return (
    <div className="space-y-3">
      <p className="text-[12px] text-ink-500">
        {presentCount} of {yogas.length} yoga definitions are satisfied in this chart.
        Participation is highlighted for the selected planet.
      </p>

      {rows.length === 0 ? (
        <Empty>No yoga matches the current filter.</Empty>
      ) : (
        <TableWrap>
          <Table className="min-w-[760px]">
            <thead>
              <tr>
                <Th>Yoga</Th>
                <Th>Status</Th>
                <Th>Participants</Th>
                <Th align="center" className="no-print">Evidence</Th>
              </tr>
            </thead>
            <tbody>
              {rows.map((yoga) => {
                const involves =
                  yoga.participants.some((p) => p.planet === selectedPlanet) ||
                  yoga.instances.some((i) => (i.participants ?? []).includes(selectedPlanet))
                return (
                  <tr
                    key={yoga.key}
                    className={cn('hover:bg-ink-50', involves && 'bg-accent-50/50')}
                  >
                    <Td className="font-medium">
                      {yoga.name}
                      <span className="ml-2 font-mono text-[10px] text-ink-400">
                        {yoga.ruleId}
                      </span>
                      {involves && <Badge className="ml-2">Involves this planet</Badge>}
                    </Td>
                    <Td><StatusPill status={yoga.status} /></Td>
                    <Td>
                      {yoga.participants.length === 0
                        ? <span className="text-ink-300">—</span>
                        : yoga.participants
                          .map((p) => `${p.planetName} (${p.role})`)
                          .join(', ')}
                    </Td>
                    <Td align="center" className="no-print">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setOpenKey(openKey === yoga.key ? null : yoga.key)}
                      >
                        {openKey === yoga.key ? 'Hide' : 'View'}
                      </Button>
                    </Td>
                  </tr>
                )
              })}
            </tbody>
          </Table>
        </TableWrap>
      )}

      {rows.map((yoga) => (
        <div
          key={`ev-${yoga.key}`}
          className={cn(
            'print-expand rounded-md border border-ink-200 p-4',
            openKey === yoga.key ? 'block' : 'hidden',
          )}
        >
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h4 className="font-serif text-sm font-semibold text-ink-900">{yoga.name}</h4>
            <div className="flex items-center gap-2">
              <StatusPill status={yoga.status} />
              <Badge>{yoga.ruleId}</Badge>
            </div>
          </div>
          <p className="mb-3 text-[12px] italic leading-relaxed text-ink-500">{yoga.summary}</p>
          <div className="mb-3">
            <FormationSummary yoga={yoga as unknown as Record<string, unknown>} />
          </div>
          <ConditionList conditions={yoga.conditions} />
          {yoga.instances.length > 0 && (
            <div className="mt-3 space-y-2">
              <p className="label">Detected instances</p>
              {yoga.instances.map((instance, index) => (
                <YogaInstance key={index} instance={instance} />
              ))}
            </div>
          )}
          {typeof yoga.note === 'string' && (
            <p className="mt-3 text-[12px] italic text-ink-500">{yoga.note}</p>
          )}
        </div>
      ))}
    </div>
  )
}

function humanise(key: string): string {
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (c) => c.toUpperCase())
    .trim()
}

function render(value: unknown): string {
  if (Array.isArray(value)) return value.map((v) => render(v)).join(', ')
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${humanise(k)}: ${render(v)}`)
      .join(' · ')
  }
  return String(value)
}
