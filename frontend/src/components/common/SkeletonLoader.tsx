import React from 'react'

export const SkeletonCard: React.FC = () => (
  <div className="glass-card p-5 rounded-xl border border-slate-800 animate-pulse space-y-3">
    <div className="h-4 bg-slate-800 rounded w-1/3"></div>
    <div className="h-8 bg-slate-800 rounded w-1/2"></div>
  </div>
)

export const SkeletonChart: React.FC = () => (
  <div className="glass-card p-6 rounded-xl border border-slate-800 animate-pulse space-y-4">
    <div className="h-5 bg-slate-800 rounded w-1/4"></div>
    <div className="h-44 bg-slate-800/60 rounded-lg"></div>
  </div>
)
