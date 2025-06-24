import React, { useState } from 'react';
import { Database, ChevronDown, ChevronUp, TableProperties, Zap } from 'lucide-react';

const CSVEnhancementIndicator = ({ csvTables, isEnhanced }) => {
  const [showDetails, setShowDetails] = useState(false);

  if (!isEnhanced || !csvTables || csvTables.length === 0) {
    return null;
  }

  return (
    <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-blue-500 rounded-full">
            <Zap className="h-3 w-3 text-white" />
          </div>
          <span className="text-sm font-medium text-blue-800">
            🧠 CSV Enhanced Query
          </span>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
            {csvTables.length} table{csvTables.length !== 1 ? 's' : ''} suggested
          </span>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-blue-600 hover:text-blue-800 transition-colors"
        >
          {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {showDetails && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <h4 className="text-xs font-medium text-blue-700 mb-2 flex items-center">
            <Database className="h-3 w-3 mr-1" />
            Intelligent Table Selection:
          </h4>
          <div className="space-y-2">
            {csvTables.slice(0, 3).map((table, index) => (
              <div key={index} className="flex items-start space-x-2 text-xs">
                <div className="flex-shrink-0 p-1 bg-blue-100 rounded">
                  <TableProperties className="h-3 w-3 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-blue-800 truncate">
                    {table.table_name}
                  </div>
                  <div className="text-blue-600 text-xs truncate">
                    {table.description} ({table.column_count} columns)
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-2 text-xs text-blue-600">
            💡 The AI automatically selected the most relevant database tables for your question.
          </div>
        </div>
      )}
    </div>
  );
};

export default CSVEnhancementIndicator;