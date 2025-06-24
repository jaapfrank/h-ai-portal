import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  ScatterChart,
  Scatter,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  Download,
  Settings,
  Filter,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Calendar,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  DollarSign,
  Package
} from 'lucide-react';
import api from '../services/api';

/**
 * 🔥 LOLA'S ADVANCED DATA VISUALIZATION & REPORTING SUITE
 * FASE C: Professional Interactive Data Visualization Dashboard
 */

const AdvancedDataVisualization = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [predictiveData, setPredictiveData] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);
  const [filters, setFilters] = useState({
    timeRange: '30d',
    category: 'all',
    chartType: 'combined'
  });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      // Load all dashboard data in parallel
      const [biResponse, perfResponse, predResponse, workflowResponse] = await Promise.allSettled([
        api.get('/advanced_bi/dashboard'),
        api.get('/performance/metrics'),
        api.get('/predictive/market_trends'),
        api.get('/workflows')
      ]);

      if (biResponse.status === 'fulfilled') {
        setDashboardData(biResponse.value.data);
      }
      if (perfResponse.status === 'fulfilled') {
        setPerformanceData(perfResponse.value.data);
      }
      if (predResponse.status === 'fulfilled') {
        setPredictiveData(predResponse.value.data);
      }
      if (workflowResponse.status === 'fulfilled') {
        setWorkflowData(workflowResponse.value.data);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('nl-NL').format(value);
  };

  const getKPICards = () => {
    if (!dashboardData?.dashboard?.kpis) return [];

    const allKPIs = [];
    Object.values(dashboardData.dashboard.kpis).forEach(categoryKPIs => {
      allKPIs.push(...categoryKPIs);
    });

    return allKPIs.slice(0, 8).map((kpi, index) => ({
      title: kpi.name,
      value: kpi.unit === 'EUR' ? formatCurrency(kpi.current_value) : 
             kpi.unit === '%' ? `${kpi.current_value.toFixed(1)}%` :
             formatNumber(kpi.current_value),
      change: kpi.change_percentage,
      trend: kpi.trend,
      icon: getKPIIcon(kpi.category),
      color: getKPIColor(kpi.category),
      status: getKPIStatus(kpi.current_value, kpi.target_value, kpi.trend)
    }));
  };

  const getKPIIcon = (category) => {
    switch (category) {
      case 'financial': return DollarSign;
      case 'production': return Package;
      case 'operational': return Activity;
      case 'customer': return Users;
      default: return Target;
    }
  };

  const getKPIColor = (category) => {
    switch (category) {
      case 'financial': return 'text-green-600 bg-green-50 border-green-200';
      case 'production': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'operational': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'customer': return 'text-purple-600 bg-purple-50 border-purple-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getKPIStatus = (current, target, trend) => {
    const ratio = current / target;
    if (ratio >= 0.95) return 'excellent';
    if (ratio >= 0.80) return 'good';
    if (ratio >= 0.60) return 'warning';
    return 'critical';
  };

  const getPerformanceChartData = () => {
    if (!performanceData?.metrics) return [];

    const chartData = [];
    Object.entries(performanceData.metrics).forEach(([category, metrics]) => {
      metrics.forEach(metric => {
        chartData.push({
          name: metric.metric_name.replace(' Usage', '').replace(' Time', ''),
          category: category,
          current: metric.current_value,
          warning: metric.threshold_warning,
          critical: metric.threshold_critical,
          status: metric.status,
          unit: metric.unit
        });
      });
    });

    return chartData;
  };

  const getRevenueChartData = () => {
    if (!dashboardData?.dashboard?.kpis?.financial) return [];

    // Generate mock monthly data for demonstration
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months.map((month, index) => ({
      month,
      revenue: 2000000 + (Math.sin(index) * 500000) + (Math.random() * 200000),
      target: 2200000,
      machines: 15 + Math.floor(Math.random() * 10),
      customers: 8 + Math.floor(Math.random() * 5)
    }));
  };

  const getPredictiveChartData = () => {
    if (!predictiveData?.market_trends) return [];

    return predictiveData.market_trends.map((trend, index) => ({
      name: trend.trend_name.replace(' Trend', ''),
      strength: trend.strength * 100,
      direction: trend.direction,
      timeframe: trend.timeframe,
      color: trend.direction === 'increasing' ? '#10b981' : 
             trend.direction === 'decreasing' ? '#ef4444' : '#6b7280'
    }));
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {getKPICards().map((kpi, index) => {
          const IconComponent = kpi.icon;
          return (
            <div key={index} className={`p-6 rounded-lg border ${kpi.color}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${kpi.color.split(' ')[1]} ${kpi.color.split(' ')[2]}`}>
                    <IconComponent className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-600">{kpi.title}</p>
                    <p className="text-lg font-bold text-gray-900">{kpi.value}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  {kpi.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : kpi.trend === 'down' ? (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <Minus className="h-4 w-4 text-gray-400" />
                  )}
                  <span className={`text-xs font-medium ${
                    kpi.change > 0 ? 'text-green-600' : 
                    kpi.change < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {kpi.change > 0 ? '+' : ''}{kpi.change.toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="mt-3">
                <div className={`text-xs font-medium ${
                  kpi.status === 'excellent' ? 'text-green-600' :
                  kpi.status === 'good' ? 'text-blue-600' :
                  kpi.status === 'warning' ? 'text-orange-600' : 'text-red-600'
                }`}>
                  {kpi.status === 'excellent' ? '🟢 Excellent' :
                   kpi.status === 'good' ? '🔵 Good' :
                   kpi.status === 'warning' ? '🟡 Warning' : '🔴 Critical'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Revenue & Production Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-hoeflon p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-hoeflon-900">Revenue Trend</h3>
            <div className="flex items-center space-x-2">
              <select 
                className="text-xs border rounded px-2 py-1"
                value={filters.timeRange}
                onChange={(e) => setFilters({...filters, timeRange: e.target.value})}
              >
                <option value="7d">7 dagen</option>
                <option value="30d">30 dagen</option>
                <option value="90d">90 dagen</option>
                <option value="1y">1 jaar</option>
              </select>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={getRevenueChartData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="revenue" orientation="left" tickFormatter={(value) => `€${(value/1000000).toFixed(1)}M`} />
              <YAxis yAxisId="count" orientation="right" />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? formatCurrency(value) : value,
                  name === 'revenue' ? 'Omzet' : 
                  name === 'machines' ? 'Machines' : 'Klanten'
                ]}
              />
              <Legend />
              <Area yAxisId="revenue" type="monotone" dataKey="revenue" fill="#059669" fillOpacity={0.1} stroke="#059669" strokeWidth={2} name="Omzet" />
              <Line yAxisId="revenue" type="monotone" dataKey="target" stroke="#dc2626" strokeDasharray="5 5" name="Target" />
              <Bar yAxisId="count" dataKey="machines" fill="#3b82f6" name="Machines" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="card-hoeflon p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-hoeflon-900">Performance Metrics</h3>
            <RefreshCw className="h-4 w-4 text-hoeflon-600 cursor-pointer" onClick={loadAllData} />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={getPerformanceChartData()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  `${value}${getPerformanceChartData().find(d => d.current === value)?.unit || ''}`,
                  name === 'current' ? 'Huidige waarde' : 
                  name === 'warning' ? 'Warning threshold' : 'Critical threshold'
                ]}
              />
              <Legend />
              <Bar dataKey="current" fill="#3b82f6" name="Huidig" />
              <Bar dataKey="warning" fill="#f59e0b" name="Warning" />
              <Bar dataKey="critical" fill="#ef4444" name="Critical" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderPredictiveTab = () => (
    <div className="space-y-6">
      <div className="card-hoeflon p-6">
        <h3 className="text-lg font-bold text-hoeflon-900 mb-4">Market Trends Analysis</h3>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={getPredictiveChartData()}>
            <PolarGrid />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar
              name="Trend Strength"
              dataKey="strength"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.2}
            />
            <Tooltip 
              formatter={(value, name) => [`${value.toFixed(1)}%`, 'Trend Strength']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Predictive Insights Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {predictiveData?.market_trends?.map((trend, index) => (
          <div key={index} className="card-hoeflon p-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-900">{trend.trend_name}</h4>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                trend.direction === 'increasing' ? 'bg-green-100 text-green-800' :
                trend.direction === 'decreasing' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {trend.direction === 'increasing' ? '📈 Stijgend' :
                 trend.direction === 'decreasing' ? '📉 Dalend' : '➡️ Stabiel'}
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-3">{trend.description}</p>
            <div className="text-xs text-gray-500">
              <strong>Timeframe:</strong> {trend.timeframe}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              <strong>Strength:</strong> {(trend.strength * 100).toFixed(1)}%
            </div>
            {trend.recommendations && trend.recommendations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <h5 className="text-xs font-medium text-gray-700 mb-1">Aanbevelingen:</h5>
                <ul className="text-xs text-gray-600 space-y-1">
                  {trend.recommendations.slice(0, 2).map((rec, i) => (
                    <li key={i} className="flex items-start space-x-1">
                      <span>•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderWorkflowTab = () => (
    <div className="space-y-6">
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-hoeflon-900">Automated Workflows</h3>
          <button className="btn-hoeflon-outline">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </button>
        </div>

        {workflowData?.workflows?.map((workflow, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  workflow.active ? 'bg-green-500' : 'bg-gray-300'
                }`}></div>
                <div>
                  <h4 className="font-medium text-gray-900">{workflow.name}</h4>
                  <p className="text-sm text-gray-600">{workflow.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-xs text-gray-500">Steps: {workflow.steps}</div>
                  <div className="text-xs text-gray-500">Triggers: {workflow.triggers}</div>
                </div>
                <button 
                  className="btn-hoeflon-outline text-xs px-3 py-1"
                  onClick={() => {/* Execute workflow */}}
                >
                  Execute
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="card-hoeflon p-6">
        <div className="flex items-center justify-center space-x-3">
          <RefreshCw className="h-5 w-5 animate-spin text-hoeflon-600" />
          <span className="text-hoeflon-600">Loading Advanced Analytics...</span>
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
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-hoeflon-900">Advanced Data Visualization</h2>
              <p className="text-sm text-hoeflon-600">FASE C: Professional Analytics Dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button onClick={loadAllData} className="btn-hoeflon-outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
            <button className="btn-hoeflon">
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { id: 'overview', label: 'Overview', icon: Eye },
            { id: 'predictive', label: 'Predictive', icon: TrendingUp },
            { id: 'workflows', label: 'Workflows', icon: Activity }
          ].map(tab => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white text-hoeflon-700 shadow'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <IconComponent className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'predictive' && renderPredictiveTab()}
      {activeTab === 'workflows' && renderWorkflowTab()}
    </div>
  );
};

export default AdvancedDataVisualization;