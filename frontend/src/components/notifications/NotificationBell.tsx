import React, { useState, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { notificationsApi } from '../../services/api'
import { NotificationDrawer } from './NotificationDrawer'

export const NotificationBell: React.FC = () => {
  const [unreadCount, setUnreadCount] = useState<number>(0)
  const [isOpen, setIsOpen] = useState<boolean>(false)

  const fetchUnreadCount = async () => {
    try {
      const data = await notificationsApi.getUnreadCount()
      setUnreadCount(data.unread_count || 0)
    } catch {
      // Silently handle if unauthenticated or offline
    }
  }

  useEffect(() => {
    fetchUnreadCount()
    // Poll unread count every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors focus:outline-none"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-rose-500 rounded-full border-2 border-[#0b0f17] animate-pulse">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <NotificationDrawer
          onClose={() => setIsOpen(false)}
          onCountChange={(count) => setUnreadCount(count)}
        />
      )}
    </div>
  )
}
