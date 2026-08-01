import React from 'react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

export interface TrendDataPoint {
  date: string
  quality_score: number
  security_issues: number
  performance_issues: number
  code_smells: number
  prs_reviewed: number
}

interface QualityTrendsChartProps {
  data: TrendDataPoint[]
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const val = payload[0].value
    return (
      <div className="bg-[#111827] border border-slate-700/80 p-3 rounded-lg shadow-xl text-xs space-y-1">
        <p className="font-semibold text-slate-300">{label}</p>
        <p className="text-emerald-400 font-bold flex items-center justify-between space-x-3">
          <span>Quality Score:</span>
          <span>{val}%</span>
        </p>
      </div>
    )
  }
  return null
}

export const QualityTrendsChart: React.FC<QualityTrendsChartProps> = ({ data }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="qualityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#64748b" fontSize={11} domain={[60, 100]} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="quality_score"
            stroke="#10b981"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#qualityGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
