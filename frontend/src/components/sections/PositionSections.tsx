import type { PlanetAnalysis } from '@/types'
import { Badge, BoolBadge, Empty, Evidence, Field, FieldGrid, Note } from '@/components/ui'
import { MaitriEvidence, RelationshipTriple, SourceBadges } from './shared'
import { yesNo } from '@/lib/utils'

/* --- SECTION A ----------------------------------------------------------- */
export function PositionSection({ a }: { a: PlanetAnalysis }) {
  const p = a.position
  return (
    <div className="space-y-4">
      <FieldGrid cols={4}>
        <Field label="Planet" value={`${p.planetName} (${p.planetSanskrit})`} />
        <Field label="Exact longitude" value={p.absoluteLongitudeDms} mono
          hint="Sidereal, measured from 0° Aries" />
        <Field label="Degree in sign" value={p.degreeInSignDms} mono />
        <Field label="Rashi" value={`${p.rashiName} (${p.rashiSanskrit})`} />
        <Field label="Rashi Lord" value={p.rashiLordName} />
        <Field label="Bhava" value={`${p.bhava}${p.bhavaCategories.length ? ` — ${p.bhavaCategories.join(', ')}` : ''}`} />
        <Field label="Bhava Chalita" value={p.bhavaChalita ?? 'Not available'} mono
          hint="Reported separately; not used by any rule" />
        <Field label="Nakshatra" value={p.nakshatraName} />
        <Field label="Pada" value={p.pada} mono />
        <Field label="Nakshatra Lord" value={p.nakshatraLordName} />
        <Field label="Navamsha" value={p.navamshaName} />
        <Field label="Navamsha Lord" value={p.navamshaLordName} />
        <Field label="Daily motion" value={p.dailyMotion !== null ? `${p.dailyMotion.toFixed(4)}°/day` : 'Not available'} mono />
        <Field label="Ecliptic latitude" value={p.eclipticLatitude !== null ? `${p.eclipticLatitude.toFixed(4)}°` : 'Not available'} mono />
      </FieldGrid>
      <Note>{p.bhavaNote}</Note>
      <SourceBadges sources={p.sources} />
    </div>
  )
}

/* --- SECTION B ----------------------------------------------------------- */
export function DignitySection({ a }: { a: PlanetAnalysis }) {
  const d = a.dignity
  const facts: { label: string; value: boolean | string }[] = [
    { label: 'Exalted', value: d.exalted },
    { label: 'Debilitated', value: d.debilitated },
    { label: 'Swarashi (own sign)', value: d.swarashi },
    { label: 'Mooltrikona', value: d.mooltrikona },
    { label: "Friend's sign", value: d.friendSign },
    { label: 'Neutral sign', value: d.neutralSign },
    { label: "Enemy's sign", value: d.enemySign },
  ]

  return (
    <div className="space-y-5">
      <FieldGrid cols={4}>
        <Field label="Current Rashi" value={d.currentRashiName} />
        <Field label="Rashi Lord" value={d.currentRashiLordName} />
        <Field label="Degree in sign" value={d.degreeInSignDms} mono />
        <Field label="Sign relationship" value={d.signRelationship} />
        <Field label="Exaltation sign" value={d.exaltationSigns.join(', ') || 'Not defined in selected rule set'} />
        <Field label="Debilitation sign" value={d.debilitationSigns.join(', ') || 'Not defined in selected rule set'} />
        <Field label="Own sign(s)" value={d.ownSigns.join(', ') || 'Not defined in selected rule set'} />
        <Field label="Mooltrikona range" value={d.mooltrikonaRange} mono />
        {d.deepExaltationLongitude && (
          <Field label="Deep exaltation"
            value={`${d.deepExaltationLongitude.signName} ${d.deepExaltationLongitude.degreeInSignDms}`} mono />
        )}
        {d.deepDebilitationLongitude && (
          <Field label="Deep debilitation"
            value={`${d.deepDebilitationLongitude.signName} ${d.deepDebilitationLongitude.degreeInSignDms}`} mono />
        )}
      </FieldGrid>

      <div>
        <p className="label mb-2">Independent dignity facts</p>
        <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-4">
          {facts.map((fact) => (
            <div key={fact.label} className="flex items-center justify-between gap-2 border-b border-ink-100 py-1.5">
              <span className="text-[13px] text-ink-700">{fact.label}</span>
              <BoolBadge value={fact.value} />
            </div>
          ))}
        </div>
      </div>

      <Evidence rule="DIGNITY_001 / DIGNITY_002" source="PyJHora dignity tables">
        <p>{d.evidence.table}</p>
        <p className="text-ink-500">{d.evidence.codeLegend}</p>
        <p>{d.evidence.exaltation}</p>
        <p>{d.evidence.mooltrikona}</p>
      </Evidence>

      {d.evidence.nodeNote && <Note>{d.evidence.nodeNote}</Note>}
    </div>
  )
}

