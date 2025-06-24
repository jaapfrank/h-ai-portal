import React from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';

const ConfidenceIndicator = ({ confidenceScore, isReliable, showDetails = false, className = "" }) => {
  // Convert score to percentage
  const percentage = Math.round((confidenceScore || 0) * 100);
  
  // Determine confidence level and styling
  const getConfidenceLevel = () => {
    if (percentage >= 90) {
      return {
        level: 'Hoge betrouwbaarheid',
        icon: CheckCircle,
        color: 'text-green-600',
        bg: 'bg-green-50',
        border: 'border-green-200',
        progressColor: 'bg-green-500',
        emoji: '🟢'
      };
    } else if (percentage >= 75) {
      return {
        level: 'Gemiddelde betrouwbaarheid',
        icon: Info,
        color: 'text-yellow-600',
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        progressColor: 'bg-yellow-500',
        emoji: '🟡'
      };
    } else if (percentage >= 60) {
      return {
        level: 'Lage betrouwbaarheid',
        icon: AlertTriangle,
        color: 'text-orange-600',
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        progressColor: 'bg-orange-500',
        emoji: '🟠'
      };
    } else {
      return {
        level: 'Onbetrouwbaar',
        icon: XCircle,
        color: 'text-red-600',
        bg: 'bg-red-50',
        border: 'border-red-200',
        progressColor: 'bg-red-500',
        emoji: '🔴'
      };
    }
  };

  const confidence = getConfidenceLevel();
  const IconComponent = confidence.icon;

  if (!showDetails) {
    // Compact version - just badge
    return (
      <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium ${confidence.bg} ${confidence.color} ${confidence.border} border ${className}`}>
        <IconComponent className="h-3 w-3" />
        <span>{confidence.emoji} {percentage}%</span>
      </div>
    );
  }

  // Detailed version
  return (
    <div className={`${confidence.bg} ${confidence.border} border rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <IconComponent className={`h-5 w-5 ${confidence.color}`} />
          <span className={`font-semibold text-sm ${confidence.color}`}>
            Betrouwbaarheid
          </span>
        </div>
        <span className={`text-xs font-mono ${confidence.color}`}>
          {percentage}%
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${confidence.progressColor}`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      
      <div className="flex items-center justify-between">
        <span className={`text-xs ${confidence.color}`}>
          {confidence.emoji} {confidence.level}
        </span>
        {!isReliable && (
          <span className="text-xs text-red-600 font-medium">
            ⚠️ Verifiëren aanbevolen
          </span>
        )}
      </div>
      
      {showDetails && percentage < 75 && (
        <div className="mt-3 p-2 bg-white rounded border border-gray-200">
          <p className="text-xs text-gray-600">
            💡 <strong>Tip:</strong> Specificeer uw vraag meer voor hogere betrouwbaarheid
          </p>
        </div>
      )}
    </div>
  );
};

export default ConfidenceIndicator;