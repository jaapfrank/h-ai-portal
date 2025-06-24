import React, { useState } from 'react';
import { Bot, Cpu, Activity, Zap, BarChart3, Brain, Database, Monitor, Shield, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const username = process.env.USERNAME || 'gebruiker';
  const [showMLMenu, setShowMLMenu] = useState(false);
  const navigate = useNavigate();

  const handleMLReports = () => {
    window.open('/ml_reports', '_blank');
  };

  const handleMLStats = () => {
    window.open('/ml_stats', '_blank');
  };

  const handleDashboards = () => {
    window.open('/dashboard?type=executive', '_blank');
  };

  const handleEnterpriseFeatures = () => {
    navigate('/enterprise');
  };

  const handleAdvancedAnalytics = () => {
    navigate('/analytics');
  };

  return (
    <header className="bg-hoeflon-900 shadow-xl border-b border-hoeflon-800">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and title */}
          <div className="flex items-center space-x-6">
            {/* Official Hoeflon Logo */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                {/* Official Hoeflon Logo */}
                <div className="flex items-center">
                  <img 
                    src="/hoeflon-logo.png" 
                    alt="Hoeflon Logo" 
                    className="h-8 w-auto"
                    style={{ maxWidth: '180px' }}
                  />
                </div>
                {/* AI indicator overlay */}
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-hoeflon-red rounded-full flex items-center justify-center shadow-lg border-2 border-hoeflon-900">
                  <Bot className="h-3 w-3 text-white" />
                </div>
              </div>
              
              {/* AI Extension Branding */}
              <div className="flex flex-col">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold text-hoeflon-red">AI</span>
                  <span className="text-sm text-hoeflon-300 font-medium">Assistant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Activity className="h-3 w-3 text-hoeflon-red animate-pulse" />
                  <p className="text-xs text-hoeflon-400 font-medium">
                    Intelligent ERP Analytics
                  </p>
                </div>
              </div>
            </div>
            
            {/* Tagline */}
            <div className="hidden md:flex items-center space-x-2 ml-6 pl-6 border-l border-hoeflon-700">
              <Zap className="h-4 w-4 text-hoeflon-red" />
              <span className="text-sm text-hoeflon-400 font-medium italic">
                "Smart and Powerful"
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {/* ML & Analytics Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowMLMenu(!showMLMenu)}
                className="flex items-center space-x-2 px-4 py-2 bg-hoeflon-800/50 hover:bg-hoeflon-700/70 text-hoeflon-100 rounded-lg border border-hoeflon-600 transition-colors"
              >
                <Brain className="h-4 w-4" />
                <span className="text-sm font-medium">ML & Analytics</span>
              </button>
              
              {showMLMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <button
                      onClick={handleMLStats}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-hoeflon-50"
                    >
                      <Cpu className="h-4 w-4 mr-2" />
                      ML Statistieken
                    </button>
                    <button
                      onClick={handleMLReports}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-hoeflon-50"
                    >
                      <BarChart3 className="h-4 w-4 mr-2" />
                      ML Rapporten
                    </button>
                    <button
                      onClick={handleDashboards}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-hoeflon-50"
                    >
                      <Monitor className="h-4 w-4 mr-2" />
                      Executive Dashboard
                    </button>
                    <button
                      onClick={handleEnterpriseFeatures}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-hoeflon-50"
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      Enterprise Features
                    </button>
                    <button
                      onClick={handleAdvancedAnalytics}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-hoeflon-50"
                    >
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Advanced Analytics
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Enterprise Features Button */}
            <button
              onClick={handleEnterpriseFeatures}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-hoeflon-600 to-hoeflon-700 hover:from-hoeflon-700 hover:to-hoeflon-800 text-white rounded-lg transition-all duration-200 border border-hoeflon-500 shadow-lg"
            >
              <Shield className="h-4 w-4" />
              <span className="text-sm font-medium">Enterprise</span>
            </button>

            {/* Direct Dashboard Button */}
            <button
              onClick={handleDashboards}
              className="flex items-center space-x-2 px-4 py-2 bg-hoeflon-orange hover:bg-orange-600 text-white rounded-lg transition-colors"
            >
              <Database className="h-4 w-4" />
              <span className="text-sm font-medium">Dashboard</span>
            </button>
          </div>

          {/* User info and status */}
          <div className="flex items-center space-x-4">
            {/* System Status */}
            <div className="hidden lg:flex items-center space-x-2 px-3 py-2 bg-hoeflon-800/50 rounded-lg border border-hoeflon-600">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-hoeflon-200 font-medium">System Online</span>
            </div>
            
            {/* User Profile */}
            <div className="flex items-center space-x-3">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-medium text-hoeflon-300 uppercase tracking-wider">
                  Ingelogd als
                </p>
                <p className="text-sm text-white font-semibold">
                  {username}
                </p>
              </div>
              <div className="relative">
                <div className="h-10 w-10 bg-hoeflon-100 rounded-xl flex items-center justify-center shadow-md border-2 border-hoeflon-500/20">
                  <span className="text-hoeflon-600 font-bold text-sm">
                    {username.charAt(0).toUpperCase()}
                  </span>
                </div>
                {/* Online indicator */}
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-hoeflon-700"></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Optional: Secondary nav or breadcrumbs */}
        <div className="mt-3 pt-3 border-t border-hoeflon-600/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-xs text-hoeflon-300">
              <span className="flex items-center space-x-1">
                <span>🏭</span>
                <span>ERP Dashboard</span>
              </span>
              <span className="text-hoeflon-500">→</span>
              <span className="flex items-center space-x-1">
                <span>💬</span>
                <span>AI Assistant</span>
              </span>
              <span className="text-hoeflon-500">→</span>
              <span className="text-hoeflon-orange font-medium">Chat Interface</span>
            </div>
            
            <div className="flex items-center space-x-2 text-xs text-hoeflon-400">
              <span>Ridder ERP Connected</span>
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;