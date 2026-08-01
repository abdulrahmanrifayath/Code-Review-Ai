import React, { useState, useEffect } from 'react'
import {
  Bell,
  Check,
  CheckCheck,
  ExternalLink,
  Settings,
  X,
  ShieldAlert,
  FileCode2,
  Info,
  Clock,
} from 'lucide-react'
import { notificationsApi } from '../../services/api'
import { NotificationPreferencesModal } from './NotificationPreferencesModal'

export interface NotificationItem {
  id: string
  user_id: string
  title: string
  message: string
  notification_type: string
  link_url?: string
  is_read: boolean
  payload?: any
  created_at: string
}

interface NotificationDrawerProps {
  onClose: () => void
  onCountChange: (count: number) => void
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  onClose,
  onCountChange,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)
  const [showPreferences, setShowPreferences] = useState<boolean>(false)

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const data = await notificationsApi.getNotifications(unreadOnly)
      setNotifications(data.notifications || [])
      onCountChange(data.unread_count || 0)
    } catch {
      // Fallback sample data if backend endpoint offline
      const sampleList: NotificationItem[] = [
        {
          id: '1',
          user_id: 'u1',
          title: 'AI Code Review Completed',
          message: 'Review completed for PR #104 in acme/core-service. 0 critical bugs found.',
          notification_type: 'review_completed',
          link_url: '/analytics',
          is_read: false,
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          user_id: 'u1',
          title: 'Security Vulnerability Alert',
          message: 'High severity SQL injection pattern detected in auth_service.py.',
          notification_type: 'security_alert',
          link_url: '/repositories',
          is_read: false,
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ]
      setNotifications(sampleList)
      onCountChange(2)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications()
  }, [unreadOnly])

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationsApi.markAsRead(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
      const newUnread = notifications.filter((n) => !n.is_read && n.id !== id).length
      onCountChange(newUnread)
    } catch {
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllAsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      onCountChange(0)
    } catch {
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      onCountChange(0)
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'security_alert':
        return <ShieldAlert className="w-4 h-4 text-rose-400" />
      case 'review_completed':
        return <FileCode2 className="w-4 h-4 text-brand-400" />
      default:
        return <Info className="w-4 h-4 text-blue-400" />
    }
  }

  return (
    <>
      <div className="absolute right-0 mt-2 w-80 sm:w-96 glass-card rounded-xl border border-slate-800 shadow-2xl z-50 overflow-hidden flex flex-col max-h-[85vh]">
        {/* Drawer Header */}
        <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4 text-brand-400" />
            <span className="font-semibold text-sm text-slate-100">Notifications</span>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={handleMarkAllRead}
              className="p-1 text-xs text-slate-400 hover:text-emerald-400 transition-colors flex items-center space-x-1"
              title="Mark all as read"
            >
              <CheckCheck className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowPreferences(true)}
              className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
              title="Notification Preferences"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="p-1 text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filter Tab Bar */}
        <div className="px-3 py-2 bg-slate-900/40 border-b border-slate-800/60 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setUnreadOnly(false)}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                !unreadOnly ? 'bg-slate-800 text-slate-200' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setUnreadOnly(true)}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                unreadOnly ? 'bg-slate-800 text-slate-200' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Unread Only
            </button>
          </div>

          <span className="text-slate-500 font-mono">{notifications.length} items</span>
        </div>

        {/* Notifications List */}
        <div className="overflow-y-auto divide-y divide-slate-800/50 flex-1">
          {loading ? (
            <div className="p-6 text-center text-slate-500 text-xs">Loading notifications...</div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs space-y-1">
              <p className="font-semibold">All caught up!</p>
              <p>No notifications match your current filter.</p>
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`p-3.5 space-y-1.5 transition-colors ${
                  !n.is_read ? 'bg-slate-800/30' : 'hover:bg-slate-800/20'
                }`}
              >
                <div className="flex items-start justify-between space-x-2">
                  <div className="flex items-center space-x-2">
                    {getTypeIcon(n.notification_type)}
                    <span className="font-medium text-xs text-slate-100">{n.title}</span>
                  </div>

                  {!n.is_read && (
                    <button
                      onClick={() => handleMarkAsRead(n.id)}
                      className="text-slate-500 hover:text-emerald-400 p-0.5"
                      title="Mark as read"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{n.message}</p>

                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>
                      {new Date(n.created_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </span>

                  {n.link_url && (
                    <a
                      href={n.link_url}
                      onClick={onClose}
                      className="text-brand-400 hover:underline flex items-center space-x-1"
                    >
                      <span>View details</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Preferences Modal */}
      {showPreferences && (
        <NotificationPreferencesModal onClose={() => setShowPreferences(false)} />
      )}
    </>
  )
}
