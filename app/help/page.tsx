'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Key, Brain, Zap, FileText, AlertCircle, CheckCircle, Globe, Download, ChevronDown, ChevronUp } from 'lucide-react';

export default function HelpPage() {
  const [showAISection, setShowAISection] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Link 
              href="/" 
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Generator
            </Link>
            <div className="w-px h-6 bg-gray-300 mx-2" />
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Help & Setup Guide</h1>
                <p className="text-sm text-gray-600">How to Generate llms.txt Files</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* How to Generate */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Globe className="w-6 h-6 text-green-600" />
            <h2 className="text-xl font-semibold text-gray-900">How to Generate llms.txt Files</h2>
          </div>

          <div className="space-y-6">
            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">Step 1: Enter Website URL</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">Enter the full URL of the website you want to generate llms.txt for:</p>
                <div className="bg-white border border-gray-300 rounded px-3 py-2 text-sm text-gray-500">
                  https://your-website.com
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">Step 2: Choose Generation Type</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">📄 Summary (llms.txt)</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Curated selection of key pages</li>
                    <li>• AI-enhanced descriptions</li>
                    <li>• Organized by sections</li>
                    <li>• Best for most use cases</li>
                  </ul>
                </div>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-medium text-purple-900 mb-2">📚 Full (llms-full.txt)</h4>
                  <ul className="text-sm text-purple-700 space-y-1">
                    <li>• Complete sitemap coverage</li>
                    <li>• All discovered pages</li>
                    <li>• Comprehensive documentation</li>
                    <li>• For large documentation sites</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">Step 3: Download Files</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-3">After generation completes:</p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <Download className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Click <strong>"Download llms.txt"</strong> to save the file</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Upload to your website root: <code className="bg-gray-200 px-1 rounded">https://your-site.com/llms.txt</code></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Verify it's accessible by visiting the URL</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Automation Info */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-4">
            <Zap className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-semibold text-gray-900">Automated Generation</h2>
          </div>

          <div className="space-y-4">
            <p className="text-gray-600">
              For automated bi-weekly generation, this self-hosted version includes cron scripts:
            </p>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">See the repository documentation for:</p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>scripts/generate-llms.sh</strong> - Automated generation</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>scripts/deploy-llms.sh</strong> - Automated deployment</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>scripts/setup-cron.sh</strong> - Bi-weekly cron setup</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>config/websites.conf</strong> - Multi-website configuration</span>
                </li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Zap className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900">Self-Hosted Automation</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    Configure multiple websites in <code className="bg-blue-100 px-1 rounded">config/websites.conf</code> and run <code className="bg-blue-100 px-1 rounded">./scripts/setup-cron.sh</code> to enable automated bi-weekly generation and deployment.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Enhancement Section (Collapsible) */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <button
            onClick={() => setShowAISection(!showAISection)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">AI-Enhanced Features (Optional)</h2>
            </div>
            {showAISection ? (
              <ChevronUp className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            )}
          </button>

          {showAISection && (
            <div className="mt-6 space-y-6">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-amber-900">Experimental Feature</h3>
                    <p className="text-sm text-amber-700 mt-1">
                      AI enhancement is not fully implemented yet. The tool works perfectly without it.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900">What AI Could Do (Future):</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span><strong>Content Cleanup:</strong> Improves readability and structure</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span><strong>Smart Descriptions:</strong> Generates intelligent summaries</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span><strong>Section Organization:</strong> Auto-categorizes content</span>
                    </li>
                  </ul>
                </div>
                
                <div className="space-y-4">
                  <h3 className="font-medium text-gray-900">Current Implementation:</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Full sitemap-based extraction</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>FAQ detection from Schema.org</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Heuristic-based categorization</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>Fully functional without API key</span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* API Key Setup */}
              <div className="border-t pt-6">
                <div className="flex items-center gap-3 mb-4">
                  <Key className="w-6 h-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">OpenAI API Key Setup (Optional)</h3>
                </div>

                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Zap className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900">Not Required</h4>
                        <p className="text-sm text-blue-700 mt-1">
                          The tool works perfectly without an API key. This is for future AI features only.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">For Local Development:</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-3">1. Get your OpenAI API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">platform.openai.com</a></p>
                      <p className="text-sm text-gray-600 mb-3">2. Create a <code className="bg-gray-200 px-1 rounded">.env</code> file:</p>
                      <pre className="bg-gray-800 text-gray-100 p-3 rounded text-sm overflow-x-auto">
{`# .env file
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key_here`}
                      </pre>
                      <p className="text-sm text-gray-600 mt-3">3. Restart the development server</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900">For Production (Self-Hosted):</h4>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600 mb-3">Set environment variable on your server:</p>
                      <div className="bg-gray-800 text-gray-100 p-3 rounded text-sm">
                        <div><code>export OPENAI_API_KEY=your_openai_api_key_here</code></div>
                      </div>
                      <p className="text-sm text-gray-600 mt-3">Or add to your systemd service file or Docker environment</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="flex gap-4 mt-8">
          <Link 
            href="/"
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center font-medium"
          >
            Start Generating
          </Link>
        </div>
      </div>
    </div>
  );
}
