import React from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { TrendDataPoint } from './QualityTrendsChart'

interface SecurityPerfTrendsChartProps {
  data: TrendDataPoint[]
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#111827] border border-slate-700/80 p-3 rounded-lg shadow-xl text-xs space-y-1.5">
        <p className="font-semibold text-slate-300">{label}</p>
        <div className="space-y-1">
          <p className="text-rose-400 flex items-center justify-between space-x-4">
            <span>Security Issues:</span>
            <span className="font-bold">{payload[0]?.value}</span>
          </p>
          <p className="text-amber-400 flex items-center justify-between space-x-4">
            <span>Performance Bottlenecks:</span>
            <span className="font-bold">{payload[1]?.value}</span>
          </p>
        </div>
      </div>
    )
  }
  return null
}

export const SecurityPerfTrendsChart: React.FC<SecurityPerfTrendsChartProps> = ({ data }) => {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }}
            formatter={(value) => <span className="text-slate-300">{value}</span>}
          />
          <Line
            type="monotone"
            name="Security Vulnerabilities"
            dataKey="security_issues"
            stroke="#f43f5e"
            strokeWidth={2}
            dot={{ r: 3, fill: '#f43f5e' }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            name="Performance Bottlenecks"
            dataKey="performance_issues"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ r: 3, fill: '#f59e0b' }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
