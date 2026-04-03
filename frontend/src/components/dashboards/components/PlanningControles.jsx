import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import dinacopeService from '../../../services/dinacope.service';
import enseignantsService from '../../../services/enseignants.service';

const PlanningControles = ({ user }) => {
  const [controles, setControles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showExecuteForm, setShowExecuteForm] = useState(false);
  const [selectedControle, setSelectedControle] = useState(null);
  const [enseignants, setEnseignants] = useState([]);
  const [presences, setPresences] = useState({});
  
  const [periode, setPeriode] = useState({
    mois: new Date().getMonth() + 1,
    annee: new Date().getFullYear()
  });

  useEffect(() => {
    loadControles();
  }, [periode]);

  const loadControles = async () => {
    try {
      const data = await dinacopeService.getControles(periode.mois, periode.annee);
      setControles(data.controles || []);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const handlePlanifier = async () => {
    if (!window.confirm(`Planifier les contrôles physiques pour ${getMoisLabel(periode.mois)} ${periode.annee} ?`)) {
      return;
    }

    try {
      const result = await dinacopeService.planifierControles(periode.mois, periode.annee);
      toast.success(result.message);
      loadControles();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la planification');
    }
  };

  const handleOuvrirControle = async (controle) => {
    setSelectedControle(controle);
    
    // Charger les enseignants de l'établissement
    try {
      const data = await enseignantsService.getAll();
      const ensEtab = data.filter(e => e.etablissement_id === controle.etablissement_id);
      setEnseignants(ensEtab);
      
      // Initialiser présences (tous présents par défaut)
      const initPresences = {};
      ensEtab.forEach(e => {
        initPresences[e.id] = true;
      });
      setPresences(initPresences);
      
      setShowExecuteForm(true);
    } catch (error) {
      toast.error('Erreur lors du chargement des enseignants');
    }
  };

  const handleEffectuerControle = async (e) => {
    e.preventDefault();
    
    const presents = Object.keys(presences).filter(id => presences[id] === true);
    const absents = Object.keys(presences).filter(id => presences[id] === false);
    
    try {
      const result = await dinacopeService.effectuerControle(
        selectedControle.id,
        presents,
        absents,
        ''
      );
      toast.success('Contrôle effectué avec succès');
      setShowExecuteForm(false);
      loadControles();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'exécution du contrôle');
    }
  };

  const getMoisLabel = (mois) => {
    const moisLabels = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    return moisLabels[mois];
  };

  const getStatutBadge = (statut) => {
    const badges = {
      'planifie': 'bg-blue-100 text-blue-800',
      'en_cours': 'bg-yellow-100 text-yellow-800',
      'termine': 'bg-green-100 text-green-800',
      'annule': 'bg-gray-100 text-gray-600'
    };
    return badges[statut] || 'bg-gray-100 text-gray-600';
  };

  if (loading) {
    return <div className="text-center py-8">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">📋 Planning Contrôles Physiques Mensuels</h2>
        {user.role === 'agent_dinacope' && (
          <button
            onClick={handlePlanifier}
            disabled={controles.length > 0}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            Planifier Contrôles du Mois
          </button>
        )}
      </div>

      {/* Sélecteur période */}
      <div className="bg-white rounded-xl shadow-sm border p-4">
        <div className="flex items-center space-x-4">
          <label className="font-medium">Période :</label>
          <select
            value={periode.mois}
            onChange={(e) => setPeriode({...periode, mois: parseInt(e.target.value)})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
              <option key={m} value={m}>{getMoisLabel(m)}</option>
            ))}
          </select>
          <select
            value={periode.annee}
            onChange={(e) => setPeriode({...periode, annee: parseInt(e.target.value)})}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            {[2024, 2025, 2026].map(a => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-600">Total Contrôles</p>
          <p className="text-3xl font-bold text-blue-700">{controles.length}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-600">Planifiés</p>
          <p className="text-3xl font-bold text-yellow-700">
            {controles.filter(c => c.statut === 'planifie').length}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-sm text-green-600">Terminés</p>
          <p className="text-3xl font-bold text-green-700">
            {controles.filter(c => c.statut === 'termine').length}
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <p className="text-sm text-purple-600">Taux Complétion</p>
          <p className="text-3xl font-bold text-purple-700">
            {controles.length > 0 ? Math.round((controles.filter(c => c.statut === 'termine').length / controles.length) * 100) : 0}%
          </p>
        </div>
      </div>

      {/* Liste des contrôles */}
      {controles.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Établissement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Province</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Enseignants</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taux Présence</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {controles.map((controle) => (
                  <tr key={controle.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{controle.etablissement_nom}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{controle.province_nom}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(controle.date_controle).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {controle.statut === 'termine' ? (
                        <span>{controle.enseignants_presents} / {controle.enseignants_total}</span>
                      ) : (
                        <span>{controle.enseignants_total}</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {controle.statut === 'termine' && (
                        <span className={`font-medium ${
                          controle.taux_presence >= 90 ? 'text-green-600' :
                          controle.taux_presence >= 75 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {controle.taux_presence}%
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatutBadge(controle.statut)}`}>
                        {controle.statut}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {controle.statut === 'planifie' && user.role === 'agent_dinacope' && (
                        <button
                          onClick={() => handleOuvrirControle(controle)}
                          className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-xs"
                        >
                          Effectuer
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <p className="text-gray-500 text-lg">Aucun contrôle planifié pour cette période</p>
          {user.role === 'agent_dinacope' && (
            <p className="text-sm text-gray-400 mt-2">Cliquez sur "Planifier Contrôles du Mois" pour créer les contrôles</p>
          )}
        </div>
      )}

      {/* Modal Exécution Contrôle */}
      {showExecuteForm && selectedControle && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-2xl font-bold">Effectuer Contrôle Physique</h3>
                <p className="text-sm text-gray-600 mt-1">{selectedControle.etablissement_nom}</p>
              </div>
              <button onClick={() => setShowExecuteForm(false)} className="text-gray-400 hover:text-gray-600 text-3xl">×</button>
            </div>

            <form onSubmit={handleEffectuerControle}>
              <div className="mb-6">
                <p className="font-medium mb-3">Marquez les présences des enseignants :</p>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {enseignants.map((ens) => (
                    <div key={ens.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded">
                      <input
                        type="checkbox"
                        checked={presences[ens.id] === true}
                        onChange={(e) => setPresences({...presences, [ens.id]: e.target.checked})}
                        className="w-5 h-5 text-indigo-600 rounded"
                      />
                      <label className="flex-1">
                        <span className="font-medium">{ens.nom}</span>
                        <span className="text-sm text-gray-500 ml-2">({ens.matricule})</span>
                      </label>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        presences[ens.id] ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {presences[ens.id] ? 'Présent' : 'Absent'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowExecuteForm(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Valider le Contrôle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanningControles;
