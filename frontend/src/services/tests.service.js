const API_URL = '';

const testsService = {
  // Récupérer les statistiques globales
  getStats: async () => {
        const response = await fetch(`${API_URL}/api/tests/stats`, {
      
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des statistiques');
    }
    
    return response.json();
  },

  // Récupérer tous les résultats (avec filtre optionnel par catégorie)
  getResultats: async (categorie = null) => {
        const url = categorie 
      ? `${API_URL}/api/tests/resultats?categorie=${categorie}`
      : `${API_URL}/api/tests/resultats`;
    
    const response = await fetch(url, {
      
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des résultats');
    }
    
    return response.json();
  },

  // Récupérer toutes les catégories avec stats
  getCategories: async () => {
        const response = await fetch(`${API_URL}/api/tests/categories`, {
      
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des catégories');
    }
    
    return response.json();
  },

  // Récupérer les établissements éligibles
  getEtablissementsEligibles: async () => {
        const response = await fetch(`${API_URL}/api/tests/etablissements-eligibles`, {
      
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des établissements éligibles');
    }
    
    return response.json();
  }
};

export default testsService;
