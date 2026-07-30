import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Bot, AlertCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export const OAuthCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const { handleGitHubCallback } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = searchParams.get('code')
    if (!code) {
      setError('OAuth authorization code missing from GitHub redirect.')
      return
    }

    handleGitHubCallback(code)
      .then(() => {
        navigate('/')
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to complete GitHub authentication.')
      })
  }, [searchParams, handleGitHubCallback, navigate])

  return (
    <div className="min-h-screen bg-[#0b0f17] flex items-center justify-center p-4">
      <div className="w-full max-w-md glass-card p-8 rounded-2xl border border-slate-800 text-center space-y-6">
        <div className="inline-flex p-3 bg-gradient-to-tr from-brand-600 to-indigo-500 rounded-xl text-white shadow-lg shadow-brand-500/20">
          <Bot className="w-8 h-8 animate-pulse" />
        </div>

        {error ? (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2 text-rose-400">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Authentication Error</span>
            </div>
            <p className="text-sm text-slate-400">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm transition-colors"
            >
              Return to Login
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <h2 className="text-xl font-bold text-slate-100">Authenticating with GitHub...</h2>
            <p className="text-sm text-slate-400">Exchanging credentials and initializing your session.</p>
            <div className="flex justify-center pt-2">
              <div className="w-6 h-6 border-2 border-brand-500/20 border-t-brand-500 rounded-full animate-spin"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
