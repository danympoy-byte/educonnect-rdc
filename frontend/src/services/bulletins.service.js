import api from './api';

const bulletinsService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.eleve_id) params.append('eleve_id', filters.eleve_id);
    if (filters.classe_id) params.append('classe_id', filters.classe_id);
    
    const url = `/bulletins${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/bulletins/${id}`);
    return response.data;
  },

  async generate(data) {
    const response = await api.post('/bulletins/generate', data);
    return response.data;
  },
};

export default bulletinsService;
