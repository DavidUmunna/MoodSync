import type React from "react"

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

type Listener = (tokens: AuthTokens | null) => void

const STORAGE_KEY = 'moodsync.tokens'
const listeners = new Set<Listener>()

export const getTokens = (): AuthTokens | null => {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthTokens
  } catch {
    return null
  }
}

export const setTokens = (tokens: AuthTokens) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
  listeners.forEach((listener) => listener(tokens))
}

export const clearTokens = () => {
  localStorage.removeItem(STORAGE_KEY)
  listeners.forEach((listener) => listener(null))
}

export const subscribeTokens = (listener: React.Dispatch<React.SetStateAction<AuthTokens | null>>) => {
  listeners.add(listener)
  
}

const decodeJwtPayload = (token: string): { exp?: number } | null => {
  const parts = token.split('.')
  if (parts.length !== 3) return null
  try {
    const payload = JSON.parse(atob(parts[1])) as { exp?: number }
    return payload
  } catch {
    return null
  }
}

export const isTokenExpired = (token: string, skewSeconds = 30) => {
  const payload = decodeJwtPayload(token)
  if (!payload?.exp) return false
  const nowSeconds = Math.floor(Date.now() / 1000)
  return payload.exp - skewSeconds <= nowSeconds
}
