import React from 'react'
import { FileCode2 } from 'lucide-react'

export const ReviewsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Code Reviews</h1>
        <p className="text-sm text-slate-400">History of generated AI code reviews and pull request reports.</p>
      </div>

      <div className="glass-card p-12 rounded-xl border border-slate-800 text-center space-y-3">
        <FileCode2 className="w-12 h-12 text-slate-600 mx-auto" />
        <h3 className="text-lg font-semibold text-slate-300">No Review Reports Yet</h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto">
          When pull requests are opened or updated in connected repositories, AI review analysis reports will appear here.
        </p>
      </div>
    </div>
  )
}
