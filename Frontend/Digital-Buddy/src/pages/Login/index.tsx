import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

export const Login = () => {
  const navigate = useNavigate()
  const { setAuthTokens } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { tokens } = await login({ email, password })
      setAuthTokens(tokens)
      navigate('/onboarding')
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Unable to sign in'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className='min-h-screen flex items-center justify-center px-4 py-10'>
      <Card className='w-full max-w-md'>
        <CardHeader className='space-y-2 text-center'>
          <CardTitle className='text-2xl'>Welcome back</CardTitle>
          <CardDescription>Sign in to continue your MoodSync journey.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className='space-y-4' onSubmit={handleSubmit}>
            <label className='block space-y-2 text-sm'>
              <span>Email</span>
              <input
                className='w-full rounded-md border border-input bg-background px-3 py-2 text-sm'
                type='email'
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </label>
            <label className='block space-y-2 text-sm'>
              <span>Password</span>
              <input
                className='w-full rounded-md border border-input bg-background px-3 py-2 text-sm'
                type='password'
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </label>
            {error ? <p className='text-sm text-destructive'>{error}</p> : null}
            <Button className='w-full h-11' type='submit' disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
            <p className='text-sm text-muted-foreground text-center'>
              New to MoodSync?{' '}
              <Link to='/register' className='text-foreground underline'>
                Create an account
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </section>
  )
}
