import React, { useState } from 'react';
import { Building2, Database, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp, Zap } from 'lucide-react';

const EnterpriseAnalysisIndicator = ({ enterpriseAnalysis }) => {
  const [showDetails, setShowDetails] = useState(false);

  if (!enterpriseAnalysis || enterpriseAnalysis.status === "not_analyzed") {
    return null;
  }

  if (enterpriseAnalysis.status === "error") {
    return (
      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          <span className="text-sm text-red-800">
            Enterprise Analysis Error: {enterpriseAnalysis.error}
          </span>
        </div>
      </div>
    );
  }

  const getIntentColor = (intent) => {
    switch (intent) {
      case 'financial': return 'bg-green-500';
      case 'operational': return 'bg-blue-500';
      case 'validation': return 'bg-yellow-500';
      case 'analytical': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getIntentIcon = (intent) => {
    switch (intent) {
      case 'financial': return '💰';
      case 'operational': return '⚙️';
      case 'validation': return '🔍';
      case 'analytical': return '📊';
      default: return '🤖';
    }
  };

  return (
    <div className="mb-4 p-3 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-indigo-500 rounded-full">
            <Building2 className="h-3 w-3 text-white" />
          </div>
          <span className="text-sm font-medium text-indigo-800">
            🚀 Enterprise Query Analysis
          </span>
          {enterpriseAnalysis.intent && (
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${getIntentColor(enterpriseAnalysis.intent)}`}></div>
              <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                {getIntentIcon(enterpriseAnalysis.intent)} {enterpriseAnalysis.intent}
              </span>
            </div>
          )}
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {showDetails && (
        <div className="mt-3 pt-3 border-t border-indigo-200 space-y-3">
          
          {/* Intent & Entities */}
          {enterpriseAnalysis.intent && (
            <div>
              <h4 className="text-xs font-medium text-indigo-700 mb-1 flex items-center">
                <Info className="h-3 w-3 mr-1" />
                Business Intent & Entities:
              </h4>
              <div className="flex flex-wrap gap-1">
                <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">
                  Intent: {enterpriseAnalysis.intent}
                </span>
                {enterpriseAnalysis.entities && enterpriseAnalysis.entities.map((entity, index) => (
                  <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Data Sources Used */}
          {enterpriseAnalysis.sources_used && enterpriseAnalysis.sources_used.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-indigo-700 mb-1 flex items-center">
                <Database className="h-3 w-3 mr-1" />
                Data Sources Selected:
              </h4>
              <div className="space-y-1">
                {enterpriseAnalysis.sources_used.map((source, index) => (
                  <div key={index} className="flex items-center space-x-2 text-xs">
                    <div className="flex-shrink-0 p-1 bg-indigo-100 rounded">
                      <Database className="h-3 w-3 text-indigo-600" />
                    </div>
                    <span className="text-indigo-800 font-medium">{source}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Validation Results */}
          {enterpriseAnalysis.validation && (
            <div>
              <h4 className="text-xs font-medium text-indigo-700 mb-1 flex items-center">
                <CheckCircle className="h-3 w-3 mr-1" />
                Data Validation:
              </h4>
              <div className="space-y-1">
                {enterpriseAnalysis.validation.checks_performed && 
                 enterpriseAnalysis.validation.checks_performed.map((check, index) => (
                  <div key={index} className="text-xs text-indigo-600">
                    ✓ {check.replace(/_/g, ' ')}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {enterpriseAnalysis.warnings && enterpriseAnalysis.warnings.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-yellow-700 mb-1 flex items-center">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Important Warnings:
              </h4>
              <div className="space-y-1">
                {enterpriseAnalysis.warnings.map((warning, index) => (
                  <div key={index} className="text-xs text-yellow-700 bg-yellow-50 px-2 py-1 rounded border border-yellow-200">
                    {warning}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Complexity Score */}
          {enterpriseAnalysis.complexity && (
            <div>
              <h4 className="text-xs font-medium text-indigo-700 mb-1">
                Query Complexity:
              </h4>
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  {[...Array(10)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded ${
                        i < enterpriseAnalysis.complexity 
                          ? 'bg-indigo-500' 
                          : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-indigo-600">
                  {enterpriseAnalysis.complexity}/10
                </span>
              </div>
            </div>
          )}

          {/* System Benefits */}
          <div className="mt-2 text-xs text-indigo-600 bg-indigo-50 px-2 py-1 rounded border border-indigo-100">
            💡 This query was automatically routed to the optimal databases using enterprise-grade federated query intelligence.
          </div>
        </div>
      )}
    </div>
  );
};

export default EnterpriseAnalysisIndicator;