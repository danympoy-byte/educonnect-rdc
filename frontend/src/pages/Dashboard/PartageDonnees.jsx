import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import APIKeys from './APIKeys';

const SOURCES_DEFINITION = {
  "Notes": { description: "Notes scolaires envoyées par les systèmes de gestion", types: ["Notes", "Coefficients", "Trimestres"] },
  "Evaluations": { description: "Résultats d'évaluations depuis les outils de tests en ligne", types: ["Notes d'évaluations", "Commentaires", "Statistiques"] },
  "Presences": { description: "Données de présence depuis les applications de gestion scolaire", types: ["Présences", "Absences", "Justifications"] },
  "Effectifs": { description: "Mises à jour des effectifs depuis les systèmes de gestion", types: ["Effectifs élèves", "Effectifs enseignants", "Classes"] },
  "Inscriptions": { description: "Inscriptions d'élèves depuis les systèmes partenaires", types: ["Inscriptions", "Données élèves"] },
  "Affectations": { description: "Affectations d'enseignants depuis les systèmes RH", types: ["Affectations", "Mutations"] }
};

const ENDPOINTS_DOC = [
  {
    method: "POST", path: "/api/externe/presences",
    description: "Recevoir les données de présence depuis les applications de gestion scolaire",
    permission: "presences",
    body: `[
  {
    "eleve_id": "string",
    "classe_id": "string",
    "etablissement_id": "string",
    "date": "YYYY-MM-DD",
    "present": true,
    "justifie": false,
    "motif": "optional"
  }
]`,
    auth: "Basic Auth (username:password)"
  },
  {
    method: "POST", path: "/api/externe/evaluations",
    description: "Recevoir les résultats d'évaluations depuis les outils de tests en ligne",
    permission: "notes",
    body: `{
  "etablissement_id": "string",
  "classe_id": "string",
  "matiere": "Mathematiques",
  "trimestre": "trimestre_1",
  "annee_scolaire": "2025-2026",
  "enseignant_id": "string",
  "notes": [
    {"eleve_id": "string", "note": 15.5, "commentaire": "optional"}
  ]
}`,
    auth: "Basic Auth (username:password)"
  },
  {
    method: "POST", path: "/api/externe/effectifs",
    description: "Mise à jour des effectifs depuis les systèmes de gestion",
    permission: "inscriptions",
    body: `[
  {
    "etablissement_id": "string",
    "total_eleves": 450,
    "total_enseignants": 28,
    "total_classes": 12,
    "date_maj": "YYYY-MM-DD",
    "details_par_niveau": {"1ere_annee_primaire": 45}
  }
]`,
    auth: "Basic Auth (username:password)"
  },
  {
    method: "POST", path: "/api/externe/notes",
    description: "Envoyer des notes individuelles (format plat ou CSV/XML)",
    permission: "notes",
    body: `[
  {
    "eleve_id": "string",
    "classe_id": "string",
    "matiere": "Francais",
    "note": 14.5,
    "coefficient": 3,
    "trimestre": "trimestre_1",
    "annee_scolaire": "2025-2026",
    "enseignant_id": "string"
  }
]`,
    auth: "Basic Auth (username:password)"
  }
];

