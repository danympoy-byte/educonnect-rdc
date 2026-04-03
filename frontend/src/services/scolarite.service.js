import api from './api';

const scolariteService = {
  // ============================================
  // GESTION DES CLIENTS API (Admin)
  // ============================================
  
  async creerClientAPI(clientData) {
    const response = await api.post('/admin/api-clients', clientData);
    return response.data;
  },

  async listerClientsAPI() {
    const response = await api.get('/admin/api-clients');
    return response.data;
  },

  async listerLogsAPI(limit = 100) {
    const response = await api.get(`/admin/api-clients/logs?limit=${limit}`);
    return response.data;
  },

  // ============================================
  // STATISTIQUES DE PRÉSENCE
  // ============================================
  
  async obtenirStatistiquesPresence(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.classe_id) queryParams.append('classe_id', params.classe_id);
    if (params.etablissement_id) queryParams.append('etablissement_id', params.etablissement_id);
    if (params.date_debut) queryParams.append('date_debut', params.date_debut);
    if (params.date_fin) queryParams.append('date_fin', params.date_fin);
    
    const response = await api.get(`/presences/statistiques?${queryParams.toString()}`);
    return response.data;
  },

  // ============================================
  // GÉNÉRATION DE BULLETINS (Désactivé)
  // ============================================
  
  // Fonctionnalité désactivée à la demande de l'utilisateur
  // async genererBulletinsAutomatique(classe_id, trimestre, annee_scolaire) {
  //   const response = await api.post('/bulletins/generer-automatique', {
  //     classe_id,
  //     trimestre,
  //     annee_scolaire
  //   });
  //   return response.data;
  // },

  async listerBulletins(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.classe_id) queryParams.append('classe_id', params.classe_id);
    if (params.eleve_id) queryParams.append('eleve_id', params.eleve_id);
    if (params.trimestre) queryParams.append('trimestre', params.trimestre);
    if (params.annee_scolaire) queryParams.append('annee_scolaire', params.annee_scolaire);
    
    const response = await api.get(`/bulletins?${queryParams.toString()}`);
    return response.data;
  }
};

export default scolariteService;
