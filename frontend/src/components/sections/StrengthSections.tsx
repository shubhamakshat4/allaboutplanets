import type { PlanetAnalysis } from '@/types'
import {
  Badge, Empty, Evidence, Field, FieldGrid, Note, StatusPill,
  Table, TableWrap, Td, Th,
} from '@/components/ui'
import { ConditionList, MaitriChip, ValueBar } from './shared'

/* --- SECTION R ----------------------------------------------------------- */
export function ShadbalaSection({ a }: { a: PlanetAnalysis }) {
  const s = a.shadbala
  if (!s.available) {
    return (
      <div className="space-y-3">
        <Field label="Shadbala" value={s.status} />
        <Empty>{s.reason}</Empty>
      </div>
    )
  }

  const groups: { name: string; total: number | null; components?: any[] }[] = [
    { name: 'Sthana Bala', total: s.sthanaBala.total, components: s.sthanaBala.components },
    { name: 'Dig Bala', total: s.digBala.total },
    { name: 'Kala Bala', total: s.kalaBala.total, components: s.kalaBala.components },
    { name: 'Cheshta Bala', total: s.cheshtaBala.total },
    { name: 'Naisargika Bala', total: s.naisargikaBala.total },
    { name: 'Drik Bala', total: s.drikBala.total },
  ]

  const maxGroup = Math.max(...groups.map((g) => Math.abs(g.total ?? 0)), 1)

  return (
    <div className="space-y-6">
      <FieldGrid cols={4}>
        <Field label="Total Shadbala (Virupas)" value={fmt(s.totalVirupa)} mono />
        <Field label="Total Shadbala (Rupas)" value={fmt(s.totalRupa)} mono />
        <Field label="Required minimum (Rupas)" value={fmt(s.requiredRupa)} mono />
        <Field label="Ratio to required" value={fmt(s.ratioToRequired)} mono />
      </FieldGrid>

      <Note>
        Values are reported exactly as PyJHora calculates them. 1 Rupa = 60 Virupas.
        No qualitative label is applied to any figure on this page.
      </Note>

      <div>
        <p className="label mb-2">Six-fold breakdown</p>
        <TableWrap>
          <Table className="min-w-[560px]">
            <thead>
              <tr>
                <Th>Bala</Th>
                <Th align="right">Virupas</Th>
                <Th className="w-1/3">Magnitude</Th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => (
                <tr key={group.name} className="hover:bg-ink-50">
                  <Td className="font-medium">{group.name}</Td>
                  <Td align="right" mono>{fmt(group.total)}</Td>
                  <Td>
                    {group.total !== null && (
                      <ValueBar value={group.total} max={maxGroup} />
                    )}
                  </Td>
                </tr>
              ))}
              <tr className="bg-ink-50 font-medium">
                <Td>Total</Td>
                <Td align="right" mono>{fmt(s.totalVirupa)}</Td>
                <Td>{''}</Td>
              </tr>
            </tbody>
          </Table>
        </TableWrap>
      </div>

      <ComponentTable title="Sthana Bala components" rows={s.sthanaBala.components} />
      <ComponentTable title="Kala Bala components" rows={s.kalaBala.components} />

      {s.drikBala.contributions && s.drikBala.contributions.length > 0 && (
        <div>
          <p className="label mb-2">Drik Bala — contributing aspects</p>
          <TableWrap>
            <Table className="min-w-[420px]">
              <thead>
                <tr>
                  <Th>Aspecting planet</Th>
                  <Th align="right">Virupas</Th>
                </tr>
              </thead>
              <tbody>
                {s.drikBala.contributions.map((c: any, index: number) => (
                  <tr key={index} className="hover:bg-ink-50">
                    <Td>{c.fromPlanetName}</Td>
                    <Td align="right" mono>{fmt(c.virupa)}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </TableWrap>
          <p className="mt-2 text-[11px] text-ink-400">
            From PyJHora's planet aspect relationship table.
          </p>
        </div>
      )}

      <Evidence source="PyJHora" label="Calculation source">
        <p>{s.sources.methodology}</p>
        <p className="text-ink-500">{s.units.virupa}</p>
        <p className="text-ink-500">{s.units.note}</p>
      </Evidence>
    </div>
  )
}

function ComponentTable({ title, rows }: { title: string; rows: any[] }) {
  if (!rows?.length) return null
  const max = Math.max(...rows.map((r) => Math.abs(r.virupa ?? 0)), 1)
  return (
    <div>
      <p className="label mb-2">{title}</p>
      <TableWrap>
        <Table className="min-w-[520px]">
          <thead>
            <tr>
              <Th>Component</Th>
              <Th align="right">Virupas</Th>
              <Th className="w-1/3">Magnitude</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.name} className="hover:bg-ink-50">
                <Td>{row.name}</Td>
                <Td align="right" mono>{fmt(row.virupa)}</Td>
                <Td>{row.virupa !== null && <ValueBar value={row.virupa} max={max} />}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </TableWrap>
    </div>
  )
}