const PartageDonnees = () => {
  const [activeTab, setActiveTab] = useState('sources');
  const [sourcesStatus, setSourcesStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, logsRes] = await Promise.all([
        api.get('/externe/sources/status'),
        api.get('/externe/logs?limit=20')
      ]);
      setSourcesStatus(statusRes.data);
      setLogs(logsRes.data.logs || []);
    } catch (err) {
      console.error('Erreur chargement:', err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { key: 'sources', label: 'Sources de Données' },
    { key: 'endpoints', label: 'Endpoints d\'Ingestion' },
    { key: 'logs', label: 'Journal d\'Activité' },
    { key: 'cles', label: 'Clés API' },
  ];

  const getStatutBadge = (statut) => {
    switch (statut) {
      case 'success':
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Actif</span>;
      case 'partial':
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">Partiel</span>;
      case 'error':
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">Erreur</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">En attente</span>;
    }
  };

  return (
    <div className="space-y-6" data-testid="partage-donnees-page">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Partage de Données</h2>
        <p className="text-sm text-gray-500 mt-1">
          Gérez les sources de données externes, les clés API et les endpoints d'ingestion pour les applications partenaires.
        </p>
      </div>

      {/* Bannière explicative */}
      <div className="bg-blue-50 border-l-4 border-blue-500 rounded-r-xl p-4" data-testid="info-banner">
        <div className="flex items-start gap-3">
          <svg className="w-6 h-6 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-blue-800">Comment ça fonctionne</h3>
            <p className="text-sm text-blue-700 mt-1">
              Les applications de gestion scolaire et de tests digitaux autorisées envoient des données à Édu-Connect via les endpoints d'ingestion (Basic Auth).
              Les données reçues alimentent automatiquement les graphiques et tableaux de bord de la plateforme.
            </p>
          </div>
        </div>
      </div>

      {/* Stats rapides */}
      {sourcesStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-xl p-5 text-white" data-testid="stat-clients">
            <p className="text-indigo-200 text-sm font-medium">Clients API Actifs</p>
            <p className="text-3xl font-bold mt-1">{sourcesStatus.nb_clients_api_actifs}</p>
          </div>
          <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl p-5 text-white" data-testid="stat-appels">
            <p className="text-emerald-200 text-sm font-medium">Total Appels API</p>
            <p className="text-3xl font-bold mt-1">{sourcesStatus.stats_globales.total_appels_api}</p>
          </div>
          <div className="bg-gradient-to-br from-amber-600 to-amber-700 rounded-xl p-5 text-white" data-testid="stat-presences">
            <p className="text-amber-200 text-sm font-medium">Présences Enregistrées</p>
            <p className="text-3xl font-bold mt-1">{sourcesStatus.stats_globales.total_presences_enregistrees}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 pb-0 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-5 py-2.5 text-sm font-medium transition border-b-2 -mb-px whitespace-nowrap ${
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
          {loading ? (
            <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div></div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(sourcesStatus?.sources || []).map((source, idx) => {
                  const def = SOURCES_DEFINITION[source.nom] || {};
                  return (
                    <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition" data-testid={`source-${source.nom.toLowerCase()}`}>
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-base font-semibold text-gray-900">{source.nom}</h3>
                        {getStatutBadge(source.dernier_statut)}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{def.description || source.endpoint}</p>
                      
                      <div className="grid grid-cols-2 gap-2 mb-3">
                        <div className="bg-gray-50 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-gray-900">{source.nb_appels}</p>
                          <p className="text-xs text-gray-500">Appels</p>
                        </div>
                        <div className="bg-gray-50 rounded-lg p-2 text-center">
                          <p className="text-lg font-bold text-gray-900">{source.nb_enregistrements_total}</p>
                          <p className="text-xs text-gray-500">Enregistrements</p>
                        </div>
                      </div>

                      {def.types && (
                        <div className="flex flex-wrap gap-1">
                          {def.types.map((t, i) => (
                            <span key={i} className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">{t}</span>
                          ))}
                        </div>
                      )}
                      
                      {source.dernier_appel && (
                        <p className="text-xs text-gray-400 mt-2">Dernier appel : {new Date(source.dernier_appel).toLocaleString('fr-FR')}</p>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Légende */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Légende des statuts</h4>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500" /><span className="text-xs text-gray-600"><strong>Actif</strong> - Dernier appel réussi</span></div>
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-amber-500" /><span className="text-xs text-gray-600"><strong>Partiel</strong> - Succès avec erreurs partielles</span></div>
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500" /><span className="text-xs text-gray-600"><strong>Erreur</strong> - Dernier appel en erreur</span></div>
                  <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-gray-400" /><span className="text-xs text-gray-600"><strong>En attente</strong> - Aucun appel reçu</span></div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Endpoints d'Ingestion */}
      {activeTab === 'endpoints' && (
        <div className="space-y-4" data-testid="endpoints-section">
          <p className="text-sm text-gray-600">
            Ces endpoints permettent aux applications partenaires autorisées d'envoyer des données à Édu-Connect.
            Chaque requête utilise <strong>Basic Auth</strong> (username + password du client API).
            Les formats supportés sont <strong>JSON</strong>, <strong>XML</strong> et <strong>CSV</strong>.
          </p>

          {ENDPOINTS_DOC.map((ep, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-5 py-3 bg-gray-50 border-b border-gray-200 flex items-center gap-3 flex-wrap">
                <span className="px-2.5 py-1 rounded text-xs font-bold bg-emerald-100 text-emerald-700">{ep.method}</span>
                <code className="text-sm font-mono text-gray-800">{ep.path}</code>
                <span className="px-2 py-0.5 rounded text-xs bg-indigo-100 text-indigo-700">Permission: {ep.permission}</span>
              </div>
              <div className="p-5 space-y-3">
                <p className="text-sm text-gray-700">{ep.description}</p>
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Authentification :</p>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">{ep.auth}</code>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Exemple de body (JSON) :</p>
                  <pre className="text-xs bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto whitespace-pre">{ep.body}</pre>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">Exemple curl :</p>
                  <pre className="text-xs bg-gray-800 text-gray-300 p-3 rounded-lg overflow-x-auto whitespace-pre">{`curl -X POST "https://votre-domaine${ep.path}" \\
  -u "username:password" \\
  -H "Content-Type: application/json" \\
  -d '...'`}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Journal d'Activité */}
      {activeTab === 'logs' && (
        <div className="space-y-4" data-testid="logs-section">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">Derniers appels API des systèmes externes</p>
            <button onClick={fetchData} className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-lg text-sm hover:bg-indigo-200 transition" data-testid="btn-refresh-logs">
              Actualiser
            </button>
          </div>

          {logs.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <p className="text-gray-500">Aucun appel API enregistré pour le moment.</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Endpoint</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Records</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Erreurs</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.map((log, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-600">{new Date(log.timestamp).toLocaleString('fr-FR')}</td>
                        <td className="px-4 py-3"><code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{log.endpoint}</code></td>
                        <td className="px-4 py-3 text-sm text-gray-600 uppercase">{log.format_donnees || '-'}</td>
                        <td className="px-4 py-3">{getStatutBadge(log.statut)}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{log.nb_enregistrements}</td>
                        <td className="px-4 py-3 text-sm text-red-600">{log.erreurs?.length > 0 ? log.erreurs[0].substring(0, 50) : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
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
