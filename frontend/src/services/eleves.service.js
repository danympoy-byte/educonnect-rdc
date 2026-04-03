import api from './api';

const elevesService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.etablissement_id) params.append('etablissement_id', filters.etablissement_id);
    if (filters.classe_id) params.append('classe_id', filters.classe_id);
    
    const url = `/eleves${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/eleves/${id}`);
    return response.data;
  },

  async getByUser(userId) {
    const response = await api.get(`/eleves/by-user/${userId}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/eleves', data);
    return response.data;
  },
};

export default elevesService;
