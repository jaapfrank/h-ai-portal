import React, { useState } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw, 
  Database, 
  Brain, 
  Shield,
  Clock,
  Cpu
} from 'lucide-react';
import { 
  testSqlConnection, 
  testAdConnection, 
  testClaudeConnection 
} from '../services/api';
import { useNavigate } from 'react-router-dom';

const StatusPanel = ({ status, onRefresh }) => {
  const [testing, setTesting] = useState({});
  const navigate = useNavigate();

  const getStatusIcon = (statusText) => {
    if (!statusText) return <AlertCircle className="h-5 w-5 text-gray-400" />;
    
    if (statusText.includes('OK')) {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    } else {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusColor = (statusText) => {
    if (!statusText) return 'text-gray-600';
    if (statusText.includes('OK')) return 'text-green-600';
    return 'text-red-600';
  };

  const runIndividualTest = async (testType) => {
    setTesting(prev => ({ ...prev, [testType]: true }));
    
    try {
      let result;
      switch (testType) {
        case 'sql':
          result = await testSqlConnection();
          break;
        case 'ad':
          result = await testAdConnection();
          break;
        case 'claude':
          result = await testClaudeConnection();
          break;
        default:
          return;
      }
      
      // Handle different response formats
      let isSuccess = false;
      let message = '';
      
      if (testType === 'sql') {
        isSuccess = result.status === 'success';
        message = isSuccess 
          ? `Database: ${result.database}\nTotaal machines: ${result.total_machines}\nGerede machines: ${result.ready_machines}`
          : result.detail || 'Database test gefaald';
      } else if (testType === 'claude') {
        isSuccess = result.status === 'success';
        message = isSuccess 
          ? `Claude AI: ${result.claude_response}`
          : result.detail || 'Claude test gefaald';
      } else {
        isSuccess = result.ok || result.status === 'success';
        message = result.msg || result.detail || JSON.stringify(result);
      }
      
      alert(`${testType.toUpperCase()} Test: ${isSuccess ? 'Succesvol' : 'Gefaald'}\n${message}`);
    } catch (error) {
      alert(`${testType.toUpperCase()} Test Gefaald: ${error.message}`);
    } finally {
      setTesting(prev => ({ ...prev, [testType]: false }));
    }
  };

  const statusItems = [
    {
      id: 'database',
      label: 'Database',
      icon: Database,
      status: status?.database,
      testFunction: () => runIndividualTest('sql')
    },
    {
      id: 'schema',
      label: 'Schema',
      icon: Database,
      status: status?.schema,
      testFunction: null // Schema doesn't have a separate test
    },
    {
      id: 'claude_ai',
      label: 'Claude AI',
      icon: Brain,
      status: status?.claude_ai,
      testFunction: () => runIndividualTest('claude')
    },
    {
      id: 'active_directory',
      label: 'Active Directory',
      icon: Shield,
      status: status?.active_directory,
      testFunction: () => runIndividualTest('ad')
    }
  ];

  return (
    <div className="space-y-6">
      {/* System Status Card */}
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-hoeflon-900">Systeemstatus</h3>
          <button
            onClick={onRefresh}
            className="p-2 text-hoeflon-500 hover:text-hoeflon-700 hover:bg-hoeflon-100 rounded-lg transition-all duration-200"
            title="Status vernieuwen"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-4">
          {statusItems.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 bg-hoeflon-25 rounded-lg border border-hoeflon-100">
              <div className="flex items-center space-x-3">
                <item.icon className="h-5 w-5 text-hoeflon-500" />
                <span className="text-sm font-semibold text-hoeflon-800">
                  {item.label}
                </span>
              </div>
              
              <div className="flex items-center space-x-3">
                {getStatusIcon(item.status)}
                {item.testFunction && (
                  <button
                    onClick={item.testFunction}
                    disabled={testing[item.id]}
                    className="btn-hoeflon-outline text-xs px-2 py-1 disabled:opacity-50"
                  >
                    {testing[item.id] ? 'Testen...' : 'Test'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {status?.timestamp && (
          <div className="mt-6 pt-4 border-t border-hoeflon-200">
            <div className="flex items-center space-x-2 text-xs text-hoeflon-500">
              <Clock className="h-3 w-3" />
              <span>
                Laatste update: {new Date(status.timestamp).toLocaleTimeString('nl-NL')}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Help Card */}
      <div className="bg-gradient-to-br from-hoeflon-blue-light to-blue-50 rounded-lg border border-hoeflon-blue/20 p-5">
        <h3 className="text-sm font-bold text-hoeflon-800 mb-3 flex items-center space-x-2">
          <Shield className="h-4 w-4 text-hoeflon-blue" />
          <span>Toegang & Beveiliging</span>
        </h3>
        <p className="text-xs text-hoeflon-700 leading-relaxed">
          Alleen leden van de AD-groep 'AI' hebben toegang tot dit portaal.
          Alle interactions worden gelogd voor audit doeleinden.
        </p>
      </div>

      {/* Quick Stats Card */}
      <div className="card-hoeflon p-5">
        <h3 className="text-sm font-bold text-hoeflon-900 mb-4 flex items-center space-x-2">
          <Database className="h-4 w-4 text-hoeflon-orange" />
          <span>Systeem Specs</span>
        </h3>
        <div className="space-y-3 text-xs">
          <div className="flex justify-between items-center p-2 bg-hoeflon-25 rounded">
            <span className="text-hoeflon-600 font-medium">Backend API:</span>
            <span className="text-hoeflon-800 font-bold">:8504</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-hoeflon-25 rounded">
            <span className="text-hoeflon-600 font-medium">Frontend UI:</span>
            <span className="text-hoeflon-800 font-bold">:3000</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-hoeflon-25 rounded">
            <span className="text-hoeflon-600 font-medium">Admin Panel:</span>
            <span className="text-hoeflon-800 font-bold">:8502</span>
          </div>
        </div>
      </div>

      {/* Enterprise Features Card */}
      <div className="bg-gradient-to-br from-hoeflon-600 to-hoeflon-700 rounded-lg border border-hoeflon-500 p-5 text-white">
        <h3 className="text-sm font-bold mb-4 flex items-center space-x-2">
          <Shield className="h-4 w-4 text-hoeflon-100" />
          <span>Enterprise Features</span>
        </h3>
        <div className="space-y-3 text-xs">
          <div className="flex justify-between items-center p-2 bg-hoeflon-500/20 rounded backdrop-blur-sm">
            <span className="text-hoeflon-100 font-medium">Intelligent Cache:</span>
            <span className="text-hoeflon-200 font-bold">Active</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-hoeflon-500/20 rounded backdrop-blur-sm">
            <span className="text-hoeflon-100 font-medium">ML Training:</span>
            <span className="text-hoeflon-200 font-bold">Running</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-hoeflon-500/20 rounded backdrop-blur-sm">
            <span className="text-hoeflon-100 font-medium">PostgreSQL MCP:</span>
            <span className="text-hoeflon-200 font-bold">Connected</span>
          </div>
        </div>
        <button
          onClick={() => navigate('/enterprise')}
          className="w-full mt-4 px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-all duration-200 text-xs font-medium border border-white/20"
        >
          View All Enterprise Features →
        </button>
      </div>

      {/* Hoeflon Branding Footer */}
      <div className="text-center py-4">
        <div className="inline-flex items-center space-x-2 px-4 py-2 bg-hoeflon-800 rounded-full text-white text-xs">
          <Cpu className="h-3 w-3" />
          <span className="font-medium">Powered by Hoeflon AI</span>
        </div>
        <p className="text-xs text-hoeflon-400 mt-2 italic">"Smart and Powerful"</p>
      </div>
    </div>
  );
};

export default StatusPanel;