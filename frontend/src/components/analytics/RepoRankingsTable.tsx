import React from 'react'
import { Trophy, Star, ShieldAlert, GitPullRequest } from 'lucide-react'

export interface RepositoryRankItem {
  rank: number
  repository_id: string
  full_name: string
  owner_login: string
  language: string
  quality_score: number
  health_grade: string
  stargazers_count: number
  open_issues_count: number
  prs_count: number
  security_vulnerabilities_count: number
  performance_bottlenecks_count: number
}

interface RepoRankingsTableProps {
  rankings: RepositoryRankItem[]
}

const getGradeBadge = (grade: string) => {
  switch (grade) {
    case 'A+':
    case 'A':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    case 'B':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/30'
    case 'C':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    default:
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30'
  }
}

export const RepoRankingsTable: React.FC<RepoRankingsTableProps> = ({ rankings }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-slate-300">
        <thead className="bg-slate-900/60 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-3.5 px-4 text-center">Rank</th>
            <th className="py-3.5 px-4">Repository</th>
            <th className="py-3.5 px-4 text-center">Grade</th>
            <th className="py-3.5 px-4">Quality Score</th>
            <th className="py-3.5 px-4 text-center">Active PRs</th>
            <th className="py-3.5 px-4 text-center">Security</th>
            <th className="py-3.5 px-4 text-center">Stars</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {rankings.map((repo) => (
            <tr key={repo.repository_id} className="hover:bg-slate-800/40 transition-colors group">
              {/* Rank */}
              <td className="py-4 px-4 text-center">
                {repo.rank === 1 ? (
                  <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">
                    <Trophy className="w-4 h-4" />
                  </span>
                ) : repo.rank === 2 ? (
                  <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-slate-400/20 text-slate-300 font-bold border border-slate-400/30">
                    2
                  </span>
                ) : repo.rank === 3 ? (
                  <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-700/20 text-amber-600 font-bold border border-amber-700/30">
                    3
                  </span>
                ) : (
                  <span className="text-slate-500 font-medium">#{repo.rank}</span>
                )}
              </td>

              {/* Repository Name & Language */}
              <td className="py-4 px-4">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-slate-100 group-hover:text-brand-400 transition-colors">
                    {repo.full_name}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    {repo.language}
                  </span>
                </div>
              </td>

              {/* Grade Badge */}
              <td className="py-4 px-4 text-center">
                <span className={`px-2.5 py-1 text-xs font-bold rounded-lg border ${getGradeBadge(repo.health_grade)}`}>
                  {repo.health_grade}
                </span>
              </td>

              {/* Quality Score Bar */}
              <td className="py-4 px-4">
                <div className="space-y-1.5 min-w-[120px]">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-300">{repo.quality_score}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        repo.quality_score >= 90
                          ? 'bg-emerald-500'
                          : repo.quality_score >= 80
                          ? 'bg-blue-500'
                          : 'bg-amber-500'
                      }`}
                      style={{ width: `${repo.quality_score}%` }}
                    />
                  </div>
                </div>
              </td>

              {/* Active PRs */}
              <td className="py-4 px-4 text-center font-medium text-slate-300">
                <div className="inline-flex items-center space-x-1">
                  <GitPullRequest className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{repo.prs_count}</span>
                </div>
              </td>

              {/* Security Issues */}
              <td className="py-4 px-4 text-center">
                {repo.security_vulnerabilities_count > 0 ? (
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-xs font-semibold border border-rose-500/20">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>{repo.security_vulnerabilities_count}</span>
                  </span>
                ) : (
                  <span className="text-emerald-400 text-xs font-medium">Clean</span>
                )}
              </td>

              {/* Stars */}
              <td className="py-4 px-4 text-center text-slate-400">
                <div className="inline-flex items-center space-x-1">
                  <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/20" />
                  <span>{repo.stargazers_count}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
