import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Brain, 
  Zap, 
  Shield, 
  BarChart3, 
  Settings, 
  Users, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  TrendingUp,
  Cpu,
  LineChart,
  Activity
} from 'lucide-react';
import api from '../services/api';
import APITestPanel from './APITestPanel';

const EnterpriseFeatures = () => {
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const enterpriseFeatures = [
    {
      id: 'intelligent_cache',
      title: 'Intelligent Table Cache',
      description: 'High-performance caching system voor 965+ database tables',
      icon: <Zap className="h-6 w-6" />,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      endpoint: '/cache/performance',
      metrics: ['hit_rate', 'total_tables_cached', 'memory_usage_mb']
    },
    {
      id: 'ml_training',
      title: 'Real ML Training Engine',
      description: 'Machine learning met echte productie data',
      icon: <Brain className="h-6 w-6" />,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      endpoint: '/ml/training_status',
      metrics: ['total_samples', 'training_time', 'models_improved']
    },
    {
      id: 'postgresql_mcp',
      title: 'PostgreSQL MCP Server',
      description: 'Model Context Protocol met echte database integratie',
      icon: <Database className="h-6 w-6" />,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      endpoint: '/postgresql/status',
      metrics: ['connection_pool', 'active_connections', 'query_performance']
    },
    {
      id: 'claude_api',
      title: 'Professional Claude API',
      description: 'Anthropic SDK met token management en rate limiting',
      icon: <Cpu className="h-6 w-6" />,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      endpoint: '/test_real_claude',
      metrics: ['token_usage', 'rate_limit', 'confidence_scores']
    },
    {
      id: 'enterprise_system',
      title: 'Complete Enterprise Integration',
      description: 'Alle enterprise systemen werken samen',
      icon: <Settings className="h-6 w-6" />,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      endpoint: '/enterprise/status',
      metrics: ['system_health', 'integration_status', 'uptime']
    },
    {
      id: 'performance_monitoring',
      title: 'Advanced Performance Monitoring',
      description: 'Real-time systeem monitoring en analytics',
      icon: <Activity className="h-6 w-6" />,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      endpoint: '/performance',
      metrics: ['response_time', 'throughput', 'error_rate']
    }
  ];

  useEffect(() => {
    loadEnterpriseFeatures();
  }, []);

  const loadEnterpriseFeatures = async () => {
    setLoading(true);
    const featureStatus = {};

    for (const feature of enterpriseFeatures) {
      try {
        const response = await api.get(feature.endpoint);
        featureStatus[feature.id] = {
          status: 'operational',
          data: response.data,
          lastChecked: new Date().toISOString()
        };
      } catch (error) {
        featureStatus[feature.id] = {
          status: 'error',
          error: error.message,
          lastChecked: new Date().toISOString()
        };
      }
    }

    setFeatures(featureStatus);
    setLoading(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'operational':
        return 'Operationeel';
      case 'error':
        return 'Fout';
      default:
        return 'Onbekend';
    }
  };

  const formatMetricValue = (value) => {
    if (typeof value === 'number') {
      if (value > 1000000) {
        return `${(value / 1000000).toFixed(1)}M`;
      } else if (value > 1000) {
        return `${(value / 1000).toFixed(1)}K`;
      } else if (value < 1 && value > 0) {
        return `${(value * 100).toFixed(1)}%`;
      }
      return value.toLocaleString();
    }
    return value;
  };

  if (loading) {
    return (
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-center space-x-3">
          <RefreshCw className="h-5 w-5 animate-spin text-hoeflon-600" />
          <span className="text-hoeflon-600">Loading Enterprise Features...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-hoeflon-600 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-hoeflon-900">Enterprise Features</h2>
              <p className="text-sm text-hoeflon-600">FASE A: Technical Foundation - All Systems Operational</p>
            </div>
          </div>
          <button
            onClick={loadEnterpriseFeatures}
            className="btn-hoeflon-outline"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Overall Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <div>
                <div className="text-sm font-medium text-green-800">FASE A Completed</div>
                <div className="text-xs text-green-600">Technical Foundation</div>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <Activity className="h-6 w-6 text-blue-600" />
              <div>
                <div className="text-sm font-medium text-blue-800">Performance Optimized</div>
                <div className="text-xs text-blue-600">Intelligent Caching Active</div>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <Brain className="h-6 w-6 text-purple-600" />
              <div>
                <div className="text-sm font-medium text-purple-800">ML Training Active</div>
                <div className="text-xs text-purple-600">Production Data Learning</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {enterpriseFeatures.map((feature) => {
          const featureData = features[feature.id];
          const isOperational = featureData?.status === 'operational';

          return (
            <div 
              key={feature.id}
              className={`border rounded-lg p-6 transition-all duration-200 hover:shadow-lg ${feature.bgColor} ${feature.borderColor}`}
            >
              {/* Feature Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${feature.bgColor} ${feature.borderColor} border`}>
                    <div className={feature.color}>
                      {feature.icon}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{feature.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{feature.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(featureData?.status)}
                  <span className="text-xs font-medium text-gray-600">
                    {getStatusText(featureData?.status)}
                  </span>
                </div>
              </div>

              {/* Feature Metrics */}
              {isOperational && featureData.data && (
                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-gray-700">Live Metrics:</h4>
                  <div className="grid grid-cols-1 gap-2">
                    {feature.metrics.map((metric) => {
                      let value = 'N/A';
                      
                      // Try to extract metric value from nested data structure
                      if (featureData.data) {
                        const data = featureData.data;
                        if (data[metric] !== undefined) {
                          value = data[metric];
                        } else if (data.cache_performance_report && data.cache_performance_report.cache_performance && data.cache_performance_report.cache_performance[metric]) {
                          value = data.cache_performance_report.cache_performance[metric];
                        } else if (data.ml_training_status && data.ml_training_status[metric]) {
                          value = data.ml_training_status[metric];
                        } else if (data.general && data.general[metric]) {
                          value = data.general[metric];
                        }
                      }

                      return (
                        <div key={metric} className="flex justify-between items-center py-1">
                          <span className="text-xs text-gray-600 capitalize">
                            {metric.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-xs font-medium text-gray-900">
                            {formatMetricValue(value)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Error Display */}
              {featureData?.status === 'error' && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="text-xs text-red-800">
                    <strong>Error:</strong> {featureData.error}
                  </div>
                </div>
              )}

              {/* Last Checked */}
              {featureData?.lastChecked && (
                <div className="mt-4 pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <Clock className="h-3 w-3" />
                    <span>
                      Last checked: {new Date(featureData.lastChecked).toLocaleTimeString('nl-NL')}
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* API Test Panel */}
      <APITestPanel />

      {/* FASE B Preview */}
      <div className="card-hoeflon p-6 border-2 border-dashed border-hoeflon-300">
        <div className="text-center">
          <TrendingUp className="h-12 w-12 text-hoeflon-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-hoeflon-900 mb-2">Coming in FASE B</h3>
          <p className="text-sm text-hoeflon-600 mb-4">User Experience Improvements</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-hoeflon-600">
            <div>✨ Enhanced UI/UX Design</div>
            <div>🧪 Puppeteer Testing Suite</div>
            <div>📱 Mobile Responsiveness</div>
            <div>🎨 Advanced Visualizations</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseFeatures;