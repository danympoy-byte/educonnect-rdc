import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import documentsService from '../../../services/documents.service';

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444'];

const DocumentStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await documentsService.getStats();
      setStats(data);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Chargement des statistiques...</div>;
  }

  if (!stats) {
    return null;
  }

  const cardsData = [
    {
      titre: 'En attente',
      valeur: stats.en_attente,
      icon: '⏳',
      color: 'bg-yellow-100 text-yellow-800',
      iconBg: 'bg-yellow-100'
    },
    {
      titre: 'Mes documents',
      valeur: stats.mes_documents,
      icon: '📄',
      color: 'bg-blue-100 text-blue-800',
      iconBg: 'bg-blue-100'
    },
    {
      titre: 'Traités',
      valeur: stats.traites,
      icon: '✓',
      color: 'bg-green-100 text-green-800',
      iconBg: 'bg-green-100'
    },
    {
      titre: 'En retard',
      valeur: stats.en_retard,
      icon: '⚠️',
      color: 'bg-red-100 text-red-800',
      iconBg: 'bg-red-100'
    }
  ];

  const pieData = [
    { name: 'En attente', value: stats.en_attente },
    { name: 'Traités', value: stats.traites },
    { name: 'En retard', value: stats.en_retard }
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Cartes statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cardsData.map((card, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{card.titre}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {card.valeur}
                </p>
              </div>
              <div className={`w-12 h-12 ${card.iconBg} rounded-full flex items-center justify-center`}>
                <span className="text-2xl">{card.icon}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Délai moyen */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Délai moyen de traitement</h3>
            <p className="text-4xl font-bold text-indigo-600 mt-2">
              {stats.delai_moyen_heures > 0 
                ? `${stats.delai_moyen_heures.toFixed(1)} heures`
                : 'Aucune donnée'
              }
            </p>
            {stats.delai_moyen_heures > 0 && (
              <p className="text-sm text-gray-500 mt-2">
                Soit environ {Math.round(stats.delai_moyen_heures / 24)} jour(s)
              </p>
            )}
          </div>
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
            <span className="text-3xl">⏱️</span>
          </div>
        </div>
      </div>

      {/* Graphique répartition */}
      {pieData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition des documents</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default DocumentStats;
