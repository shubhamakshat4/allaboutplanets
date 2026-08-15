import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, ApiError } from '@/api/client'
import type { BirthRequest, Meta, PlaceResult } from '@/types'
import {
  Button, Card, CardBody, CardHeader, CardTitle, ErrorBox, Field, Input,
  Label, Note, Select, Spinner,
} from '@/components/ui'
import { cn, debounce } from '@/lib/utils'

interface Props {
  meta: Meta | null
  onGenerated: (chartId: string) => void
}

type TzMode = 'iana' | 'offset'

export function BirthForm({ meta, onGenerated }: Props) {
  const [date, setDate] = useState('1990-05-15')
  const [time, setTime] = useState('10:30:00')
  const [placeQuery, setPlaceQuery] = useState('Chennai, Tamil Nadu, India')
  const [placeName, setPlaceName] = useState('Chennai, Tamil Nadu, India')
  const [latitude, setLatitude] = useState('13.0827')
  const [longitude, setLongitude] = useState('80.2707')
  const [timezone, setTimezone] = useState('Asia/Kolkata')
  const [offset, setOffset] = useState('5.5')
  const [tzMode, setTzMode] = useState<TzMode>('iana')
  const [ayanamsha, setAyanamsha] = useState('LAHIRI')

  const [suggestions, setSuggestions] = useState<PlaceResult[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [searching, setSearching] = useState(false)
  const [geoMessage, setGeoMessage] = useState<string | null>(null)
  const [tzMessage, setTzMessage] = useState<string | null>(null)

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const boxRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (meta) setAyanamsha(meta.default_ayanamsha)
  }, [meta])

  useEffect(() => {
    function onClickAway(event: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(event.target as Node)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', onClickAway)
    return () => document.removeEventListener('mousedown', onClickAway)
  }, [])

  const runSearch = useMemo(
    () =>
      debounce(async (q: string) => {
        if (q.trim().length < 2) {
          setSuggestions([])
          return
        }
        setSearching(true)
        setGeoMessage(null)
        try {
          const results = await api.searchPlaces(q)
          setSuggestions(results)
          setShowSuggestions(true)
          if (results.length === 0) {
            setGeoMessage(
              'No match found. Enter the latitude, longitude and timezone manually.',
            )
          }
        } catch (e) {
          setSuggestions([])
          setGeoMessage(
            e instanceof ApiError
              ? e.message
              : 'Place lookup failed. Enter the coordinates manually.',
          )
        } finally {
          setSearching(false)
        }
      }, 350),
    [],
  )

  const parsed = useMemo(() => {
    const [y, mo, d] = date.split('-').map(Number)
    const [h, mi, s] = time.split(':').map(Number)
    return {
      year: y, month: mo, day: d,
      hour: h ?? 0, minute: mi ?? 0, second: s ?? 0,
    }
  }, [date, time])

  const resolveTimezone = useCallback(
    async (lat: number, lon: number) => {
      setTzMessage(null)
      try {
        const result = await api.resolveTimezone({
          latitude: lat, longitude: lon, ...parsed,
        })
        if (result.resolved && result.timezone) {
          setTimezone(result.timezone)
          setOffset(String(result.utc_offset_hours ?? ''))
          setTzMode('iana')
          setTzMessage(result.message)
        } else {
          setTzMessage(
            result.message ??
            'The timezone could not be determined. Enter the UTC offset manually.',
          )
          setTzMode('offset')
        }
      } catch {
        setTzMessage(
          'The timezone service could not be reached. Enter the UTC offset manually.',
        )
        setTzMode('offset')
      }
    },
    [parsed],
  )

  function selectPlace(place: PlaceResult) {
    setPlaceName(place.display_name)
    setPlaceQuery(place.display_name)
    setLatitude(place.latitude.toFixed(4))
    setLongitude(place.longitude.toFixed(4))
    setShowSuggestions(false)
    setGeoMessage(null)
    if (place.timezone) {
      setTimezone(place.timezone)
      setTzMode('iana')
      void resolveTimezone(place.latitude, place.longitude)
    } else {
      void resolveTimezone(place.latitude, place.longitude)
    }
  }

  // Re-evaluate the offset when the birth date changes, since DST depends on it.
  useEffect(() => {
    if (tzMode !== 'iana' || !timezone) return
    const lat = Number(latitude)
    const lon = Number(longitude)
    if (Number.isNaN(lat) || Number.isNaN(lon)) return
    let cancelled = false
    api
      .resolveTimezone({ latitude: lat, longitude: lon, ...parsed })
      .then((r) => {
        if (cancelled || !r.resolved) return
        if (r.timezone === timezone && r.utc_offset_hours !== null) {
          setOffset(String(r.utc_offset_hours))
        }
      })
      .catch(() => undefined)
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [date, timezone, tzMode])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)

    const lat = Number(latitude)
    const lon = Number(longitude)

    if (!placeName.trim()) return setError('A place of birth is required.')
    if (Number.isNaN(lat) || lat < -90 || lat > 90) {
      return setError('Latitude must be a number between −90 and 90.')
    }
    if (Number.isNaN(lon) || lon < -180 || lon > 180) {
      return setError('Longitude must be a number between −180 and 180.')
    }
    if (!date) return setError('A date of birth is required.')
    if (!time) return setError('A time of birth is required.')
    if (tzMode === 'iana' && !timezone.trim()) {
      return setError('A timezone is required. Nothing is assumed.')
    }
    if (tzMode === 'offset' && Number.isNaN(Number(offset))) {
      return setError('The UTC offset must be a number, for example 5.5 or −4.')
    }

    const payload: BirthRequest = {
      ...parsed,
      place_name: placeName.trim(),
      latitude: lat,
      longitude: lon,
      ayanamsha_mode: ayanamsha,
      ...(tzMode === 'iana'
        ? { timezone: timezone.trim() }
        : { utc_offset_hours: Number(offset) }),
    }

    setSubmitting(true)
    try {
      const chart = await api.createChart(payload)
      onGenerated(chart.chart_id)
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'The chart could not be generated.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:py-14">
      <header className="mb-8 text-center">
        <span className="mb-3 inline-block text-5xl" aria-hidden>✨</span>
        <h1 className="font-display text-4xl font-bold tracking-tight text-ink-800">
          Let us look at your chart
        </h1>
        <p className="mx-auto mt-2.5 max-w-lg text-[15px] leading-relaxed text-ink-500">
          Enter the birth date, time and place. Then pick any planet to see its
          strengths, its challenges, and everything in between.
        </p>
      </header>

      <form onSubmit={submit} className="space-y-5">
        <Card>
          <CardHeader><CardTitle>Birth details</CardTitle></CardHeader>
          <CardBody className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="dob">Date of birth</Label>
                <Input
                  id="dob" type="date" value={date} required
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="tob">Time of birth</Label>
                <Input
                  id="tob" type="time" step={1} value={time} required
                  onChange={(e) => setTime(e.target.value)}
                />
                <p className="mt-1 text-[11px] text-ink-400">
                  Local civil time at the place of birth, to the second.
                </p>
              </div>
            </div>

            <div ref={boxRef} className="relative">
              <Label htmlFor="place">Place of birth</Label>
              <Input
                id="place"
                value={placeQuery}
                placeholder="City, town or village"
                autoComplete="off"
                onChange={(e) => {
                  setPlaceQuery(e.target.value)
                  setPlaceName(e.target.value)
                  runSearch(e.target.value)
                }}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              />
              {searching && (
                <span className="absolute right-3 top-[30px] text-[11px] text-ink-400">
                  Searching…
                </span>
              )}
              {showSuggestions && suggestions.length > 0 && (
                <ul
                  role="listbox"
                  className={cn(
                    'absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md',
                    'border border-ink-300 bg-white py-1 shadow-lg',
                  )}
                >
                  {suggestions.map((place, index) => (
                    <li key={`${place.display_name}-${index}`}>
                      <button
                        type="button"
                        onClick={() => selectPlace(place)}
                        className="flex w-full flex-col gap-0.5 px-3 py-2 text-left hover:bg-ink-100"
                      >
                        <span className="text-sm text-ink-900">{place.display_name}</span>
                        <span className="font-mono text-[11px] tabular text-ink-500">
                          {place.latitude.toFixed(4)}, {place.longitude.toFixed(4)}
                          {place.timezone && ` · ${place.timezone}`}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
              {geoMessage && (
                <p className="mt-1.5 text-[12px] text-amber-700">{geoMessage}</p>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="lat">Latitude</Label>
                <Input
                  id="lat" value={latitude} inputMode="decimal"
                  onChange={(e) => setLatitude(e.target.value)}
                  className="font-mono tabular"
                />
              </div>
              <div>
                <Label htmlFor="lon">Longitude</Label>
                <Input
                  id="lon" value={longitude} inputMode="decimal"
                  onChange={(e) => setLongitude(e.target.value)}
                  className="font-mono tabular"
                />
              </div>
            </div>
            <p className="text-[11px] text-ink-400">
              Positive latitude is north, positive longitude is east. Correct these
              manually if the resolved values are not right.
            </p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Timezone</CardTitle></CardHeader>
          <CardBody className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {(['iana', 'offset'] as TzMode[]).map((mode) => (
                <Button
                  key={mode}
                  type="button"
                  size="sm"
                  variant={tzMode === mode ? 'primary' : 'outline'}
                  onClick={() => setTzMode(mode)}
                >
                  {mode === 'iana' ? 'Named timezone' : 'Explicit UTC offset'}
                </Button>
              ))}
            </div>

            {tzMode === 'iana' ? (
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="tz">IANA timezone</Label>
                  <Input
                    id="tz" value={timezone} placeholder="Asia/Kolkata"
                    onChange={(e) => setTimezone(e.target.value)}
                    className="font-mono"
                  />
                </div>
                <Field
                  label="Resolved UTC offset at the birth instant"
                  value={offset === '' ? 'Not resolved' : formatOffset(Number(offset))}
                  mono
                  hint="Evaluated for the birth date, so historical daylight-saving rules apply."
                />
              </div>
            ) : (
              <div className="sm:max-w-xs">
                <Label htmlFor="off">UTC offset in hours</Label>
                <Input
                  id="off" value={offset} inputMode="decimal" placeholder="5.5"
                  onChange={(e) => setOffset(e.target.value)}
                  className="font-mono tabular"
                />
                <p className="mt-1 text-[11px] text-ink-400">
                  Use a decimal, for example 5.5 for UTC+05:30 or −4 for UTC−04:00.
                </p>
              </div>
            )}

            {tzMessage && <Note>{tzMessage}</Note>}
          </CardBody>
        </Card>

        <Card>
          <CardHeader><CardTitle>Ayanamsha</CardTitle></CardHeader>
          <CardBody className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="ayanamsha">Ayanamsha</Label>
                <Select
                  id="ayanamsha" value={ayanamsha}
                  onChange={(e) => setAyanamsha(e.target.value)}
                >
                  {(meta?.ayanamsha_modes ?? [{ value: 'LAHIRI', label: 'Lahiri' }]).map(
                    (mode) => (
                      <option key={mode.value} value={mode.value}>{mode.label}</option>
                    ),
                  )}
                </Select>
              </div>
            </div>
            <p className="text-[12.5px] text-ink-400">
              Lahiri is the usual choice. Change it only if you follow another.
            </p>
          </CardBody>
        </Card>

        {error && <ErrorBox>{error}</ErrorBox>}

        {submitting ? (
          <Spinner label="Generating chart…" />
        ) : (
          <div className="flex justify-center">
            <Button type="submit" variant="primary" size="lg">
              Show my chart →
            </Button>
          </div>
        )}
      </form>
    </div>
  )
}

function formatOffset(hours: number): string {
  if (Number.isNaN(hours)) return 'Not resolved'
  const sign = hours >= 0 ? '+' : '−'
  const total = Math.round(Math.abs(hours) * 60)
  const hh = String(Math.floor(total / 60)).padStart(2, '0')
  const mm = String(total % 60).padStart(2, '0')
  return `UTC${sign}${hh}:${mm}`
}
