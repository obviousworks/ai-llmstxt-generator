'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface MonitoredSite {
  url: string;
  last_check: string;
  last_update: string;
  check_interval_hours: number;
  max_pages: number;
}

interface UpdateResult {
  url: string;
  status: string;
  updated: boolean;
  changes?: {
    severity: string;
    new_pages: string[];
    removed_pages: string[];
    modified_pages: any[];
  };
  update_reason?: string;
  message?: string;
}

export default function MonitorPage() {
  const [monitoredSites, setMonitoredSites] = useState<MonitoredSite[]>([]);
  const [newSiteUrl, setNewSiteUrl] = useState('');
  const [checkInterval, setCheckInterval] = useState(24);
  const [maxPages, setMaxPages] = useState(20);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [checkingUpdates, setCheckingUpdates] = useState(false);
  const [updateResults, setUpdateResults] = useState<UpdateResult[]>([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

  // Determine scheduler URL based on environment
  const getSchedulerUrl = () => {
    if (API_URL === 'http://localhost:8000') {
      return 'http://localhost:8001'; // Local scheduler service
    }
    return API_URL; // Production - same origin with /api/scheduler
  };

  const SCHEDULER_URL = getSchedulerUrl();

  useEffect(() => {
    loadMonitoredSites();
  }, []);

  const loadMonitoredSites = async () => {
    try {
      const endpoint = API_URL === 'http://localhost:8000' ? '/scheduler' : '/api/scheduler';
      const response = await fetch(`${SCHEDULER_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'list_sites' })
      });
      const data = await response.json();
      if (data.monitored_sites) {
        setMonitoredSites(data.monitored_sites);
      }
    } catch (error) {
      console.error('Error loading monitored sites:', error);
    }
  };

  const addSiteToMonitoring = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSiteUrl.trim()) return;

    setLoading(true);
    setMessage('');

    try {
      const endpoint = API_URL === 'http://localhost:8000' ? '/scheduler' : '/api/scheduler';
      const response = await fetch(`${SCHEDULER_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_site',
          url: newSiteUrl,
          max_pages: maxPages,
          check_interval: checkInterval * 3600 // Convert hours to seconds
        })
      });

      const data = await response.json();
      
      if (data.error) {
        setMessage(`Error: ${data.error}`);
      } else {
        setMessage(`✅ Site added to monitoring! Will check every ${checkInterval} hours.`);
        setNewSiteUrl('');
        loadMonitoredSites();
      }
    } catch (error) {
      setMessage(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const checkForUpdates = async (specificUrl?: string) => {
    setCheckingUpdates(true);
    setUpdateResults([]);

    try {
      const endpoint = API_URL === 'http://localhost:8000' ? '/scheduler' : '/api/scheduler';
      const response = await fetch(`${SCHEDULER_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'check_updates',
          url: specificUrl
        })
      });

      const data = await response.json();
      
      if (specificUrl) {
        setUpdateResults([data]);
      } else if (data.checked_sites) {
        setUpdateResults(data.checked_sites);
      }
      
      loadMonitoredSites();
    } catch (error) {
      console.error('Error checking for updates:', error);
    } finally {
      setCheckingUpdates(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Never';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'major': return 'text-red-600';
      case 'moderate': return 'text-orange-600';
      case 'minor': return 'text-yellow-600';
      case 'minimal': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Generator
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Automated LLMs.txt Monitoring</h1>
          <p className="mt-2 text-gray-600">
            Add websites to automated monitoring. The system will check for structure changes and regenerate llms.txt files when needed.
          </p>
        </div>

        {/* Add New Site Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Site to Monitoring</h2>
          
          <form onSubmit={addSiteToMonitoring} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                Website URL
              </label>
              <input
                type="url"
                id="url"
                value={newSiteUrl}
                onChange={(e) => setNewSiteUrl(e.target.value)}
                placeholder="https://docs.example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="interval" className="block text-sm font-medium text-gray-700 mb-1">
                  Check Interval (hours)
                </label>
                <select
                  id="interval"
                  value={checkInterval}
                  onChange={(e) => setCheckInterval(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                >
                  <option value={1}>Every hour</option>
                  <option value={6}>Every 6 hours</option>
                  <option value={12}>Every 12 hours</option>
                  <option value={24}>Daily (recommended)</option>
                  <option value={72}>Every 3 days</option>
                  <option value={168}>Weekly</option>
                </select>
              </div>

              <div>
                <label htmlFor="pages" className="block text-sm font-medium text-gray-700 mb-1">
                  Max Pages to Crawl
                </label>
                <select
                  id="pages"
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                >
                  <option value={10}>10 pages</option>
                  <option value={20}>20 pages (recommended)</option>
                  <option value={50}>50 pages</option>
                  <option value={100}>100 pages</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add to Monitoring'}
            </button>
          </form>

          {message && (
            <div className={`mt-4 p-3 rounded-md ${message.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
              {message}
            </div>
          )}
        </div>

        {/* Monitored Sites */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Monitored Sites ({monitoredSites.length})</h2>
            <button
              onClick={() => checkForUpdates()}
              disabled={checkingUpdates}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              {checkingUpdates ? 'Checking...' : 'Check All for Updates'}
            </button>
          </div>

          {monitoredSites.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No sites are currently being monitored.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Site</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Check Interval</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Check</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Update</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {monitoredSites.map((site) => (
                    <tr key={site.url}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{site.url}</div>
                        <div className="text-sm text-gray-500">Max {site.max_pages} pages</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Every {site.check_interval_hours}h
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(site.last_check)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(site.last_update)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => checkForUpdates(site.url)}
                          disabled={checkingUpdates}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          Check Now
                        </button>
                        <button
                          onClick={() => window.open(`${API_URL}/api/scheduler`, '_blank')}
                          className="text-green-600 hover:text-green-900"
                        >
                          View LLMs.txt
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Update Results */}
        {updateResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Latest Update Results</h2>
            
            <div className="space-y-4">
              {updateResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{result.url}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      result.status === 'checked' ? 'bg-green-100 text-green-800' :
                      result.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {result.status}
                    </span>
                  </div>

                  {result.updated && (
                    <div className="mb-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ✨ Updated
                      </span>
                      {result.update_reason && (
                        <p className="text-sm text-gray-600 mt-1">{result.update_reason}</p>
                      )}
                    </div>
                  )}

                  {result.changes && (
                    <div className="text-sm text-gray-600">
                      <span className={`font-medium ${getSeverityColor(result.changes.severity)}`}>
                        {result.changes.severity.toUpperCase()} changes:
                      </span>
                      {result.changes.new_pages.length > 0 && (
                        <span className="ml-2">+{result.changes.new_pages.length} new pages</span>
                      )}
                      {result.changes.removed_pages.length > 0 && (
                        <span className="ml-2">-{result.changes.removed_pages.length} removed pages</span>
                      )}
                      {result.changes.modified_pages.length > 0 && (
                        <span className="ml-2">~{result.changes.modified_pages.length} modified pages</span>
                      )}
                    </div>
                  )}

                  {result.message && (
                    <p className="text-sm text-gray-600">{result.message}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">How Automated Monitoring Works</h3>
          <ul className="text-blue-800 space-y-1 text-sm">
            <li>• System automatically checks sites every 6 hours (or your custom interval)</li>
            <li>• Detects changes in page structure, titles, and content organization</li>
            <li>• Regenerates llms.txt files when significant changes are detected</li>
            <li>• Change severity: <span className="text-red-600">Major (50%+)</span>, <span className="text-orange-600">Moderate (20%+)</span>, <span className="text-yellow-600">Minor (5%+)</span>, <span className="text-green-600">Minimal (&lt;5%)</span></li>
            <li>• Only updates for Minor+ changes to avoid unnecessary regeneration</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 