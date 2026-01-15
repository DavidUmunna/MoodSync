import { getTokens, isTokenExpired, clearTokens } from '../auth/tokenStore'
import { refreshTokens } from '../auth/authService'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

let refreshPromise: Promise<void> | null = null

const ensureFreshAccessToken = async () => {
  const tokens = getTokens()
  if (!tokens?.accessToken || !tokens.refreshToken) return
  if (!isTokenExpired(tokens.accessToken)) return

  if (!refreshPromise) {
    refreshPromise = refreshTokens(tokens.refreshToken)
      .then(() => undefined)
      .finally(() => {
        refreshPromise = null
      })
  }

  await refreshPromise
}

export interface ApiRequestOptions extends RequestInit {
  auth?: boolean
}

export interface ApiErrorPayload {
  error: string
  status_code?: number
}

export class ApiError extends Error {
  status?: number
  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const buildUrl = (input: RequestInfo | URL) => {
  if (typeof input === 'string') {
    return `${API_BASE_URL}${input}`
  }
  return input
}

const parseError = async (response: Response) => {
  try {
    const data = (await response.json()) as ApiErrorPayload
    if (data?.error) {
      return new ApiError(data.error, response.status)
    }
  } catch {
    // fall through
  }
  const text = await response.text()
  return new ApiError(text || 'Request failed', response.status)
}

export const apiRequest = async (input: RequestInfo | URL, options: ApiRequestOptions = {}) => {
  const { auth = true, headers, ...rest } = options

  if (auth) {
    await ensureFreshAccessToken()
  }

  const tokens = getTokens()
  const mergedHeaders = new Headers(headers)
  if (auth && tokens?.accessToken) {
    mergedHeaders.set('Authorization', `Bearer ${tokens.accessToken}`)
  }

  const response = await fetch(buildUrl(input), {
    ...rest,
    headers: mergedHeaders,
  })

  if (!response.ok && response.status !== 401) {
    throw await parseError(response)
  }

  if (response.status !== 401 || !auth) {
    return response
  }

  if (!tokens?.refreshToken) {
    clearTokens()
    if (!response.ok) {
      throw await parseError(response)
    }
    return response
  }

  try {
    await refreshTokens(tokens.refreshToken)
  } catch {
    return response
  }

  const retryTokens = getTokens()
  if (!retryTokens?.accessToken) {
    return response
  }

  mergedHeaders.set('Authorization', `Bearer ${retryTokens.accessToken}`)
  const retry = await fetch(buildUrl(input), {
    ...rest,
    headers: mergedHeaders,
  })
  if (!retry.ok) {
    throw await parseError(retry)
  }
  return retry
}
