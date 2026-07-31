import React, { useState } from 'react'
import { Zap, AlertTriangle, Cpu, Database, Clock, HardDrive, Globe, Code, ArrowRight, CheckCircle2 } from 'lucide-react'

export interface PerformanceFinding {
  id?: string
  rule_id?: string
  category?: string
  title: string
  description: string
  impact_level: 'HIGH' | 'MEDIUM' | 'LOW' | string
  complexity_delta?: string
  suggestion_type?: 'Caching' | 'Pagination' | 'Indexes' | 'Async' | 'Lazy loading' | string
  file_path: string
  start_line: number
  end_line: number
  code_snippet?: string
  optimization_suggestion?: string
  structured_recommendation?: string
}

export interface PerformanceDashboardProps {
  repositoryFullName: string
  prNumber: number
  findings: PerformanceFinding[]
  highImpactCount: number
  mediumImpactCount: number
  lowImpactCount: number
}

export const PerformanceDashboardCard: React.FC<PerformanceDashboardProps> = ({
  repositoryFullName,
  prNumber,
  findings,
  highImpactCount,
  mediumImpactCount,
  lowImpactCount,
}) => {
  const [selectedFilter, setSelectedFilter] = useState<string>('ALL')
  const [selectedSuggestion, setSelectedSuggestion] = useState<string>('ALL')

  const filteredFindings = findings.filter((f) => {
    const categoryMatch =
      selectedFilter === 'ALL' || (f.category && f.category.toUpperCase() === selectedFilter.toUpperCase())
    const suggestionMatch =
      selectedSuggestion === 'ALL' ||
      (f.suggestion_type && f.suggestion_type.toUpperCase() === selectedSuggestion.toUpperCase())
    return categoryMatch && suggestionMatch
  })

  const getImpactBadge = (impact: string) => {
    switch (impact.toUpperCase()) {
      case 'HIGH':
        return 'bg-rose-500/20 border-rose-500/40 text-rose-300'
      case 'MEDIUM':
        return 'bg-amber-500/20 border-amber-500/40 text-amber-300'
      default:
        return 'bg-blue-500/20 border-blue-500/40 text-blue-300'
    }
  }

  const getSuggestionBadge = (suggestion?: string) => {
    switch ((suggestion || '').toUpperCase()) {
      case 'CACHING':
        return 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
      case 'PAGINATION':
        return 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
      case 'INDEXES':
        return 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
      case 'ASYNC':
        return 'bg-violet-500/20 border-violet-500/40 text-violet-300'
      case 'LAZY LOADING':
        return 'bg-amber-500/20 border-amber-500/40 text-amber-300'
      default:
        return 'bg-slate-800 border-slate-700 text-slate-300'
    }
  }

  const getCategoryIcon = (category?: string) => {
    switch ((category || '').toUpperCase()) {
      case 'NESTED LOOPS':
        return <Cpu className="w-4 h-4 text-purple-400" />
      case 'REPEATED DATABASE QUERIES':
        return <Database className="w-4 h-4 text-cyan-400" />
      case 'BLOCKING OPERATIONS':
        return <Clock className="w-4 h-4 text-rose-400" />
      case 'LARGE MEMORY ALLOCATIONS':
        return <HardDrive className="w-4 h-4 text-amber-400" />
      case 'REPEATED API CALLS':
        return <Globe className="w-4 h-4 text-blue-400" />
      case 'EXPENSIVE REGEX':
        return <Code className="w-4 h-4 text-emerald-400" />
      default:
        return <Zap className="w-4 h-4 text-amber-400" />
    }
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Performance Analyzer</h3>
            <p className="text-xs text-slate-400">
              {repositoryFullName} • PR #{prNumber}
            </p>
          </div>
        </div>
        <span className="px-3 py-1 bg-slate-900 border border-slate-800 text-amber-400 text-xs font-semibold rounded-full self-start sm:self-auto">
          {findings.length} Bottlenecks Detected
        </span>
      </div>

      {/* Impact Counters */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl text-center">
          <span className="text-xs font-semibold text-rose-400 block">HIGH IMPACT</span>
          <span className="text-2xl font-extrabold text-slate-100 mt-1 block">{highImpactCount}</span>
        </div>
        <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl text-center">
          <span className="text-xs font-semibold text-amber-400 block">MEDIUM IMPACT</span>
          <span className="text-2xl font-extrabold text-slate-100 mt-1 block">{mediumImpactCount}</span>
        </div>
        <div className="p-3.5 bg-slate-900/60 border border-slate-800 rounded-xl text-center">
          <span className="text-xs font-semibold text-blue-400 block">LOW IMPACT</span>
          <span className="text-2xl font-extrabold text-slate-100 mt-1 block">{lowImpactCount}</span>
        </div>
      </div>

      {/* Suggestion Filter Chips */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-slate-400">Filter by Suggestion:</span>
        <div className="flex flex-wrap gap-2">
          {['ALL', 'Caching', 'Pagination', 'Indexes', 'Async', 'Lazy loading'].map((sug) => (
            <button
              key={sug}
              onClick={() => setSelectedSuggestion(sug)}
              className={`px-3 py-1 text-xs font-medium rounded-lg border transition-all ${
                selectedSuggestion === sug
                  ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                  : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              {sug}
            </button>
          ))}
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 text-slate-500 text-sm">
            No performance bottlenecks matching selected criteria.
          </div>
        ) : (
          filteredFindings.map((finding, idx) => (
            <div
              key={idx}
              className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4 transition-all hover:border-slate-700"
            >
              {/* Top metadata */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2.5 py-0.5 border text-[11px] font-extrabold rounded-md uppercase tracking-wider ${getImpactBadge(
                      finding.impact_level
                    )}`}
                  >
                    {finding.impact_level}
                  </span>
                  {finding.suggestion_type && (
                    <span
                      className={`px-2.5 py-0.5 border text-[11px] font-bold rounded-md uppercase ${getSuggestionBadge(
                        finding.suggestion_type
                      )}`}
                    >
                      Suggest: {finding.suggestion_type}
                    </span>
                  )}
                  <div className="flex items-center space-x-1 text-xs font-semibold text-slate-400">
                    {getCategoryIcon(finding.category)}
                    <span>{finding.category}</span>
                  </div>
                </div>
                {finding.complexity_delta && (
                  <span className="px-2.5 py-0.5 bg-slate-800 border border-slate-700 text-amber-300 font-mono text-[11px] rounded flex items-center space-x-1">
                    <span>Delta:</span>
                    <span className="font-bold">{finding.complexity_delta}</span>
                  </span>
                )}
              </div>

              {/* Title & Description */}
              <div>
                <h4 className="text-sm font-bold text-slate-200">{finding.title}</h4>
                <p className="text-xs text-slate-400 mt-1">{finding.description}</p>
              </div>

              {/* Code Snippet */}
              {finding.code_snippet && (
                <div className="p-3 bg-[#0a0e17] rounded-lg border border-slate-800/80 font-mono text-xs text-amber-300/90 overflow-x-auto">
                  <div className="text-[11px] text-slate-500 mb-1 font-sans">
                    {finding.file_path}: Lines {finding.start_line}-{finding.end_line}
                  </div>
                  <pre className="whitespace-pre-wrap">{finding.code_snippet}</pre>
                </div>
              )}

              {/* Structured Recommendation */}
              {finding.structured_recommendation && (
                <div className="p-3.5 bg-amber-500/10 border border-amber-500/20 rounded-xl space-y-2 text-xs">
                  <span className="font-bold text-amber-300 flex items-center space-x-1.5">
                    <CheckCircle2 className="w-4 h-4 text-amber-400" />
                    <span>Structured Recommendation ({finding.suggestion_type}):</span>
                  </span>
                  <pre className="whitespace-pre-wrap font-mono text-slate-200 text-[11px] bg-slate-950/80 p-2.5 rounded-lg border border-amber-500/20">
                    {finding.structured_recommendation}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
