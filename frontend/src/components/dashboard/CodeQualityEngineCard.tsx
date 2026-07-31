import React from 'react'
import { Activity, ShieldCheck, Wrench, FileText, Layers, TrendingUp, Award } from 'lucide-react'

export interface QualityMetrics {
  maintainability_score: number
  technical_debt_hours: number
  complexity_score: number
  doc_coverage_percentage: number
  architecture_score: number
  overall_quality_score: number
  grade: string
}

export interface TrendPoint {
  date: string
  maintainability_score: number
  technical_debt_hours: number
  complexity_score: number
  doc_coverage_percentage: number
  architecture_score: number
  overall_quality_score: number
}

export interface CodeQualityEngineCardProps {
  repositoryFullName: string
  currentQualityScore: number
  grade: string
  metrics: QualityMetrics
  trends: TrendPoint[]
}

export const CodeQualityEngineCard: React.FC<CodeQualityEngineCardProps> = ({
  repositoryFullName,
  currentQualityScore,
  grade,
  metrics,
  trends,
}) => {
  const getGradeColor = (g: string) => {
    switch (g.toUpperCase()) {
      case 'A+':
      case 'A':
        return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10'
      case 'B':
        return 'text-blue-400 border-blue-500/40 bg-blue-500/10'
      case 'C':
        return 'text-amber-400 border-amber-500/40 bg-amber-500/10'
      default:
        return 'text-rose-400 border-rose-500/40 bg-rose-500/10'
    }
  }

  // Calculate max score for trends scaling
  const maxScore = 100

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-xl text-blue-400">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Code Quality Engine</h3>
            <p className="text-xs text-slate-400">{repositoryFullName} • Health & Quality Metrics</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`px-4 py-1.5 border rounded-xl font-extrabold text-lg ${getGradeColor(grade)}`}>
            Grade {grade}
          </div>
        </div>
      </div>

      {/* Overall Score & Core Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {/* Maintainability */}
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Maintainability</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">{metrics.maintainability_score}/100</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
            <div
              className="bg-emerald-400 h-full transition-all duration-500"
              style={{ width: `${Math.min(100, metrics.maintainability_score)}%` }}
            />
          </div>
        </div>

        {/* Technical Debt */}
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Technical Debt</span>
            <Wrench className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">{metrics.technical_debt_hours} hrs</div>
          <p className="text-[10px] text-slate-500">Est. remediation time</p>
        </div>

        {/* Complexity */}
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Complexity</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">{metrics.complexity_score}</div>
          <p className="text-[10px] text-slate-500">Cyclomatic score</p>
        </div>

        {/* Doc Coverage */}
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Doc Coverage</span>
            <FileText className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">{metrics.doc_coverage_percentage}%</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
            <div
              className="bg-cyan-400 h-full transition-all duration-500"
              style={{ width: `${Math.min(100, metrics.doc_coverage_percentage)}%` }}
            />
          </div>
        </div>

        {/* Architecture Score */}
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1 col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Architecture</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-100">{metrics.architecture_score}/100</div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-2">
            <div
              className="bg-indigo-400 h-full transition-all duration-500"
              style={{ width: `${Math.min(100, metrics.architecture_score)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Historical Quality Trends Chart */}
      <div className="p-5 bg-slate-900/40 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Quality Score Trend Timeline</h4>
          </div>
          <span className="text-[11px] text-slate-500">Last 7 Snapshots</span>
        </div>

        {/* Bar chart representation */}
        <div className="h-36 flex items-end justify-between gap-2 pt-4 px-2 border-b border-slate-800">
          {trends.slice(-7).map((point, idx) => {
            const heightPercent = Math.max(10, Math.min(100, (point.overall_quality_score / maxScore) * 100))
            return (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group">
                <span className="text-[10px] font-semibold text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  {point.overall_quality_score}
                </span>
                <div className="w-full bg-slate-800/80 rounded-t-lg relative flex items-end overflow-hidden h-28">
                  <div
                    className="w-full bg-gradient-to-t from-blue-600 to-cyan-400 rounded-t-lg transition-all duration-500 group-hover:from-emerald-500 group-hover:to-cyan-300"
                    style={{ height: `${heightPercent}%` }}
                  />
                </div>
                <span className="text-[10px] text-slate-500 font-mono">{point.date}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
