import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import sirhService from '../../../services/sirh.service';

const FicheAgentDetaillee = ({ enseignantId, onClose }) => {
  const [fiche, setFiche] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('infos');

  useEffect(() => {
    loadFiche();
  }, [enseignantId]);

  const loadFiche = async () => {
    try {
      const data = await sirhService.getFicheAgentDetaillee(enseignantId);
      setFiche(data);
    } catch (error) {
      toast.error('Erreur lors du chargement de la fiche');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8">
          <p>Chargement de la fiche...</p>
        </div>
      </div>
    );
  }

  if (!fiche) return null;

  const { enseignant, utilisateur, etablissement_actuel, province_actuelle } = fiche;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6 border-b pb-4">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">
                {utilisateur.prenom} {utilisateur.nom}
              </h2>
              <p className="text-gray-600 mt-1">Matricule : {enseignant.matricule}</p>
              <p className="text-sm text-gray-500">Grade : {enseignant.grade || 'Non renseigné'}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-3xl"
            >
              ×
            </button>
          </div>

          {/* Tabs */}
          <div className="flex space-x-4 border-b mb-6">
            <button
              onClick={() => setActiveTab('infos')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'infos'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📋 Informations
            </button>
            <button
              onClick={() => setActiveTab('affectations')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'affectations'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📍 Affectations
            </button>
            <button
              onClick={() => setActiveTab('promotions')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'promotions'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📈 Promotions
            </button>
            <button
              onClick={() => setActiveTab('mutations')}
              className={`px-4 py-2 font-medium ${
                activeTab === 'mutations'
                  ? 'border-b-2 border-indigo-600 text-indigo-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🔄 Mutations
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'infos' && (
            <div className="space-y-6">
              {/* Infos professionnelles */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-lg mb-4">Informations Professionnelles</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Matricule</p>
                    <p className="font-medium">{enseignant.matricule}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Grade</p>
                    <p className="font-medium">{enseignant.grade || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Établissement actuel</p>
                    <p className="font-medium">{etablissement_actuel?.nom || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Province</p>
                    <p className="font-medium">{province_actuelle?.nom || 'N/A'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-600">Matières enseignées</p>
                    <p className="font-medium">{enseignant.matieres?.join(', ') || 'Aucune'}</p>
                  </div>
                </div>
              </div>

              {/* Infos personnelles DINACOPE */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-lg mb-4">Informations Personnelles (DINACOPE)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Adresse</p>
                    <p className="font-medium">{enseignant.adresse_personnelle || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Téléphone</p>
                    <p className="font-medium">{enseignant.telephone_personnel || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Email personnel</p>
                    <p className="font-medium">{enseignant.email_personnel || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">État civil</p>
                    <p className="font-medium">{enseignant.etat_civil || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Nombre d'enfants</p>
                    <p className="font-medium">{enseignant.nombre_enfants || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Banque</p>
                    <p className="font-medium">{enseignant.banque || 'Non renseigné'}</p>
                  </div>
                </div>
                {fiche.derniere_verification_dinacope && (
                  <div className="mt-4 p-3 bg-green-100 rounded border border-green-300">
                    <p className="text-sm text-green-800">
                      ✅ Dernière vérification : {new Date(fiche.derniere_verification_dinacope.date_verification).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'affectations' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Historique des Affectations</h3>
              {fiche.historique_affectations && fiche.historique_affectations.length > 0 ? (
                <div className="relative">
                  {/* Timeline */}
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300"></div>
                  {fiche.historique_affectations.map((affectation, index) => (
                    <div key={affectation.id} className="relative pl-12 pb-6">
                      <div className="absolute left-0 w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                        {index + 1}
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-lg">{affectation.etablissement_nom}</p>
                            <p className="text-sm text-gray-600">{affectation.province_nom}</p>
                            <p className="text-xs text-gray-500 mt-2">Motif : {affectation.motif}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-700">
                              {new Date(affectation.date_debut).toLocaleDateString('fr-FR')}
                            </p>
                            <p className="text-sm text-gray-500">
                              {affectation.date_fin 
                                ? `→ ${new Date(affectation.date_fin).toLocaleDateString('fr-FR')}`
                                : '→ Actuellement'
                              }
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Aucun historique d'affectation</p>
              )}
            </div>
          )}

          {activeTab === 'promotions' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Historique des Promotions</h3>
              {fiche.historique_promotions && fiche.historique_promotions.length > 0 ? (
                <div className="space-y-3">
                  {fiche.historique_promotions.map((promotion) => (
                    <div key={promotion.id} className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold text-lg">
                            {promotion.ancien_grade} → {promotion.nouveau_grade}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">Motif : {promotion.motif}</p>
                          <p className="text-xs text-gray-500 mt-2">Référence : {promotion.decision_reference}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-700">
                            {new Date(promotion.date_promotion).toLocaleDateString('fr-FR')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Aucune promotion enregistrée</p>
              )}
            </div>
          )}

          {activeTab === 'mutations' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-lg">Demandes de Mutation</h3>
              {fiche.mutations && fiche.mutations.length > 0 ? (
                <div className="space-y-3">
                  {fiche.mutations.map((mutation) => (
                    <div key={mutation.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-semibold">{mutation.numero_reference}</p>
                          <p className="text-sm text-gray-600">Type : {mutation.type_mutation}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          mutation.statut === 'approuvee' ? 'bg-green-100 text-green-800' :
                          mutation.statut === 'rejetee' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {mutation.statut}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">Motif : {mutation.motif}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        Demandé le {new Date(mutation.date_demande).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Aucune demande de mutation</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FicheAgentDetaillee;
