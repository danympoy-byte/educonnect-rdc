import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#D946EF'];

const TRANCHE_LABELS = {
  '0': '0-4',
  '5': '5-7',
  '8': '8-9',
  '10': '10-11',
  '12': '12-13',
  '14': '14-15',
  '16': '16-20'
};

const Evaluations = () => {
  const [statsNotes, setStatsNotes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedView, setSelectedView] = useState('overview');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await api.get('/stats/notes');
      setStatsNotes(res.data);
    } catch (err) {
      console.error('Erreur chargement stats notes:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12" data-testid="evaluations-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const matieresData = statsNotes?.par_matiere || [];
  const distributionData = (statsNotes?.distribution || []).map(d => ({
    ...d,
    label: TRANCHE_LABELS[d.tranche] || d.tranche
  }));
  const trimestresData = statsNotes?.par_trimestre || [];

  // Radar chart data
  const radarData = matieresData.map(m => ({
    matiere: m.matiere.length > 10 ? m.matiere.substring(0, 10) + '.' : m.matiere,
    moyenne: m.moyenne,
    fullMark: 20
  }));

  // Calcul de la moyenne générale
  const moyenneGenerale = matieresData.length > 0
    ? (matieresData.reduce((acc, m) => acc + m.moyenne, 0) / matieresData.length).toFixed(2)
    : 0;

  const totalNotes = matieresData.reduce((acc, m) => acc + m.count, 0);

  return (
    <div className="space-y-6" data-testid="evaluations-page">
      {/* Bannière d'avertissement */}
      <div className="bg-amber-50 border-l-4 border-amber-500 rounded-r-xl p-4" data-testid="disclaimer-banner">
        <div className="flex items-start gap-3">
          <svg className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-amber-800">Information importante</h3>
            <p className="text-sm text-amber-700 mt-1">
              Les donnees presentees ici sont fournies a titre indicatif uniquement. Seul le bulletin officiel delivre par l'etablissement fait foi en matiere de resultats scolaires.
            </p>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Evaluations et Notes</h2>
          <p className="text-sm text-gray-500 mt-1">
            Annee scolaire 2025-2026 | {totalNotes.toLocaleString()} notes enregistrees
          </p>
        </div>
        <div className="flex gap-2">
          {[
            { key: 'overview', label: 'Vue Generale' },
            { key: 'matieres', label: 'Par Matiere' },
            { key: 'distribution', label: 'Distribution' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setSelectedView(tab.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                selectedView === tab.key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              data-testid={`tab-${tab.key}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-xl p-5 text-white" data-testid="stat-moyenne-gen">
          <p className="text-indigo-200 text-sm font-medium">Moyenne Generale</p>
          <p className="text-3xl font-bold mt-1">{moyenneGenerale}/20</p>
        </div>
        <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl p-5 text-white" data-testid="stat-total-notes">
          <p className="text-emerald-200 text-sm font-medium">Total Notes</p>
          <p className="text-3xl font-bold mt-1">{totalNotes.toLocaleString()}</p>
        </div>
        <div className="bg-gradient-to-br from-amber-600 to-amber-700 rounded-xl p-5 text-white" data-testid="stat-nb-matieres">
          <p className="text-amber-200 text-sm font-medium">Matieres</p>
          <p className="text-3xl font-bold mt-1">{matieresData.length}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl p-5 text-white" data-testid="stat-nb-trimestres">
          <p className="text-purple-200 text-sm font-medium">Trimestres</p>
          <p className="text-3xl font-bold mt-1">{trimestresData.length}</p>
        </div>
      </div>

      {/* Vue Generale */}
      {selectedView === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Radar Chart */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="radar-chart">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Profil moyen par matiere</h3>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="matiere" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis angle={90} domain={[0, 20]} tick={{ fontSize: 10 }} />
                <Radar name="Moyenne" dataKey="moyenne" stroke="#4F46E5" fill="#4F46E5" fillOpacity={0.3} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Moyennes par trimestre */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="trimestre-chart">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Moyennes par trimestre</h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={trimestresData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="trimestre" />
                <YAxis domain={[0, 20]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="moyenne" fill="#4F46E5" name="Moyenne" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Distribution des notes */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 lg:col-span-2" data-testid="distribution-overview">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Distribution des notes</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" name="Nombre de notes" radius={[4, 4, 0, 0]}>
                  {distributionData.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Vue Par Matiere */}
      {selectedView === 'matieres' && (
        <div className="space-y-6">
          {/* Bar chart horizontal des moyennes */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="matieres-chart">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Moyenne par matiere</h3>
            <ResponsiveContainer width="100%" height={Math.max(400, matieresData.length * 40)}>
              <BarChart data={matieresData} layout="vertical" margin={{ left: 120 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 20]} />
                <YAxis dataKey="matiere" type="category" tick={{ fontSize: 12 }} width={120} />
                <Tooltip />
                <Legend />
                <Bar dataKey="moyenne" fill="#4F46E5" name="Moyenne" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Tableau détaillé */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" data-testid="matieres-table">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h3 className="text-base font-semibold text-gray-900">Detail par matiere</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matiere</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Moyenne</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nb Notes</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appreciation</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {matieresData.map((m, idx) => {
                    const appreciation = m.moyenne >= 16 ? 'Excellent' :
                      m.moyenne >= 14 ? 'Tres Bien' :
                      m.moyenne >= 12 ? 'Bien' :
                      m.moyenne >= 10 ? 'Assez Bien' :
                      m.moyenne >= 8 ? 'Passable' : 'Insuffisant';
                    const color = m.moyenne >= 14 ? 'text-emerald-600' :
                      m.moyenne >= 10 ? 'text-blue-600' :
                      m.moyenne >= 8 ? 'text-amber-600' : 'text-red-600';
                    return (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-3 text-sm font-medium text-gray-900">{m.matiere}</td>
                        <td className={`px-6 py-3 text-sm font-bold ${color}`}>{m.moyenne}/20</td>
                        <td className="px-6 py-3 text-sm text-gray-600">{m.min}/20</td>
                        <td className="px-6 py-3 text-sm text-gray-600">{m.max}/20</td>
                        <td className="px-6 py-3 text-sm text-gray-600">{m.count.toLocaleString()}</td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            m.moyenne >= 14 ? 'bg-emerald-100 text-emerald-700' :
                            m.moyenne >= 10 ? 'bg-blue-100 text-blue-700' :
                            m.moyenne >= 8 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {appreciation}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Vue Distribution */}
      {selectedView === 'distribution' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie chart distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="distribution-pie">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Repartition des notes</h3>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={(entry) => `${entry.label}: ${entry.count}`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend formatter={(value, entry) => {
                  const item = distributionData[entry.index || 0];
                  return item?.label || value;
                }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Barres de distribution */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="distribution-bars">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Distribution detaillee</h3>
            <div className="space-y-3">
              {distributionData.map((d, idx) => {
                const maxCount = Math.max(...distributionData.map(x => x.count));
                const pct = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
                const totalPct = totalNotes > 0 ? ((d.count / totalNotes) * 100).toFixed(1) : 0;
                return (
                  <div key={idx}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">{d.label}/20</span>
                      <span className="text-sm text-gray-500">{d.count.toLocaleString()} ({totalPct}%)</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-3">
                      <div
                        className="h-3 rounded-full transition-all"
                        style={{ width: `${pct}%`, backgroundColor: COLORS[idx % COLORS.length] }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Legende */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 lg:col-span-2" data-testid="appreciation-legend">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Echelle d'appreciation</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {[
                { label: 'Excellent', range: '16-20', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
                { label: 'Tres Bien', range: '14-15', color: 'bg-teal-100 text-teal-700 border-teal-200' },
                { label: 'Bien', range: '12-13', color: 'bg-blue-100 text-blue-700 border-blue-200' },
                { label: 'Assez Bien', range: '10-11', color: 'bg-sky-100 text-sky-700 border-sky-200' },
                { label: 'Passable', range: '8-9', color: 'bg-amber-100 text-amber-700 border-amber-200' },
                { label: 'Insuffisant', range: '0-7', color: 'bg-red-100 text-red-700 border-red-200' }
              ].map(a => (
                <div key={a.label} className={`rounded-lg p-3 border ${a.color} text-center`}>
                  <p className="font-semibold text-sm">{a.label}</p>
                  <p className="text-xs mt-0.5">{a.range}/20</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Evaluations;
