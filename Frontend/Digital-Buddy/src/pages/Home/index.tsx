import { useMemo } from 'react'
import { useRecommendation } from '../../hooks/useRecommendation'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

const getGreeting = (date: Date) => {
  const hour = date.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}

const StatSkeleton = () => (
  <Card className='animate-pulse'>
    <CardHeader className='space-y-2'>
      <div className='h-3 w-16 rounded bg-muted' />
      <div className='h-6 w-20 rounded bg-muted' />
    </CardHeader>
  </Card>
)

export const Home = () => {
  const greeting = useMemo(() => getGreeting(new Date()), [])
  const { recommendation, loading, error, fallback, requestRecommendation } = useRecommendation()

  const stats = {
    mood: '🙂',
    energy: 'Medium',
    sessionsToday: 3,
    focusMinutes: 95,
  }

  return (
    <section className='space-y-6'>
      <header className='space-y-2'>
        <p className='text-sm text-muted-foreground'>Today</p>
        <h1 className='text-2xl font-semibold'>{greeting}</h1>
        <p className='text-sm text-muted-foreground'>
          Keep your day balanced with small, intentional check-ins.
        </p>
      </header>

      <Button
        className='h-14 w-full text-base font-semibold shadow-sm'
        onClick={requestRecommendation}
        disabled={loading}
      >
        {loading ? 'Getting recommendation...' : 'What should I do right now?'}
      </Button>

      <div className='grid gap-4 sm:grid-cols-2'>
        <Card>
          <CardHeader className='pb-2'>
            <CardDescription>Mood</CardDescription>
            <CardTitle className='text-3xl'>{stats.mood}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardDescription>Energy</CardDescription>
            <CardTitle className='text-2xl'>{stats.energy}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardDescription>Sessions today</CardDescription>
            <CardTitle className='text-2xl'>{stats.sessionsToday}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardDescription>Total focus time</CardDescription>
            <CardTitle className='text-2xl'>{stats.focusMinutes} min</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {loading ? (
        <div className='grid gap-4 sm:grid-cols-2'>
          <StatSkeleton />
          <StatSkeleton />
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Recommendation</CardTitle>
          <CardDescription>Based on your recent check-ins.</CardDescription>
        </CardHeader>
        <CardContent>
          {recommendation ? (
            <div className='space-y-2'>
              <p className='text-lg font-semibold'>{recommendation.taskType}</p>
              <p className='text-sm text-muted-foreground'>{recommendation.reason}</p>
            </div>
          ) : null}
          {fallback ? <p className='text-sm text-muted-foreground'>{fallback}</p> : null}
          {error ? <p className='text-sm text-destructive'>{error}</p> : null}
          {!recommendation && !fallback && !error && !loading ? (
            <p className='text-sm text-muted-foreground'>
              Tap the button above to get a focused recommendation.
            </p>
          ) : null}
        </CardContent>
      </Card>
    </section>
  )
}
