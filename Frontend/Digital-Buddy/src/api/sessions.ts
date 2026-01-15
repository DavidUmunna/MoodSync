import { apiRequest } from './client'
import type { SessionPayload } from '../types/session'

interface CreateSessionResponse {
  id: string
}

export const createSession = async (payload: SessionPayload) => {
  const response = await apiRequest('/sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Failed to save session')
  }

  return (await response.json()) as CreateSessionResponse
}
