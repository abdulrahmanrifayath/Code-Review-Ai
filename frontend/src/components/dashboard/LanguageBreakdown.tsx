import React from 'react'

interface LanguageShare {
  language: string
  percentage: number
  color: string
}

interface LanguageBreakdownProps {
  languages: LanguageShare[]
}

export const LanguageBreakdown: React.FC<LanguageBreakdownProps> = ({ languages }) => {
  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
      <h3 className="text-base font-semibold text-slate-200">Languages Breakdown</h3>

      {/* Multi-color Bar */}
      <div className="h-3 w-full bg-slate-800 rounded-full flex overflow-hidden">
        {languages.map((lang, idx) => (
          <div
            key={idx}
            style={{
              width: `${lang.percentage}%`,
              backgroundColor: lang.color,
            }}
            title={`${lang.language}: ${lang.percentage}%`}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
        {languages.map((lang, idx) => (
          <div key={idx} className="flex items-center space-x-2">
            <span
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: lang.color }}
            />
            <span className="text-xs font-medium text-slate-300 truncate">{lang.language}</span>
            <span className="text-xs font-semibold text-slate-500">{lang.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
