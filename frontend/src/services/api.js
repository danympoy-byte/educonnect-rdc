import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Envoie automatiquement les cookies httpOnly
  headers: {
    'Content-Type': 'application/json',
  },
});

// Les cookies httpOnly sont envoyés automatiquement par le navigateur
// Plus besoin d'intercepteur pour ajouter le token manuellement

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Cookie expiré ou invalide - nettoyer et rediriger
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
