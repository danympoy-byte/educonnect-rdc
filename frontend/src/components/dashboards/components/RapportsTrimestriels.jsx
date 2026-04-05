import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_URL = '';

const RapportsTrimestriels = ({ user }) => {
  const [rapports, setRapports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRapport, setSelectedRapport] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadRapports();
  }, []);

  const loadRapports = async () => {
    try {
            const response = await fetch(`${API_URL}/api/rapports/`, {
        
      });
      
      if (response.ok) {
        const data = await response.json();
        setRapports(data.rapports || []);
      } else {
        toast.error('Erreur lors du chargement des rapports');
      }
    } catch (error) {
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const genererRapportManuel = async (trimestre, annee) => {
    setGenerating(true);
    try {
            const response = await fetch(`${API_URL}/api/rapports/generer?trimestre=${trimestre}&annee=${annee}`, {
        method: 'POST',
        
      });
      
      if (response.ok) {
        toast.success('Rapport généré avec succès');
        loadRapports();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur lors de la génération');
      }
    } catch (error) {
      toast.error('Erreur lors de la génération');
    } finally {
      setGenerating(false);
    }
  };

  const consulterRapport = async (rapportId) => {
    try {
            const response = await fetch(`${API_URL}/api/rapports/${rapportId}`, {
        
      });
      
      if (response.ok) {
        const data = await response.json();
        setSelectedRapport(data);
        setShowDetail(true);
      } else {
        toast.error('Erreur lors du chargement du rapport');
      }
    } catch (error) {
      toast.error('Erreur lors du chargement');
    }
  };

  const prepareChartData = (rapport) => {
    if (!rapport) return [];
    
    return [
      {
        name: 'Administratif',
        créés: rapport.stats_par_type?.administratif?.total || 0,
        validés: rapport.stats_par_type?.administratif?.valides || 0,
        rejetés: rapport.stats_par_type?.administratif?.rejetes || 0
      },
      {
        name: 'RH',
        créés: rapport.stats_par_type?.rh?.total || 0,
        validés: rapport.stats_par_type?.rh?.valides || 0,
        rejetés: rapport.stats_par_type?.rh?.rejetes || 0
      },
      {
        name: 'Financier',
        créés: rapport.stats_par_type?.financier?.total || 0,
        validés: rapport.stats_par_type?.financier?.valides || 0,
        rejetés: rapport.stats_par_type?.financier?.rejetes || 0
      },
      {
        name: 'Pédagogique',
        créés: rapport.stats_par_type?.pedagogique?.total || 0,
        validés: rapport.stats_par_type?.pedagogique?.valides || 0,
        rejetés: rapport.stats_par_type?.pedagogique?.rejetes || 0
      }
    ];
  };

  const getTrimestre = (trimestre, annee) => {
    const labels = {1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4'};
    return `${labels[trimestre]} ${annee}`;
  };

  if (loading) {
    return <div className="text-center py-8">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">📊 Rapports Trimestriels GED</h2>
        {user.role === 'administrateur_technique' && (
          <button
            onClick={() => {
              const trimestre = parseInt(prompt('Trimestre (1-4):'));
              const annee = parseInt(prompt('Année:'));
              if (trimestre && annee) genererRapportManuel(trimestre, annee);
            }}
            disabled={generating}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {generating ? 'Génération...' : '+ Générer Rapport Manuel'}
          </button>
        )}
      </div>

      {/* Liste des rapports */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {rapports.map((rapport) => (
          <div
            key={rapport.id}
            onClick={() => consulterRapport(rapport.id)}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md cursor-pointer transition"
          >
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-indigo-600">
                {getTrimestre(rapport.trimestre, rapport.annee)}
              </h3>
              <span className="text-xs text-gray-500">
                {new Date(rapport.date_generation).toLocaleDateString('fr-FR')}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-xs text-gray-600">Documents créés</p>
                <p className="text-2xl font-bold text-blue-600">{rapport.total_documents_crees}</p>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-xs text-gray-600">Validés</p>
                <p className="text-2xl font-bold text-green-600">{rapport.total_documents_valides}</p>
              </div>
              <div className="bg-yellow-50 p-3 rounded-lg">
                <p className="text-xs text-gray-600">Taux validation</p>
                <p className="text-2xl font-bold text-yellow-600">{rapport.taux_validation}%</p>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg">
                <p className="text-xs text-gray-600">Délai moyen</p>
                <p className="text-2xl font-bold text-purple-600">{rapport.delai_moyen_validation_heures}h</p>
              </div>
            </div>

            <div className="mt-4 text-center">
              <button className="text-indigo-600 hover:text-indigo-800 font-medium text-sm">
                Voir détails →
              </button>
            </div>
          </div>
        ))}
      </div>

      {rapports.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <p className="text-gray-500">Aucun rapport disponible</p>
          <p className="text-sm text-gray-400 mt-2">Les rapports sont générés automatiquement chaque trimestre</p>
        </div>
      )}

      {/* Modal détail */}
      {showDetail && selectedRapport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-3xl font-bold text-gray-900">
                    Rapport {getTrimestre(selectedRapport.trimestre, selectedRapport.annee)}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Période: {new Date(selectedRapport.periode_debut).toLocaleDateString('fr-FR')} → {new Date(selectedRapport.periode_fin).toLocaleDateString('fr-FR')}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowDetail(false);
                    setSelectedRapport(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-3xl">×</span>
                </button>
              </div>

              {/* Statistiques globales */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-600 font-medium">Documents créés</p>
                  <p className="text-3xl font-bold text-blue-700">{selectedRapport.total_documents_crees}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <p className="text-sm text-green-600 font-medium">Validés</p>
                  <p className="text-3xl font-bold text-green-700">{selectedRapport.total_documents_valides}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <p className="text-sm text-red-600 font-medium">Rejetés</p>
                  <p className="text-3xl font-bold text-red-700">{selectedRapport.total_documents_rejetes}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <p className="text-sm text-yellow-600 font-medium">Taux validation</p>
                  <p className="text-3xl font-bold text-yellow-700">{selectedRapport.taux_validation}%</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <p className="text-sm text-purple-600 font-medium">Délai moyen</p>
                  <p className="text-3xl font-bold text-purple-700">{selectedRapport.delai_moyen_validation_heures}h</p>
                </div>
              </div>

              {/* Graphique par type */}
              <div className="mb-8">
                <h4 className="text-xl font-semibold text-gray-900 mb-4">Statistiques par Type de Document</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepareChartData(selectedRapport)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="créés" fill="#3B82F6" />
                    <Bar dataKey="validés" fill="#10B981" />
                    <Bar dataKey="rejetés" fill="#EF4444" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Top Créateurs */}
              {selectedRapport.top_createurs && selectedRapport.top_createurs.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">🏆 Top Créateurs</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedRapport.top_createurs.slice(0, 10).map((user, index) => (
                      <div key={user.user_id} className="flex items-center space-x-3 bg-gray-50 p-3 rounded-lg">
                        <span className={`text-2xl ${index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '📄'}`}>
                          {index < 3 ? (index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉') : `${index + 1}.`}
                        </span>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{user.nom}</p>
                          <p className="text-sm text-gray-500">{user.documents_crees} documents</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Top Validateurs */}
              {selectedRapport.top_validateurs && selectedRapport.top_validateurs.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">✅ Top Validateurs</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedRapport.top_validateurs.slice(0, 10).map((user, index) => (
                      <div key={user.user_id} className="flex items-center space-x-3 bg-green-50 p-3 rounded-lg">
                        <span className="text-2xl">{index + 1}.</span>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{user.nom}</p>
                          <p className="text-sm text-green-600">{user.validations_effectuees} validations</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Documents en retard */}
              {selectedRapport.documents_en_retard > 0 && (
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <h4 className="text-lg font-semibold text-red-800 mb-2">
                    ⚠️ Documents en retard
                  </h4>
                  <p className="text-red-700">
                    {selectedRapport.documents_en_retard} document(s) en attente depuis plus de 48h
                  </p>
                </div>
              )}

              {/* Comparaison trimestre précédent */}
              {selectedRapport.comparaison_trimestre_precedent && Object.keys(selectedRapport.comparaison_trimestre_precedent).length > 0 && (
                <div className="mt-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">📈 Évolution vs Trimestre Précédent</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {selectedRapport.comparaison_trimestre_precedent.documents_crees && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Documents créés</p>
                        <p className={`text-2xl font-bold ${selectedRapport.comparaison_trimestre_precedent.documents_crees.evolution_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {selectedRapport.comparaison_trimestre_precedent.documents_crees.evolution_pct >= 0 ? '+' : ''}
                          {selectedRapport.comparaison_trimestre_precedent.documents_crees.evolution_pct}%
                        </p>
                      </div>
                    )}
                    {selectedRapport.comparaison_trimestre_precedent.taux_validation && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Taux de validation</p>
                        <p className={`text-2xl font-bold ${selectedRapport.comparaison_trimestre_precedent.taux_validation.evolution_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {selectedRapport.comparaison_trimestre_precedent.taux_validation.evolution_pct >= 0 ? '+' : ''}
                          {selectedRapport.comparaison_trimestre_precedent.taux_validation.evolution_pct}%
                        </p>
                      </div>
                    )}
                    {selectedRapport.comparaison_trimestre_precedent.delai_moyen && (
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <p className="text-sm text-gray-600">Délai moyen</p>
                        <p className={`text-2xl font-bold ${selectedRapport.comparaison_trimestre_precedent.delai_moyen.evolution_pct <= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {selectedRapport.comparaison_trimestre_precedent.delai_moyen.evolution_pct >= 0 ? '+' : ''}
                          {selectedRapport.comparaison_trimestre_precedent.delai_moyen.evolution_pct}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RapportsTrimestriels;
