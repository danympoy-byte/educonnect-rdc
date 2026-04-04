import React, { useState } from 'react';
import APIKeys from './APIKeys';

const SOURCES_DONNEES = [
  {
    nom: "Gestion Scolaire",
    description: "Applications de gestion scolaire qui transmettent les donnees d'effectifs, presences et informations des etablissements.",
    types: ["Presences", "Effectifs eleves", "Effectifs enseignants", "Informations etablissements"],
    statut: "en_attente",
    endpoint: "POST /api/externe/gestion-scolaire"
  },
  {
    nom: "Tests et Evaluations",
    description: "Outils de tests en ligne et plateformes d'evaluation qui envoient les resultats des evaluations numeriques.",
    types: ["Notes d'evaluations", "Resultats de tests", "Statistiques de performance"],
    statut: "en_attente",
    endpoint: "POST /api/externe/evaluations"
  },
  {
    nom: "SECOPE",
    description: "Systeme de paie des enseignants. Fournit les donnees de remuneration et suivi des paiements.",
    types: ["Donnees de paie", "Statistiques salariales", "Suivi des paiements"],
    statut: "simulation",
    endpoint: "POST /api/externe/secope"
  },
  {
    nom: "DINACOPE",
    description: "Direction Nationale de Controle et de la Paie des Enseignants. Controle de conformite et verification.",
    types: ["Rapports de controle", "Verifications", "Audits"],
    statut: "simulation",
    endpoint: "POST /api/externe/dinacope"
  }
];

const ENDPOINTS_INGESTION = [
  {
    method: "POST",
    path: "/api/externe/presences",
    description: "Recevoir les donnees de presence depuis les applications de gestion scolaire",
    body: '{ "etablissement_id": "string", "date": "YYYY-MM-DD", "classe_id": "string", "presents": 45, "absents": 3 }',
    auth: "Bearer API_KEY"
  },
  {
    method: "POST",
    path: "/api/externe/evaluations",
    description: "Recevoir les resultats d'evaluations depuis les outils de tests en ligne",
    body: '{ "etablissement_id": "string", "classe_id": "string", "matiere": "string", "notes": [{"eleve_id": "string", "note": 15.5}] }',
    auth: "Bearer API_KEY"
  },
  {
    method: "POST",
    path: "/api/externe/effectifs",
    description: "Mise a jour des effectifs depuis les systemes de gestion",
    body: '{ "etablissement_id": "string", "total_eleves": 450, "total_enseignants": 28, "date_maj": "YYYY-MM-DD" }',
    auth: "Bearer API_KEY"
  },
  {
    method: "POST",
    path: "/api/externe/etablissement",
    description: "Enregistrer ou mettre a jour un etablissement",
    body: '{ "code_esecope": "string", "nom": "string", "province": "string", "type": "ecole_primaire|college|lycee" }',
    auth: "Bearer API_KEY"
  }
];

const PartageDonnees = () => {
  const [activeTab, setActiveTab] = useState('sources');

  const tabs = [
    { key: 'sources', label: 'Sources de Donnees' },
    { key: 'endpoints', label: 'Endpoints d\'Ingestion' },
    { key: 'cles', label: 'Cles API' },
  ];

  const getStatutBadge = (statut) => {
    switch (statut) {
      case 'connectee':
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Connectee</span>;
      case 'simulation':
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Simulation</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">En attente</span>;
    }
  };

  return (
    <div className="space-y-6" data-testid="partage-donnees-page">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Partage de Donnees</h2>
        <p className="text-sm text-gray-500 mt-1">
          Gerez les sources de donnees externes, les cles API et les endpoints d'ingestion pour les applications partenaires.
        </p>
      </div>

      {/* Bannière explicative */}
      <div className="bg-blue-50 border-l-4 border-blue-500 rounded-r-xl p-4" data-testid="info-banner">
        <div className="flex items-start gap-3">
          <svg className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-blue-800">Comment ca fonctionne</h3>
            <p className="text-sm text-blue-700 mt-1">
              Les applications de gestion scolaire et de tests digitaux autorisees peuvent envoyer des donnees a Edu-Connect via les endpoints d'ingestion. 
              Chaque application partenaire recoit une cle API unique pour s'authentifier. Les donnees recues alimentent automatiquement les graphiques et tableaux de bord.
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-0">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-5 py-2.5 text-sm font-medium transition border-b-2 -mb-px ${
              activeTab === tab.key
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            data-testid={`tab-${tab.key}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sources de Données */}
      {activeTab === 'sources' && (
        <div className="space-y-4" data-testid="sources-section">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {SOURCES_DONNEES.map((source, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-base font-semibold text-gray-900">{source.nom}</h3>
                  {getStatutBadge(source.statut)}
                </div>
                <p className="text-sm text-gray-600 mb-3">{source.description}</p>
                <div className="space-y-1.5">
                  <p className="text-xs font-medium text-gray-500 uppercase">Types de donnees :</p>
                  <div className="flex flex-wrap gap-1.5">
                    {source.types.map((type, i) => (
                      <span key={i} className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">{type}</span>
                    ))}
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-400 font-mono">{source.endpoint}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Légende des statuts */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Legende des statuts</h4>
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-xs text-gray-600"><strong>Connectee</strong> - Source active envoyant des donnees en temps reel</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-xs text-gray-600"><strong>Simulation</strong> - Donnees simulees pour demonstration</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-gray-400" />
                <span className="text-xs text-gray-600"><strong>En attente</strong> - En attente d'autorisation de l'application partenaire</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Endpoints d'Ingestion */}
      {activeTab === 'endpoints' && (
        <div className="space-y-4" data-testid="endpoints-section">
          <p className="text-sm text-gray-600">
            Ces endpoints permettent aux applications partenaires autorisees d'envoyer des donnees a Edu-Connect. 
            Chaque requete doit inclure une cle API valide dans le header <code className="px-1.5 py-0.5 bg-gray-100 rounded text-xs">Authorization</code>.
          </p>

          {ENDPOINTS_INGESTION.map((ep, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-5 py-3 bg-gray-50 border-b border-gray-200 flex items-center gap-3">
                <span className="px-2.5 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700">{ep.method}</span>
                <code className="text-sm font-mono text-gray-800">{ep.path}</code>
              </div>
              <div className="p-5 space-y-3">
                <p className="text-sm text-gray-700">{ep.description}</p>
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Authentification :</p>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">{ep.auth}</code>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Exemple de body :</p>
                  <pre className="text-xs bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto">{ep.body}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Clés API */}
      {activeTab === 'cles' && (
        <div data-testid="cles-section">
          <APIKeys />
        </div>
      )}
    </div>
  );
};

export default PartageDonnees;
