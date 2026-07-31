import React, { useState } from 'react'
import { FileText, Download, Copy, Check, Sparkles, BookOpen, Code2, Layers, MessageSquare, Terminal } from 'lucide-react'
import { docGeneratorApi } from '../../services/api'

export interface DocGeneratorCardProps {
  repositoryFullName?: string
  defaultTargetFile?: string
  defaultCodeContent?: string
}

export const DocGeneratorCard: React.FC<DocGeneratorCardProps> = ({
  repositoryFullName = 'Repository Code',
  defaultTargetFile = 'user_service.py',
  defaultCodeContent = `def process_user_registration(user_data):\n    if not user_data or "email" not in user_data:\n        raise ValueError("Invalid user payload")\n    return {"status": "created", "id": 101, "email": user_data["email"]}`,
}) => {
  const [targetFile, setTargetFile] = useState(defaultTargetFile)
  const [codeContent, setCodeContent] = useState(defaultCodeContent)
  const [docType, setDocType] = useState<
    'docstring' | 'javadoc' | 'readme' | 'api_doc' | 'missing_comments' | 'function_description' | 'usage_examples'
  >('docstring')
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(false)

  const [result, setResult] = useState<{
    doc_id: string
    doc_type: string
    doc_title: string
    target_file: string
    content: string
    download_url: string
  } | null>(null)

  const handleGenerate = async () => {
    if (!codeContent.trim()) return
    setGenerating(true)
    try {
      const data = await docGeneratorApi.generateDocs({
        target_file: targetFile || 'source_code.py',
        code_content: codeContent,
        doc_type: docType,
      })
      setResult(data)
    } catch {
      alert('Failed to generate documentation.')
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = () => {
    if (!result) return
    navigator.clipboard.writeText(result.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    if (!result) return
    const blob = new Blob([result.content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    let ext = '.md'
    if (result.doc_type === 'javadoc') ext = '.java'
    else if (result.doc_type === 'docstring') ext = '.py'
    a.download = `DOC_${result.doc_type.toUpperCase()}_${result.target_file}${ext}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-400">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">AI Documentation Generator</h3>
            <p className="text-xs text-slate-400">Generate Docstrings, JavaDocs, READMEs, API Docs & Examples ({repositoryFullName})</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold rounded-full self-start sm:self-auto flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Auto-Doc Engine</span>
        </span>
      </div>

      {/* Mode Selection Chips */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-400 block">Select Documentation Mode:</label>
        <div className="flex flex-wrap gap-2">
          {[
            { id: 'docstring', label: 'Docstrings (Python)' },
            { id: 'javadoc', label: 'JavaDocs (Java)' },
            { id: 'readme', label: 'README Updates' },
            { id: 'api_doc', label: 'API Documentation' },
            { id: 'missing_comments', label: 'Missing Comments' },
            { id: 'function_description', label: 'Function Specs' },
            { id: 'usage_examples', label: 'Executable Examples' },
          ].map((mode) => (
            <button
              key={mode.id}
              onClick={() => setDocType(mode.id as any)}
              className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                docType === mode.id
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      {/* Target File & Code Input */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400">Target File & Code Payload:</label>
          <input
            type="text"
            value={targetFile}
            onChange={(e) => setTargetFile(e.target.value)}
            placeholder="e.g. user_service.py or UserService.java"
            className="px-3 py-1 bg-slate-900/80 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
        <textarea
          rows={5}
          value={codeContent}
          onChange={(e) => setCodeContent(e.target.value)}
          placeholder="Paste function, class, or API code here to generate comprehensive technical documentation..."
          className="w-full p-3.5 bg-[#0a0e17] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
        />
      </div>

      {/* Action Button */}
      <button
        onClick={handleGenerate}
        disabled={generating || !codeContent.trim()}
        className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-cyan-600/20 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
      >
        <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
        <span>{generating ? 'Generating Documentation...' : `Generate ${docType.toUpperCase().replace('_', ' ')}`}</span>
      </button>

      {/* Generated Documentation View */}
      {result && (
        <div className="space-y-4 pt-4 border-t border-slate-800/80">
          {/* Result Header & Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-bold text-slate-200">{result.doc_title}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopy}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg flex items-center space-x-1.5 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy'}</span>
              </button>
              <button
                onClick={handleDownload}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg flex items-center space-x-1.5 shadow-lg shadow-emerald-600/20 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Doc File</span>
              </button>
            </div>
          </div>

          {/* Generated Markdown / Code Display */}
          <div className="p-4 bg-[#070a12] border border-slate-800 rounded-xl font-mono text-xs text-cyan-200/90 overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
            {result.content}
          </div>
        </div>
      )}
    </div>
  )
}
