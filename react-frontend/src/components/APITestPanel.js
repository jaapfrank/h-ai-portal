import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw, 
  Database, 
  Brain, 
  Shield,
  Clock,
  Cpu,
  Zap,
  Activity,
  Settings
} from 'lucide-react';
import api from '../services/api';

const APITestPanel = () => {
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState(false);

  const apiEndpoints = [
    {
      id: 'status',
      name: 'System Status',
      url: '/status',
      icon: <Activity className="h-4 w-4" />,
      critical: true
    },
    {
      id: 'test_sql',
      name: 'Database Test',
      url: '/test_sql',
      icon: <Database className="h-4 w-4" />,
      critical: true
    },
    {
      id: 'test_claude',
      name: 'Claude AI Test',
      url: '/test_claude',
      icon: <Brain className="h-4 w-4" />,
      critical: true
    },
    {
      id: 'test_ad',
      name: 'Active Directory Test',
      url: '/test_ad',
      icon: <Shield className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'cache_performance',
      name: 'Cache Performance',
      url: '/cache/performance',
      icon: <Zap className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'cache_stats',
      name: 'Cache Statistics',
      url: '/cache/stats',
      icon: <Zap className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'ml_training_status',
      name: 'ML Training Status',
      url: '/ml/training_status',
      icon: <Brain className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'enterprise_status',
      name: 'Enterprise Status',
      url: '/enterprise/status',
      icon: <Settings className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'postgresql_status',
      name: 'PostgreSQL Status',
      url: '/postgresql/status',
      icon: <Database className="h-4 w-4" />,
      critical: false
    },
    {
      id: 'performance',
      name: 'Performance Stats',
      url: '/performance',
      icon: <Activity className="h-4 w-4" />,
      critical: false
    }
  ];

  useEffect(() => {
    runAllTests();
  }, []);

  const runAllTests = async () => {
    setTesting(true);
    const results = {};

    for (const endpoint of apiEndpoints) {
      try {
        const startTime = Date.now();
        const response = await api.get(endpoint.url);
        const responseTime = Date.now() - startTime;

        results[endpoint.id] = {
          status: 'success',
          responseTime,
          data: response.data,
          error: null
        };
      } catch (error) {
        results[endpoint.id] = {
          status: 'error',
          responseTime: null,
          data: null,
          error: error.message
        };
      }
    }

    setTestResults(results);
    setTesting(false);
  };

  const runSingleTest = async (endpoint) => {
    setTestResults(prev => ({
      ...prev,
      [endpoint.id]: { ...prev[endpoint.id], status: 'testing' }
    }));

    try {
      const startTime = Date.now();
      const response = await api.get(endpoint.url);
      const responseTime = Date.now() - startTime;

      setTestResults(prev => ({
        ...prev,
        [endpoint.id]: {
          status: 'success',
          responseTime,
          data: response.data,
          error: null
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [endpoint.id]: {
          status: 'error',
          responseTime: null,
          data: null,
          error: error.message
        }
      }));
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'testing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'testing':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getCriticalEndpoints = () => {
    return apiEndpoints.filter(ep => ep.critical);
  };

  const getNonCriticalEndpoints = () => {
    return apiEndpoints.filter(ep => !ep.critical);
  };

  const getOverallHealth = () => {
    const criticalEndpoints = getCriticalEndpoints();
    const criticalResults = criticalEndpoints.map(ep => testResults[ep.id]?.status);
    const criticalSuccessCount = criticalResults.filter(status => status === 'success').length;
    
    if (criticalSuccessCount === criticalEndpoints.length) {
      return { status: 'healthy', message: 'All critical systems operational' };
    } else if (criticalSuccessCount >= criticalEndpoints.length / 2) {
      return { status: 'warning', message: 'Some critical systems have issues' };
    } else {
      return { status: 'error', message: 'Multiple critical systems failing' };
    }
  };

  const overallHealth = getOverallHealth();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-hoeflon-900">API Endpoint Tests</h2>
              <p className="text-sm text-hoeflon-600">Frontend-Backend Connectivity Status</p>
            </div>
          </div>
          <button
            onClick={runAllTests}
            disabled={testing}
            className="btn-hoeflon-outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${testing ? 'animate-spin' : ''}`} />
            {testing ? 'Testing...' : 'Run All Tests'}
          </button>
        </div>

        {/* Overall Health */}
        <div className={`p-4 rounded-lg border ${
          overallHealth.status === 'healthy' ? 'bg-green-50 border-green-200' :
          overallHealth.status === 'warning' ? 'bg-yellow-50 border-yellow-200' :
          'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center space-x-3">
            {overallHealth.status === 'healthy' ? 
              <CheckCircle className="h-6 w-6 text-green-600" /> :
              overallHealth.status === 'warning' ?
              <AlertCircle className="h-6 w-6 text-yellow-600" /> :
              <XCircle className="h-6 w-6 text-red-600" />
            }
            <div>
              <div className={`font-semibold ${
                overallHealth.status === 'healthy' ? 'text-green-800' :
                overallHealth.status === 'warning' ? 'text-yellow-800' :
                'text-red-800'
              }`}>
                System Health: {overallHealth.status.toUpperCase()}
              </div>
              <div className={`text-sm ${
                overallHealth.status === 'healthy' ? 'text-green-600' :
                overallHealth.status === 'warning' ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {overallHealth.message}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Critical Endpoints */}
      <div className="card-hoeflon p-6">
        <h3 className="text-lg font-bold text-hoeflon-900 mb-4">Critical System Endpoints</h3>
        <div className="space-y-3">
          {getCriticalEndpoints().map((endpoint) => {
            const result = testResults[endpoint.id];
            return (
              <div key={endpoint.id} className={`p-4 rounded-lg border ${getStatusColor(result?.status)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {endpoint.icon}
                    <div>
                      <div className="font-semibold">{endpoint.name}</div>
                      <div className="text-xs text-gray-600">{endpoint.url}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    {result?.responseTime && (
                      <span className="text-xs text-gray-600">
                        {result.responseTime}ms
                      </span>
                    )}
                    {getStatusIcon(result?.status)}
                    <button
                      onClick={() => runSingleTest(endpoint)}
                      disabled={result?.status === 'testing'}
                      className="btn-hoeflon-outline text-xs px-2 py-1"
                    >
                      Test
                    </button>
                  </div>
                </div>
                
                {result?.error && (
                  <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                    Error: {result.error}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Enterprise Endpoints */}
      <div className="card-hoeflon p-6">
        <h3 className="text-lg font-bold text-hoeflon-900 mb-4">Enterprise Feature Endpoints</h3>
        <div className="space-y-3">
          {getNonCriticalEndpoints().map((endpoint) => {
            const result = testResults[endpoint.id];
            return (
              <div key={endpoint.id} className={`p-4 rounded-lg border ${getStatusColor(result?.status)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {endpoint.icon}
                    <div>
                      <div className="font-semibold">{endpoint.name}</div>
                      <div className="text-xs text-gray-600">{endpoint.url}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    {result?.responseTime && (
                      <span className="text-xs text-gray-600">
                        {result.responseTime}ms
                      </span>
                    )}
                    {getStatusIcon(result?.status)}
                    <button
                      onClick={() => runSingleTest(endpoint)}
                      disabled={result?.status === 'testing'}
                      className="btn-hoeflon-outline text-xs px-2 py-1"
                    >
                      Test
                    </button>
                  </div>
                </div>
                
                {result?.error && (
                  <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                    Error: {result.error}
                  </div>
                )}
                
                {result?.data && result.status === 'success' && (
                  <div className="mt-2 text-xs text-gray-600">
                    Response: {JSON.stringify(result.data).substring(0, 100)}...
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card-hoeflon p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {Object.values(testResults).filter(r => r.status === 'success').length}
          </div>
          <div className="text-sm text-gray-600">Successful</div>
        </div>
        <div className="card-hoeflon p-4 text-center">
          <div className="text-2xl font-bold text-red-600">
            {Object.values(testResults).filter(r => r.status === 'error').length}
          </div>
          <div className="text-sm text-gray-600">Failed</div>
        </div>
        <div className="card-hoeflon p-4 text-center">
          <div className="text-2xl font-bold text-hoeflon-600">
            {Object.values(testResults).length > 0 ? 
              Math.round(Object.values(testResults).reduce((acc, r) => acc + (r.responseTime || 0), 0) / Object.values(testResults).filter(r => r.responseTime).length) :
              0
            }ms
          </div>
          <div className="text-sm text-gray-600">Avg Response</div>
        </div>
      </div>
    </div>
  );
};

export default APITestPanel;