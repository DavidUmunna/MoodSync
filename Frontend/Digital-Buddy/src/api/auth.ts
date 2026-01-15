import { apiRequest } from './client'
import type { AuthTokens } from '../auth/tokenStore'

interface AuthResponse {
  user_id: string
  access_token: string
  refresh_token: string
  expires_at: string
}

interface RegisterPayload {
  email: string
  password: string
  first_name?: string
  last_name?: string
}

interface LoginPayload {
  email: string
  password: string
  device_name?: string
  device_id?: string
}

const toTokens = (response: AuthResponse): AuthTokens => ({
  accessToken: response.access_token,
  refreshToken: response.refresh_token,
})

export const register = async (payload: RegisterPayload) => {
  const response = await apiRequest('/auth/register', {
    method: 'POST',
    auth: false,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = (await response.json()) as AuthResponse
  return { data, tokens: toTokens(data) }
}

export const login = async (payload: LoginPayload) => {
  const response = await apiRequest('/auth/login', {
    method: 'POST',
    auth: false,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = (await response.json()) as AuthResponse
  return { data, tokens: toTokens(data) }
}

export const logout = async (refreshToken: string) => {
  const response = await apiRequest('/auth/logout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })

  await response.json().catch(() => undefined)
}
