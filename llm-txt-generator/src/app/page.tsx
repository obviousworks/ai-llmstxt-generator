'use client'

import { useState } from 'react'
import { Download, Globe, FileText, Loader2, AlertCircle, CheckCircle } from 'lucide-react'

interface PageInfo {
  url: string
  title: string
  description: string
  content_length: number
  importance_score: number
  section: string
}

interface GenerationResult {
  llms_txt: string
  llms_full_txt: string
  pages_analyzed: PageInfo[]
  generation_time: number
}

// Get API URL - use environment variable, or detect if we're in development vs production
const getApiUrl = () => {
  console.log('getApiUrl called')
  console.log('process.env.NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
  console.log('window available:', typeof window !== 'undefined')
  
  if (typeof window !== 'undefined') {
    console.log('window.location.hostname:', window.location.hostname)
    console.log('window.location.port:', window.location.port)
    console.log('window.location.origin:', window.location.origin)
  }
  
  // If explicitly set via environment variable, use that
  if (process.env.NEXT_PUBLIC_API_URL) {
    console.log('Using env variable:', process.env.NEXT_PUBLIC_API_URL)
    return process.env.NEXT_PUBLIC_API_URL
  }
  
  // If running on localhost (any port), use backend on localhost:8000
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    console.log('Detected localhost, using http://localhost:8000')
    return 'http://localhost:8000'
  }
  
  // Otherwise, use same origin (production on Vercel)
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  console.log('Using same origin:', origin)
  return origin
}

const API_URL = getApiUrl()

export default function Home() {
  const [url, setUrl] = useState('')
  const [maxPages, setMaxPages] = useState(20)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState('')

  const generateLLMSText = async () => {
    if (!url) return

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      // Use different endpoints for development vs production
      const endpoint = API_URL === 'http://localhost:8000' ? '/generate' : '/api/generate'
      const fullUrl = `${API_URL}${endpoint}`
      
      console.log('API_URL:', API_URL)
      console.log('Full URL:', fullUrl)
      console.log('Current location:', window.location.href)
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          max_pages: maxPages,
          depth_limit: 3
        }),
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      const responseText = await response.text()
      console.log('Raw response:', responseText.substring(0, 200))

      if (!response.ok) {
        let errorData
        try {
          errorData = JSON.parse(responseText)
        } catch {
          throw new Error(`Server returned ${response.status}: ${responseText.substring(0, 100)}`)
        }
        throw new Error(errorData.error || 'Failed to generate llms.txt')
      }

      const data: GenerationResult = JSON.parse(responseText)
      setResult(data)
    } catch (err) {
      console.error('Full error:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const downloadFile = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">LLMs.txt Generator</h1>
              <p className="text-sm text-gray-600">Automated llms.txt file generation for websites</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate llms.txt</h2>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                    Website URL
                  </label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="url"
                      id="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://example.com"
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="maxPages" className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Pages to Crawl
                  </label>
                  <select
                    id="maxPages"
                    value={maxPages}
                    onChange={(e) => setMaxPages(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading}
                  >
                    <option value={10}>10 pages</option>
                    <option value={20}>20 pages</option>
                    <option value={50}>50 pages</option>
                    <option value={100}>100 pages</option>
                  </select>
                </div>

                <button
                  onClick={generateLLMSText}
                  disabled={!url || isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5" />
                      Generate llms.txt
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* About Section */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">About llms.txt</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <p>
                  The llms.txt standard helps Large Language Models understand your website content by providing:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Structured content navigation</li>
                  <li>Key page descriptions and metadata</li>
                  <li>Curated links to important resources</li>
                  <li>AI-friendly markdown format</li>
                </ul>
                <p>
                  Learn more about the specification at{' '}
                  <a href="https://llmstxt.org" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                    llmstxt.org
                  </a>
                </p>
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {result && (
              <>
                {/* Generation Success */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-green-800">Generation Complete</h3>
                    <p className="text-sm text-green-700 mt-1">
                      Analyzed {result.pages_analyzed.length} pages in {result.generation_time.toFixed(2)} seconds
                    </p>
                  </div>
                </div>

                {/* Download Buttons */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Download Files</h3>
                  <div className="space-y-3">
                    <button
                      onClick={() => downloadFile(result.llms_txt, 'llms.txt')}
                      className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-5 h-5" />
                      Download llms.txt
                    </button>
                    <button
                      onClick={() => downloadFile(result.llms_full_txt, 'llms-full.txt')}
                      className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-5 h-5" />
                      Download llms-full.txt
                    </button>
                  </div>
                </div>

                {/* Pages Analyzed */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Pages Analyzed</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {result.pages_analyzed.map((page, index) => (
                      <div key={index} className="p-3 border border-gray-200 rounded-lg">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-medium text-gray-900 truncate">{page.title}</h4>
                            <p className="text-xs text-gray-500 truncate mt-1">{page.url}</p>
                            {page.description && (
                              <p className="text-xs text-gray-600 mt-1 line-clamp-2">{page.description}</p>
                            )}
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {page.section}
                            </span>
                            <span className="text-xs text-gray-500">
                              Score: {page.importance_score.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Preview */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">llms.txt Preview</h3>
                  <div className="bg-gray-50 rounded-lg p-4 text-sm font-mono max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-gray-800">{result.llms_txt}</pre>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center text-sm text-gray-600">
            <p>Built for the llms.txt standard. Learn more at <a href="https://llmstxt.org" className="text-blue-600 hover:underline">llmstxt.org</a></p>
          </div>
        </div>
      </footer>
    </div>
  )
}
