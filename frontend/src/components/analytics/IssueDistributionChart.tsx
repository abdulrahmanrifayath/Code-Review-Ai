import React from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'

export interface IssueDistributionData {
  total_findings: number
  by_severity: {
    critical: number
    high: number
    medium: number
    low: number
  }
  by_category: {
    security: number
    performance: number
    code_smell: number
    syntax_error: number
  }
  by_language: Record<string, number>
}

interface IssueDistributionChartProps {
  data: IssueDistributionData
}

const SEVERITY_COLORS = {
  Critical: '#ef4444', // Red
  High: '#f97316',     // Orange
  Medium: '#eab308',   // Yellow
  Low: '#3b82f6',      // Blue
}

export const IssueDistributionChart: React.FC<IssueDistributionChartProps> = ({ data }) => {
  const severityChartData = [
    { name: 'Critical', value: data.by_severity.critical, color: SEVERITY_COLORS.Critical },
    { name: 'High', value: data.by_severity.high, color: SEVERITY_COLORS.High },
    { name: 'Medium', value: data.by_severity.medium, color: SEVERITY_COLORS.Medium },
    { name: 'Low', value: data.by_severity.low, color: SEVERITY_COLORS.Low },
  ].filter((item) => item.value > 0)

  return (
    <div className="h-64 w-full flex flex-col justify-center items-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={severityChartData}
            cx="50%"
            cy="45%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={4}
            dataKey="value"
          >
            {severityChartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
            itemStyle={{ color: '#f8fafc' }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            wrapperStyle={{ fontSize: '12px' }}
            formatter={(value) => <span className="text-slate-300">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
