import React, { createContext, useContext, useState, useEffect } from 'react'
import { apiClient } from '../services/api'
import { User } from '../types'

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  role: string | null
  login: (email: string, password: string) => Promise<void>
  loginWithGitHub: () => Promise<void>
  handleGitHubCallback: (code: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'))
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.get('/auth/me')
      setUser(response.data)
    } catch {
      setUser(null)
      localStorage.removeItem('access_token')
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCurrentUser()
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const res = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const { access_token } = res.data
    localStorage.setItem('access_token', access_token)
    setToken(access_token)

    const meRes = await apiClient.get('/auth/me')
    setUser(meRes.data)
    setIsLoading(false)
  }

  const loginWithGitHub = async () => {
    const res = await apiClient.get('/auth/github/url')
    const { url } = res.data
    window.location.href = url
  }

  const handleGitHubCallback = async (code: string) => {
    setIsLoading(true)
    const res = await apiClient.post('/auth/github/callback', { code })
    const { access_token } = res.data
    localStorage.setItem('access_token', access_token)
    setToken(access_token)

    const meRes = await apiClient.get('/auth/me')
    setUser(meRes.data)
    setIsLoading(false)
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
      setToken(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        role: user?.role || null,
        login,
        loginWithGitHub,
        handleGitHubCallback,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuthContext = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}
