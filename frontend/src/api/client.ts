import type {
  BirthRequest, Chart, Meta, PlaceResult, PlanetAnalysis,
} from '@/types'

const BASE = '/api'

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError(
      'The calculation service could not be reached. Confirm the backend is running.',
      0,
    )
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
      else if (Array.isArray(body?.detail)) {
        detail = body.detail
          .map((d: any) => `${(d.loc ?? []).slice(1).join('.')}: ${d.msg}`)
          .join('; ')
      }
    } catch {
      /* keep the default message */
    }
    throw new ApiError(detail, response.status)
  }

  return response.json() as Promise<T>
}

/* --- Chart recovery ------------------------------------------------------
 *
 * The server holds calculated charts in memory only, so a restart or an LRU
 * eviction can retire a chart_id that an open tab is still using. Charts are
 * deterministic — the id is a hash of the birth details — so remembering the
 * request lets us rebuild the identical chart transparently and retry, instead
 * of dead-ending the user on "regenerate it from the birth details".
 */
const REQUEST_KEY = 'psa.lastBirthRequest'
const CHART_EXPIRED = 'no longer held on the server'

export function rememberBirthRequest(payload: BirthRequest) {
  try {
    window.localStorage.setItem(REQUEST_KEY, JSON.stringify(payload))
  } catch {
    /* storage unavailable — recovery is simply not possible, not an error */
  }
}

export function forgetBirthRequest() {
  try {
    window.localStorage.removeItem(REQUEST_KEY)
  } catch {
    /* ignore */
  }
}

function storedBirthRequest(): BirthRequest | null {
  try {
    const raw = window.localStorage.getItem(REQUEST_KEY)
    return raw ? (JSON.parse(raw) as BirthRequest) : null
  } catch {
    return null
  }
}

/** Rebuild the chart from the remembered birth details. Returns its id. */
async function recreateChart(): Promise<string | null> {
  const payload = storedBirthRequest()
  if (!payload) return null
  try {
    const chart = await request<Chart>('/chart', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    return chart.chart_id
  } catch {
    return null
  }
}

function isExpiredChart(error: unknown): boolean {
  return error instanceof ApiError
    && error.status === 404
    && error.message.includes(CHART_EXPIRED)
}

export const api = {
  meta: () => request<Meta>('/meta'),

  searchPlaces: (q: string) =>
    request<{ results: PlaceResult[] }>(`/places?q=${encodeURIComponent(q)}`)
      .then((r) => r.results),

  resolveTimezone: (payload: {
    latitude: number; longitude: number
    year: number; month: number; day: number
    hour: number; minute: number; second: number
  }) =>
    request<{
      timezone: string | null
      utc_offset_hours: number | null
      utc_offset_label: string | null
      resolved: boolean
      message: string | null
    }>('/timezone', { method: 'POST', body: JSON.stringify(payload) }),

  createChart: async (payload: BirthRequest) => {
    const chart = await request<Chart>('/chart', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    rememberBirthRequest(payload)
    return chart
  },

  getChart: async (chartId: string): Promise<Chart> => {
    try {
      return await request<Chart>(`/chart/${chartId}`)
    } catch (error) {
      if (!isExpiredChart(error)) throw error
      const rebuilt = await recreateChart()
      if (!rebuilt) throw error
      return request<Chart>(`/chart/${rebuilt}`)
    }
  },

  getPlanetAnalysis: async (
    chartId: string,
    planetId: number,
  ): Promise<PlanetAnalysis> => {
    const fetchFor = (id: string) =>
      request<{ chart_id: string; analysis: PlanetAnalysis }>(
        `/chart/${id}/planet/${planetId}`,
      ).then((r) => r.analysis)

    try {
      return await fetchFor(chartId)
    } catch (error) {
      // Only a retired chart is recoverable. An unknown planet id is also a
      // 404 and must surface as itself.
      if (!isExpiredChart(error)) throw error
      const rebuilt = await recreateChart()
      if (!rebuilt) throw error
      return fetchFor(rebuilt)
    }
  },

  rules: () =>
    request<{ rules: Array<Record<string, any>> }>('/rules').then((r) => r.rules),
}
