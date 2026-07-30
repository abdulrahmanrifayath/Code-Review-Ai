import React from 'react'
import { ShieldAlert, Zap, Bug } from 'lucide-react'

interface QualityScoreCardProps {
  score: number
  healthScore: number
  grade: string
  securityCount: number
  performanceCount: number
  codeSmellsCount: number
}

export const QualityScoreCard: React.FC<QualityScoreCardProps> = ({
  score,
  healthScore,
  grade,
  securityCount,
  performanceCount,
  codeSmellsCount,
}) => {
  const getGradeColor = (g: string) => {
    switch (g) {
      case 'A+':
      case 'A':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
      case 'B':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
      default:
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20'
    }
  }

  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-200">Repository Health & Quality</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-bold border ${getGradeColor(
            grade
          )}`}
        >
          Grade {grade}
        </span>
      </div>

      <div className="flex items-center justify-around py-2">
        {/* Quality Score Radial */}
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center">
            <svg className="w-24 h-24 transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="36"
                stroke="currentColor"
                strokeWidth="8"
                className="text-slate-800"
                fill="transparent"
              />
              <circle
                cx="48"
                cy="48"
                r="36"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={226}
                strokeDashoffset={226 - (226 * score) / 100}
                className="text-brand-500 transition-all duration-1000 ease-out"
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <span className="absolute text-xl font-bold text-slate-100">{score}%</span>
          </div>
          <p className="text-xs font-medium text-slate-400 mt-2">Quality Score</p>
        </div>

        {/* Health Score Radial */}
        <div className="text-center">
          <div className="relative inline-flex items-center justify-center">
            <svg className="w-24 h-24 transform -rotate-90">
              <circle
                cx="48"
                cy="48"
                r="36"
                stroke="currentColor"
                strokeWidth="8"
                className="text-slate-800"
                fill="transparent"
              />
              <circle
                cx="48"
                cy="48"
                r="36"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray={226}
                strokeDashoffset={226 - (226 * healthScore) / 100}
                className="text-indigo-400 transition-all duration-1000 ease-out"
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <span className="absolute text-xl font-bold text-slate-100">{healthScore}%</span>
          </div>
          <p className="text-xs font-medium text-slate-400 mt-2">Health Rating</p>
        </div>
      </div>

      {/* Findings Breakdown */}
      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800/80">
        <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg text-center">
          <ShieldAlert className="w-4 h-4 text-rose-400 mx-auto mb-1" />
          <span className="text-sm font-bold text-rose-300">{securityCount}</span>
          <p className="text-[10px] text-slate-400 uppercase">Security</p>
        </div>
        <div className="p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-center">
          <Zap className="w-4 h-4 text-amber-400 mx-auto mb-1" />
          <span className="text-sm font-bold text-amber-300">{performanceCount}</span>
          <p className="text-[10px] text-slate-400 uppercase">Performance</p>
        </div>
        <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-lg text-center">
          <Bug className="w-4 h-4 text-blue-400 mx-auto mb-1" />
          <span className="text-sm font-bold text-blue-300">{codeSmellsCount}</span>
          <p className="text-[10px] text-slate-400 uppercase">Code Smells</p>
        </div>
      </div>
    </div>
  )
}
