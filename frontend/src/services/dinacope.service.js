import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const getAuthHeaders = () => {
    return {    'Content-Type': 'application/json'
  };
};

// ============================================
// PAIE
// ============================================

const genererFichierPaie = async (mois, annee) => {
  const response = await axios.post(
    `${API_URL}/api/dinacope/paie/generer`,
    { mois, annee },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const getFichesPaie = async (mois = null, annee = null, enseignantId = null) => {
  const params = {};
  if (mois) params.mois = mois;
  if (annee) params.annee = annee;
  if (enseignantId) params.enseignant_id = enseignantId;
  
  const response = await axios.get(
    `${API_URL}/api/dinacope/paie`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

const getStatistiquesPaie = async (mois, annee) => {
  const response = await axios.get(
    `${API_URL}/api/dinacope/paie/statistiques`,
    { headers: getAuthHeaders(), params: { mois, annee } }
  );
  return response.data;
};

// ============================================
// CONTRÔLES PHYSIQUES
// ============================================

const planifierControles = async (mois, annee) => {
  const response = await axios.post(
    `${API_URL}/api/dinacope/controles/planifier`,
    { mois, annee },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const getControles = async (mois = null, annee = null, statut = null) => {
  const params = {};
  if (mois) params.mois = mois;
  if (annee) params.annee = annee;
  if (statut) params.statut = statut;
  
  const response = await axios.get(
    `${API_URL}/api/dinacope/controles`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

const effectuerControle = async (controleId, enseignantsPresents, enseignantsAbsents, observations = '') => {
  const response = await axios.post(
    `${API_URL}/api/dinacope/controles/${controleId}/effectuer`,
    {
      enseignants_presents: enseignantsPresents,
      enseignants_absents: enseignantsAbsents,
      observations
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ============================================
// VIABILITÉ
// ============================================

const evaluerViabilite = async (etablissementId, anneeScolaire, donnees) => {
  const response = await axios.post(
    `${API_URL}/api/dinacope/viabilite/evaluer`,
    {
      etablissement_id: etablissementId,
      annee_scolaire: anneeScolaire,
      ...donnees
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const getEvaluationsViabilite = async (etablissementId = null, niveau = null) => {
  const params = {};
  if (etablissementId) params.etablissement_id = etablissementId;
  if (niveau) params.niveau = niveau;
  
  const response = await axios.get(
    `${API_URL}/api/dinacope/viabilite`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

// ============================================
// EXPORTS
// ============================================

const genererExport = async (typeExport, mois, annee, formatFichier = 'csv') => {
  const response = await axios.post(
    `${API_URL}/api/dinacope/exports/generer`,
    {
      type_export: typeExport,
      mois,
      annee,
      format_fichier: formatFichier
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const dinacopeService = {
  // Paie
  genererFichierPaie,
  getFichesPaie,
  getStatistiquesPaie,
  
  // Contrôles
  planifierControles,
  getControles,
  effectuerControle,
  
  // Viabilité
  evaluerViabilite,
  getEvaluationsViabilite,
  
  // Exports
  genererExport
};

export default dinacopeService;
