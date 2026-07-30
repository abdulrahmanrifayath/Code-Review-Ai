import React from 'react'
import { GitCommit } from 'lucide-react'

interface CommitPoint {
  date: string
  count: number
}

interface CommitActivityChartProps {
  data: CommitPoint[]
}

export const CommitActivityChart: React.FC<CommitActivityChartProps> = ({ data }) => {
  const maxCount = Math.max(...data.map((d) => d.count), 1)

  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <GitCommit className="w-5 h-5 text-brand-400" />
          <h3 className="text-base font-semibold text-slate-200">Commit Activity (Last 7 Days)</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">Daily Frequency</span>
      </div>

      <div className="h-40 flex items-end justify-between space-x-3 pt-6 pb-2 px-2 border-b border-slate-800">
        {data.map((item, idx) => {
          const heightPercent = Math.round((item.count / maxCount) * 100)
          return (
            <div key={idx} className="flex-1 flex flex-col items-center group relative">
              {/* Tooltip */}
              <div className="absolute -top-8 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-slate-200 text-[10px] py-1 px-2 rounded shadow border border-slate-700 pointer-events-none whitespace-nowrap z-10">
                {item.count} commits on {item.date}
              </div>

              {/* Bar */}
              <div
                style={{ height: `${Math.max(heightPercent, 8)}%` }}
                className="w-full bg-gradient-to-t from-brand-600 to-indigo-500 rounded-t group-hover:from-brand-500 group-hover:to-indigo-400 transition-all duration-300 shadow-md shadow-brand-500/10"
              ></div>

              {/* Label */}
              <span className="text-[10px] text-slate-400 font-medium mt-2">{item.date}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
