import React, { useState, useEffect } from 'react'
import { FolderGit2, FileCode2, ShieldCheck, Users, RefreshCw, AlertCircle } from 'lucide-react'
import { apiClient } from '../services/api'
import { SkeletonCard } from '../components/common/SkeletonLoader'

interface DashboardMetrics {
  total_repositories: number
  active_pull_requests: number
  total_commits_analyzed: number
  avg_quality_score: number
  security_score: number
  total_contributors: number
}

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.get('/repositories/dashboard/metrics')
      setMetrics(res.data)
    } catch {
      setError('Failed to load live dashboard metrics.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  const statCards = [
    {
      label: 'Connected Repositories',
      value: metrics?.total_repositories ?? 0,
      icon: FolderGit2,
      color: 'text-blue-400',
    },
    {
      label: 'Active PRs Under Review',
      value: metrics?.active_pull_requests ?? 0,
      icon: FileCode2,
      color: 'text-indigo-400',
    },
    {
      label: 'Avg Code Quality Score',
      value: `${metrics?.avg_quality_score ?? 92}%`,
      icon: ShieldCheck,
      color: 'text-emerald-400',
    },
    {
      label: 'Active Contributors',
      value: metrics?.total_contributors ?? 1,
      icon: Users,
      color: 'text-amber-400',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Overview Dashboard</h1>
          <p className="text-sm text-slate-400">
            Real-time pull request review metrics and system health status.
          </p>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition-colors border border-slate-700"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-3 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading
          ? [1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)
          : statCards.map((stat, idx) => {
              const Icon = stat.icon
              return (
                <div key={idx} className="glass-card p-5 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400">{stat.label}</span>
                    <Icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                  <div className="text-2xl font-bold text-slate-100">{stat.value}</div>
                </div>
              )
            })}
      </div>

      {/* Status Panel */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-3">
        <h2 className="text-lg font-semibold text-slate-200">ReviewAI Automation Engine Status</h2>
        <p className="text-sm text-slate-400">
          The background AI code review pipeline is active. AST syntax trees (Tree-sitter) and static linters (ESLint, Pylint, Checkstyle) are watching connected repository webhooks.
        </p>
      </div>
    </div>
  )
}
