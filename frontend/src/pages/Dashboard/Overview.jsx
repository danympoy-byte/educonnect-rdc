import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';
import { useDashboardData } from '../../hooks/useDashboardData';
import StatsCards from '../../components/dashboards/components/StatsCards';
import StatsCharts from '../../components/dashboards/components/StatsCharts';


const Overview = () => {
  const { stats, statsSexe, loading } = useDashboardData();
  const [evolutionData, setEvolutionData] = useState(null);

  useEffect(() => {
    const fetchEvolution = async () => {
      try {
        const res = await api.get('/stats/evolution');
        setEvolutionData(res.data);
      } catch (err) {
        console.error('Evolution stats error:', err);
      }
    };
    fetchEvolution();
  }, []);

  const handleExportStats = async () => {
    try {
      const response = await api.get(`/exports/dashboard/stats`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `educonnect_stats_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Export Excel telecharge avec succes !');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Tableau de bord</h2>
        <button
          onClick={handleExportStats}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
          data-testid="export-stats-btn"
        >
          <span>Exporter Excel</span>
        </button>
      </div>

      <StatsCards stats={stats} />
      <StatsCharts stats={stats} statsSexe={statsSexe} evolutionData={evolutionData} />
    </div>
  );
};

export default Overview;
