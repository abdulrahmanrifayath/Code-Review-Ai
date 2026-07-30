import { User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

let state: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
}

const listeners: Array<() => void> = []

export const authStore = {
  getState: () => state,
  setAuth: (user: User, token: string) => {
    localStorage.setItem('access_token', token)
    state = { user, token, isAuthenticated: true }
    listeners.forEach((l) => l())
  },
  logout: () => {
    localStorage.removeItem('access_token')
    state = { user: null, token: null, isAuthenticated: false }
    listeners.forEach((l) => l())
  },
  subscribe: (listener: () => void) => {
    listeners.push(listener)
    return () => {
      const idx = listeners.indexOf(listener)
      if (idx > -1) listeners.splice(idx, 1)
    }
  },
}
