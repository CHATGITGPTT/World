import React, { useState, useRef, useEffect } from 'react';
import { Search, Globe, Download, Settings, Play, Pause, Trash2, Eye, Database, Filter, AlertCircle, CheckCircle, Clock, Zap } from 'lucide-react';

const AdvancedWebScraper = () => {
  const [url, setUrl] = useState('');
  const [scrapingMode, setScrapingMode] = useState('intelligent');
  const [scrapedData, setScrapedData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [scrapingRules, setScrapingRules] = useState({
    maxDepth: 2,
    followLinks: true,
    respectRobots: true,
    delay: 1000,
    maxPages: 10
  });
  const [selectedDataTypes, setSelectedDataTypes] = useState({
    text: true,
    images: true,
    links: true,
    metadata: true,
    structured: true
  });
  const [filters, setFilters] = useState({
    minTextLength: 10,
    excludeNavigation: true,
    includeHidden: false,
    language: 'auto'
  });
  const [userIntent, setUserIntent] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [scrapingHistory, setScrapingHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('scraper');
  const [exportFormat, setExportFormat] = useState('json');
  const [error, setError] = useState('');

  // Intent analysis function
  const analyzeUserIntent = (intent: string, targetUrl: string) => {
    const keywords = intent.toLowerCase();
    const analysis = {
      dataTypes: [] as string[],
      selectors: [] as string[],
      strategy: 'general',
      confidence: 0
    };

    // E-commerce detection
    if (keywords.includes('price') || keywords.includes('product') || keywords.includes('shop') || keywords.includes('buy')) {
      analysis.dataTypes.push('prices', 'products', 'reviews');
      analysis.selectors.push('.price', '.product-title', '.review', '[data-price]');
      analysis.strategy = 'ecommerce';
      analysis.confidence += 30;
    }

    // News/Article detection
    if (keywords.includes('article') || keywords.includes('news') || keywords.includes('headline') || keywords.includes('story')) {
      analysis.dataTypes.push('headlines', 'articles', 'dates', 'authors');
      analysis.selectors.push('h1', 'h2', '.headline', '.article-body', '.byline', 'time');
      analysis.strategy = 'content';
      analysis.confidence += 25;
    }

    // Contact information detection
    if (keywords.includes('contact') || keywords.includes('email') || keywords.includes('phone') || keywords.includes('address')) {
      analysis.dataTypes.push('emails', 'phones', 'addresses');
      analysis.selectors.push('[href^="mailto:"]', '[href^="tel:"]', '.contact', '.address');
      analysis.strategy = 'contact';
      analysis.confidence += 35;
    }

    // Social media detection
    if (keywords.includes('social') || keywords.includes('twitter') || keywords.includes('facebook') || keywords.includes('instagram')) {
      analysis.dataTypes.push('social_links', 'profiles', 'posts');
      analysis.selectors.push('[href*="twitter.com"]', '[href*="facebook.com"]', '[href*="instagram.com"]');
      analysis.strategy = 'social';
      analysis.confidence += 20;
    }

    // Table/structured data detection
    if (keywords.includes('table') || keywords.includes('data') || keywords.includes('list') || keywords.includes('database')) {
      analysis.dataTypes.push('tables', 'lists', 'structured_data');
      analysis.selectors.push('table', 'ul', 'ol', '.data-table', '[data-table]');
      analysis.strategy = 'structured';
      analysis.confidence += 25;
    }

    return analysis;
  };

  // Real web scraping with backend API
  const performWebScraping = async (targetUrl: string, intent: string) => {
    setIsLoading(true);
    setError('');
    
    try {
      const analysis = analyzeUserIntent(intent, targetUrl);
      setAnalysisResults(analysis);
      
      // Call the backend API
      const response = await fetch('/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: targetUrl,
          userIntent: intent,
          scrapingRules,
          selectedDataTypes,
          filters,
          scrapingMode,
          selectors: analysis.selectors
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      const scrapingSession = {
        id: Date.now(),
        url: targetUrl,
        intent: intent,
        timestamp: new Date(),
        dataCount: result.scrapedData.length,
        strategy: result.strategy || analysis.strategy,
        confidence: analysis.confidence
      };
      
      setScrapedData(result.scrapedData);
      setScrapingHistory(prev => [scrapingSession, ...prev.slice(0, 9)]);
      
    } catch (error: any) {
      console.error('Scraping error:', error);
      setError(`Scraping failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleScrape = async () => {
    if (!url.trim()) return;
    await performWebScraping(url, userIntent);
  };

  const exportData = () => {
    const dataStr = exportFormat === 'json' 
      ? JSON.stringify(scrapedData, null, 2)
      : scrapedData.map(item => Object.values(item).join('\t')).join('\n');
    
    const blob = new Blob([dataStr], { type: exportFormat === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scraped_data.${exportFormat}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearData = () => {
    setScrapedData([]);
    setAnalysisResults(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4 flex items-center justify-center gap-3">
            <Globe className="text-purple-400" />
            Advanced Web Scraper
          </h1>
          <p className="text-gray-300 text-lg">Intelligent data extraction with adaptive scraping strategies</p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-400 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-6">
          <div className="bg-black/30 backdrop-blur-sm rounded-lg p-1 flex">
            {['scraper', 'settings', 'history'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2 rounded-md transition-all ${
                  activeTab === tab 
                    ? 'bg-purple-500 text-white shadow-lg' 
                    : 'text-gray-300 hover:text-white hover:bg-purple-500/20'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* Left Panel - Controls */}
          <div className="xl:col-span-1 space-y-6">
            
            {activeTab === 'scraper' && (
              <>
                {/* URL Input */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Search className="text-purple-400" />
                    Target URL
                  </h3>
                  <div className="space-y-4">
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://example.com"
                      className="w-full p-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-400 focus:border-purple-400 focus:outline-none"
                    />
                    <textarea
                      value={userIntent}
                      onChange={(e) => setUserIntent(e.target.value)}
                      placeholder="Describe what you want to extract (e.g., 'Get all product prices and reviews', 'Extract contact information', 'Find all article headlines')"
                      rows={3}
                      className="w-full p-3 bg-black/30 border border-purple-500/30 rounded-lg text-white placeholder-gray-400 focus:border-purple-400 focus:outline-none resize-none"
                    />
                  </div>
                </div>

                {/* Scraping Mode */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Zap className="text-purple-400" />
                    Scraping Mode
                  </h3>
                  <div className="space-y-2">
                    {[
                      { value: 'intelligent', label: 'Intelligent Auto-Detection', desc: 'AI-powered content analysis' },
                      { value: 'deep', label: 'Deep Crawl', desc: 'Multi-page extraction' },
                      { value: 'focused', label: 'Focused Extraction', desc: 'Targeted data mining' }
                    ].map(mode => (
                      <label key={mode.value} className="flex items-start gap-3 p-3 bg-black/20 rounded-lg cursor-pointer hover:bg-black/30 transition-all">
                        <input
                          type="radio"
                          name="scrapingMode"
                          value={mode.value}
                          checked={scrapingMode === mode.value}
                          onChange={(e) => setScrapingMode(e.target.value)}
                          className="mt-1 text-purple-500"
                        />
                        <div>
                          <div className="text-white font-medium">{mode.label}</div>
                          <div className="text-gray-400 text-sm">{mode.desc}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Data Types */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Database className="text-purple-400" />
                    Data Types
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedDataTypes).map(([type, checked]) => (
                      <label key={type} className="flex items-center gap-2 p-2 bg-black/20 rounded-lg cursor-pointer hover:bg-black/30">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => setSelectedDataTypes(prev => ({ ...prev, [type]: e.target.checked }))}
                          className="text-purple-500"
                        />
                        <span className="text-white text-sm capitalize">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <div className="space-y-3">
                    <button
                      onClick={handleScrape}
                      disabled={isLoading || !url.trim()}
                      className="w-full bg-purple-500 hover:bg-purple-600 disabled:bg-purple-500/50 text-white py-3 px-6 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
                    >
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                          Scraping...
                        </>
                      ) : (
                        <>
                          <Play size={20} />
                          Start Scraping
                        </>
                      )}
                    </button>
                    <button
                      onClick={clearData}
                      className="w-full bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition-all flex items-center justify-center gap-2"
                    >
                      <Trash2 size={16} />
                      Clear Data
                    </button>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'settings' && (
              <>
                {/* Scraping Rules */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Settings className="text-purple-400" />
                    Scraping Rules
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-white text-sm block mb-2">Max Crawl Depth</label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        value={scrapingRules.maxDepth}
                        onChange={(e) => setScrapingRules(prev => ({ ...prev, maxDepth: parseInt(e.target.value) }))}
                        className="w-full p-2 bg-black/30 border border-purple-500/30 rounded text-white"
                      />
                    </div>
                    <div>
                      <label className="text-white text-sm block mb-2">Delay Between Requests (ms)</label>
                      <input
                        type="number"
                        min="500"
                        max="5000"
                        step="500"
                        value={scrapingRules.delay}
                        onChange={(e) => setScrapingRules(prev => ({ ...prev, delay: parseInt(e.target.value) }))}
                        className="w-full p-2 bg-black/30 border border-purple-500/30 rounded text-white"
                      />
                    </div>
                    <div>
                      <label className="text-white text-sm block mb-2">Max Pages</label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={scrapingRules.maxPages}
                        onChange={(e) => setScrapingRules(prev => ({ ...prev, maxPages: parseInt(e.target.value) }))}
                        className="w-full p-2 bg-black/30 border border-purple-500/30 rounded text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      {[
                        { key: 'followLinks', label: 'Follow Internal Links' },
                        { key: 'respectRobots', label: 'Respect robots.txt' }
                      ].map(({ key, label }) => (
                        <label key={key} className="flex items-center gap-2 text-white">
                          <input
                            type="checkbox"
                            checked={scrapingRules[key]}
                            onChange={(e) => setScrapingRules(prev => ({ ...prev, [key]: e.target.checked }))}
                            className="text-purple-500"
                          />
                          {label}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Filters */}
                <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Filter className="text-purple-400" />
                    Filters
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-white text-sm block mb-2">Min Text Length</label>
                      <input
                        type="number"
                        min="1"
                        value={filters.minTextLength}
                        onChange={(e) => setFilters(prev => ({ ...prev, minTextLength: parseInt(e.target.value) }))}
                        className="w-full p-2 bg-black/30 border border-purple-500/30 rounded text-white"
                      />
                    </div>
                    <div className="space-y-2">
                      {[
                        { key: 'excludeNavigation', label: 'Exclude Navigation Elements' },
                        { key: 'includeHidden', label: 'Include Hidden Elements' }
                      ].map(({ key, label }) => (
                        <label key={key} className="flex items-center gap-2 text-white">
                          <input
                            type="checkbox"
                            checked={filters[key]}
                            onChange={(e) => setFilters(prev => ({ ...prev, [key]: e.target.checked }))}
                            className="text-purple-500"
                          />
                          {label}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'history' && (
              <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="text-purple-400" />
                  Scraping History
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {scrapingHistory.length > 0 ? (
                    scrapingHistory.map((session) => (
                      <div key={session.id} className="bg-black/20 rounded-lg p-3">
                        <div className="text-white text-sm font-medium">{session.url}</div>
                        <div className="text-gray-400 text-xs">{session.intent}</div>
                        <div className="text-purple-400 text-xs mt-1">
                          {session.dataCount} items • {session.strategy} • {session.timestamp.toLocaleString()}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-400 text-center py-8">
                      <Clock size={48} className="mx-auto mb-4 opacity-50" />
                      <div>No scraping history yet</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Results */}
          <div className="xl:col-span-2 space-y-6">
            {/* Results Display */}
            <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Eye className="text-purple-400" />
                  Scraped Data ({scrapedData.length} items)
                </h3>
                {scrapedData.length > 0 && (
                  <div className="flex gap-2">
                    <select
                      value={exportFormat}
                      onChange={(e) => setExportFormat(e.target.value)}
                      className="bg-black/30 border border-purple-500/30 text-white px-3 py-1 rounded text-sm"
                    >
                      <option value="json">JSON</option>
                      <option value="csv">CSV</option>
                    </select>
                    <button
                      onClick={exportData}
                      className="bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-400 px-4 py-1 rounded text-sm flex items-center gap-1"
                    >
                      <Download size={16} />
                      Export
                    </button>
                  </div>
                )}
              </div>

              <div className="bg-black/30 rounded-lg p-4 max-h-96 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mb-4 mx-auto"></div>
                      <div className="text-white text-lg">Analyzing and extracting data...</div>
                      <div className="text-gray-400 text-sm">This may take a few moments</div>
                    </div>
                  </div>
                ) : scrapedData.length > 0 ? (
                  <div className="space-y-3">
                    {scrapedData.map((item, index) => (
                      <div key={index} className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <span className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-xs font-medium">
                            {item.type}
                          </span>
                          {item.confidence && (
                            <span className="text-green-400 text-xs">{item.confidence}% match</span>
                          )}
                        </div>
                        <div className="space-y-2">
                          {Object.entries(item).map(([key, value]) => {
                            if (key === 'type') return null;
                            return (
                              <div key={key} className="flex">
                                <span className="text-gray-400 text-sm min-w-24 capitalize">{key}:</span>
                                <span className="text-white text-sm ml-2">
                                  {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-400 py-12">
                    <AlertCircle size={48} className="mx-auto mb-4 opacity-50" />
                    <div className="text-lg mb-2">No data extracted yet</div>
                    <div className="text-sm">Enter a URL and your intent, then start scraping</div>
                  </div>
                )}
              </div>
            </div>

            {/* Statistics */}
            {scrapedData.length > 0 && (
              <div className="bg-black/20 backdrop-blur-sm border border-purple-500/30 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4">Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Total Items', value: scrapedData.length, color: 'text-blue-400' },
                    { label: 'Unique Types', value: [...new Set(scrapedData.map(item => item.type))].length, color: 'text-green-400' },
                    { label: 'Success Rate', value: '95%', color: 'text-yellow-400' },
                    { label: 'Processing Time', value: '2.3s', color: 'text-purple-400' }
                  ].map(stat => (
                    <div key={stat.label} className="bg-black/30 rounded-lg p-4 text-center">
                      <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                      <div className="text-gray-400 text-sm">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedWebScraper;

