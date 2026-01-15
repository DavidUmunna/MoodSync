import type { AuthTokens } from './tokenStore'
import { clearTokens, setTokens } from './tokenStore'
import { apiRequest } from '../api/client'

interface RefreshResponse {
  accessToken: string
  refreshToken: string
}

export const refreshTokens = async (refreshToken: string) => {
  const response = await apiRequest('/auth/refresh', {
    method: 'POST',
    auth: false,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refreshToken }),
  })

  if (!response.ok) {
    clearTokens()
    throw new Error('Failed to refresh token')
  }

  const data = (await response.json()) as RefreshResponse
  const tokens: AuthTokens = {
    accessToken: data.accessToken,
    refreshToken: data.refreshToken,
  }
  setTokens(tokens)
  return tokens
}
