import React, { useState } from 'react'
import { ShieldAlert, AlertOctagon, AlertTriangle, Info, CheckCircle2, Code2 } from 'lucide-react'

export interface SecurityFinding {
  id?: string
  rule_id: string
  category: string
  cwe_id: string
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | string
  title: string
  description: string
  file_path: string
  line_number: number
  code_snippet?: string
  remediation_suggestion?: string
}

export interface SecurityDashboardProps {
  repositoryFullName: string
  prNumber: number
  totalVulnerabilitiesCount: number
  criticalCount: number
  highCount: number
  mediumCount: number
  lowCount: number
  findings: SecurityFinding[]
}

export const SecurityDashboardCard: React.FC<SecurityDashboardProps> = ({
  repositoryFullName,
  prNumber,
  totalVulnerabilitiesCount,
  criticalCount,
  highCount,
  mediumCount,
  lowCount,
  findings,
}) => {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL')

  const filteredFindings =
    selectedSeverity === 'ALL'
      ? findings
      : findings.filter((f) => f.severity.toUpperCase() === selectedSeverity)

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 border-rose-500/40 text-rose-400'
      case 'HIGH':
        return 'bg-amber-500/20 border-amber-500/40 text-amber-400'
      case 'MEDIUM':
        return 'bg-yellow-500/20 border-yellow-500/40 text-yellow-400'
      default:
        return 'bg-blue-500/20 border-blue-500/40 text-blue-400'
    }
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">SAST Security Dashboard</h3>
            <p className="text-xs text-slate-400">
              {repositoryFullName} • PR #{prNumber}
            </p>
          </div>
        </div>
        <span className="px-3 py-1 bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold rounded-full self-start sm:self-auto">
          {totalVulnerabilitiesCount} Vulnerabilities Detected
        </span>
      </div>

      {/* Severity Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          onClick={() => setSelectedSeverity(selectedSeverity === 'CRITICAL' ? 'ALL' : 'CRITICAL')}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            selectedSeverity === 'CRITICAL'
              ? 'bg-rose-500/20 border-rose-500 text-rose-300 shadow-lg shadow-rose-500/10'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-rose-400">
            <span>CRITICAL</span>
            <AlertOctagon className="w-4 h-4" />
          </div>
          <div className="text-2xl font-extrabold mt-1">{criticalCount}</div>
        </button>

        <button
          onClick={() => setSelectedSeverity(selectedSeverity === 'HIGH' ? 'ALL' : 'HIGH')}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            selectedSeverity === 'HIGH'
              ? 'bg-amber-500/20 border-amber-500 text-amber-300 shadow-lg shadow-amber-500/10'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-amber-400">
            <span>HIGH</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-extrabold mt-1">{highCount}</div>
        </button>

        <button
          onClick={() => setSelectedSeverity(selectedSeverity === 'MEDIUM' ? 'ALL' : 'MEDIUM')}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            selectedSeverity === 'MEDIUM'
              ? 'bg-yellow-500/20 border-yellow-500 text-yellow-300 shadow-lg shadow-yellow-500/10'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-yellow-400">
            <span>MEDIUM</span>
            <Info className="w-4 h-4" />
          </div>
          <div className="text-2xl font-extrabold mt-1">{mediumCount}</div>
        </button>

        <button
          onClick={() => setSelectedSeverity(selectedSeverity === 'LOW' ? 'ALL' : 'LOW')}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            selectedSeverity === 'LOW'
              ? 'bg-blue-500/20 border-blue-500 text-blue-300 shadow-lg shadow-blue-500/10'
              : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
          }`}
        >
          <div className="flex items-center justify-between text-xs font-semibold text-blue-400">
            <span>LOW / INFO</span>
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="text-2xl font-extrabold mt-1">{lowCount}</div>
        </button>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800/60 text-slate-500 text-sm">
            No vulnerabilities found matching the selected filter.
          </div>
        ) : (
          filteredFindings.map((finding, idx) => (
            <div
              key={idx}
              className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3 transition-all hover:border-slate-700"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <span
                    className={`px-2.5 py-0.5 border text-[11px] font-extrabold rounded-md uppercase tracking-wider ${getSeverityBadge(
                      finding.severity
                    )}`}
                  >
                    {finding.severity}
                  </span>
                  <span className="px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[11px] rounded">
                    {finding.cwe_id}
                  </span>
                  <span className="text-xs font-semibold text-slate-400">{finding.category}</span>
                </div>
                <span className="text-xs font-mono text-slate-500">
                  {finding.file_path}:L{finding.line_number}
                </span>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-200">{finding.title}</h4>
                <p className="text-xs text-slate-400 mt-1">{finding.description}</p>
              </div>

              {finding.code_snippet && (
                <div className="p-3 bg-[#0a0e17] rounded-lg border border-slate-800/80 font-mono text-xs text-rose-300/90 overflow-x-auto flex items-start space-x-2">
                  <Code2 className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                  <code>{finding.code_snippet}</code>
                </div>
              )}

              {finding.remediation_suggestion && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-300 space-y-1">
                  <span className="font-bold flex items-center space-x-1.5 text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Recommended Fix:</span>
                  </span>
                  <p className="text-emerald-200/90">{finding.remediation_suggestion}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
