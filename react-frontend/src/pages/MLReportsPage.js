import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

function MLReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch('http://localhost:8504/ml_reports');
        if (response.ok) {
          const data = await response.json();
          setReports(data.reports || []);
        } else {
          setError('Failed to fetch ML reports');
        }
      } catch (err) {
        setError('Network error: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
    // Refresh every 60 seconds
    const interval = setInterval(fetchReports, 60000);
    return () => clearInterval(interval);
  }, []);

  const downloadReport = async (filename) => {
    try {
      const response = await fetch(`http://localhost:8504/ml_reports/${filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getReportIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'json results': return '📄';
      case 'html report': return '📊';
      case 'analysis': return '🔍';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
        <Header />
        <main className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hoeflon-600 mx-auto"></div>
            <p className="text-center mt-4 text-gray-600">Loading ML Reports...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
        <Header />
        <main className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h1 className="text-2xl font-bold text-red-800 mb-4">❌ Error Loading ML Reports</h1>
            <p className="text-red-700">{error}</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
      <Header />
      <main className="container mx-auto px-4 py-6 max-w-6xl">
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">📊 Machine Learning Reports</h1>
            <p className="text-gray-600">Comprehensive analysis reports from Hoeflon's ML training system</p>
            <div className="mt-4 flex flex-wrap gap-4 text-sm">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                📄 {reports.filter(r => r.type?.includes('JSON')).length} JSON Reports
              </span>
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                📊 {reports.filter(r => r.type?.includes('HTML')).length} HTML Reports
              </span>
              <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
                📋 {reports.length} Total Reports
              </span>
            </div>
          </div>

          {/* Reports List */}
          {reports.length > 0 ? (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📂 Available Reports</h2>
              <div className="space-y-3">
                {reports.map((report, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{getReportIcon(report.type)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-800">{report.filename || report.name}</h3>
                          <p className="text-sm text-gray-600">{report.description || report.type}</p>
                          <div className="flex space-x-4 text-xs text-gray-500 mt-1">
                            <span>📅 {new Date(report.created).toLocaleString()}</span>
                            <span>📏 {formatFileSize(report.size)}</span>
                            <span>🏷️ {report.type}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => downloadReport(report.filename || report.name)}
                          className="bg-hoeflon-600 hover:bg-hoeflon-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                        >
                          📥 Download
                        </button>
                        {report.type?.includes('HTML') && (
                          <button
                            onClick={() => window.open(`http://localhost:8504/ml_reports/${report.filename}`, '_blank')}
                            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                          >
                            👁️ View
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">No Reports Available</h2>
              <p className="text-gray-600 mb-4">ML analysis reports will appear here when training is completed.</p>
              <button
                onClick={() => window.location.reload()}
                className="bg-hoeflon-600 hover:bg-hoeflon-700 text-white px-6 py-2 rounded-md font-medium transition-colors"
              >
                🔄 Refresh
              </button>
            </div>
          )}

          {/* Report Generation Info */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">ℹ️ About ML Reports</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">📄 JSON Reports</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Raw analysis results and metrics</li>
                  <li>• Model performance statistics</li>
                  <li>• Training data summaries</li>
                  <li>• Machine-readable format</li>
                </ul>
              </div>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">📊 HTML Reports</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Visual data analysis charts</li>
                  <li>• Interactive performance dashboards</li>
                  <li>• Business insights summaries</li>
                  <li>• Human-readable presentations</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700 leading-relaxed">
                Reports are automatically generated when ML training sessions complete. They provide detailed 
                insights into model performance, data quality, and business intelligence derived from Hoeflon's 
                operational data. Use these reports to track ML system improvements and validate business decisions.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default MLReportsPage;