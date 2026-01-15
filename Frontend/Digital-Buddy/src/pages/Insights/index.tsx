import { useEffect, useMemo, useState } from 'react'
import { fetchInsightSummary } from '../../api/insights'
import type { DeepWorkSlot, InsightSummary } from '../../api/insights'
import { Badge } from '../../components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const groupByDay = (slots: DeepWorkSlot[]) => {
  return slots.reduce<Record<number, DeepWorkSlot[]>>((acc, slot) => {
    acc[slot.dayOfWeek] = acc[slot.dayOfWeek] || []
    acc[slot.dayOfWeek].push(slot)
    return acc
  }, {})
}

export const Insights = () => {
  const [data, setData] = useState<InsightSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    const loadInsights = async () => {
      try {
        const summary = await fetchInsightSummary()
        if (isMounted) {
          setData(summary)
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to load insights'
        if (isMounted) {
          setError(message)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    loadInsights()
    return () => {
      isMounted = false
    }
  }, [])

  const dayGroups = useMemo(() => groupByDay(data?.bestDeepWorkSlots ?? []), [data?.bestDeepWorkSlots])
  const maxScore = useMemo(() => {
    const scores = data?.bestDeepWorkSlots?.map((slot) => slot.score) ?? []
    return scores.length ? Math.max(...scores) : 1
  }, [data?.bestDeepWorkSlots])

  if (loading) {
    return (
      <section className='space-y-4'>
        <h1 className='text-2xl font-semibold'>Insights</h1>
        <p className='text-sm text-muted-foreground'>Loading insights...</p>
      </section>
    )
  }

  if (error) {
    return (
      <section className='space-y-4'>
        <h1 className='text-2xl font-semibold'>Insights</h1>
        <p className='text-sm text-destructive'>{error}</p>
      </section>
    )
  }

  return (
    <section className='space-y-6'>
      <header className='space-y-2'>
        <p className='text-sm text-muted-foreground'>Insights</p>
        <h1 className='text-2xl font-semibold'>Your productivity patterns</h1>
        <p className='text-sm text-muted-foreground'>
          Aggregated from your recent sessions and check-ins.
        </p>
      </header>

      <div className='grid gap-4 lg:grid-cols-3'>
        <Card className='lg:col-span-2'>
          <CardHeader className='space-y-1'>
            <CardTitle>Best time for deep work</CardTitle>
            <CardDescription>Heatmap-ready slots grouped by day and hour.</CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid gap-3'>
              {dayLabels.map((day, index) => {
                const slots = dayGroups[index] || []
                return (
                  <div key={day} className='space-y-2'>
                    <div className='flex items-center justify-between text-xs text-muted-foreground'>
                      <span>{day}</span>
                      <span>{slots.length ? `${slots.length} slots` : 'No data'}</span>
                    </div>
                    <div className='grid grid-cols-12 gap-1'>
                      {slots.map((slot) => {
                        const intensity = Math.max(0.2, slot.score / maxScore)
                        return (
                          <div
                            key={`${slot.dayOfWeek}-${slot.hour}`}
                            title={`${day} ${slot.hour}:00`}
                            className='h-8 rounded-md bg-primary/20'
                            style={{ opacity: intensity }}
                          />
                        )
                      })}
                      {!slots.length ? (
                        <div className='col-span-12 h-8 rounded-md border border-dashed border-border' />
                      ) : null}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <div className='grid gap-4'>
          <Card>
            <CardHeader>
              <CardTitle>Mood x energy</CardTitle>
              <CardDescription>Performance insight</CardDescription>
            </CardHeader>
            <CardContent>
              <p className='text-sm text-muted-foreground'>
                {data?.moodEnergyInsight || 'No insight yet. Keep logging sessions.'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className='flex flex-row items-center justify-between'>
              <div>
                <CardTitle>{data?.warningCard?.title || 'Suggestion'}</CardTitle>
                <CardDescription>Actionable guidance</CardDescription>
              </div>
              <Badge>
                {data?.warningCard?.severity ? data.warningCard.severity.toUpperCase() : 'INFO'}
              </Badge>
            </CardHeader>
            <CardContent>
              <p className='text-sm text-muted-foreground'>
                {data?.warningCard?.message ||
                  'Try a short focus block in your strongest energy window today.'}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