/* --- SECTION S ----------------------------------------------------------- */
export function DivisionalSection({ a }: { a: PlanetAnalysis }) {
  return (
    <div className="space-y-3">
      <TableWrap>
        <Table className="min-w-[640px]">
          <thead>
            <tr>
              <Th>Varga</Th>
              <Th>Rashi</Th>
              <Th>Rashi Lord</Th>
              <Th align="right">Degree</Th>
              <Th>Dignity</Th>
              <Th align="center">Same as D1</Th>
            </tr>
          </thead>
          <tbody>
            {a.divisionalPositions.map((v: any) => (
              <tr key={v.factor} className="hover:bg-ink-50">
                <Td className="whitespace-nowrap font-medium">{v.name}</Td>
                {v.available ? (
                  <>
                    <Td>{v.rashiName}</Td>
                    <Td>{v.rashiLordName}</Td>
                    <Td align="right" mono>{v.degreeDms ?? '—'}</Td>
                    <Td>{v.dignity}</Td>
                    <Td align="center">
                      {v.sameAsD1
                        ? <Badge className="border-ink-800 bg-ink-800 text-white">Yes</Badge>
                        : <span className="text-ink-300">—</span>}
                    </Td>
                  </>
                ) : (
                  <Td className="italic text-ink-400" align="left">{v.status}</Td>
                )}
              </tr>
            ))}
          </tbody>
        </Table>
      </TableWrap>
      <p className="text-[11px] text-ink-400">
        Divisional charts are calculated by PyJHora using its standard varga methods.
        The D1/D9 match is the Vargottama condition, reported in the Navamsha section.
      </p>
    </div>
  )
}

/* --- SECTION T ----------------------------------------------------------- */
export function DispositorSection({ a }: { a: PlanetAnalysis }) {
  const d = a.dispositorChain
  return (
    <div className="space-y-5">
      <div className="rounded-md border border-ink-200 bg-ink-50/60 px-4 py-3">
        <p className="label mb-1.5">Chain</p>
        <p className="font-mono text-sm text-ink-900">{d.chainText}</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge
            className={d.cycleDetected
              ? 'border-amber-300 bg-amber-50 text-amber-800'
              : 'border-ink-300 bg-white text-ink-700'}
          >
            {d.termination}
          </Badge>
          {d.cycleDetected && (
            <span className="text-[12px] text-ink-600">
              Cycle members: {d.cycleMembers.map((m: any) => m.planetName).join(' → ')}
            </span>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {d.chain.map((link: any, index: number) => (
          <div key={index} className="rounded-md border border-ink-200 p-3.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-[13px] font-medium text-ink-900">
                <span className="mr-2 font-mono text-[11px] text-ink-400">
                  {index + 1}
                </span>
                {link.planetName} → {link.signLordName}
                {link.isSelfDispositor && (
                  <Badge className="ml-2">Self-dispositor</Badge>
                )}
              </p>
              {!link.isSelfDispositor && <MaitriChip relationship={link.relationship} showParts />}
            </div>
            <FieldGrid cols={3} className="mt-3">
              <Field label="Planet" value={link.planetName} />
              <Field label="Sign occupied" value={link.signName} />
              <Field label="Sign lord" value={link.signLordName} />
            </FieldGrid>
            <Evidence rule="DISPOSITOR_001" source="Custom Rule Engine">
              <p>{link.evidence}</p>
            </Evidence>
          </div>
        ))}
      </div>

      {d.nodeNote && <Note>{d.nodeNote}</Note>}
    </div>
  )
}

/* --- SECTION U ----------------------------------------------------------- */
export function NeechaBhangaSection({ a }: { a: PlanetAnalysis }) {
  const n = a.neechaBhanga

  if (!n.applicable) {
    return (
      <div className="space-y-3">
        <Field label="Neecha Bhanga" value={n.status} />
        <Empty>{n.reason}</Empty>
        <Note>{n.exclusionNote}</Note>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <FieldGrid cols={4}>
        <Field label="Debilitated" value={<StatusPill status="Satisfied" />} />
        <Field label="Debilitation sign" value={n.debilitationSignName} />
        <Field label="Debilitation sign lord" value={n.debilitationLordName} />
        <Field label="Exaltation sign" value={n.exaltationSignName} />
        <Field label="Exaltation sign lord" value={n.exaltationLordName} />
        <Field label="Conditions satisfied" value={`${n.conditionsSatisfied} of 6`} mono />
      </FieldGrid>

      <div>
        <p className="label mb-2">Cancellation conditions, evaluated independently</p>
        <ConditionList conditions={n.conditions} />
      </div>

      <div className="rounded-md border border-ink-300 p-4">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h4 className="font-serif text-sm font-semibold text-ink-900">
            Neecha Bhanga Raja Yoga
          </h4>
          <StatusPill status={n.neechaBhangaRajaYoga.present ? 'Present' : 'Not Present'} />
        </div>
        <p className="mb-3 text-[12px] italic leading-relaxed text-ink-500">
          {n.neechaBhangaRajaYoga.statement}
        </p>
        <ConditionList conditions={n.neechaBhangaRajaYoga.conditions} />
      </div>

      <Note>{n.exclusionNote}</Note>
    </div>
  )
}

function fmt(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'Not available'
  return value.toFixed(2)
}
