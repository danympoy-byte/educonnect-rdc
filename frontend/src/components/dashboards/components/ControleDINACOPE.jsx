import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import sirhService from '../../../services/sirh.service';
import enseignantsService from '../../../services/enseignants.service';

const ControleDINACOPE = ({ user }) => {
  const [enseignants, setEnseignants] = useState([]);
  const [verifications, setVerifications] = useState([]);
  const [fraudes, setFraudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('enseignants');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [ensData, verifData, fraudeData] = await Promise.all([
        enseignantsService.getAll(),
        sirhService.getVerificationsDINACOPE(),
        sirhService.getFraudesDINACOPE()
      ]);
      setEnseignants(ensData);
      setVerifications(verifData.verifications || []);
      setFraudes(fraudeData.fraudes || []);
    } catch (error) {
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleEnvoyerLien = async (enseignantId) => {
    try {
      const result = await sirhService.envoyerLienVerification(enseignantId);
      toast.success('Lien de vérification envoyé avec succès');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi');
    }
  };

  const getStatutBadge = (statut) => {
    const badges = {
      'en_attente': 'bg-yellow-100 text-yellow-800',
      'verifie': 'bg-green-100 text-green-800',
      'expiree': 'bg-gray-100 text-gray-600'
    };
    return badges[statut] || 'bg-gray-100 text-gray-600';
  };

  const getGraviteBadge = (gravite) => {
    const badges = {
      'faible': 'bg-blue-100 text-blue-800',
      'moyen': 'bg-yellow-100 text-yellow-800',
      'eleve': 'bg-orange-100 text-orange-800',
      'critique': 'bg-red-100 text-red-800'
    };
    return badges[gravite] || 'bg-gray-100 text-gray-600';
  };

  if (loading) {
    return <div className="text-center py-8">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">🔍 Contrôle Physique DINACOPE</h2>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-600">Total Enseignants</p>
          <p className="text-3xl font-bold text-blue-700">{enseignants.length}</p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-600">En attente</p>
          <p className="text-3xl font-bold text-yellow-700">
            {verifications.filter(v => v.statut === 'en_attente').length}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-sm text-green-600">Vérifiés</p>
          <p className="text-3xl font-bold text-green-700">
            {verifications.filter(v => v.statut === 'verifie').length}
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <p className="text-sm text-red-600">Fraudes détectées</p>
          <p className="text-3xl font-bold text-red-700">
            {fraudes.filter(f => f.statut === 'detectee').length}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 border-b">
        <button
          onClick={() => setActiveTab('enseignants')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'enseignants'
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          👥 Enseignants
        </button>
        <button
          onClick={() => setActiveTab('verifications')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'verifications'
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          ✅ Vérifications
        </button>
        <button
          onClick={() => setActiveTab('fraudes')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'fraudes'
              ? 'border-b-2 border-indigo-600 text-indigo-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          ⚠️ Fraudes
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'enseignants' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matricule</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dernière vérif.</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {enseignants.slice(0, 50).map((ens) => (
                <tr key={ens.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{ens.matricule}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{ens.nom || 'N/A'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{ens.grade || 'Non renseigné'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {ens.derniere_verification_dinacope 
                      ? new Date(ens.derniere_verification_dinacope).toLocaleDateString('fr-FR')
                      : 'Jamais'
                    }
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => handleEnvoyerLien(ens.id)}
                      className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm"
                    >
                      Envoyer lien
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'verifications' && (
        <div className="space-y-3">
          {verifications.map((verif) => (
            <div key={verif.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">{verif.enseignant_nom}</p>
                  <p className="text-sm text-gray-600">Matricule : {verif.enseignant_matricule}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Envoyé le {new Date(verif.date_envoi).toLocaleDateString('fr-FR')} par {verif.agent_dinacope_nom}
                  </p>
                  {verif.statut === 'verifie' && verif.champs_modifies && verif.champs_modifies.length > 0 && (
                    <p className="text-xs text-green-600 mt-1">
                      Champs modifiés : {verif.champs_modifies.join(', ')}
                    </p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatutBadge(verif.statut)}`}>
                  {verif.statut}
                </span>
              </div>
            </div>
          ))}
          {verifications.length === 0 && (
            <p className="text-center py-8 text-gray-500">Aucune vérification</p>
          )}
        </div>
      )}

      {activeTab === 'fraudes' && (
        <div className="space-y-3">
          {fraudes.map((fraude) => (
            <div key={fraude.id} className={`border rounded-lg p-4 ${
              fraude.niveau_gravite === 'critique' ? 'bg-red-50 border-red-200' :
              fraude.niveau_gravite === 'eleve' ? 'bg-orange-50 border-orange-200' :
              fraude.niveau_gravite === 'moyen' ? 'bg-yellow-50 border-yellow-200' :
              'bg-blue-50 border-blue-200'
            }`}>
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-semibold">{fraude.type_fraude.replace('_', ' ')}</p>
                  <p className="text-sm text-gray-600">Champ : {fraude.champ_problematique}</p>
                  <p className="text-sm text-gray-600">Valeur : {fraude.valeur_problematique}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getGraviteBadge(fraude.niveau_gravite)}`}>
                  {fraude.niveau_gravite}
                </span>
              </div>
              <div className="bg-white rounded p-3">
                <p className="text-sm font-medium mb-2">Enseignants concernés :</p>
                {fraude.enseignants_concernes.map((ens, idx) => (
                  <p key={idx} className="text-sm text-gray-700">
                    • {ens.nom} ({ens.matricule}) - {ens.etablissement}
                  </p>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Détecté le {new Date(fraude.date_detection).toLocaleDateString('fr-FR')}
              </p>
            </div>
          ))}
          {fraudes.length === 0 && (
            <p className="text-center py-8 text-gray-500">Aucune fraude détectée</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ControleDINACOPE;
