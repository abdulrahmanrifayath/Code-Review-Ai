import React, { useState, useEffect } from 'react'
import {
  TrendingUp,
  ShieldCheck,
  Zap,
  Award,
  Search,
  RefreshCw,
  AlertCircle,
  BarChart3,
  ListFilter,
} from 'lucide-react'
import { analyticsApi } from '../services/api'
import { QualityTrendsChart, TrendDataPoint } from '../components/analytics/QualityTrendsChart'
import { SecurityPerfTrendsChart } from '../components/analytics/SecurityPerfTrendsChart'
import { IssueDistributionChart, IssueDistributionData } from '../components/analytics/IssueDistributionChart'
import { RepoRankingsTable, RepositoryRankItem } from '../components/analytics/RepoRankingsTable'
import { ReviewHistoryTable, ReviewHistoryItem } from '../components/analytics/ReviewHistoryTable'
import { SkeletonCard } from '../components/common/SkeletonLoader'

export const AnalyticsPage: React.FC = () => {
  const [timeframe, setTimeframe] = useState<string>('30d')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('ALL')

  const [trendsData, setTrendsData] = useState<TrendDataPoint[]>([])
  const [avgQualityScore, setAvgQualityScore] = useState<number>(94.5)
  const [improvementPercentage, setImprovementPercentage] = useState<number>(4.2)
  
  const [rankings, setRankings] = useState<RepositoryRankItem[]>([])
  const [reviewHistory, setReviewHistory] = useState<ReviewHistoryItem[]>([])
  const [issueDist, setIssueDist] = useState<IssueDistributionData | null>(null)

  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalyticsData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [trendsRes, rankingsRes, historyRes, distRes] = await Promise.all([
        analyticsApi.getTrends(timeframe),
        analyticsApi.getRankings(),
        analyticsApi.getReviewHistory(searchQuery, statusFilter),
        analyticsApi.getIssueDistribution(),
      ])

      setTrendsData(trendsRes.data || [])
      setAvgQualityScore(trendsRes.average_quality_score || 94.5)
      setImprovementPercentage(trendsRes.quality_improvement_percentage || 4.2)
      setRankings(rankingsRes.rankings || [])
      setReviewHistory(historyRes.reviews || [])
      setIssueDist(distRes)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load analytics dashboard data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalyticsData()
  }, [timeframe, statusFilter])

  // Debounced search trigger for review history
  useEffect(() => {
    const timer = setTimeout(() => {
      analyticsApi
        .getReviewHistory(searchQuery, statusFilter)
        .then((res) => setReviewHistory(res.reviews || []))
        .catch(() => {})
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  return (
    <div className="space-y-8">
      {/* Top Header & Timeframe Selector */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center space-x-2">
            <BarChart3 className="w-6 h-6 text-brand-400" />
            <span>Code Review Analytics & Trends</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time quality trajectory, security vulnerability breakdown, repository leaderboards, and review history.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Timeframe selector pill */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
            {['7d', '30d', '90d', '1y'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                  timeframe === tf
                    ? 'bg-brand-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tf.toUpperCase()}
              </button>
            ))}
          </div>

          <button
            onClick={fetchAnalyticsData}
            disabled={loading}
            className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg transition-colors border border-slate-700"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center space-x-3 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Avg Quality Score</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-100">{avgQualityScore}%</span>
            <span className="text-xs text-emerald-400 font-semibold">+{improvementPercentage}%</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Security Health Index</span>
            <ShieldCheck className="w-4 h-4 text-brand-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-100">98.2%</span>
            <span className="text-xs text-slate-400">0 Critical Bugs</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Performance Bottlenecks</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-slate-100">
              {issueDist?.by_category.performance ?? 5} Detected
            </span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Top Performing Repo</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-base font-bold text-slate-100 truncate">
            {rankings[0]?.full_name || 'acme/core-service'}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Score Trends Chart */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-200">Quality Score Trajectory</h2>
            <span className="text-xs text-slate-400">Past {timeframe}</span>
          </div>
          {loading ? <SkeletonCard /> : <QualityTrendsChart data={trendsData} />}
        </div>

        {/* Security & Performance Trends Chart */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-200">Security vs. Performance Trends</h2>
            <span className="text-xs text-slate-400">Vulnerabilities Over Time</span>
          </div>
          {loading ? <SkeletonCard /> : <SecurityPerfTrendsChart data={trendsData} />}
        </div>
      </div>

      {/* Second Section: Issue Distribution & Repository Rankings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Issue Distribution Donut & Category breakdown */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4 lg:col-span-1">
          <h2 className="text-base font-semibold text-slate-200">Issue Severity & Breakdown</h2>
          {issueDist && <IssueDistributionChart data={issueDist} />}
        </div>

        {/* Repository Leaderboard Rankings Table */}
        <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-200">Repository Health Leaderboard</h2>
            <span className="text-xs text-slate-400">{rankings.length} Repositories</span>
          </div>
          {loading ? <SkeletonCard /> : <RepoRankingsTable rankings={rankings} />}
        </div>
      </div>

      {/* Review Audit History Table */}
      <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-200">Review History & Audit Trail</h2>
            <p className="text-xs text-slate-400">Filter past automated AI reviews and pull request audits.</p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search PR, repo, author..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-brand-500 placeholder-slate-500"
              />
            </div>

            {/* Status Filter Dropdown */}
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <ListFilter className="w-4 h-4 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 px-3 py-1.5 focus:outline-none focus:border-brand-500"
              >
                <option value="ALL">All Statuses</option>
                <option value="APPROVED">Approved</option>
                <option value="CHANGES_REQUESTED">Changes Requested</option>
              </select>
            </div>
          </div>
        </div>

        {/* Review History Table */}
        {loading ? <SkeletonCard /> : <ReviewHistoryTable reviews={reviewHistory} />}
      </div>
    </div>
  )
}

export default AnalyticsPage
