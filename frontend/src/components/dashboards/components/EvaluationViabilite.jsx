import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import dinacopeService from '../../../services/dinacope.service';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const EvaluationViabilite = ({ user }) => {
  const [evaluations, setEvaluations] = useState([]);
  const [etablissements, setEtablissements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [formData, setFormData] = useState({
    etablissement_id: '',
    annee_scolaire: '2024-2025',
    nombre_eleves: 0,
    nombre_enseignants: 0,
    nombre_classes: 0,
    ratio_eleves_enseignants: 0,
    salles_classes_fonctionnelles: 0,
    salles_classes_necessaires: 0,
    latrines_fonctionnelles: 0,
    point_eau_disponible: false,
    electricite_disponible: false,
    cloture_perimetre: false,
    manuels_scolaires_suffisants: false,
    materiel_didactique_adequat: false,
    bibliotheque_presente: false,
    frais_scolaires_conformes: true,
    subvention_etat_recue: false,
    budget_annuel_adequat: false
  });

  // Calculer les statistiques pour le graphique
  const getViabilityStats = () => {
    if (evaluations.length === 0) {
      // Données d'exemple avec parts égales
      return [
        { name: 'Excellent (90-100)', value: 20, color: '#10B981' },
        { name: 'Bon (80-89)', value: 20, color: '#3B82F6' },
        { name: 'Moyen (70-79)', value: 20, color: '#FBBF24' },
        { name: 'Faible (60-69)', value: 20, color: '#F97316' },
        { name: 'Critique (<60)', value: 20, color: '#EF4444' }
      ];
    }

    const stats = {
      excellent: 0,
      bon: 0,
      moyen: 0,
      faible: 0,
      critique: 0
    };

    evaluations.forEach(evaluation => {
      const niveau = evaluation.niveau_viabilite?.toLowerCase() || '';
      if (niveau.includes('excellent')) stats.excellent++;
      else if (niveau.includes('bon')) stats.bon++;
      else if (niveau.includes('moyen')) stats.moyen++;
      else if (niveau.includes('faible')) stats.faible++;
      else if (niveau.includes('critique')) stats.critique++;
    });

    return [
      { name: 'Excellent (90-100)', value: stats.excellent, color: '#10B981' },
      { name: 'Bon (80-89)', value: stats.bon, color: '#3B82F6' },
      { name: 'Moyen (70-79)', value: stats.moyen, color: '#FBBF24' },
      { name: 'Faible (60-69)', value: stats.faible, color: '#F97316' },
      { name: 'Critique (<60)', value: stats.critique, color: '#EF4444' }
    ];
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const evalData = await dinacopeService.getEvaluationsViabilite();
      setEvaluations(evalData.evaluations || []);
      
      // Charger les établissements via l'API service
      try {
        const response = await fetch(`${API_URL}/api/etablissements`, { 
          credentials: 'include' // Utiliser les cookies httpOnly
        });
        if (response.ok) {
          const etabData = await response.json();
          setEtablissements(etabData || []);
        }
      } catch (etabError) {
        console.log('Impossible de charger les établissements');
      }
    } catch (error) {
      console.log('Erreur chargement données viabilité:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Calculer ratio
    const ratio = formData.nombre_enseignants > 0 
      ? Math.round(formData.nombre_eleves / formData.nombre_enseignants) 
      : 0;

    try {
      await dinacopeService.evaluerViabilite(
        formData.etablissement_id,
        formData.annee_scolaire,
        { ...formData, ratio_eleves_enseignants: ratio }
      );
      toast.success('Évaluation créée avec succès');
      setShowForm(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur');
    }
  };

  const getNiveauBadge = (niveau) => {
    const badges = {
      'excellent': 'bg-green-100 text-green-800',
      'bon': 'bg-blue-100 text-blue-800',
      'moyen': 'bg-yellow-100 text-yellow-800',
      'faible': 'bg-orange-100 text-orange-800',
      'critique': 'bg-red-100 text-red-800'
    };
    return badges[niveau] || 'bg-gray-100 text-gray-600';
  };

  if (loading) return <div className="text-center py-8">Chargement...</div>;

  const viabilityData = getViabilityStats();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">🏫 Viabilité des Établissements</h2>
        <div className="flex gap-3">
          <button
            onClick={() => setShowGuide(true)}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 flex items-center gap-2"
          >
            ℹ️ Guide d'Évaluation
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            + Nouvelle Évaluation
          </button>
        </div>
      </div>

      {/* Graphique en Camembert - Répartition des Niveaux */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📊 Répartition des Niveaux de Viabilité</h3>
        <div className="flex flex-col md:flex-row items-center justify-center gap-8">
          {/* Graphique */}
          <div className="w-full md:w-1/2" style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={viabilityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) => 
                    value > 0 ? `${(percent * 100).toFixed(0)}%` : ''
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {viabilityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value) => [`${value} établissement(s)`, 'Nombre']}
                />
                <Legend 
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value, entry) => (
                    <span className="text-sm">
                      {entry.payload.name}: <strong>{entry.payload.value}</strong>
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Légende détaillée */}
          <div className="w-full md:w-1/2 space-y-3">
            {viabilityData.map((item) => (
              <div 
                key={item.name}
                className="flex items-center justify-between p-3 rounded-lg border"
                style={{ borderLeftWidth: '4px', borderLeftColor: item.color }}
              >
                <div className="flex items-center gap-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="font-medium text-gray-700">{item.name}</span>
                </div>
                <span className="text-lg font-bold" style={{ color: item.color }}>
                  {item.value}
                </span>
              </div>
            ))}
            
            {evaluations.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  <strong>Total : </strong>
                  {evaluations.length} établissement(s) évalué(s)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Liste */}
      <div className="space-y-3">
        {evaluations.map((evaluation) => (
          <div key={evaluation.id} className="bg-white border rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <p className="font-semibold text-lg">{evaluation.etablissement_nom}</p>
                <p className="text-sm text-gray-600">{evaluation.province_nom} - {evaluation.annee_scolaire}</p>
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getNiveauBadge(evaluation.niveau_viabilite)}`}>
                  {evaluation.niveau_viabilite}
                </span>
                <p className="text-3xl font-bold text-indigo-600 mt-2">{evaluation.score_total}/100</p>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-3 mb-3">
              <div className="bg-blue-50 p-2 rounded">
                <p className="text-xs text-gray-600">Effectifs</p>
                <p className="font-bold text-blue-700">{evaluation.score_effectifs}/25</p>
              </div>
              <div className="bg-green-50 p-2 rounded">
                <p className="text-xs text-gray-600">Infrastructure</p>
                <p className="font-bold text-green-700">{evaluation.score_infrastructures}/25</p>
              </div>
              <div className="bg-yellow-50 p-2 rounded">
                <p className="text-xs text-gray-600">Pédagogique</p>
                <p className="font-bold text-yellow-700">{evaluation.score_pedagogique}/25</p>
              </div>
              <div className="bg-purple-50 p-2 rounded">
                <p className="text-xs text-gray-600">Financier</p>
                <p className="font-bold text-purple-700">{evaluation.score_financier}/25</p>
              </div>
            </div>

            {evaluation.recommandations && evaluation.recommandations.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <p className="text-sm font-medium text-yellow-800 mb-1">📋 Recommandations :</p>
                <ul className="text-sm text-yellow-700 list-disc list-inside">
                  {evaluation.recommandations.slice(0, 3).map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Modal Guide d'Évaluation */}
      {showGuide && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto p-8">
            <div className="flex justify-between items-start mb-6">
              <h3 className="text-3xl font-bold text-gray-900">📖 Guide d'Évaluation de la Viabilité</h3>
              <button
                onClick={() => setShowGuide(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ✕
              </button>
            </div>

            {/* Objectif */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h4 className="text-xl font-bold text-blue-900 mb-3">🎯 Objectif</h4>
              <p className="text-blue-800">
                Identifier les établissements performants, ceux nécessitant un soutien, et ceux en situation critique nécessitant une fermeture.
              </p>
            </div>

            {/* Système de Notation */}
            <div className="mb-8">
              <h4 className="text-2xl font-bold text-gray-900 mb-4">📊 Système de Notation (100 Points)</h4>
              
              {/* Pilier 1 */}
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-5 mb-4">
                <h5 className="text-lg font-bold text-blue-900 mb-2">1️⃣ Score Effectifs (25 points)</h5>
                <p className="text-blue-800 mb-2"><strong>Critère :</strong> Ratio élèves/enseignants</p>
                <p className="text-blue-800 mb-2"><strong>Idéal :</strong> 40-50 élèves par enseignant = 25 pts</p>
                <div className="bg-white rounded p-3 text-sm">
                  <p className="text-green-700 font-medium">✅ Exemple : 450 élèves, 10 enseignants = ratio 45 → <strong>25 points</strong></p>
                </div>
              </div>

              {/* Pilier 2 */}
              <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-5 mb-4">
                <h5 className="text-lg font-bold text-green-900 mb-3">2️⃣ Score Infrastructures (25 points)</h5>
                <ul className="space-y-2 text-green-800">
                  <li className="flex justify-between"><span>• Salles de classe fonctionnelles</span><strong>10 pts</strong></li>
                  <li className="flex justify-between"><span>• Latrines (≥ 4)</span><strong>5 pts</strong></li>
                  <li className="flex justify-between"><span>• Point d'eau</span><strong>5 pts</strong></li>
                  <li className="flex justify-between"><span>• Électricité</span><strong>3 pts</strong></li>
                  <li className="flex justify-between"><span>• Clôture</span><strong>2 pts</strong></li>
                </ul>
              </div>

              {/* Pilier 3 */}
              <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-5 mb-4">
                <h5 className="text-lg font-bold text-yellow-900 mb-3">3️⃣ Score Pédagogique (25 points)</h5>
                <ul className="space-y-2 text-yellow-800">
                  <li className="flex justify-between"><span>• Manuels scolaires</span><strong>10 pts</strong></li>
                  <li className="flex justify-between"><span>• Matériel didactique</span><strong>10 pts</strong></li>
                  <li className="flex justify-between"><span>• Bibliothèque</span><strong>5 pts</strong></li>
                </ul>
              </div>

              {/* Pilier 4 */}
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-5 mb-4">
                <h5 className="text-lg font-bold text-purple-900 mb-3">4️⃣ Score Financier (25 points)</h5>
                <ul className="space-y-2 text-purple-800">
                  <li className="flex justify-between"><span>• Frais scolaires conformes</span><strong>10 pts</strong></li>
                  <li className="flex justify-between"><span>• Subvention État</span><strong>10 pts</strong></li>
                  <li className="flex justify-between"><span>• Budget adéquat</span><strong>5 pts</strong></li>
                </ul>
              </div>
            </div>

            {/* Niveaux de Viabilité */}
            <div className="mb-8">
              <h4 className="text-2xl font-bold text-gray-900 mb-4">🎖️ Niveaux de Viabilité</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="border border-gray-300 px-4 py-3 font-semibold">Score</th>
                      <th className="border border-gray-300 px-4 py-3 font-semibold">Niveau</th>
                      <th className="border border-gray-300 px-4 py-3 font-semibold">Décision</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="bg-green-50">
                      <td className="border border-gray-300 px-4 py-3">90-100</td>
                      <td className="border border-gray-300 px-4 py-3"><span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-medium">🟢 Excellent</span></td>
                      <td className="border border-gray-300 px-4 py-3">Viable - Établissement modèle</td>
                    </tr>
                    <tr className="bg-blue-50">
                      <td className="border border-gray-300 px-4 py-3">80-89</td>
                      <td className="border border-gray-300 px-4 py-3"><span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">🔵 Bon</span></td>
                      <td className="border border-gray-300 px-4 py-3">Viable - Très bon fonctionnement</td>
                    </tr>
                    <tr className="bg-yellow-50">
                      <td className="border border-gray-300 px-4 py-3">60-79</td>
                      <td className="border border-gray-300 px-4 py-3"><span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full font-medium">🟡 Moyen</span></td>
                      <td className="border border-gray-300 px-4 py-3">Sous surveillance - Amélioration nécessaire</td>
                    </tr>
                    <tr className="bg-orange-50">
                      <td className="border border-gray-300 px-4 py-3">40-59</td>
                      <td className="border border-gray-300 px-4 py-3"><span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full font-medium">🟠 Faible</span></td>
                      <td className="border border-gray-300 px-4 py-3">Besoin d'amélioration - Intervention requise</td>
                    </tr>
                    <tr className="bg-red-50">
                      <td className="border border-gray-300 px-4 py-3">0-39</td>
                      <td className="border border-gray-300 px-4 py-3"><span className="px-3 py-1 bg-red-100 text-red-800 rounded-full font-medium">🔴 Critique</span></td>
                      <td className="border border-gray-300 px-4 py-3">Fermeture recommandée - Situation alarmante</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recommandations Automatiques */}
            <div className="mb-6">
              <h4 className="text-2xl font-bold text-gray-900 mb-4">💡 Recommandations Automatiques</h4>
              <p className="text-gray-700 mb-3">Le système génère automatiquement des recommandations selon les scores :</p>
              
              <div className="space-y-3">
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <p className="font-semibold text-orange-900 mb-2">Si infrastructures faibles :</p>
                  <p className="text-orange-800 text-sm">→ "Construire/réhabiliter salles de classe et latrines"</p>
                </div>
                
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="font-semibold text-red-900 mb-2">Si ratio élevé {'(> 60)'} :</p>
                  <p className="text-red-800 text-sm">→ "Recruter des enseignants supplémentaires"</p>
                </div>
                
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="font-semibold text-yellow-900 mb-2">Si matériel pédagogique insuffisant :</p>
                  <p className="text-yellow-800 text-sm">→ "Acquérir manuels scolaires et matériel didactique"</p>
                </div>
              </div>
            </div>

            {/* Recommandations pour atteindre 100% */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-100 border-2 border-green-300 rounded-lg p-6">
              <h4 className="text-xl font-bold text-green-900 mb-4">🏆 Pour atteindre 100% (Excellence) :</h4>
              <ul className="space-y-2 text-green-800">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">⚡</span>
                  <span>Acquérir groupe électrogène ou panneaux solaires</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">🌐</span>
                  <span>Acquérir connexion internet (Starlink)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">💻</span>
                  <span>Acquérir 12 ordinateurs pour salle informatique</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">🔬</span>
                  <span>Acquérir salle laboratoire scientifique</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">📚</span>
                  <span>Créer une bibliothèque avec minimum 500 ouvrages</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">🏃</span>
                  <span>Aménager terrain de sport et espace récréatif</span>
                </li>
              </ul>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => setShowGuide(false)}
                className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
              >
                J'ai compris
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h3 className="text-2xl font-bold mb-6">Évaluer un Établissement</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <select
                value={formData.etablissement_id}
                onChange={(e) => setFormData({...formData, etablissement_id: e.target.value})}
                required
                className="w-full px-4 py-2 border rounded-lg"
              >
                <option value="">Sélectionner établissement</option>
                {etablissements.map(e => (
                  <option key={e.id} value={e.id}>{e.nom}</option>
                ))}
              </select>

              <div className="grid grid-cols-3 gap-4">
                <input type="number" placeholder="Nombre élèves" value={formData.nombre_eleves} onChange={(e) => setFormData({...formData, nombre_eleves: parseInt(e.target.value)})} className="px-4 py-2 border rounded-lg" />
                <input type="number" placeholder="Nombre enseignants" value={formData.nombre_enseignants} onChange={(e) => setFormData({...formData, nombre_enseignants: parseInt(e.target.value)})} className="px-4 py-2 border rounded-lg" />
                <input type="number" placeholder="Salles fonctionnelles" value={formData.salles_classes_fonctionnelles} onChange={(e) => setFormData({...formData, salles_classes_fonctionnelles: parseInt(e.target.value)})} className="px-4 py-2 border rounded-lg" />
              </div>

              <div className="space-y-2">
                {['point_eau_disponible', 'electricite_disponible', 'manuels_scolaires_suffisants'].map(key => (
                  <label key={key} className="flex items-center space-x-2">
                    <input type="checkbox" checked={formData[key]} onChange={(e) => setFormData({...formData, [key]: e.target.checked})} className="w-4 h-4" />
                    <span className="text-sm">{key.replace(/_/g, ' ')}</span>
                  </label>
                ))}
              </div>

              <div className="flex justify-end space-x-3">
                <button type="button" onClick={() => setShowForm(false)} className="px-6 py-2 border rounded-lg">Annuler</button>
                <button type="submit" className="px-6 py-2 bg-indigo-600 text-white rounded-lg">Évaluer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvaluationViabilite;
