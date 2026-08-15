import type { PlanetAnalysis } from '@/types'
import {
  BoolBadge, Empty, Evidence, Field, FieldGrid, Note, Table, TableWrap, Td, Th,
} from '@/components/ui'
import { MaitriChip, MaitriEvidence, SourceBadges } from './shared'

/* --- SECTION J ----------------------------------------------------------- */
export function RetrogradeSection({ a }: { a: PlanetAnalysis }) {
  const r = a.retrograde
  return (
    <div className="space-y-4">
      <FieldGrid cols={4}>
        <Field label="Retrograde" value={<BoolBadge value={r.retrograde} />} />
        <Field label="Motion" value={r.motion} />
        <Field label="Stationary" value={<BoolBadge value={r.stationary} />} />
        <Field
          label="Daily motion"
          value={r.dailyMotionDegrees !== null ? `${r.dailyMotionDegrees.toFixed(6)}°/day` : 'Not available'}
          mono
        />
      </FieldGrid>
      {r.note && <Note>{r.note}</Note>}
      <Evidence source={r.sources.source}>
        <p>{r.evidence}</p>
        <p className="text-ink-500">{r.sources.methodology}</p>
      </Evidence>
    </div>
  )
}

/* --- SECTION K ----------------------------------------------------------- */
export function CombustionSection({ a }: { a: PlanetAnalysis }) {
  const c = a.combustion
  if (!c.applicable) {
    return (
      <div className="space-y-3">
        <Field label="Combust" value={c.status} />
        <Empty>{c.reason}</Empty>
        <SourceBadges sources={c.sources} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <FieldGrid cols={4}>
        <Field label="Combust" value={<BoolBadge value={c.combust} />} />
        <Field label="Separation from the Sun" value={c.distanceFromSunDms} mono
          hint="Shorter arc" />
        <Field label="Classical orb" value={`${c.thresholdDegrees}°`} mono
          hint={c.thresholdBasis} />
        <Field label="Sun's longitude" value={c.sunLongitudeDms} mono />
        <Field label={`${a.planetName}'s longitude`} value={c.planetLongitudeDms} mono />
        <Field
          label="PyJHora's verdict"
          value={
            <span className="flex items-center gap-2">
              <BoolBadge value={c.pyjhoraVerdict} />
              {!c.verdictsAgree && (
                <span className="text-[11px] font-medium text-amber-700">differs</span>
              )}
            </span>
          }
          hint="Shown for comparison; not used"
        />
      </FieldGrid>
      {!c.verdictsAgree && (
        <Note>
          The calculation engine reports a different result here. This
          application applies the classical orb (rule COMBUST_001); PyJHora
          4.8.7 misindexes its own orb table. Both are shown so the divergence
          is visible.
        </Note>
      )}
      <Evidence source={c.sources.source} rule={c.sources.rule}>
        <p>{c.evidence}</p>
        <p className="text-ink-500">{c.note}</p>
        <p className="text-ink-500">{c.sources.methodology}</p>
      </Evidence>
    </div>
  )
}

/* --- SECTION L ----------------------------------------------------------- */
export function PlanetaryWarSection({ a }: { a: PlanetAnalysis }) {
  const w = a.planetaryWar
  if (!w.applicable) {
    return (
      <div className="space-y-3">
        <Field label="Graha Yuddha" value={w.status} />
        <Empty>{w.reason}</Empty>
        <SourceBadges sources={w.sources} />
      </div>
    )
  }
  if (!w.inWar) {
    return (
      <div className="space-y-3">
        <Field label="Graha Yuddha" value={<BoolBadge value={false} />} />
        <Empty>{w.reason}</Empty>
        <SourceBadges sources={w.sources} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {w.engagements.map((e: any, index: number) => (
        <div key={index} className="rounded-md border border-ink-200 p-4">
          <h4 className="mb-3 font-serif text-sm font-semibold text-ink-900">
            {a.planetName} ↔ {e.opposingPlanetName}
          </h4>
          <FieldGrid cols={4}>
            <Field label="Category" value={e.category} />
            <Field label={`${a.planetName}'s degree`} value={e.planetDegreeDms} mono />
            <Field label={`${e.opposingPlanetName}'s degree`} value={e.opposingDegreeDms} mono />
            <Field label="Separation" value={e.separationDms} mono />
            <Field label="Panchadha Maitri" value={<MaitriChip relationship={e.relationship} />} />
          </FieldGrid>
          <Evidence source="PyJHora"><p>{e.evidence}</p></Evidence>
        </div>
      ))}
    </div>
  )
}

/* --- SECTION M ----------------------------------------------------------- */
export function ConjunctionSection({
  a, filter,
}: { a: PlanetAnalysis; filter: string }) {
  const rows = a.conjunctions.filter((c) => matches(filter, [
    c.planetBName, c.rashiName, c.relationship.panchadhaMaitri,
    c.relationship.naturalRelationship, c.relationship.temporaryRelationship,
  ]))

  if (a.conjunctions.length === 0) {
    return <Empty>No planet shares {a.planetName}'s Rashi.</Empty>
  }
  if (rows.length === 0) return <Empty>No conjunction matches the current filter.</Empty>

  return (
    <div className="space-y-4">
      {rows.map((c) => (
        <div key={c.planetB} className="rounded-md border border-ink-200 p-4">
          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
            <h4 className="font-serif text-sm font-semibold text-ink-900">
              {a.planetName} conjunct {c.planetBName}
            </h4>
            <MaitriChip relationship={c.relationship} showParts />
          </div>

          <FieldGrid cols={4}>
            <Field label="Rashi" value={c.rashiName} />
            <Field label={`${a.planetName}`} value={c.degreeADms} mono />
            <Field label={`${c.planetBName}`} value={c.degreeBDms} mono />
            <Field label="Separation" value={c.separationDms} mono />
            <Field label="Same Rashi" value={<BoolBadge value={c.sameRashi} />} />
            <Field label="Same Bhava" value={<BoolBadge value={c.sameBhava} />}
              hint={`Bhava ${c.bhavaA} and ${c.bhavaB}`} />
            <Field label="Natural" value={c.relationship.naturalRelationship} />
            <Field label="Temporary" value={c.relationship.temporaryRelationship} />
          </FieldGrid>

          <Evidence rule="CONJ_001" source="Custom Rule Engine"><p>{c.evidence}</p></Evidence>
          <MaitriEvidence relationship={c.relationship} />
        </div>
      ))}
    </div>
  )
}

/* --- SECTION N ----------------------------------------------------------- */
export function AspectsReceivedSection({
  a, filter,
}: { a: PlanetAnalysis; filter: string }) {
  const rows = a.aspectsReceived.filter((r) => matches(filter, [
    r.sourcePlanetName, r.aspectType, r.relationship.panchadhaMaitri,
    r.relationship.naturalRelationship, r.relationship.temporaryRelationship,
  ]))

  if (a.aspectsReceived.length === 0) {
    return <Empty>No planet casts Graha Drishti on {a.planetName}.</Empty>
  }
  if (rows.length === 0) return <Empty>No aspect matches the current filter.</Empty>

  return (
    <div className="space-y-4">
      <TableWrap>
        <Table className="min-w-[720px]">
          <thead>
            <tr>
              <Th>Aspecting planet</Th>
              <Th>Aspect</Th>
              <Th align="right">From Bhava</Th>
              <Th align="right">To Bhava</Th>
              <Th>Natural</Th>
              <Th>Temporary</Th>
              <Th>Panchadha</Th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.sourcePlanet} className="hover:bg-ink-50">
                <Td className="font-medium">{r.sourcePlanetName}</Td>
                <Td>{r.aspectType}</Td>
                <Td align="right" mono>{r.sourceHouse}</Td>
                <Td align="right" mono>{r.targetHouse}</Td>
                <Td>{r.relationship.naturalRelationship}</Td>
                <Td>{r.relationship.temporaryRelationship}</Td>
                <Td><MaitriChip relationship={r.relationship} /></Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </TableWrap>

      {rows.map((r) => (
        <div key={`ev-${r.sourcePlanet}`} className="rounded-md border border-ink-200 px-4 py-3">
          <p className="text-[13px] font-medium text-ink-900">
            {r.sourcePlanetName} → {a.planetName} · {r.aspectType}
          </p>
          <Evidence source="PyJHora" rule="ASPECT_001"><p>{r.evidence}</p></Evidence>
          <MaitriEvidence relationship={r.relationship} />
        </div>
      ))}
    </div>
  )
}

/* --- SECTION O ----------------------------------------------------------- */
export function AspectsGivenSection({
  a, filter,
}: { a: PlanetAnalysis; filter: string }) {
  const g = a.aspectsGiven
  const houses = g.houses.filter((h) => matches(filter, [
    h.targetSignName, h.aspectType, String(h.targetHouse), h.targetHouseLordName,
    ...h.occupyingPlanets.map((p) => p.planetName),
  ]))
  const planets = g.planets.filter((p) => matches(filter, [
    p.targetPlanetName, p.aspectType, p.relationship.panchadhaMaitri,
  ]))

  return (
    <div className="space-y-6">
      <Field label="Graha Drishti set for this planet" value={g.drishtiSetText} />
      {g.nodeNote && <Note>{g.nodeNote}</Note>}

      <div>
        <p className="label mb-2">Houses receiving the aspect</p>
        {houses.length === 0 ? (
          <Empty>No house matches the current filter.</Empty>
        ) : (
          <TableWrap>
            <Table className="min-w-[680px]">
              <thead>
                <tr>
                  <Th>Aspect</Th>
                  <Th align="right">Target house</Th>
                  <Th>Target Rashi</Th>
                  <Th>House lord</Th>
                  <Th>Occupying planets</Th>
                </tr>
              </thead>
              <tbody>
                {houses.map((h) => (
                  <tr key={h.targetSign} className="hover:bg-ink-50">
                    <Td className="font-medium">{h.aspectType}</Td>
                    <Td align="right" mono>{h.targetHouse}</Td>
                    <Td>{h.targetSignName}</Td>
                    <Td>{h.targetHouseLordName}</Td>
                    <Td>
                      {h.occupyingPlanets.length === 0
                        ? <span className="text-ink-300">Empty</span>
                        : h.occupyingPlanets.map((p) => p.planetName).join(', ')}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </TableWrap>
        )}
      </div>

      <div>
        <p className="label mb-2">Planets receiving the aspect</p>
        {planets.length === 0 ? (
          <Empty>
            {g.planets.length === 0
              ? `${a.planetName} casts no Graha Drishti on an occupied sign.`
              : 'No planet matches the current filter.'}
          </Empty>
        ) : (
          <div className="space-y-3">
            <TableWrap>
              <Table className="min-w-[680px]">
                <thead>
                  <tr>
                    <Th>Target planet</Th>
                    <Th>Aspect</Th>
                    <Th align="right">Target Bhava</Th>
                    <Th>Natural</Th>
                    <Th>Temporary</Th>
                    <Th>Panchadha</Th>
                  </tr>
                </thead>
                <tbody>
                  {planets.map((p) => (
                    <tr key={p.targetPlanet} className="hover:bg-ink-50">
                      <Td className="font-medium">{p.targetPlanetName}</Td>
                      <Td>{p.aspectType}</Td>
                      <Td align="right" mono>{p.targetHouse}</Td>
                      <Td>{p.relationship.naturalRelationship}</Td>
                      <Td>{p.relationship.temporaryRelationship}</Td>
                      <Td><MaitriChip relationship={p.relationship} /></Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </TableWrap>

            {planets.map((p) => (
              <div key={`ev-${p.targetPlanet}`} className="rounded-md border border-ink-200 px-4 py-3">
                <p className="text-[13px] font-medium text-ink-900">
                  {a.planetName} → {p.targetPlanetName} · {p.aspectType}
                </p>
                <Evidence source="PyJHora" rule="ASPECT_001"><p>{p.evidence}</p></Evidence>
                <MaitriEvidence relationship={p.relationship} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* --- SECTIONS P & Q ------------------------------------------------------ */
export function RelationshipProfileSection({
  a, filter,
}: { a: PlanetAnalysis; filter: string }) {
  const rows = a.relationships.filter((r) => matches(filter, [
    r.planetBName, r.naturalRelationship, r.temporaryRelationship, r.panchadhaMaitri,
  ]))

  return (
    <div className="space-y-4">
      {rows.length === 0 ? (
        <Empty>No planet matches the current filter.</Empty>
      ) : (
        <TableWrap>
          <Table className="min-w-[620px]">
            <thead>
              <tr>
                <Th>Planet</Th>
                <Th>Natural</Th>
                <Th>Temporary</Th>
                <Th>Panchadha Maitri</Th>
                <Th>Combination</Th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.planetB} className="hover:bg-ink-50">
                  <Td className="font-medium">{r.planetBName}</Td>
                  <Td>{r.naturalRelationship}</Td>
                  <Td>{r.temporaryRelationship}</Td>
                  <Td><MaitriChip relationship={r} /></Td>
                  <Td className="text-[12px] text-ink-500">
                    {String((r.evidence as any).combination ?? '')}
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </TableWrap>
      )}

      <Evidence label="How the Panchadha Maitri table works"
        rule="MAITRI_003" source="Custom Rule Engine">
        <p>Natural Friend + Temporary Friend = Ati Mitra</p>
        <p>Natural Neutral + Temporary Friend = Mitra</p>
        <p>Natural Friend + Temporary Enemy = Sama</p>
        <p>Natural Enemy + Temporary Friend = Sama</p>
        <p>Natural Neutral + Temporary Enemy = Shatru</p>
        <p>Natural Enemy + Temporary Enemy = Ati Shatru</p>
        <p className="mt-2 border-t border-ink-200 pt-2 text-ink-500">
          Temporary friendship: planets in the 2nd, 3rd, 4th, 10th, 11th or 12th sign
          from a planet are its temporary friends; those in the 1st, 5th, 6th, 7th,
          8th or 9th are its temporary enemies.
        </p>
      </Evidence>
    </div>
  )
}

function matches(filter: string, haystack: (string | null | undefined)[]): boolean {
  const q = filter.trim().toLowerCase()
  if (!q) return true
  return haystack.some((value) => (value ?? '').toLowerCase().includes(q))
}
