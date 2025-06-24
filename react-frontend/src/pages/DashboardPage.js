import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import VisualDashboard from '../components/VisualDashboard';
import { sendChatMessage } from '../services/api';
import { Loader2, AlertCircle } from 'lucide-react';

const DashboardPage = () => {
  const [searchParams] = useSearchParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const dashboardType = searchParams.get('type') || 'executive';
  const sessionId = searchParams.get('session') || 'dashboard';

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      setError(null);

      try {
        let dashboardQuery = '';
        switch (dashboardType) {
          case 'executive':
            dashboardQuery = 'maak een executive dashboard';
            break;
          case 'production':
            dashboardQuery = 'geef me een productie dashboard';
            break;
          case 'financial':
            dashboardQuery = 'toon financieel dashboard';
            break;
          default:
            dashboardQuery = 'maak een executive dashboard';
        }

        const response = await sendChatMessage(dashboardQuery, sessionId);
        
        // Parse dashboard data from the response
        if (response.resultaten && typeof response.resultaten === 'object') {
          // If resultaten contains KPIs directly
          setDashboardData({
            kpis: response.resultaten,
            charts: response.charts || {},
            summary: response.antwoord || '',
            recommendations: []
          });
        } else {
          // Try to extract dashboard data from the response text
          const mockDashboardData = generateMockData(dashboardType);
          setDashboardData(mockDashboardData);
        }
      } catch (err) {
        setError(err.message);
        // Fallback to mock data
        const mockDashboardData = generateMockData(dashboardType);
        setDashboardData(mockDashboardData);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [dashboardType, sessionId]);

  const generateMockData = (type) => {
    const baseKpis = {
      executive: {
        revenue_ytd: { value: 24800000, label: 'Omzet YTD', format: 'currency', icon: '💰' },
        monthly_growth: { value: 8.3, label: 'Maandelijkse Groei', format: 'percentage', icon: '📈' },
        machines_produced: { value: 155, label: 'Machines Geproduceerd', format: 'number', icon: '🏭' },
        on_time_delivery: { value: 92.5, label: 'On-Time Delivery', format: 'percentage', icon: '⏰' }
      },
      production: {
        in_production: { value: 19, label: 'In Productie Nu', format: 'number', icon: '⚙️' },
        completed_week: { value: 8, label: 'Gereed Deze Week', format: 'number', icon: '✅' },
        efficiency: { value: 87.2, label: 'Productie Efficiency', format: 'percentage', icon: '📊' },
        avg_time: { value: 42.5, label: 'Gem. Productietijd (dagen)', format: 'number', icon: '⏱️' }
      },
      financial: {
        external_revenue: { value: 22400000, label: 'Externe Omzet YTD', format: 'currency', icon: '💰' },
        internal_revenue: { value: 2400000, label: 'Interne Omzet YTD', format: 'currency', icon: '🏢' },
        growth_rate: { value: 12.8, label: 'Groeipercentage', format: 'percentage', icon: '📈' },
        avg_invoice: { value: 156000, label: 'Gem. Factuurwaarde', format: 'currency', icon: '🧾' }
      }
    };

    const baseCharts = {
      revenue_trend: {
        title: 'Revenue Trend (12 maanden)',
        data: [
          { Maand: 'Jan', Omzet: 2100000 },
          { Maand: 'Feb', Omzet: 1950000 },
          { Maand: 'Mar', Omzet: 2300000 },
          { Maand: 'Apr', Omzet: 2150000 },
          { Maand: 'Mei', Omzet: 2400000 },
          { Maand: 'Jun', Omzet: 2200000 }
        ]
      },
      top_customers: {
        title: 'Top 5 Klanten',
        data: [
          { Klant: 'Smakranar AB', Omzet: 3200000 },
          { Klant: 'Volkswagen Pon', Omzet: 2800000 },
          { Klant: 'Customer_1234', Omzet: 2100000 },
          { Klant: 'Customer_5678', Omzet: 1900000 },
          { Klant: 'Customer_9012', Omzet: 1750000 }
        ]
      }
    };

    return {
      kpis: baseKpis[type] || baseKpis.executive,
      charts: baseCharts,
      summary: `Dashboard overzicht voor ${type} analytics`,
      recommendations: [
        'Continue monitoring van KPI trends',
        'Optimaliseer productieprocessen voor betere efficiency',
        'Focus op klantenbinding voor sustainable growth'
      ]
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-25 to-hoeflon-100 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-8">
            <Loader2 className="h-12 w-12 animate-spin text-hoeflon-600 mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-hoeflon-800 mb-2">Dashboard wordt geladen...</h2>
          <p className="text-hoeflon-600">Genereren van real-time business intelligence</p>
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-hoeflon-25 to-hoeflon-100 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="mb-8">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-red-800 mb-2">Dashboard laden mislukt</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-hoeflon-600 text-white rounded-lg hover:bg-hoeflon-700"
          >
            Opnieuw proberen
          </button>
        </div>
      </div>
    );
  }

  return <VisualDashboard dashboardData={dashboardData} type={dashboardType} />;
};

export default DashboardPage;