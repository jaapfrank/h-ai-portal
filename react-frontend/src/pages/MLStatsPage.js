import React, { useState, useEffect } from 'react';
import Header from '../components/Header';

function MLStatsPage() {
  const [mlStats, setMLStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMLStats = async () => {
      try {
        const response = await fetch('http://localhost:8504/ml_stats');
        if (response.ok) {
          const data = await response.json();
          setMLStats(data);
        } else {
          setError('Failed to fetch ML statistics');
        }
      } catch (err) {
        setError('Network error: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMLStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchMLStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
        <Header />
        <main className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hoeflon-600 mx-auto"></div>
            <p className="text-center mt-4 text-gray-600">Loading ML Statistics...</p>
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
            <h1 className="text-2xl font-bold text-red-800 mb-4">❌ Error Loading ML Statistics</h1>
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
            <h1 className="text-3xl font-bold text-gray-800 mb-2">🤖 Machine Learning Statistics</h1>
            <p className="text-gray-600">Real-time insights into Hoeflon's ML training and model performance</p>
            <p className="text-sm text-gray-500 mt-2">Last updated: {new Date(mlStats?.timestamp).toLocaleString()}</p>
          </div>

          {/* ML Statistics Cards */}
          {mlStats?.success && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Models Loaded */}
              <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">🧠 Models Loaded</h3>
                <p className="text-3xl font-bold text-blue-600">
                  {mlStats.ml_statistics.models_loaded}
                </p>
                <p className="text-sm text-gray-600 mt-2">Active ML models in memory</p>
              </div>

              {/* Training Samples */}
              <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">📊 Training Samples</h3>
                <p className="text-3xl font-bold text-green-600">
                  {mlStats.ml_statistics.training_samples.toLocaleString()}
                </p>
                <p className="text-sm text-gray-600 mt-2">Data points used for training</p>
              </div>

              {/* Model Accuracy */}
              <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">🎯 Model Accuracy</h3>
                <p className="text-3xl font-bold text-purple-600">
                  {(mlStats.ml_statistics.accuracy * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600 mt-2">Overall prediction accuracy</p>
              </div>

              {/* Training Status */}
              <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-orange-500">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">⚡ Training Status</h3>
                <p className="text-xl font-bold text-orange-600">
                  {mlStats.ml_statistics.training_status}
                </p>
                <p className="text-sm text-gray-600 mt-2">Current ML training state</p>
              </div>

              {/* Last Training */}
              <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-indigo-500 md:col-span-2">
                <h3 className="text-lg font-semibold text-gray-800 mb-2">📅 Last Training Session</h3>
                <p className="text-xl font-bold text-indigo-600">
                  {mlStats.ml_statistics.last_training}
                </p>
                <p className="text-sm text-gray-600 mt-2">Most recent model training completed</p>
              </div>
            </div>
          )}

          {/* ML Features Overview */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">🔧 ML Capabilities</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">🤖 Active Models</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Confidence Prediction Model</li>
                  <li>• Query Quality Classifier</li>
                  <li>• Anomaly Detection System</li>
                  <li>• Demand Forecasting Engine</li>
                </ul>
              </div>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">📊 Learning Features</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>• Real-time pattern recognition</li>
                  <li>• Automated feedback integration</li>
                  <li>• Continuous model improvement</li>
                  <li>• Business rule validation</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">📈 Performance Insights</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700 leading-relaxed">
                The ML system continuously learns from user interactions and query patterns to improve 
                response accuracy and relevance. Performance metrics are updated in real-time to ensure 
                optimal system behavior for Hoeflon's business intelligence needs.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default MLStatsPage;