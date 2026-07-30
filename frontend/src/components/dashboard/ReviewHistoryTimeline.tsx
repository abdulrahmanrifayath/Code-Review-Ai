import React from 'react'
import { GitPullRequest, CheckCircle2, AlertTriangle } from 'lucide-react'

interface ReviewItem {
  id: string
  pr_number: number
  pr_title: string
  status: string
  quality_score: number
  findings_count: number
  created_at: string
}

interface ReviewHistoryTimelineProps {
  reviews: ReviewItem[]
}

export const ReviewHistoryTimeline: React.FC<ReviewHistoryTimelineProps> = ({ reviews }) => {
  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
      <h3 className="text-base font-semibold text-slate-200">Recent Review Audit History</h3>

      {reviews.length === 0 ? (
        <div className="text-center py-6 text-slate-500 text-xs">No recent AI code review executions.</div>
      ) : (
        <div className="space-y-4 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
          {reviews.map((item) => (
            <div key={item.id} className="flex items-start space-x-4 relative">
              <div className="p-1 bg-slate-900 border border-slate-700 rounded-full z-10 text-brand-400">
                <GitPullRequest className="w-4 h-4" />
              </div>
              <div className="flex-1 bg-slate-900/40 p-3 rounded-lg border border-slate-800/60 flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-slate-200">
                    PR #{item.pr_number}: {item.pr_title}
                  </p>
                  <p className="text-slate-500 mt-0.5">
                    {new Date(item.created_at).toLocaleDateString()} • {item.findings_count} findings detected
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-brand-500/10 border border-brand-500/20 text-brand-400 font-bold rounded">
                    {item.quality_score}% Quality
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
