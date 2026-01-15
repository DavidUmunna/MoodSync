import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../../api/auth'
import { ApiError } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

export const Register = () => {
  const navigate = useNavigate()
  const { setAuthTokens } = useAuth()
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { tokens } = await register({
        email,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
      })
      setAuthTokens(tokens)
      navigate('/onboarding')
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : 'Unable to create account'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className='min-h-screen flex items-center justify-center px-4 py-10'>
      <Card className='w-full max-w-md'>
        <CardHeader className='space-y-2 text-center'>
          <CardTitle className='text-2xl'>Create your account</CardTitle>
          <CardDescription>Start tracking your focus and mood.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className='space-y-4' onSubmit={handleSubmit}>
            <div className='grid gap-3 sm:grid-cols-2'>
              <label className='block space-y-2 text-sm'>
                <span>First name</span>
                <input
                  className='w-full rounded-md border border-input bg-background px-3 py-2 text-sm'
                  type='text'
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                />
              </label>
              <label className='block space-y-2 text-sm'>
                <span>Last name</span>
                <input
                  className='w-full rounded-md border border-input bg-background px-3 py-2 text-sm'
                  type='text'
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                />
              </label>
            </div>
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
              {loading ? 'Creating account...' : 'Create account'}
            </Button>
            <p className='text-sm text-muted-foreground text-center'>
              Already have an account?{' '}
              <Link to='/login' className='text-foreground underline'>
                Sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </section>
  )
}
