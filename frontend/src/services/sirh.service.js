import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const getAuthHeaders = () => {
    return {    'Content-Type': 'application/json'
  };
};

// ============================================
// FICHE AGENT DÉTAILLÉE
// ============================================

const getFicheAgentDetaillee = async (enseignantId) => {
  const response = await axios.get(
    `${API_URL}/api/sirh/enseignants/${enseignantId}/fiche-detaillee`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ============================================
// CONTRÔLE DINACOPE
// ============================================

const getVerificationsDINACOPE = async (statut = null) => {
  const params = statut ? { statut } : {};
  const response = await axios.get(
    `${API_URL}/api/sirh/dinacope/verifications`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

const envoyerLienVerification = async (enseignantId) => {
  const response = await axios.post(
    `${API_URL}/api/sirh/dinacope/envoyer-lien`,
    { enseignant_id: enseignantId },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const getFormulaireVerification = async (token) => {
  const response = await axios.get(
    `${API_URL}/api/sirh/dinacope/verifier/${token}`
  );
  return response.data;
};

const soumettreVerification = async (token, donnees) => {
  const response = await axios.post(
    `${API_URL}/api/sirh/dinacope/verifier/${token}`,
    donnees
  );
  return response.data;
};

const getFraudesDINACOPE = async (statut = null) => {
  const params = statut ? { statut } : {};
  const response = await axios.get(
    `${API_URL}/api/sirh/dinacope/fraudes`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

// ============================================
// MUTATIONS MULTI-NIVEAUX
// ============================================

const creerDemandeMutation = async (demande) => {
  const response = await axios.post(
    `${API_URL}/api/sirh/mutations`,
    demande,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const getMutations = async (statut = null, enseignantId = null) => {
  const params = {};
  if (statut) params.statut = statut;
  if (enseignantId) params.enseignant_id = enseignantId;
  
  const response = await axios.get(
    `${API_URL}/api/sirh/mutations`,
    { headers: getAuthHeaders(), params }
  );
  return response.data;
};

const validerMutation = async (mutationId, commentaire = '') => {
  const response = await axios.post(
    `${API_URL}/api/sirh/mutations/${mutationId}/valider`,
    { commentaire },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const rejeterMutation = async (mutationId, raison) => {
  const response = await axios.post(
    `${API_URL}/api/sirh/mutations/${mutationId}/rejeter`,
    { raison },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

const sirhService = {
  // Fiche agent
  getFicheAgentDetaillee,
  
  // DINACOPE
  getVerificationsDINACOPE,
  envoyerLienVerification,
  getFormulaireVerification,
  soumettreVerification,
  getFraudesDINACOPE,
  
  // Mutations
  creerDemandeMutation,
  getMutations,
  validerMutation,
  rejeterMutation
};

export default sirhService;
