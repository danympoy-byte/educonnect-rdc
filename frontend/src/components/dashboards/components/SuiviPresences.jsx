import React, { useState, useEffect } from 'react';
import { Calendar, AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import scolariteService from '@/services/scolarite.service';
import toast from 'react-hot-toast';

const SuiviPresences = ({ etablissements = [], classes = [] }) => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    classe_id: '',
    etablissement_id: '',
    date_debut: '',
    date_fin: ''
  });

  const COLORS = ['#10B981', '#EF4444', '#F59E0B', '#6366F1'];

  const chargerStatistiques = async () => {
    setLoading(true);
    try {
      const data = await scolariteService.obtenirStatistiquesPresence(filters);
      setStats(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des statistiques');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chargerStatistiques();
  }, []);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleSearch = () => {
    chargerStatistiques();
  };

  // Préparer les données pour le graphique en camembert
  const pieData = stats ? [
    { name: 'Présences', value: stats.nb_presences, color: '#10B981' },
    { name: 'Absences justifiées', value: stats.nb_absences_justifiees, color: '#F59E0B' },
    { name: 'Absences injustifiées', value: stats.nb_absences_injustifiees, color: '#EF4444' }
  ] : [];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Calendar className="w-8 h-8 text-indigo-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Suivi des Présences</h2>
            <p className="text-sm text-gray-600">Analyse de l'assiduité des élèves</p>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Établissement
            </label>
            <select
              value={filters.etablissement_id}
              onChange={(e) => handleFilterChange('etablissement_id', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Tous les établissements</option>
              {etablissements.map(etab => (
                <option key={etab.id} value={etab.id}>{etab.nom}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Classe
            </label>
            <select
              value={filters.classe_id}
              onChange={(e) => handleFilterChange('classe_id', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="">Toutes les classes</option>
              {classes.map(classe => (
                <option key={classe.id} value={classe.id}>{classe.nom}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date début
            </label>
            <input
              type="date"
              value={filters.date_debut}
              onChange={(e) => handleFilterChange('date_debut', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date fin
            </label>
            <input
              type="date"
              value={filters.date_fin}
              onChange={(e) => handleFilterChange('date_fin', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Chargement...' : 'Rechercher'}
          </button>
        </div>
      </div>

      {/* Statistiques globales */}
      {stats && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Taux de Présence</p>
                  <p className="text-3xl font-bold text-green-600">{stats.taux_presence}%</p>
                </div>
                <CheckCircle className="w-12 h-12 text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Présences</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.nb_presences}</p>
                </div>
                <TrendingUp className="w-12 h-12 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Absences Justifiées</p>
                  <p className="text-3xl font-bold text-yellow-600">{stats.nb_absences_justifiees}</p>
                </div>
                <AlertTriangle className="w-12 h-12 text-yellow-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Absences Injustifiées</p>
                  <p className="text-3xl font-bold text-red-600">{stats.nb_absences_injustifiees}</p>
                </div>
                <XCircle className="w-12 h-12 text-red-500" />
              </div>
            </div>
          </div>

          {/* Graphiques */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Graphique en camembert */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition Présences/Absences</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Liste des élèves avec fort absentéisme */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Élèves à Risque (Absentéisme {'>'} 20%)
              </h3>
              {stats.eleves_absenteisme_eleve.length > 0 ? (
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {stats.eleves_absenteisme_eleve.map((eleve, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{eleve.nom}</p>
                        <p className="text-sm text-gray-600">
                          {eleve.nb_absences} absences sur {eleve.nb_total_jours} jours
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-red-600">{eleve.taux_absence}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-3" />
                  <p className="text-gray-600">Aucun élève avec un absentéisme élevé</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {!stats && !loading && (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Sélectionnez des filtres et cliquez sur "Rechercher"</p>
        </div>
      )}
    </div>
  );
};

export default SuiviPresences;
