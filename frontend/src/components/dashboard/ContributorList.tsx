import React from 'react'
import { Users, User } from 'lucide-react'

interface Contributor {
  author_name: string
  commits_count: number
  prs_count: number
  avatar_url?: string
}

interface ContributorListProps {
  contributors: Contributor[]
}

export const ContributorList: React.FC<ContributorListProps> = ({ contributors }) => {
  return (
    <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-slate-200">Active Contributors</h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">{contributors.length} Total</span>
      </div>

      <div className="space-y-3">
        {contributors.map((c, idx) => (
          <div
            key={idx}
            className="p-3 bg-slate-900/50 border border-slate-800/80 rounded-lg flex items-center justify-between text-xs"
          >
            <div className="flex items-center space-x-3">
              <div className="p-1.5 bg-slate-800 rounded-full text-slate-400">
                <User className="w-4 h-4" />
              </div>
              <div>
                <p className="font-semibold text-slate-200">{c.author_name}</p>
                <p className="text-slate-500">{c.commits_count} commits submitted</p>
              </div>
            </div>

            <span className="px-2.5 py-1 bg-slate-800 text-slate-300 rounded font-medium">
              {c.prs_count} PRs
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
