import { useState } from 'react'
import axios from 'axios'
import { ShieldAlert, ShieldCheck, Shield, UploadCloud, AlertTriangle } from 'lucide-react'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError('')
      setResult(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('mask', true)
    formData.append('log_analysis', true)

    try {
      const res = await axios.post('https://ai-secure-data.onrender.com/analyze/upload', formData)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred during analysis.")
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'text-red-500'
      case 'high': return 'text-orange-500'
      case 'medium': return 'text-yellow-400'
      case 'low': return 'text-blue-400'
      default: return 'text-green-500'
    }
  }

  const getRiskIcon = (level) => {
    if (level === 'critical' || level === 'high') return <ShieldAlert className="w-8 h-8 text-red-500" />
    if (level === 'medium' || level === 'low') return <AlertTriangle className="w-8 h-8 text-yellow-400" />
    return <ShieldCheck className="w-8 h-8 text-green-500" />
  }

  return (
    <div className="min-h-screen p-8 font-sans">
      <header className="mb-8 flex items-center gap-3 border-b border-slate-700 pb-4">
        <Shield className="w-10 h-10 text-indigo-500" />
        <h1 className="text-3xl font-bold tracking-tight">AI Secure Data Intelligence Platform</h1>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left Column: Upload */}
        <div className="col-span-1 bg-slate-800 p-6 rounded-xl border border-slate-700 h-fit">
          <h2 className="text-xl font-semibold mb-4 text-indigo-400">Scan Data File</h2>

          <label className="border-2 border-dashed border-slate-600 rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-indigo-500 transition-colors bg-slate-800/50">
            <UploadCloud className="w-12 h-12 text-slate-400 mb-3" />
            <span className="text-sm text-slate-300">Click to upload .log, .txt, .pdf, or .docx</span>
            <input type="file" className="hidden" onChange={handleFileChange} accept=".log,.txt,.pdf,.docx,.doc" />
          </label>

          {file && (
            <div className="mt-4 p-3 bg-slate-700 rounded text-sm break-all">
              Selected: <span className="font-mono text-indigo-300">{file.name}</span>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
          >
            {loading ? 'Analyzing...' : 'Run Security Analysis'}
          </button>

          {error && <div className="mt-4 text-red-400 text-sm bg-red-900/20 p-3 rounded">{error}</div>}
        </div>

        {/* Right Column: Results */}
        <div className="col-span-1 lg:col-span-2 space-y-6">

          {!result && !loading && (
            <div className="h-full flex items-center justify-center text-slate-500 border border-dashed border-slate-700 rounded-xl min-h-[300px]">
              Upload a file to see analysis results here
            </div>
          )}

          {result && (
            <>
              {/* Summary Banner */}
              <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex items-center gap-6">
                {getRiskIcon(result.risk_level)}
                <div>
                  <h2 className={`text-2xl font-bold uppercase tracking-wider ${getRiskColor(result.risk_level)}`}>
                    RISK LEVEL: {result.risk_level}
                  </h2>
                  <p className="text-slate-300 mt-1">{result.summary}</p>
                  <p className="text-sm text-slate-400 mt-2">
                    Score: <strong className="text-white">{result.risk_score}</strong> | Action taken: <strong className="text-white uppercase">{result.action}</strong>
                  </p>
                </div>
              </div>

              {/* Insights & Findings Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* AI Insights */}
                <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                  <h3 className="text-lg font-semibold text-indigo-400 mb-4 border-b border-slate-700 pb-2">AI Insights</h3>
                  <ul className="space-y-3 list-none max-w-full">
                    {result.insights.map((insight, i) => (
                      <li key={i} className="flex gap-2 text-sm text-slate-300">
                        <span className="text-indigo-500 shrink-0">•</span> <span>{insight}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Raw Findings */}
                <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 max-h-[300px] overflow-y-auto">
                  <h3 className="text-lg font-semibold text-indigo-400 mb-4 border-b border-slate-700 pb-2">Detected Secrets</h3>
                  {result.findings.length === 0 ? (
                    <span className="text-sm text-slate-500">None detected.</span>
                  ) : (
                    <ul className="space-y-3">
                      {result.findings.map((f, i) => (
                        <li key={i} className="text-sm bg-slate-900 p-3 rounded border border-slate-700">
                          <div className="flex justify-between mb-1">
                            <span className="font-mono text-indigo-300">{f.type}</span>
                            <span className={`uppercase text-xs font-bold ${getRiskColor(f.risk)}`}>{f.risk}</span>
                          </div>
                          {f.line && <div className="text-slate-500 text-xs mt-1">Found on line: {f.line}</div>}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              {/* Masked Content Viewer */}
              {result.masked_content && (
                <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
                  <h3 className="text-lg font-semibold text-emerald-400 mb-4 border-b border-slate-700 pb-2">Secured (Masked) Output</h3>
                  <pre className="text-xs font-mono bg-slate-900 p-4 rounded overflow-x-auto text-slate-300 border border-slate-700 whitespace-pre-wrap">
                    {result.masked_content}
                  </pre>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
