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
  const chartData = data && data.length > 0 ? data : [
    { date: 'Mon', count: 4 },
    { date: 'Tue', count: 7 },
    { date: 'Wed', count: 3 },
    { date: 'Thu', count: 8 },
    { date: 'Fri', count: 5 },
    { date: 'Sat', count: 2 },
    { date: 'Sun', count: 6 },
  ]

  const maxCount = Math.max(...chartData.map((d) => d.count), 1)

  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <GitCommit className="w-5 h-5 text-brand-400" />
          <h3 className="text-base font-semibold text-slate-200">Commit Activity (Last 7 Days)</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">Daily Frequency</span>
      </div>

      <div className="h-32 flex items-end justify-between space-x-2 pt-4 pb-1 px-1 border-b border-slate-800">
        {chartData.map((item, idx) => {
          const heightPercent = Math.round((item.count / maxCount) * 100)
          return (
            <div key={idx} className="flex-1 h-full flex flex-col justify-end items-center group relative">
              {/* Tooltip */}
              <div className="absolute -top-8 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 text-slate-200 text-[10px] py-1 px-2 rounded shadow border border-slate-700 pointer-events-none whitespace-nowrap z-10">
                {item.count} commits on {item.date}
              </div>

              {/* Count Badge */}
              <span className="text-[10px] font-semibold text-slate-400 mb-1 group-hover:text-brand-400 transition-colors">
                {item.count}
              </span>

              {/* Bar */}
              <div
                style={{ height: `${Math.max(heightPercent, 14)}%` }}
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
