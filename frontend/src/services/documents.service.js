import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const getAuthHeader = () => {
    return { };
};

const documentsService = {
  // Créer un document
  async create(formData) {
    const response = await axios.post(
      `${API_URL}/api/documents/`,
      formData,
      {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },

  // Lister les documents
  async getAll(statut = null) {
    const params = statut ? { statut } : {};
    const response = await axios.get(`${API_URL}/api/documents/`, {
      headers: getAuthHeader(),
      params
    });
    return response.data;
  },

  // Obtenir un document par ID
  async getById(id) {
    const response = await axios.get(`${API_URL}/api/documents/${id}`, {
      headers: getAuthHeader()
    });
    return response.data;
  },

  // Prendre en charge un document
  async prendreEnCharge(id, accepter, raisonRefus = null) {
    const response = await axios.post(
      `${API_URL}/api/documents/${id}/prendre-en-charge`,
      { accepter, raison_refus: raisonRefus },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Transmettre un document
  async transmettre(id, destinataireId, destinataireNom, commentaire = null) {
    const response = await axios.post(
      `${API_URL}/api/documents/${id}/transmettre`,
      {
        destinataire_id: destinataireId,
        destinataire_nom: destinataireNom,
        commentaire
      },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Valider un document
  async valider(id, commentaire = null) {
    const response = await axios.post(
      `${API_URL}/api/documents/${id}/valider`,
      { commentaire },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Ajouter un commentaire
  async ajouterCommentaire(id, contenu, estInterne = true) {
    const response = await axios.post(
      `${API_URL}/api/documents/${id}/commentaires`,
      { contenu, est_interne: estInterne },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Télécharger un document
  async telecharger(id, nomFichier) {
    const response = await axios.get(
      `${API_URL}/api/documents/${id}/telecharger`,
      {
        headers: getAuthHeader(),
        responseType: 'blob'
      }
    );
    
    // Créer un lien de téléchargement
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', nomFichier);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    return response.data;
  },

  // Obtenir les statistiques dashboard
  async getStats() {
    const response = await axios.get(`${API_URL}/api/documents/stats/dashboard`, {
      headers: getAuthHeader()
    });
    return response.data;
  },

  // Rechercher des documents
  async search(query, filters = {}) {
    const params = { q: query, ...filters };
    const response = await axios.get(`${API_URL}/api/documents/search`, {
      headers: getAuthHeader(),
      params
    });
    return response.data;
  },

  // Avancer dans le circuit de validation
  async avancerCircuit(id, commentaire = null) {
    const response = await axios.post(
      `${API_URL}/api/documents/${id}/avancer-circuit`,
      { commentaire },
      { headers: getAuthHeader() }
    );
    return response.data;
  },

  // Récupérer la liste des modèles (templates)
  async getTemplates() {
    const response = await axios.get(`${API_URL}/api/documents/templates/list`, {
      headers: getAuthHeader()
    });
    return response.data;
  }
};

export default documentsService;
