import React, { useState, useEffect } from 'react';
import { Brain, Activity, Database, Zap, Clock, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

const AIMonitoringPanel = () => {
  const [aiMetrics, setAiMetrics] = useState({
    activeQueries: [],
    memoryUsage: 0,
    mlModels: [],
    conversationContext: {},
    systemPerformance: {}
  });
  
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Fetch AI monitoring data
    const fetchAIMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8504/ai_monitoring');
        if (response.ok) {
          const data = await response.json();
          setAiMetrics(data);
          setIsConnected(true);
        }
      } catch (error) {
        console.error('AI Monitoring fetch error:', error);
        setIsConnected(false);
      }
    };

    fetchAIMetrics();
    const interval = setInterval(fetchAIMetrics, 2000); // Update every 2 seconds
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">AI & ML Monitoring</h2>
            <p className="text-sm text-gray-600">Real-time inzicht in AI verwerking</p>
          </div>
        </div>
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
          isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isConnected ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Real-time Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Active Queries */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <Activity className="h-5 w-5 text-blue-600" />
            <span className="text-xs font-medium text-blue-600">ACTIEF</span>
          </div>
          <div className="text-2xl font-bold text-blue-800">
            {aiMetrics.activeQueries?.length || 0}
          </div>
          <div className="text-sm text-blue-600">Active AI Queries</div>
        </div>

        {/* Memory Usage */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <Database className="h-5 w-5 text-purple-600" />
            <span className="text-xs font-medium text-purple-600">MEMORY</span>
          </div>
          <div className="text-2xl font-bold text-purple-800">
            {Math.round(aiMetrics.memoryUsage || 0)}%
          </div>
          <div className="text-sm text-purple-600">Conversation Memory</div>
        </div>

        {/* Processing Speed */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <Zap className="h-5 w-5 text-green-600" />
            <span className="text-xs font-medium text-green-600">SPEED</span>
          </div>
          <div className="text-2xl font-bold text-green-800">
            {aiMetrics.systemPerformance?.avgResponseTime || 0}ms
          </div>
          <div className="text-sm text-green-600">Avg Response Time</div>
        </div>

        {/* ML Models */}
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-5 w-5 text-orange-600" />
            <span className="text-xs font-medium text-orange-600">MODELS</span>
          </div>
          <div className="text-2xl font-bold text-orange-800">
            {aiMetrics.mlModels?.filter(m => m.status === 'active').length || 0}
          </div>
          <div className="text-sm text-orange-600">Active ML Models</div>
        </div>
      </div>

      {/* Active Queries Section */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
          <Activity className="h-5 w-5 mr-2 text-blue-600" />
          Actieve AI Verwerking
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 min-h-[120px]">
          {aiMetrics.activeQueries?.length > 0 ? (
            <div className="space-y-2">
              {aiMetrics.activeQueries.map((query, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                  <div className="flex items-center space-x-3">
                    <div className="animate-pulse w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="font-medium text-gray-800">{query.question}</span>
                    <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                      {query.stage}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>{query.elapsed}s</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-20 text-gray-500">
              <div className="text-center">
                <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Geen actieve AI verwerking</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ML Models Status */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-orange-600" />
          Machine Learning Models
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {aiMetrics.mlModels?.length > 0 ? aiMetrics.mlModels.map((model, index) => (
            <div key={index} className="bg-white border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-800">{model.name}</span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  model.status === 'active' ? 'bg-green-100 text-green-800' : 
                  model.status === 'training' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {model.status}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <div>Accuracy: {model.accuracy}%</div>
                <div>Last Updated: {model.lastUpdate}</div>
              </div>
            </div>
          )) : (
            <div className="col-span-2 text-center p-6 text-gray-500">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>Geen actieve ML models</p>
            </div>
          )}
        </div>
      </div>

      {/* Conversation Memory */}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
          <Database className="h-5 w-5 mr-2 text-purple-600" />
          Conversational Memory
        </h3>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-purple-800">
                {aiMetrics.conversationContext?.activeSessions || 0}
              </div>
              <div className="text-sm text-purple-600">Active Sessions</div>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-800">
                {aiMetrics.conversationContext?.storedInteractions || 0}
              </div>
              <div className="text-sm text-purple-600">Stored Interactions</div>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-800">
                {aiMetrics.conversationContext?.contextMatches || 0}
              </div>
              <div className="text-sm text-purple-600">Context Matches</div>
            </div>
            <div>
              <div className="text-lg font-bold text-purple-800">
                {Math.round(aiMetrics.conversationContext?.memoryEfficiency || 0)}%
              </div>
              <div className="text-sm text-purple-600">Memory Efficiency</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIMonitoringPanel;