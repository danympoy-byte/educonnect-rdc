import api from './api';

const enseignantsService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.etablissement_id) params.append('etablissement_id', filters.etablissement_id);
    
    const url = `/enseignants${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/enseignants/${id}`);
    return response.data;
  },

  async getByUser(userId) {
    const response = await api.get(`/enseignants/by-user/${userId}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/enseignants', data);
    return response.data;
  },
};

export default enseignantsService;
