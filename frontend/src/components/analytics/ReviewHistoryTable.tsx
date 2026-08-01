import React from 'react'
import { ExternalLink, CheckCircle2, XCircle, Clock, GitPullRequest } from 'lucide-react'

export interface ReviewHistoryItem {
  id: string
  pr_number: number
  pr_title: string
  repository_full_name: string
  author_login: string
  state: string
  review_status: string
  quality_score: number
  findings_count: number
  created_at: string
  html_url?: string
}

interface ReviewHistoryTableProps {
  reviews: ReviewHistoryItem[]
}

const getStatusBadge = (reviewStatus: string) => {
  switch (reviewStatus) {
    case 'APPROVED':
      return (
        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Approved</span>
        </span>
      )
    case 'CHANGES_REQUESTED':
      return (
        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-400 text-xs font-semibold border border-rose-500/20">
          <XCircle className="w-3.5 h-3.5" />
          <span>Changes Requested</span>
        </span>
      )
    default:
      return (
        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-semibold border border-amber-500/20">
          <Clock className="w-3.5 h-3.5" />
          <span>In Review</span>
        </span>
      )
  }
}

export const ReviewHistoryTable: React.FC<ReviewHistoryTableProps> = ({ reviews }) => {
  if (reviews.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm">
        No review history matches your current search & filter criteria.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-slate-300">
        <thead className="bg-slate-900/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-3.5 px-4">Pull Request</th>
            <th className="py-3.5 px-4">Repository</th>
            <th className="py-3.5 px-4">Author</th>
            <th className="py-3.5 px-4 text-center">Status</th>
            <th className="py-3.5 px-4 text-center">Quality Score</th>
            <th className="py-3.5 px-4 text-center">Issues</th>
            <th className="py-3.5 px-4 text-right">Date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {reviews.map((rev) => (
            <tr key={rev.id} className="hover:bg-slate-800/40 transition-colors group">
              {/* PR Title & Number */}
              <td className="py-3.5 px-4">
                <div className="flex items-center space-x-2">
                  <GitPullRequest className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                  <a
                    href={rev.html_url || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="font-medium text-slate-100 hover:text-brand-400 transition-colors flex items-center space-x-1"
                  >
                    <span>#{rev.pr_number} {rev.pr_title}</span>
                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400" />
                  </a>
                </div>
              </td>

              {/* Repository */}
              <td className="py-3.5 px-4 text-slate-400 text-xs font-mono">
                {rev.repository_full_name}
              </td>

              {/* Author */}
              <td className="py-3.5 px-4 font-medium text-slate-300">
                @{rev.author_login}
              </td>

              {/* Review Status */}
              <td className="py-3.5 px-4 text-center">
                {getStatusBadge(rev.review_status)}
              </td>

              {/* Score */}
              <td className="py-3.5 px-4 text-center font-bold">
                <span
                  className={
                    rev.quality_score >= 90
                      ? 'text-emerald-400'
                      : rev.quality_score >= 80
                      ? 'text-blue-400'
                      : 'text-amber-400'
                  }
                >
                  {rev.quality_score}%
                </span>
              </td>

              {/* Findings count */}
              <td className="py-3.5 px-4 text-center text-xs">
                {rev.findings_count > 0 ? (
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 font-semibold border border-amber-500/20">
                    {rev.findings_count} findings
                  </span>
                ) : (
                  <span className="text-emerald-400 font-medium">0 issues</span>
                )}
              </td>

              {/* Date */}
              <td className="py-3.5 px-4 text-right text-xs text-slate-500">
                {new Date(rev.created_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
