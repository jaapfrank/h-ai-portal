import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, Users, Factory, Calendar, ArrowUp, ArrowDown } from 'lucide-react';

const VisualDashboard = ({ dashboardData, type = 'executive' }) => {
  const [kpis, setKpis] = useState({});
  const [charts, setCharts] = useState({});
  const [summary, setSummary] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    if (dashboardData) {
      setKpis(dashboardData.kpis || {});
      setCharts(dashboardData.charts || {});
      setSummary(dashboardData.summary || '');
      setRecommendations(dashboardData.recommendations || []);
    }
  }, [dashboardData]);

  const formatValue = (value, format) => {
    if (format === 'currency') {
      return `€${value.toLocaleString('nl-NL', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    } else if (format === 'percentage') {
      return `${value.toFixed(1)}%`;
    } else if (format === 'number') {
      return value.toLocaleString('nl-NL');
    }
    return value;
  };

  const getKpiIcon = (icon) => {
    switch (icon) {
      case '💰': return <DollarSign className="h-6 w-6" />;
      case '📈': return <TrendingUp className="h-6 w-6" />;
      case '🏭': return <Factory className="h-6 w-6" />;
      case '👥': return <Users className="h-6 w-6" />;
      case '⏰': return <Calendar className="h-6 w-6" />;
      default: return <BarChart3 className="h-6 w-6" />;
    }
  };

  const getKpiTrendIcon = (value, format) => {
    if (format === 'percentage' && value > 0) {
      return <ArrowUp className="h-4 w-4 text-green-500" />;
    } else if (format === 'percentage' && value < 0) {
      return <ArrowDown className="h-4 w-4 text-red-500" />;
    }
    return null;
  };

  const getDashboardTitle = () => {
    switch (type) {
      case 'executive': return '🏭 HOEFLON EXECUTIVE DASHBOARD';
      case 'production': return '⚙️ HOEFLON PRODUCTION DASHBOARD';
      case 'financial': return '💰 HOEFLON FINANCIAL DASHBOARD';
      default: return '📊 HOEFLON DASHBOARD';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-hoeflon-25 via-hoeflon-50 to-hoeflon-100">
      {/* Header */}
      <div className="hoeflon-gradient text-white p-6 shadow-lg">
        <div className="container mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">{getDashboardTitle()}</h1>
              <p className="text-hoeflon-200 mt-2">
                Real-time business intelligence • Gegenereerd op {new Date().toLocaleString('nl-NL')}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <img 
                src="/hoeflon-logo.svg" 
                alt="Hoeflon Logo" 
                className="h-12 w-auto"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto p-6">
        {/* KPI Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
          {Object.entries(kpis).map(([key, kpi]) => (
            <div key={key} className="bg-white rounded-xl shadow-hoeflon border border-hoeflon-200 p-6 hover:shadow-hoeflon-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-hoeflon-500 to-hoeflon-600 rounded-lg text-white">
                  {getKpiIcon(kpi.icon)}
                </div>
                {getKpiTrendIcon(kpi.value, kpi.format)}
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-hoeflon-600 uppercase tracking-wide">
                  {kpi.label}
                </h3>
                <div className="flex items-end space-x-2">
                  <span className="text-2xl font-bold text-hoeflon-800">
                    {formatValue(kpi.value, kpi.format)}
                  </span>
                  {kpi.amount && (
                    <span className="text-sm text-hoeflon-500">
                      ({formatValue(kpi.amount, 'currency')})
                    </span>
                  )}
                </div>
                
                {kpi.format === 'percentage' && (
                  <div className="w-full bg-hoeflon-100 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        kpi.value > 0 ? 'bg-green-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(Math.abs(kpi.value), 100)}%` }}
                    ></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Charts Section */}
        {Object.keys(charts).length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {Object.entries(charts).map(([key, chart]) => (
              <div key={key} className="bg-white rounded-xl shadow-hoeflon border border-hoeflon-200 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-hoeflon-100 rounded-lg">
                    <BarChart3 className="h-5 w-5 text-hoeflon-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-hoeflon-800">{chart.title}</h3>
                    <p className="text-sm text-hoeflon-500">{chart.data?.length || 0} datapunten</p>
                  </div>
                </div>
                
                {/* Simple Chart Visualization */}
                <div className="space-y-3">
                  {chart.data?.slice(0, 8).map((item, index) => {
                    const keys = Object.keys(item);
                    const labelKey = keys[0];
                    const valueKey = keys.find(k => typeof item[k] === 'number') || keys[1];
                    const maxValue = Math.max(...chart.data.map(d => d[valueKey] || 0));
                    const percentage = ((item[valueKey] || 0) / maxValue) * 100;
                    
                    return (
                      <div key={index} className="space-y-1">
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-hoeflon-700 font-medium">{item[labelKey]}</span>
                          <span className="text-hoeflon-600">
                            {typeof item[valueKey] === 'number' && valueKey.toLowerCase().includes('omzet') 
                              ? formatValue(item[valueKey], 'currency')
                              : item[valueKey]?.toLocaleString?.('nl-NL') || item[valueKey]
                            }
                          </span>
                        </div>
                        <div className="w-full bg-hoeflon-100 rounded-full h-2">
                          <div 
                            className="h-2 bg-gradient-to-r from-hoeflon-500 to-hoeflon-600 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                
                {chart.data?.length > 8 && (
                  <p className="text-xs text-hoeflon-500 mt-4 text-center">
                    ... en {chart.data.length - 8} meer items
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Summary Section */}
          {summary && (
            <div className="bg-white rounded-xl shadow-hoeflon border border-hoeflon-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-hoeflon-800">Samenvatting</h3>
              </div>
              <div className="prose prose-sm max-w-none text-hoeflon-700">
                {summary.split('\n').map((line, index) => (
                  <p key={index} className={line.startsWith('**') ? 'font-semibold text-hoeflon-800' : ''}>
                    {line.replace(/\*\*/g, '')}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations Section */}
          {recommendations.length > 0 && (
            <div className="bg-white rounded-xl shadow-hoeflon border border-hoeflon-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-hoeflon-800">Aanbevelingen</h3>
              </div>
              <div className="space-y-3">
                {recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-hoeflon-25 rounded-lg">
                    <div className="flex-shrink-0 w-6 h-6 bg-hoeflon-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                    <p className="text-sm text-hoeflon-700 leading-relaxed">
                      {rec.replace(/^[🔴🟡🟢💡📊🔗⚠️]\s*/, '')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-sm border border-hoeflon-200">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-hoeflon-600 font-medium">
              Dashboard automatisch gegenereerd door Hoeflon AI
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VisualDashboard;