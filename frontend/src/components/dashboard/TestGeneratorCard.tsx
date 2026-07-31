import React, { useState } from 'react'
import { TestTube2, Download, Copy, Check, FileCode, Play, Sparkles, BookOpen, Layers, ShieldAlert, CheckCircle2 } from 'lucide-react'
import { testGeneratorApi } from '../../services/api'

export interface TestGeneratorCardProps {
  repositoryFullName?: string
  defaultTargetFile?: string
  defaultCodeContent?: string
}

export const TestGeneratorCard: React.FC<TestGeneratorCardProps> = ({
  repositoryFullName = 'Repository Code',
  defaultTargetFile = 'user_service.py',
  defaultCodeContent = `def process_user_registration(user_data):\n    if not user_data or "email" not in user_data:\n        raise ValueError("Invalid user payload")\n    return {"status": "created", "id": 101, "email": user_data["email"]}`,
}) => {
  const [targetFile, setTargetFile] = useState(defaultTargetFile)
  const [codeContent, setCodeContent] = useState(defaultCodeContent)
  const [testFramework, setTestFramework] = useState<'pytest' | 'junit' | 'jest'>('pytest')
  const [testCategory, setTestCategory] = useState<'comprehensive' | 'positive' | 'negative' | 'boundary' | 'mock'>('comprehensive')
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(false)

  const [result, setResult] = useState<{
    test_id: string
    test_name: string
    generated_code: string
    workflow_explanation: string
    download_url: string
  } | null>(null)

  const handleGenerate = async () => {
    if (!codeContent.trim()) return
    setGenerating(true)
    try {
      const data = await testGeneratorApi.generateTests({
        target_file: targetFile || 'source_code.py',
        code_content: codeContent,
        test_framework: testFramework,
        test_category: testCategory,
      })
      setResult(data)
    } catch {
      alert('Failed to generate test suite.')
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = () => {
    if (!result) return
    navigator.clipboard.writeText(result.generated_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    if (!result) return
    const blob = new Blob([result.generated_code], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = result.test_name || 'generated_test.py'
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
          <div className="p-2.5 bg-violet-500/10 border border-violet-500/20 rounded-xl text-violet-400">
            <TestTube2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">AI Test Generator</h3>
            <p className="text-xs text-slate-400">Auto-generate unit & integration test suites ({repositoryFullName})</p>
          </div>
        </div>
        <span className="px-3 py-1 bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-semibold rounded-full self-start sm:self-auto flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>JUnit • pytest • Jest</span>
        </span>
      </div>

      {/* Options Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Framework Selection */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-400 block">Select Test Framework:</label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: 'pytest', label: 'pytest (Python)' },
              { id: 'junit', label: 'JUnit 5 (Java)' },
              { id: 'jest', label: 'Jest (JS/TS)' },
            ].map((fw) => (
              <button
                key={fw.id}
                onClick={() => setTestFramework(fw.id as any)}
                className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                  testFramework === fw.id
                    ? 'bg-violet-500/20 border-violet-500 text-violet-300 shadow-lg shadow-violet-500/10'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                {fw.label}
              </button>
            ))}
          </div>
        </div>

        {/* Category Selection */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-400 block">Select Test Category:</label>
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'comprehensive', label: 'All (Comprehensive)' },
              { id: 'positive', label: 'Positive Tests' },
              { id: 'negative', label: 'Negative Tests' },
              { id: 'boundary', label: 'Boundary Tests' },
              { id: 'mock', label: 'Mock Tests' },
            ].map((cat) => (
              <button
                key={cat.id}
                onClick={() => setTestCategory(cat.id as any)}
                className={`py-1.5 px-3 text-xs font-medium rounded-lg border transition-all ${
                  testCategory === cat.id
                    ? 'bg-brand-500/20 border-brand-500 text-brand-300'
                    : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Target File Input & Code Payload */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400">Target Source Code File & Content:</label>
          <input
            type="text"
            value={targetFile}
            onChange={(e) => setTargetFile(e.target.value)}
            placeholder="e.g. UserService.java or test_api.py"
            className="px-3 py-1 bg-slate-900/80 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
        </div>
        <textarea
          rows={5}
          value={codeContent}
          onChange={(e) => setCodeContent(e.target.value)}
          placeholder="Paste function or class source code here to generate targeted test suites..."
          className="w-full p-3.5 bg-[#0a0e17] border border-slate-800 rounded-xl text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500"
        />
      </div>

      {/* Generate Action Button */}
      <button
        onClick={handleGenerate}
        disabled={generating || !codeContent.trim()}
        className="w-full py-3 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-violet-600/20 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
      >
        <Sparkles className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
        <span>{generating ? 'Generating Test Suite...' : `Generate ${testFramework.toUpperCase()} Test Suite`}</span>
      </button>

      {/* Generated Result & Workflow Explanation */}
      {result && (
        <div className="space-y-5 pt-4 border-t border-slate-800/80">
          {/* Action Bar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileCode className="w-4 h-4 text-violet-400" />
              <span className="text-sm font-mono font-bold text-slate-200">{result.test_name}</span>
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
                <span>Download Test File</span>
              </button>
            </div>
          </div>

          {/* Generated Code Display */}
          <div className="p-4 bg-[#070a12] border border-slate-800 rounded-xl font-mono text-xs text-violet-200/90 overflow-x-auto max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap">{result.generated_code}</pre>
          </div>

          {/* Workflow Explanation */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center space-x-2 text-violet-400">
              <BookOpen className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Workflow & Test Strategy Explanation</h4>
            </div>
            <div className="text-xs text-slate-300 font-mono whitespace-pre-wrap leading-relaxed">
              {result.workflow_explanation}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
