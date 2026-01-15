import { apiRequest } from './client'

export interface SessionListItem {
  id: string
  date: string
  taskType: string
  mood: number
  durationMinutes: number
}

export interface SessionDetail extends SessionListItem {
  energy?: string
  notes?: string
  goodSession?: boolean
}

export interface SessionHistoryResponse {
  items: SessionListItem[]
  nextCursor?: string | null
}

export const fetchSessionHistory = async (limit: number, cursor?: string | null) => {
  const params = new URLSearchParams()
  params.set('limit', String(limit))
  if (cursor) {
    params.set('cursor', cursor)
  }

  const response = await apiRequest(`/sessions/history?${params.toString()}`, { method: 'GET' })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Failed to load session history')
  }

  return (await response.json()) as SessionHistoryResponse
}

export const fetchSessionDetail = async (sessionId: string) => {
  const response = await apiRequest(`/sessions/${sessionId}`, { method: 'GET' })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Failed to load session detail')
  }

  return (await response.json()) as SessionDetail
}
