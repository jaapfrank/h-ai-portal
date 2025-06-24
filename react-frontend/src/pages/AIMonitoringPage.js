import React from 'react';
import AIMonitoringPanel from '../components/AIMonitoringPanel';
import Header from '../components/Header';

const AIMonitoringPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-hoeflon-50 to-hoeflon-100">
      <Header />
      
      <main className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-hoeflon-800 mb-2">
            AI & ML Monitoring
          </h1>
          <p className="text-hoeflon-600">
            Real-time inzicht in AI verwerking, machine learning modellen en conversational memory
          </p>
        </div>
        
        <AIMonitoringPanel />
      </main>
    </div>
  );
};

export default AIMonitoringPage;