import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import dinacopeService from '../../../services/dinacope.service';

const DashboardPaie = ({ user }) => {
  const [fiches, setFiches] = useState([]);
  const [statistiques, setStatistiques] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  
  const [periode, setPeriode] = useState({
    mois: new Date().getMonth() + 1,
    annee: new Date().getFullYear()
  });

  useEffect(() => {
    loadData();
  }, [periode]);

  const loadData = async () => {
    try {
      const [fichesData, statsData] = await Promise.all([
        dinacopeService.getFichesPaie(periode.mois, periode.annee),
        dinacopeService.getStatistiquesPaie(periode.mois, periode.annee)
      ]);
      setFiches(fichesData.fiches || []);
      setStatistiques(statsData);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const handleGenererPaie = async () => {
    if (!window.confirm(`Générer le fichier de paie pour ${getMoisLabel(periode.mois)} ${periode.annee} ?`)) {
      return;
    }

    setGenerating(true);
    try {
      const result = await dinacopeService.genererFichierPaie(periode.mois, periode.annee);
      toast.success(result.message);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la génération');
    } finally {
      setGenerating(false);
    }
  };

  const handleExporterCSV = async () => {
    try {
      const result = await dinacopeService.genererExport('fichier_paie', periode.mois, periode.annee, 'csv');
      
      // Télécharger le fichier CSV
      const blob = new Blob([result.contenu], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = result.export.fichier_nom;
      a.click();
      
      toast.success('Export CSV généré avec succès');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  const getMoisLabel = (mois) => {
    const moisLabels = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    return moisLabels[mois];
  };

  const formatMontant = (montant) => {
    return new Intl.NumberFormat('fr-CD', { style: 'currency', currency: 'CDF' }).format(montant);
  };

  if (loading) {
    return <div className="text-center py-8">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">💰 Gestion de la Paie DINACOPE</h2>
        <div className="flex space-x-3">
          {['administrateur_technique', 'ministre'].includes(user.role) && (
            <>
              <button
                onClick={handleGenererPaie}
                disabled={generating || fiches.length > 0}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {generating ? 'Génération...' : 'Générer Fichier Paie'}
              </button>
              {fiches.length > 0 && (
                <button
                  onClick={handleExporterCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  📥 Exporter CSV
                </button>
              )}
            </>
          )}
        </div>
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

      {/* Statistiques */}
      {statistiques && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-600">Total Enseignants</p>
              <p className="text-3xl font-bold text-blue-700">{statistiques.periode_actuelle.total_enseignants}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <p className="text-sm text-green-600">Payés</p>
              <p className="text-3xl font-bold text-green-700">{statistiques.periode_actuelle.enseignants_payes}</p>
              <p className="text-xs text-green-600 mt-1">{statistiques.periode_actuelle.taux_paiement}%</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
              <p className="text-sm text-purple-600">Masse Salariale</p>
              <p className="text-2xl font-bold text-purple-700">
                {formatMontant(statistiques.periode_actuelle.masse_salariale)}
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <p className="text-sm text-yellow-600">Évolution</p>
              <p className={`text-3xl font-bold ${statistiques.evolution.enseignants >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {statistiques.evolution.enseignants >= 0 ? '+' : ''}{statistiques.evolution.enseignants}
              </p>
              <p className="text-xs text-yellow-600 mt-1">{statistiques.evolution.taux_evolution}%</p>
            </div>
          </div>

          {/* Graphique comparaison */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Comparaison avec le mois précédent</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                {
                  name: statistiques.periode_precedente.periode,
                  'Enseignants': statistiques.periode_precedente.total_enseignants,
                  'Payés': statistiques.periode_precedente.enseignants_payes
                },
                {
                  name: statistiques.periode_actuelle.periode,
                  'Enseignants': statistiques.periode_actuelle.total_enseignants,
                  'Payés': statistiques.periode_actuelle.enseignants_payes
                }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Enseignants" fill="#3B82F6" />
                <Bar dataKey="Payés" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {/* Liste des fiches */}
      {fiches.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matricule</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Établissement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Salaire Net</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contrôle</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {fiches.slice(0, 100).map((fiche) => (
                  <tr key={fiche.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{fiche.matricule_secope}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{fiche.enseignant_nom}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{fiche.grade} (E{fiche.echelon})</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{fiche.etablissement_nom}</td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{formatMontant(fiche.salaire_net)}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        fiche.statut_paiement === 'paye' ? 'bg-green-100 text-green-800' :
                        fiche.statut_paiement === 'suspendu' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {fiche.statut_paiement}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {fiche.controle_physique_effectue ? (
                        <span className="text-green-600">✓ Effectué</span>
                      ) : (
                        <span className="text-gray-400">En attente</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {fiches.length > 100 && (
            <div className="bg-gray-50 px-6 py-3 text-sm text-gray-500 text-center">
              Affichage de 100 fiches sur {fiches.length} total
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
          <p className="text-gray-500 text-lg">Aucune fiche de paie pour cette période</p>
          {['administrateur_technique', 'ministre'].includes(user.role) && (
            <p className="text-sm text-gray-400 mt-2">Cliquez sur "Générer Fichier Paie" pour créer les fiches</p>
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardPaie;
