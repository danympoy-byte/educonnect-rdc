import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const inscriptionService = {
  // Étape 1 : Informations personnelles
  async etape1(data) {
    const response = await axios.post(`${API_URL}/api/inscription/etape1`, data);
    return response.data;
  },

  // Étape 2 : Sélection du service
  async etape2(data) {
    const response = await axios.post(`${API_URL}/api/inscription/etape2`, data);
    return response.data;
  },

  // Étape 3 : Complétion du profil
  async etape3(data) {
    const response = await axios.post(`${API_URL}/api/inscription/etape3`, data);
    return response.data;
  },

  // Upload photo de profil
  async uploadPhoto(userId, photoFile) {
    const formData = new FormData();
    formData.append('photo', photoFile);
    
    const response = await axios.post(
      `${API_URL}/api/inscription/upload-photo/${userId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },

  // Récupérer la notification de profil incomplet
  async getNotificationProfil(userId) {
        const response = await axios.get(
      `${API_URL}/api/inscription/notification-profil/${userId}`,
      {
        
      }
    );
    return response.data;
  }
};

export default inscriptionService;
