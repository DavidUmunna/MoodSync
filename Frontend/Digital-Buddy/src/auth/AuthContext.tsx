import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { AuthTokens } from './tokenStore'
import { clearTokens, getTokens, setTokens, subscribeTokens } from './tokenStore'

interface AuthContextValue {
  tokens: AuthTokens | null
  isAuthenticated: boolean
  setAuthTokens: (tokens: AuthTokens) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [tokens, setTokensState] = useState<AuthTokens | null>(() => getTokens())

  useEffect(() => {
    return subscribeTokens(setTokensState)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      tokens,
      isAuthenticated: Boolean(tokens?.accessToken),
      setAuthTokens: setTokens,
      logout: clearTokens,
    }),
    [tokens]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