/* --- SECTION C ----------------------------------------------------------- */
export function RashiLordSection({ a }: { a: PlanetAnalysis }) {
  const r = a.rashiLordRelationship
  return (
    <div className="space-y-4">
      <FieldGrid cols={4}>
        <Field label="Planet" value={a.planetName} />
        <Field label="Occupied Rashi" value={r.rashi} />
        <Field label="Rashi Lord" value={r.rashiLordName} />
        <Field label="Rashi Lord's position" value={`${r.rashiLordSign} · Bhava ${r.rashiLordBhava}`} />
      </FieldGrid>
      {r.isSelfLorded ? (
        <Note>
          {a.planetName} occupies its own sign, so the Rashi Lord is {a.planetName} itself.
          A planet has no Panchadha Maitri with itself under this rule set.
        </Note>
      ) : (
        <>
          <RelationshipTriple relationship={r.relationship} />
          <MaitriEvidence relationship={r.relationship} />
        </>
      )}
    </div>
  )
}

/* --- SECTIONS D & E ------------------------------------------------------ */
export function LordshipSection({ a }: { a: PlanetAnalysis }) {
  const l = a.lordship
  const roles: { label: string; value: boolean }[] = [
    { label: 'Kendra Lord', value: l.kendraLord },
    { label: 'Trikona Lord', value: l.trikonaLord },
    { label: 'Dusthana Lord', value: l.dusthanaLord },
    { label: 'Upachaya Lord', value: l.upachayaLord },
    { label: 'Maraka Lord', value: l.marakaLord },
    { label: 'Badhakesh', value: l.badhakesh },
    { label: 'Yoga Karaka', value: l.yogaKaraka },
  ]

  return (
    <div className="space-y-5">
      {l.ownsNoHouse ? (
        <Empty>{l.nodeNote ?? `${a.planetName} owns no house.`}</Empty>
      ) : (
        <div>
          <p className="label mb-2">Houses owned</p>
          <div className="space-y-1.5">
            {l.housesOwnedDetail.map((house: any) => (
              <div key={house.house}
                className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-md border border-ink-200 bg-ink-50/60 px-3 py-2">
                <span className="font-mono text-[13px] font-medium tabular text-ink-900">
                  House {house.house}
                </span>
                <span className="text-[13px] text-ink-600">{house.signName}</span>
                <span aria-hidden className="text-ink-300">→</span>
                <span className="flex flex-wrap gap-1">
                  {house.categories.length === 0 ? (
                    <span className="text-[12px] italic text-ink-400">No category</span>
                  ) : (
                    house.categories.map((c: string) => <Badge key={c}>{c}</Badge>)
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <p className="label mb-2">Functional classification components</p>
        <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-4">
          {roles.map((role) => (
            <div key={role.label}
              className="flex items-center justify-between gap-2 border-b border-ink-100 py-1.5">
              <span className="text-[13px] text-ink-700">{role.label}</span>
              <BoolBadge value={role.value} />
            </div>
          ))}
        </div>
      </div>

      <FieldGrid cols={4}>
        <Field label="Lagna modality" value={l.lagnaModality} />
        <Field label="Badhaka house" value={`${l.badhakaHouse} (${l.badhakaSign})`} />
        <Field label="Badhakesh (badhaka lord)" value={l.badhakaLordName} />
      </FieldGrid>

      <Evidence rule="FUNC_001 – FUNC_005" source="Custom Rule Engine + PyJHora lordship table">
        <p>{l.evidence.ownership}</p>
        <p>{l.evidence.badhaka}</p>
        <p>{l.evidence.yogaKaraka}</p>
        <div className="mt-2 border-t border-ink-200 pt-2">
          {Object.entries(l.categoryDefinitions as Record<string, string>).map(([k, v]) => (
            <p key={k} className="text-ink-500"><span className="font-medium">{k}:</span> {v}</p>
          ))}
        </div>
      </Evidence>
    </div>
  )
}

/* --- SECTION F ----------------------------------------------------------- */
export function LagnaSection({ a }: { a: PlanetAnalysis }) {
  const l = a.lagnaRelationship
  const facts = [
    { label: `Is ${a.planetName} the Lagnesh?`, value: l.isLagnesh },
    { label: `Is ${a.planetName} placed in the Lagna?`, value: l.isPlacedInLagna },
    { label: `Does ${a.planetName} aspect the Lagna?`, value: l.aspectsLagna },
    { label: `Is ${a.planetName} conjunct the Lagnesh?`, value: l.isConjunctLagnesh },
  ]

  return (
    <div className="space-y-5">
      <FieldGrid cols={4}>
        <Field label="Lagna sign" value={l.lagnaSignName} />
        <Field label="Lagna degree" value={l.lagnaDegreeDms} mono />
        <Field label="Lagnesh" value={l.lagneshName} />
        <Field label="Lagnesh position" value={`${l.lagneshSign} · Bhava ${l.lagneshBhava}`} />
      </FieldGrid>

      <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {facts.map((fact) => (
          <div key={fact.label}
            className="flex items-center justify-between gap-2 border-b border-ink-100 py-1.5">
            <span className="text-[13px] text-ink-700">{fact.label}</span>
            <BoolBadge value={fact.value} />
          </div>
        ))}
      </div>

      {l.aspectsLagna && l.aspectType && (
        <Field label="Aspect on the Lagna" value={l.aspectType} />
      )}

      {l.isLagnesh ? (
        <Note>{a.planetName} is itself the Lagnesh, so no Lagnesh relationship is computed.</Note>
      ) : (
        <>
          <div>
            <p className="label mb-2">Relationship with the Lagnesh ({l.lagneshName})</p>
            <RelationshipTriple relationship={l.relationshipWithLagnesh} />
          </div>
          <MaitriEvidence relationship={l.relationshipWithLagnesh} />
        </>
      )}

      <Evidence rule="ASPECT_001" source="PyJHora Graha Drishti">
        <p>{l.aspectEvidence}</p>
        <p>{l.conjunctLagneshEvidence}</p>
      </Evidence>
    </div>
  )
}

/* --- SECTION G ----------------------------------------------------------- */
export function NakshatraSection({ a }: { a: PlanetAnalysis }) {
  const n = a.nakshatraRelationship
  return (
    <div className="space-y-4">
      <FieldGrid cols={4}>
        <Field label="Nakshatra" value={`${n.nakshatraName} (#${n.nakshatra})`} />
        <Field label="Pada" value={n.pada} mono />
        <Field label="Nakshatra Lord" value={n.nakshatraLordName} />
        <Field label="Lord's Rashi" value={n.nakshatraLordRashiName} />
        <Field label="Lord's Bhava" value={n.nakshatraLordBhava} mono />
      </FieldGrid>

      {n.isSelfLorded ? (
        <Note>{a.planetName} occupies its own nakshatra, so no relationship pair is formed.</Note>
      ) : (
        <>
          <div>
            <p className="label mb-2">Relationship with the Nakshatra Lord</p>
            <RelationshipTriple relationship={n.relationship} />
          </div>
          <MaitriEvidence relationship={n.relationship} />
        </>
      )}

      <Evidence rule="NAK_001" source="PyJHora + Custom Rule Engine">
        <p>{n.evidence}</p>
      </Evidence>
    </div>
  )
}

/* --- SECTION H ----------------------------------------------------------- */
export function NavamshaSection({ a }: { a: PlanetAnalysis }) {
  const n = a.navamshaRelationship
  if (!n.available) return <Empty>{n.reason ?? 'D9 position not available.'}</Empty>

  const v = n.vargottama
  return (
    <div className="space-y-5">
      <FieldGrid cols={4}>
        <Field label="D1 Rashi" value={n.d1RashiName} />
        <Field label="D9 Rashi" value={n.d9RashiName} />
        <Field label="D9 degree" value={n.d9DegreeDms} mono />
        <Field label="D9 Lord" value={n.d9LordName} />
        <Field label="D9 Lord's position" value={`${n.d9LordSign} · Bhava ${n.d9LordBhava}`} />
        <Field label="Dignity in D9 sign" value={n.d9Dignity} />
      </FieldGrid>

      <div className="flex items-center gap-3 rounded-md border border-ink-200 bg-ink-50/60 px-3 py-2.5">
        <span className="label">Vargottama</span>
        <BoolBadge value={v.isVargottama} />
        <span className="text-[12px] text-ink-500">{yesNo(v.isVargottama) === 'Yes' ? 'D1 and D9 signs match' : 'D1 and D9 signs differ'}</span>
      </div>
      <Evidence rule="VARGA_001" source="Custom Rule Engine">
        <p>{v.evidence}</p>
      </Evidence>

      {n.isSelfLorded ? (
        <Note>{a.planetName} lords its own Navamsha sign, so no relationship pair is formed.</Note>
      ) : (
        <>
          <div>
            <p className="label mb-2">Relationship with the D9 Lord</p>
            <RelationshipTriple relationship={n.relationship} />
          </div>
          <MaitriEvidence relationship={n.relationship} />
        </>
      )}
    </div>
  )
}

/* --- SECTION I ----------------------------------------------------------- */
export function AvasthaSection({ a }: { a: PlanetAnalysis }) {
  return (
    <div className="grid gap-5 lg:grid-cols-2">
      {[a.avastha.kumaradi, a.avastha.chaitanyadi].map((av: any) => (
        <div key={av.name} className="rounded-md border border-ink-200 p-4">
          <div className="mb-3 flex items-baseline justify-between gap-3">
            <h4 className="font-serif text-sm font-semibold text-ink-900">{av.name}</h4>
            <span className="font-serif text-lg font-semibold text-accent-700">{av.result}</span>
          </div>

          <FieldGrid cols={2} className="mb-3">
            <Field label="Sign" value={`${av.signName} (${av.signType})`} />
            <Field label="Degree" value={av.degreeDms} mono />
            <Field label="Range used" value={av.rangeUsed} mono />
          </FieldGrid>

          <table className="w-full border-collapse text-[12px]">
            <tbody>
              {av.bands.map((band: any) => (
                <tr key={band.range}
                  className={band.active ? 'bg-accent-50 font-medium text-ink-900' : 'text-ink-500'}>
                  <td className="border-b border-ink-100 px-2 py-1 font-mono tabular">{band.range}</td>
                  <td className="border-b border-ink-100 px-2 py-1">{band.value}</td>
                  <td className="border-b border-ink-100 px-2 py-1 text-right">
                    {band.active && <span className="text-accent-700">◄ applied</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Evidence rule={av.sources.rule} source={av.sources.source}>
            <p>{av.ruleApplied}</p>
            <p className="font-mono text-[11px]">{av.evidence}</p>
          </Evidence>

          {av.applicabilityNote && <Note className="mt-3">{av.applicabilityNote}</Note>}
        </div>
      ))}
    </div>
  )
}
