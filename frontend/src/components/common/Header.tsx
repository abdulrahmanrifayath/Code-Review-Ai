import React from 'react'
import { Bot, LogOut, User } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import { NotificationBell } from '../notifications/NotificationBell'

export const Header: React.FC = () => {
  const { user, logout } = useAuth()

  return (
    <header className="h-16 border-b border-dark-border bg-dark-card/50 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-brand-600 to-indigo-500 rounded-lg text-white shadow-lg shadow-brand-500/20">
          <Bot className="w-5 h-5" />
        </div>
        <span className="font-bold text-lg text-slate-100 tracking-tight">ReviewAI</span>
      </div>

      <div className="flex items-center space-x-4">
        <NotificationBell />
        {user && (
          <div className="flex items-center space-x-2 text-sm text-slate-300">
            <User className="w-4 h-4 text-slate-400" />
            <span>{user.username}</span>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center space-x-1 text-sm text-slate-400 hover:text-slate-200 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </header>
  )
}
