import React, { useState, useEffect } from 'react'
import {
  FileText,
  Download,
  Copy,
  Check,
  Sparkles,
  ShieldAlert,
  Zap,
  Bug,
  TestTube2,
  Activity,
  FileCheck,
  ExternalLink,
  Layers,
} from 'lucide-react'
import { reportsApi, apiClient } from '../services/api'
import { Repository } from '../types'
import { LoadingSpinner } from '../components/common/LoadingSpinner'

export const ReportsPage: React.FC = () => {
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string>('')
  const [prNumber, setPrNumber] = useState<number>(1)
  const [exportFormat, setExportFormat] = useState<'PDF' | 'MARKDOWN' | 'HTML' | 'JSON'>('PDF')
  const [loading, setLoading] = useState<boolean>(false)
  const [copied, setCopied] = useState<boolean>(false)

  const [reportResult, setReportResult] = useState<{
    report_id: string
    repository_full_name: string
    pr_number: number
    report_type: string
    report_title: string
    content: string
    report_metadata: any
    download_url: string
  } | null>(null)

  useEffect(() => {
    const fetchRepos = async () => {
      try {
        const res = await apiClient.get('/github/repos')
        setRepositories(res.data)
        if (res.data.length > 0) {
          setSelectedRepo(res.data[0].full_name)
        }
      } catch {
        setSelectedRepo('acme-corp/user-service')
      }
    }
    fetchRepos()
  }, [])

  const handleGenerateReport = async () => {
    setLoading(true)
    try {
      const repoName = selectedRepo || 'acme-corp/core-service'
      const data = await reportsApi.generateReport({
        repository_full_name: repoName,
        pr_number: prNumber,
        format: exportFormat,
      })
      setReportResult(data)
    } catch {
      alert('Failed to generate review report.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (!reportResult) return
    navigator.clipboard.writeText(reportResult.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    if (!reportResult) return
    const fmt = exportFormat.toLowerCase()
    let mediaType = 'text/plain;charset=utf-8'
    let ext = '.md'

    if (fmt === 'pdf') {
      mediaType = 'text/html;charset=utf-8'
      ext = '.html'
    } else if (fmt === 'html') {
      mediaType = 'text/html;charset=utf-8'
      ext = '.html'
    } else if (fmt === 'json') {
      mediaType = 'application/json;charset=utf-8'
      ext = '.json'
    }

    const blob = new Blob([reportResult.content], { type: mediaType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const safeRepo = reportResult.repository_full_name.replace('/', '_')
    a.download = `REVIEW_REPORT_${safeRepo}_PR${reportResult.pr_number}${ext}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const meta = reportResult?.report_metadata

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 flex items-center space-x-3">
            <FileText className="w-8 h-8 text-brand-400" />
            <span>Executive Review Reports</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Generate and export comprehensive code review reports across PDF, Markdown, HTML, and JSON formats.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {['PDF', 'MARKDOWN', 'HTML', 'JSON'].map((fmt) => (
            <button
              key={fmt}
              onClick={() => setExportFormat(fmt as any)}
              className={`px-4 py-2 text-xs font-bold rounded-xl border transition-all ${
                exportFormat === fmt
                  ? 'bg-brand-500/20 border-brand-500 text-brand-300 shadow-lg shadow-brand-500/10'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              {fmt}
            </button>
          ))}
        </div>
      </div>

      {/* Control Panel Card */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-2">Target Repository:</label>
            {repositories.length > 0 ? (
              <select
                value={selectedRepo}
                onChange={(e) => setSelectedRepo(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-medium text-slate-200 focus:outline-none focus:border-brand-500"
              >
                {repositories.map((r) => (
                  <option key={r.id} value={r.full_name}>
                    {r.full_name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={selectedRepo}
                onChange={(e) => setSelectedRepo(e.target.value)}
                placeholder="owner/repository"
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono text-slate-200"
              />
            )}
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-2">Pull Request Number:</label>
            <input
              type="number"
              min={1}
              value={prNumber}
              onChange={(e) => setPrNumber(parseInt(e.target.value) || 1)}
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono text-slate-200"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleGenerateReport}
              disabled={loading}
              className="w-full py-2.5 bg-brand-500 hover:bg-brand-400 text-white font-bold text-sm rounded-xl shadow-lg shadow-brand-500/20 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <Sparkles className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Compiling Report...' : `Generate ${exportFormat} Report`}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Generated Report Output */}
      {reportResult && (
        <div className="space-y-6">
          {/* Top Metric Highlights Cards */}
          {meta && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400">Quality Score</p>
                  <p className="text-2xl font-black text-emerald-400 mt-1">
                    {meta.quality_score?.overall_score}/100 ({meta.quality_score?.grade})
                  </p>
                </div>
                <Activity className="w-8 h-8 text-emerald-400/30" />
              </div>

              <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400">Security Risks</p>
                  <p className="text-2xl font-black text-rose-400 mt-1">
                    {meta.security_summary?.total_vulnerabilities} Issues
                  </p>
                </div>
                <ShieldAlert className="w-8 h-8 text-rose-400/30" />
              </div>

              <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400">Performance</p>
                  <p className="text-2xl font-black text-amber-400 mt-1">
                    {meta.performance_summary?.total_bottlenecks} Bottlenecks
                  </p>
                </div>
                <Zap className="w-8 h-8 text-amber-400/30" />
              </div>

              <div className="glass-card p-5 rounded-xl border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400">AI Tests</p>
                  <p className="text-2xl font-black text-violet-400 mt-1">
                    {meta.generated_tests?.total_generated} Test Cases
                  </p>
                </div>
                <TestTube2 className="w-8 h-8 text-violet-400/30" />
              </div>
            </div>
          )}

          {/* Action Bar & Live Preview */}
          <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-slate-100">{reportResult.report_title}</h3>
                <p className="text-xs text-slate-400">
                  Format: <span className="font-mono text-brand-400">{reportResult.report_type}</span> | Ready for download
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleCopy}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl flex items-center space-x-2 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? 'Copied!' : 'Copy Raw Report'}</span>
                </button>
                <button
                  onClick={handleDownload}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl flex items-center space-x-2 shadow-lg shadow-emerald-600/20 transition-all"
                >
                  <Download className="w-4 h-4" />
                  <span>Download {exportFormat} File</span>
                </button>
              </div>
            </div>

            {/* Document Content Box */}
            {exportFormat === 'HTML' || exportFormat === 'PDF' ? (
              <iframe
                title="Report Preview"
                srcDoc={reportResult.content}
                className="w-full h-[600px] border border-slate-800 rounded-xl bg-white"
              />
            ) : (
              <pre className="p-5 bg-[#070a12] border border-slate-800 rounded-xl font-mono text-xs text-slate-200 overflow-x-auto max-h-[600px] overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {reportResult.content}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
