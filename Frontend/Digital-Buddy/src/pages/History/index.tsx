import { useEffect, useState } from 'react'
import { fetchSessionDetail, fetchSessionHistory } from '../../api/history'
import type { SessionDetail, SessionListItem } from '../../api/history'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

const PAGE_SIZE = 10

export const History = () => {
  const [sessions, setSessions] = useState<SessionListItem[]>([])
  const [nextCursor, setNextCursor] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<SessionDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)

  const loadSessions = async (cursor?: string | null, append = false) => {
    try {
      const response = await fetchSessionHistory(PAGE_SIZE, cursor)
      setSessions((prev) => (append ? [...prev, ...response.items] : response.items))
      setNextCursor(response.nextCursor ?? null)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load history'
      setError(message)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  const handleLoadMore = () => {
    if (!nextCursor) return
    setLoadingMore(true)
    loadSessions(nextCursor, true)
  }

  const handleSelect = async (sessionId: string) => {
    setDetailLoading(true)
    setDetailError(null)
    try {
      const detail = await fetchSessionDetail(sessionId)
      setSelected(detail)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load session detail'
      setDetailError(message)
    } finally {
      setDetailLoading(false)
    }
  }

  return (
    <section className='space-y-6'>
      <header className='space-y-2'>
        <p className='text-sm text-muted-foreground'>History</p>
        <h1 className='text-2xl font-semibold'>Past sessions</h1>
        <p className='text-sm text-muted-foreground'>
          Review what you logged and open a session for details.
        </p>
      </header>

      {loading ? <p className='text-sm text-muted-foreground'>Loading sessions...</p> : null}
      {error ? <p className='text-sm text-destructive'>{error}</p> : null}

      {!loading && !sessions.length ? (
        <Card>
          <CardHeader>
            <CardTitle>No sessions yet</CardTitle>
            <CardDescription>Log a session and it will show up here.</CardDescription>
          </CardHeader>
        </Card>
      ) : null}

      <div className='grid gap-3'>
        {sessions.map((session) => (
          <button
            key={session.id}
            type='button'
            onClick={() => handleSelect(session.id)}
            className='text-left'
          >
            <Card>
              <CardContent className='flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between'>
                <div className='space-y-1'>
                  <p className='text-sm text-muted-foreground'>
                    {new Date(session.date).toLocaleDateString()}
                  </p>
                  <p className='text-base font-semibold'>{session.taskType}</p>
                </div>
                <div className='flex items-center gap-4 text-sm text-muted-foreground'>
                  <span>Mood {session.mood}</span>
                  <span>{session.durationMinutes} min</span>
                </div>
              </CardContent>
            </Card>
          </button>
        ))}
      </div>

      {nextCursor ? (
        <Button type='button' variant='secondary' onClick={handleLoadMore} disabled={loadingMore}>
          {loadingMore ? 'Loading...' : 'Load more'}
        </Button>
      ) : null}

      {detailLoading ? <p className='text-sm text-muted-foreground'>Loading session detail...</p> : null}
      {detailError ? <p className='text-sm text-destructive'>{detailError}</p> : null}

      {selected ? (
        <Card>
          <CardHeader>
            <CardTitle>Session detail</CardTitle>
            <CardDescription>{new Date(selected.date).toLocaleString()}</CardDescription>
          </CardHeader>
          <CardContent className='space-y-2'>
            <p className='text-sm'>Task: {selected.taskType}</p>
            <p className='text-sm'>Mood: {selected.mood}</p>
            <p className='text-sm'>Duration: {selected.durationMinutes} min</p>
            {selected.energy ? <p className='text-sm'>Energy: {selected.energy}</p> : null}
            {selected?.goodSession !== undefined ? (
              <p className='text-sm'>Good session: {selected.goodSession ? 'Yes' : 'No'}</p>
            ) : null}
            <Button type='button' variant='outline' onClick={() => setSelected(null)}>
              Close
            </Button>
          </CardContent>
        </Card>
      ) : null}
    </section>
  )
}
