import api from './api';

const classesService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.etablissement_id) params.append('etablissement_id', filters.etablissement_id);
    
    const url = `/classes${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/classes/${id}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/classes', data);
    return response.data;
  },
};

export default classesService;
