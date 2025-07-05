import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import StatusPanel from './components/StatusPanel';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import MLStatsPage from './pages/MLStatsPage';
import MLReportsPage from './pages/MLReportsPage';
import EnterpriseFeatures from './components/EnterpriseFeatures';
import AdvancedDataVisualization from './components/AdvancedDataVisualization';
import DocumentUpload from './components/DocumentUpload';
import { checkSystemStatus } from './services/api';

function App() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const status = await checkSystemStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to load system status:', error);
        setSystemStatus(null);
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    
    // Refresh status every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-25 via-hoeflon-50 to-hoeflon-100 flex items-center justify-center">
        <div className="text-center">
          {/* Hoeflon Logo with loading animation */}
          <div className="relative mb-8">
            <div className="w-24 h-24 bg-white rounded-2xl shadow-hoeflon-lg flex items-center justify-center mx-auto">
              <img 
                src="/hoeflon-logo.svg" 
                alt="Hoeflon Logo" 
                className="h-12 w-auto"
                style={{ maxWidth: '100px' }}
              />
            </div>
            {/* Rotating ring */}
            <div className="absolute inset-0 rounded-2xl border-4 border-transparent border-t-hoeflon-600 animate-spin"></div>
            {/* Pulsing ring */}
            <div className="absolute inset-0 rounded-2xl border-4 border-hoeflon-orange/30 animate-pulse"></div>
          </div>
          
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-hoeflon-800">Hoeflon AI</h2>
            <p className="text-hoeflon-600 font-medium">Intelligent ERP Assistant</p>
            <p className="text-sm text-hoeflon-500">Verbinding maken met Ridder ERP...</p>
          </div>
          
          {/* Loading dots */}
          <div className="flex justify-center space-x-2 mt-6">
            <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Dashboard Route - Full screen */}
        <Route path="/dashboard" element={<DashboardPage />} />
        
        {/* ML Stats Route - Full screen */}
        <Route path="/ml_stats" element={<MLStatsPage />} />
        
        {/* ML Reports Route - Full screen */}
        <Route path="/ml_reports" element={<MLReportsPage />} />
        
        {/* Enterprise Features Route - Full screen */}
        <Route path="/enterprise" element={
          <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
            <Header />
            <main className="container mx-auto px-4 py-6 max-w-7xl">
              <EnterpriseFeatures />
            </main>
          </div>
        } />
        
        {/* Advanced Data Visualization Route - Full screen */}
        <Route path="/analytics" element={
          <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
            <Header />
            <main className="container mx-auto px-4 py-6 max-w-7xl">
              <AdvancedDataVisualization />
            </main>
          </div>
        } />
        
        {/* Document Upload Route - Full screen */}
        <Route path="/documents" element={
          <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
            <Header />
            <main className="container mx-auto px-4 py-6 max-w-7xl">
              <DocumentUpload />
            </main>
          </div>
        } />
        
        {/* Main Chat Interface */}
        <Route path="/" element={
          <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
            <Header />
            
            <main className="container mx-auto px-4 py-6 max-w-6xl">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Chat Interface - Takes up most space */}
                <div className="lg:col-span-3">
                  <ChatInterface systemStatus={systemStatus} />
                </div>
                
                {/* Status Panel - Sidebar */}
                <div className="lg:col-span-1">
                  <StatusPanel 
                    status={systemStatus} 
                    onRefresh={() => window.location.reload()} 
                  />
                </div>
              </div>
            </main>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;