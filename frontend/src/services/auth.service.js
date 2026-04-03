import api from './api';

const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    // Le cookie httpOnly est automatiquement défini par le serveur
    // On stocke uniquement les infos utilisateur (non sensibles) dans localStorage
    if (response.data.user) {
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  async logout() {
    // Appeler le backend pour supprimer le cookie httpOnly
    await api.post('/auth/logout');
    // Nettoyer les données locales
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken() {
    // Les cookies httpOnly ne sont pas accessibles en JavaScript
    // Le navigateur les envoie automatiquement
    return null;
  },

  isAuthenticated() {
    // Vérifier si l'utilisateur est stocké localement
    // La vraie authentification se fait côté serveur via le cookie
    return !!this.getCurrentUser();
  },
};

export default authService;
