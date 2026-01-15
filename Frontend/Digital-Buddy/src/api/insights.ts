import { apiRequest } from './client'

export interface DeepWorkSlot {
  dayOfWeek: number
  hour: number
  score: number
}

export interface InsightSummary {
  bestDeepWorkSlots: DeepWorkSlot[]
  moodEnergyInsight: string
  warningCard?: {
    title: string
    message: string
    severity: 'info' | 'warning' | 'critical'
  }
}

export const fetchInsightSummary = async () => {
  const response = await apiRequest('/analytics/insights', { method: 'GET' })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || 'Failed to load insights')
  }

  return (await response.json()) as InsightSummary
}
