import { useCallback, useState } from 'react'
import { apiRequest } from '../api/client'

interface RecommendationResponse {
  taskType: string
  reason: string
}

interface RecommendationState {
  taskType: string
  reason: string
}

export const useRecommendation = () => {
  const [recommendation, setRecommendation] = useState<RecommendationState | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fallback, setFallback] = useState<string | null>(null)

  const requestRecommendation = useCallback(async () => {
    setLoading(true)
    setError(null)
    setFallback(null)

    try {
      const response = await apiRequest('/recommendation', { method: 'GET' })

      if (response.status === 204 || response.status === 404) {
        setRecommendation(null)
        setFallback('Not enough data yet. Log a few sessions to get recommendations.')
        return
      }

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'Unable to load recommendation')
      }

      const data = (await response.json()) as RecommendationResponse
      setRecommendation({ taskType: data.taskType, reason: data.reason })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load recommendation'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    recommendation,
    loading,
    error,
    fallback,
    requestRecommendation,
  }
}
