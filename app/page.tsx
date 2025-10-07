'use client'

import { useState } from 'react'
import { Download, Globe, FileText, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import Link from 'next/link'

interface ValidationError {
  type?: string
  loc?: string[]
  msg?: string
  input?: string
  ctx?: Record<string, unknown>
  url?: string
}

interface ErrorResponse {
  detail?: ValidationError[] | string
  error?: string
}

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
  ai_enhanced: boolean
  ai_model: string | null
  used_existing?: boolean
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

// Helper function to normalize URLs
const normalizeUrl = (inputUrl: string): string => {
  const trimmed = inputUrl.trim()
  
  // If it already has a protocol, return as-is
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed
  }
  
  // Add https:// prefix for URLs without protocol
  return `https://${trimmed}`
}

export default function Home() {
  const [url, setUrl] = useState('')
  const [maxPages, setMaxPages] = useState(20)
  const [crawlAll, setCrawlAll] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingFulltext, setIsLoadingFulltext] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [fulltextResult, setFulltextResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState('')
  const [fulltextError, setFulltextError] = useState('')

  const generateLLMSText = async (fulltext: boolean = false) => {
    if (!url) return

    if (fulltext) {
      setIsLoadingFulltext(true)
      setFulltextError('')
      setFulltextResult(null)
    } else {
      setIsLoading(true)
      setError('')
      setResult(null)
    }

    try {
      // Normalize the URL to ensure it has a protocol
      const normalizedUrl = normalizeUrl(url)
      
      // Use different endpoints for development vs production
      const endpoint = API_URL === 'http://localhost:8000' ? '/generate' : '/api/generate'
      const fullUrl = `${API_URL}${endpoint}`
      
      console.log('API_URL:', API_URL)
      console.log('Full URL:', fullUrl)
      console.log('Original URL:', url)
      console.log('Normalized URL:', normalizedUrl)
      console.log('Current location:', window.location.href)
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: normalizedUrl,
          max_pages: fulltext ? 999999 : maxPages,
          depth_limit: fulltext ? 999 : 3,
          crawl_all: fulltext || crawlAll,
          generation_type: fulltext ? 'fulltext' : 'summary'
        }),
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      const responseText = await response.text()
      console.log('Raw response:', responseText.substring(0, 200))

      if (!response.ok) {
        let errorData: ErrorResponse
        try {
          errorData = JSON.parse(responseText)
        } catch {
          throw new Error(`Server returned ${response.status}: ${responseText.substring(0, 100)}`)
        }
        
        // Extract more helpful error message from Pydantic validation errors
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const urlError = errorData.detail.find((err: ValidationError) => err.loc?.includes('url'))
          if (urlError) {
            throw new Error(`Invalid URL format: ${urlError.msg}. Please enter a valid URL like https://example.com`)
          }
        }
        
        const errorMessage = typeof errorData.detail === 'string' 
          ? errorData.detail 
          : errorData.error || 'Failed to generate llms.txt'
        throw new Error(errorMessage)
      }

      const data: GenerationResult = JSON.parse(responseText)
      if (fulltext) {
        setFulltextResult(data)
      } else {
        setResult(data)
      }
    } catch (err) {
      console.error('Full error:', err)
      const errorMsg = err instanceof Error ? err.message : 'An error occurred'
      if (fulltext) {
        setFulltextError(errorMsg)
      } else {
        setError(errorMsg)
      }
    } finally {
      if (fulltext) {
        setIsLoadingFulltext(false)
      } else {
        setIsLoading(false)
      }
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
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">LLMs.txt Generator</h1>
                <p className="text-sm text-gray-600">Automated llms.txt file generation for websites</p>
              </div>
            </div>
            <nav>
              <Link 
                href="/monitor"
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors duration-200 text-sm font-medium"
              >
                🔄 Auto-Monitor Sites
              </Link>
            </nav>
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
                      placeholder="Enter website URL (e.g., docs.anthropic.com or https://docs.anthropic.com)"
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-700 placeholder:text-gray-700 text-gray-900"
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="maxPages" className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Pages to Crawl (for Summary)
                  </label>
                  <select
                    id="maxPages"
                    value={maxPages}
                    onChange={(e) => setMaxPages(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading || isLoadingFulltext}
                  >
                    <option value={10}>10 pages</option>
                    <option value={20}>20 pages (recommended)</option>
                    <option value={50}>50 pages</option>
                    <option value={100}>100 pages</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="crawlAll"
                    checked={crawlAll}
                    onChange={(e) => setCrawlAll(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    disabled={isLoading || isLoadingFulltext}
                  />
                  <label htmlFor="crawlAll" className="ml-2 text-sm text-gray-700">
                    Crawl all pages (ignores page limit for summary)
                  </label>
                </div>

                <div className="space-y-3">
                  <button
                    onClick={() => generateLLMSText(false)}
                    disabled={!url || isLoading || isLoadingFulltext}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Generating Summary...
                      </>
                    ) : (
                      <>
                        <FileText className="w-5 h-5" />
                        Generate llms.txt (Summary)
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => generateLLMSText(true)}
                    disabled={!url || isLoading || isLoadingFulltext}
                    className="w-full bg-gradient-to-r from-green-600 to-teal-600 text-white py-3 px-6 rounded-lg font-medium hover:from-green-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {isLoadingFulltext ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Crawling All Pages...
                      </>
                    ) : (
                      <>
                        <FileText className="w-5 h-5" />
                        Generate llms-full.txt (All Pages)
                      </>
                    )}
                  </button>
                </div>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-red-800">Error (Summary)</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              )}

              {fulltextError && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-red-800">Error (Fulltext)</h3>
                    <p className="text-sm text-red-700 mt-1">{fulltextError}</p>
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
            {(result || fulltextResult) && (
              <>
                {/* Generation Success - Summary */}
                {result && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-sm font-medium text-blue-800">
                        Summary Generation Complete
                      </h3>
                      <p className="text-sm text-blue-700 mt-1">
                        Analyzed {result.pages_analyzed.length} pages in {result.generation_time.toFixed(2)} seconds
                        {result.ai_enhanced && (
                          <span className="block">Enhanced with AI ({result.ai_model})</span>
                        )}
                      </p>
                    </div>
                  </div>
                )}

                {/* Generation Success - Fulltext */}
                {fulltextResult && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-sm font-medium text-green-800">
                        Fulltext Generation Complete
                      </h3>
                      <p className="text-sm text-green-700 mt-1">
                        Crawled ALL {fulltextResult.pages_analyzed.length} pages in {fulltextResult.generation_time.toFixed(2)} seconds
                        {fulltextResult.ai_enhanced && (
                          <span className="block">Enhanced with AI ({fulltextResult.ai_model})</span>
                        )}
                      </p>
                    </div>
                  </div>
                )}

                {/* Download Buttons */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Download Files</h3>
                  <div className="space-y-3">
                    {result && (
                      <button
                        onClick={() => downloadFile(result.llms_txt, 'llms.txt')}
                        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                      >
                        <Download className="w-5 h-5" />
                        Download llms.txt (Summary)
                      </button>
                    )}
                    {fulltextResult && (
                      <button
                        onClick={() => downloadFile(fulltextResult.llms_full_txt, 'llms-full.txt')}
                        className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                      >
                        <Download className="w-5 h-5" />
                        Download llms-full.txt (All Pages)
                      </button>
                    )}
                  </div>
                </div>

                {/* Pages Analyzed */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Pages Analyzed {fulltextResult ? '(Fulltext - All Pages)' : '(Summary)'}
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {(fulltextResult || result)?.pages_analyzed.map((page, index) => (
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
                {result && (
                  <div className="bg-white rounded-xl shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">llms.txt Preview (Summary)</h3>
                    <div className="bg-gray-50 rounded-lg p-4 text-sm font-mono max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-gray-800">{result.llms_txt}</pre>
                    </div>
                  </div>
                )}

                {fulltextResult && (
                  <div className="bg-white rounded-xl shadow-sm border p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">llms-full.txt Preview (All Pages)</h3>
                    <div className="bg-gray-50 rounded-lg p-4 text-sm font-mono max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-gray-800">{fulltextResult.llms_full_txt}</pre>
                    </div>
                  </div>
                )}
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
