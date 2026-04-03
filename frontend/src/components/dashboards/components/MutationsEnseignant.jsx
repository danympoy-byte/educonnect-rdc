import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import sirhService from '../../../services/sirh.service';
import enseignantsService from '../../../services/enseignants.service';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const MutationsEnseignant = ({ user }) => {
  const [mutations, setMutations] = useState([]);
  const [enseignants, setEnseignants] = useState([]);
  const [etablissements, setEtablissements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedMutation, setSelectedMutation] = useState(null);

  const [formData, setFormData] = useState({
    type_mutation: 'geographique',
    enseignant_id: '',
    motif: '',
    justification: '',
    etablissement_destination_id: '',
    grade_demande: '',
    nouvelles_matieres: [],
    date_souhaitee: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
            const [mutData, ensData, etabData] = await Promise.all([
        sirhService.getMutations(),
        enseignantsService.getAll(),
        fetch(`${API_URL}/api/etablissements`, { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json())
      ]);
      setMutations(mutData.mutations || []);
      setEnseignants(ensData || []);
      setEtablissements(etabData || []);
    } catch (error) {
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMutation = async (e) => {
    e.preventDefault();
    try {
      await sirhService.creerDemandeMutation(formData);
      toast.success('Demande de mutation créée avec succès');
      setShowCreateForm(false);
      loadData();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleValider = async (mutationId) => {
    const commentaire = prompt('Commentaire (optionnel):');
    try {
      await sirhService.validerMutation(mutationId, commentaire || '');
      toast.success('Mutation validée');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la validation');
    }
  };

  const handleRejeter = async (mutationId) => {
    const raison = prompt('Raison du rejet (obligatoire):');
    if (!raison) return;
    
    try {
      await sirhService.rejeterMutation(mutationId, raison);
      toast.success('Mutation rejetée');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors du rejet');
    }
  };

  const resetForm = () => {
    setFormData({
      type_mutation: 'geographique',
      enseignant_id: '',
      motif: '',
      justification: '',
      etablissement_destination_id: '',
      grade_demande: '',
      nouvelles_matieres: [],
      date_souhaitee: ''
    });
  };

  const getStatutBadge = (statut) => {
    const badges = {
      'en_attente': 'bg-yellow-100 text-yellow-800',
      'validee_directeur': 'bg-blue-100 text-blue-800',
      'validee_dpe_origine': 'bg-blue-100 text-blue-800',
      'validee_dpe_destination': 'bg-blue-100 text-blue-800',
      'validee_secretaire_general': 'bg-blue-100 text-blue-800',
      'approuvee': 'bg-green-100 text-green-800',
      'rejetee': 'bg-red-100 text-red-800'
    };
    return badges[statut] || 'bg-gray-100 text-gray-600';
  };

  const peutValider = (mutation) => {
    const userId = user.id;
    const circuit = mutation.circuit_validation || [];
    
    for (const etape of circuit) {
      if (etape.user_id === userId && etape.statut === 'en_attente') {
        return true;
      }
    }
    return false;
  };

  if (loading) {
    return <div className="text-center py-8">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">🔄 Gestion des Mutations</h2>
        {['enseignant', 'directeur_ecole', 'chef_etablissement', 'directeur_provincial'].includes(user.role) && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            + Nouvelle Demande
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-600">En attente</p>
          <p className="text-3xl font-bold text-yellow-700">
            {mutations.filter(m => m.statut === 'en_attente' || m.statut.includes('validee')).length}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-sm text-green-600">Approuvées</p>
          <p className="text-3xl font-bold text-green-700">
            {mutations.filter(m => m.statut === 'approuvee').length}
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <p className="text-sm text-red-600">Rejetées</p>
          <p className="text-3xl font-bold text-red-700">
            {mutations.filter(m => m.statut === 'rejetee').length}
          </p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-600">Total</p>
          <p className="text-3xl font-bold text-blue-700">{mutations.length}</p>
        </div>
      </div>

      {/* Liste des mutations */}
      <div className="space-y-3">
        {mutations.map((mutation) => (
          <div key={mutation.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <p className="font-semibold text-lg">{mutation.numero_reference}</p>
                <p className="text-sm text-gray-600">
                  {mutation.enseignant_nom} ({mutation.enseignant_matricule})
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Type : <span className="font-medium">{mutation.type_mutation}</span>
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatutBadge(mutation.statut)}`}>
                {mutation.statut.replace(/_/g, ' ')}
              </span>
            </div>

            {/* Détails selon type */}
            <div className="bg-gray-50 rounded p-3 mb-3">
              {mutation.type_mutation === 'geographique' && (
                <div>
                  <p className="text-sm text-gray-700">
                    <strong>Origine :</strong> {mutation.etablissement_actuel_nom} ({mutation.province_actuelle_nom})
                  </p>
                  <p className="text-sm text-gray-700">
                    <strong>Destination :</strong> {mutation.etablissement_destination_nom} ({mutation.province_destination_nom})
                  </p>
                </div>
              )}
              {mutation.type_mutation === 'promotion' && (
                <p className="text-sm text-gray-700">
                  <strong>Promotion :</strong> {mutation.grade_actuel} → {mutation.grade_demande}
                </p>
              )}
              {mutation.type_mutation === 'discipline' && (
                <p className="text-sm text-gray-700">
                  <strong>Nouvelles matières :</strong> {mutation.matieres_demandees?.join(', ')}
                </p>
              )}
              <p className="text-sm text-gray-700 mt-2">
                <strong>Motif :</strong> {mutation.motif}
              </p>
            </div>

            {/* Circuit de validation */}
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-2">Circuit de validation :</p>
              <div className="flex items-center space-x-2">
                {mutation.circuit_validation?.map((etape, idx) => (
                  <React.Fragment key={idx}>
                    <div className={`px-3 py-1 rounded text-sm ${
                      etape.statut === 'valide' ? 'bg-green-100 text-green-800' :
                      etape.statut === 'en_attente' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {etape.role.replace('_', ' ')}
                      {etape.statut === 'valide' && ' ✓'}
                    </div>
                    {idx < mutation.circuit_validation.length - 1 && (
                      <span className="text-gray-400">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Actions */}
            {peutValider(mutation) && (
              <div className="flex space-x-2 pt-3 border-t">
                <button
                  onClick={() => handleValider(mutation.id)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                >
                  ✓ Valider
                </button>
                <button
                  onClick={() => handleRejeter(mutation.id)}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                >
                  ✗ Rejeter
                </button>
              </div>
            )}

            <p className="text-xs text-gray-500 mt-3">
              Demandé le {new Date(mutation.date_demande).toLocaleDateString('fr-FR')} par {mutation.initiateur_nom}
            </p>
          </div>
        ))}

        {mutations.length === 0 && (
          <p className="text-center py-8 text-gray-500">Aucune demande de mutation</p>
        )}
      </div>

      {/* Modal Création */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-6">
              <h3 className="text-2xl font-bold">Nouvelle Demande de Mutation</h3>
              <button onClick={() => setShowCreateForm(false)} className="text-gray-400 hover:text-gray-600 text-3xl">×</button>
            </div>

            <form onSubmit={handleCreateMutation} className="space-y-4">
              {/* Type de mutation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type de mutation</label>
                <select
                  value={formData.type_mutation}
                  onChange={(e) => setFormData({...formData, type_mutation: e.target.value})}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="geographique">Mutation géographique</option>
                  <option value="promotion">Promotion de grade</option>
                  <option value="discipline">Mutation de discipline</option>
                </select>
              </div>

              {/* Enseignant */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Enseignant concerné</label>
                <select
                  value={formData.enseignant_id}
                  onChange={(e) => setFormData({...formData, enseignant_id: e.target.value})}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Sélectionner un enseignant</option>
                  {enseignants.map(ens => (
                    <option key={ens.id} value={ens.id}>{ens.nom} ({ens.matricule})</option>
                  ))}
                </select>
              </div>

              {/* Établissement destination (si géographique) */}
              {formData.type_mutation === 'geographique' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Établissement de destination</label>
                  <select
                    value={formData.etablissement_destination_id}
                    onChange={(e) => setFormData({...formData, etablissement_destination_id: e.target.value})}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Sélectionner un établissement</option>
                    {etablissements.map(etab => (
                      <option key={etab.id} value={etab.id}>{etab.nom}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Grade demandé (si promotion) */}
              {formData.type_mutation === 'promotion' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nouveau grade</label>
                  <select
                    value={formData.grade_demande}
                    onChange={(e) => setFormData({...formData, grade_demande: e.target.value})}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="">Sélectionner un grade</option>
                    <option value="qualifié">Qualifié</option>
                    <option value="diplômé">Diplômé</option>
                    <option value="licencié">Licencié</option>
                    <option value="maître_assistant">Maître Assistant</option>
                    <option value="chef_de_travaux">Chef de Travaux</option>
                  </select>
                </div>
              )}

              {/* Motif */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Motif</label>
                <input
                  type="text"
                  value={formData.motif}
                  onChange={(e) => setFormData({...formData, motif: e.target.value})}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  placeholder="Ex: Rapprochement familial"
                />
              </div>

              {/* Justification */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Justification</label>
                <textarea
                  value={formData.justification}
                  onChange={(e) => setFormData({...formData, justification: e.target.value})}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  placeholder="Détails et justification de la demande"
                />
              </div>

              {/* Boutons */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Créer la demande
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MutationsEnseignant;
