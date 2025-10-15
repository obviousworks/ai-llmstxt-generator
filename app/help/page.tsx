'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Key, Brain, Zap, FileText, Monitor, AlertCircle, CheckCircle } from 'lucide-react';

export default function HelpPage() {
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
                <p className="text-sm text-gray-600">AI Support & Configuration</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* AI Support Overview */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">AI-Enhanced Features</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">What AI Does:</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>Content Cleanup:</strong> Improves readability and structure of extracted content</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>Smart Descriptions:</strong> Generates intelligent page descriptions</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>Section Organization:</strong> Automatically categorizes content into logical sections</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span><strong>Summary Generation:</strong> Creates comprehensive website summaries</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">Without AI:</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                  <span>Basic content extraction only</span>
                </li>
                <li className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                  <span>Simple heuristic-based categorization</span>
                </li>
                <li className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                  <span>No content cleanup or enhancement</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Still fully functional for basic use</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* API Key Setup */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Key className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-semibold text-gray-900">OpenAI API Key Setup</h2>
          </div>

          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Zap className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900">AI Enhancement Optional</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    The tool works perfectly without an API key. AI features enhance quality but are not required.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">For Local Development:</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-3">1. Get your OpenAI API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">platform.openai.com</a></p>
                <p className="text-sm text-gray-600 mb-3">2. Create a <code className="bg-gray-200 px-1 rounded">.env</code> file in the project root:</p>
                <pre className="bg-gray-800 text-gray-100 p-3 rounded text-sm overflow-x-auto">
{`# .env file
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_api_key_here`}
                </pre>
                <p className="text-sm text-gray-600 mt-3">3. Restart the development server</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">For Production (Self-Hosted):</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-3">1. Set environment variable on your server:</p>
                <div className="bg-gray-800 text-gray-100 p-3 rounded text-sm">
                  <div><code>export OPENAI_API_KEY=your_openai_api_key_here</code></div>
                </div>
                <p className="text-sm text-gray-600 mt-3">2. Or add to your systemd service file or Docker environment</p>
                <p className="text-sm text-gray-600 mt-3">3. Restart your application services</p>
              </div>
            </div>
          </div>
        </div>

        {/* Monitor Page Info */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-4">
            <Monitor className="w-6 h-6 text-green-600" />
            <h2 className="text-xl font-semibold text-gray-900">Automated Monitoring</h2>
          </div>

          <div className="space-y-4">
            <p className="text-gray-600">
              The <Link href="/monitor" className="text-blue-600 hover:underline font-medium">Monitor page</Link> allows you to:
            </p>
            
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span><strong>Add websites</strong> for automatic monitoring</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span><strong>Set check intervals</strong> (hourly to weekly)</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span><strong>Configure page limits</strong> for large sites</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span><strong>View update history</strong> and change detection</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span><strong>Force manual updates</strong> when needed</span>
              </li>
            </ul>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-amber-900">Production Note</h3>
                  <p className="text-sm text-amber-700 mt-1">
                    Automated monitoring requires cron jobs on your server. 
                    Use the provided scripts in the repository for bi-weekly automated generation.
                    Local development uses manual monitoring only.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-4 mt-8">
          <Link 
            href="/"
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center font-medium"
          >
            Start Generating
          </Link>
          <Link 
            href="/monitor"
            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors text-center font-medium"
          >
            Setup Monitoring
          </Link>
        </div>
      </div>
    </div>
  );
}
