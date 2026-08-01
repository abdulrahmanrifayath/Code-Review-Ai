import React, { useState, useEffect } from 'react'
import {
  X,
  Send,
  Save,
  CheckCircle2,
  AlertCircle,
  Mail,
  Slack,
  MessageSquare,
  GitCommit,
  Bell,
  RefreshCw,
} from 'lucide-react'
import { notificationsApi } from '../../services/api'

interface NotificationPreferencesModalProps {
  onClose: () => void
}

export const NotificationPreferencesModal: React.FC<NotificationPreferencesModalProps> = ({
  onClose,
}) => {
  const [emailEnabled, setEmailEnabled] = useState<boolean>(true)
  const [emailAddress, setEmailAddress] = useState<string>('')

  const [slackEnabled, setSlackEnabled] = useState<boolean>(false)
  const [slackWebhookUrl, setSlackWebhookUrl] = useState<string>('')

  const [discordEnabled, setDiscordEnabled] = useState<boolean>(false)
  const [discordWebhookUrl, setDiscordWebhookUrl] = useState<string>('')

  const [githubCommentsEnabled, setGithubCommentsEnabled] = useState<boolean>(true)
  const [inAppEnabled, setInAppEnabled] = useState<boolean>(true)

  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)
  const [testing, setTesting] = useState<boolean>(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const fetchPreferences = async () => {
    setLoading(true)
    try {
      const pref = await notificationsApi.getPreferences()
      setEmailEnabled(pref.email_enabled)
      setEmailAddress(pref.email_address || '')
      setSlackEnabled(pref.slack_enabled)
      setSlackWebhookUrl(pref.slack_webhook_url || '')
      setDiscordEnabled(pref.discord_enabled)
      setDiscordWebhookUrl(pref.discord_webhook_url || '')
      setGithubCommentsEnabled(pref.github_comments_enabled)
      setInAppEnabled(pref.in_app_enabled)
    } catch {
      // Defaults if offline
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPreferences()
  }, [])

  const handleSavePreferences = async () => {
    setSaving(true)
    setMessage(null)
    try {
      await notificationsApi.updatePreferences({
        email_enabled: emailEnabled,
        email_address: emailAddress || undefined,
        slack_enabled: slackEnabled,
        slack_webhook_url: slackWebhookUrl || undefined,
        discord_enabled: discordEnabled,
        discord_webhook_url: discordWebhookUrl || undefined,
        github_comments_enabled: githubCommentsEnabled,
        in_app_enabled: inAppEnabled,
      })
      setMessage({ type: 'success', text: 'Notification preferences saved successfully!' })
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err?.response?.data?.detail || 'Failed to save preferences.',
      })
    } finally {
      setSaving(false)
    }
  }

  const handleTestNotification = async () => {
    setTesting(true)
    setMessage(null)
    try {
      const res = await notificationsApi.sendTestNotification({
        channel: 'all',
        title: 'ReviewAI Multi-Channel Notification Test',
        message: 'Notification engine test across Slack, Discord, Email, GitHub, and In-App channels.',
      })
      setMessage({
        type: 'success',
        text: res.message || 'Test notification dispatched across active channels!',
      })
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err?.response?.data?.detail || 'Failed to send test notification.',
      })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="glass-card w-full max-w-xl rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-brand-400" />
            <h2 className="text-base font-bold text-slate-100">Notification Channel Preferences</h2>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-xs">
          {message && (
            <div
              className={`p-3.5 rounded-xl border flex items-center space-x-2 text-xs font-medium ${
                message.type === 'success'
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
              }`}
            >
              {message.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
              )}
              <span>{message.text}</span>
            </div>
          )}

          {loading ? (
            <div className="p-8 text-center text-slate-500">Loading preferences...</div>
          ) : (
            <div className="space-y-5">
              {/* GitHub PR Comments */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <GitCommit className="w-4 h-4 text-purple-400" />
                    <div>
                      <span className="font-semibold text-slate-200">GitHub PR Comments</span>
                      <p className="text-slate-400 text-[11px]">
                        Post automated review summaries and inline findings directly to GitHub PRs.
                      </p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={githubCommentsEnabled}
                    onChange={(e) => setGithubCommentsEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-brand-500 focus:ring-0"
                  />
                </div>
              </div>

              {/* Email Notifications */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <Mail className="w-4 h-4 text-blue-400" />
                    <div>
                      <span className="font-semibold text-slate-200">Email Notifications</span>
                      <p className="text-slate-400 text-[11px]">Send HTML code review summaries to your inbox.</p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={emailEnabled}
                    onChange={(e) => setEmailEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-brand-500 focus:ring-0"
                  />
                </div>

                {emailEnabled && (
                  <input
                    type="email"
                    placeholder="dev@company.com"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
                  />
                )}
              </div>

              {/* Slack Webhook */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <Slack className="w-4 h-4 text-emerald-400" />
                    <div>
                      <span className="font-semibold text-slate-200">Slack Webhook Integration</span>
                      <p className="text-slate-400 text-[11px]">Send Block Kit alerts to Slack channels.</p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={slackEnabled}
                    onChange={(e) => setSlackEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-brand-500 focus:ring-0"
                  />
                </div>

                {slackEnabled && (
                  <input
                    type="text"
                    placeholder="https://hooks.slack.com/services/T00/B00/XXXXX"
                    value={slackWebhookUrl}
                    onChange={(e) => setSlackWebhookUrl(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 font-mono text-[11px] placeholder-slate-500 focus:outline-none focus:border-brand-500"
                  />
                )}
              </div>

              {/* Discord Webhook */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <MessageSquare className="w-4 h-4 text-indigo-400" />
                    <div>
                      <span className="font-semibold text-slate-200">Discord Webhook Integration</span>
                      <p className="text-slate-400 text-[11px]">Send Embed cards to Discord channels.</p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={discordEnabled}
                    onChange={(e) => setDiscordEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-brand-500 focus:ring-0"
                  />
                </div>

                {discordEnabled && (
                  <input
                    type="text"
                    placeholder="https://discord.com/api/webhooks/123/xyz"
                    value={discordWebhookUrl}
                    onChange={(e) => setDiscordWebhookUrl(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 font-mono text-[11px] placeholder-slate-500 focus:outline-none focus:border-brand-500"
                  />
                )}
              </div>

              {/* In-App Notifications */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    <Bell className="w-4 h-4 text-amber-400" />
                    <div>
                      <span className="font-semibold text-slate-200">In-App Navbar Notifications</span>
                      <p className="text-slate-400 text-[11px]">Display real-time bell badge indicators.</p>
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={inAppEnabled}
                    onChange={(e) => setInAppEnabled(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-brand-500 focus:ring-0"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-900/80 border-t border-slate-800 flex items-center justify-between">
          <button
            onClick={handleTestNotification}
            disabled={testing || loading}
            className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors border border-slate-700"
          >
            <Send className={`w-3.5 h-3.5 ${testing ? 'animate-spin' : ''}`} />
            <span>{testing ? 'Testing...' : 'Send Test Alert'}</span>
          </button>

          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSavePreferences}
              disabled={saving || loading}
              className="flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium rounded-lg transition-colors shadow-lg shadow-brand-600/20"
            >
              <Save className={`w-3.5 h-3.5 ${saving ? 'animate-spin' : ''}`} />
              <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
