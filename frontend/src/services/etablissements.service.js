import api from './api';

const etablissementsService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.province_id) params.append('province_id', filters.province_id);
    if (filters.sous_division_id) params.append('sous_division_id', filters.sous_division_id);
    if (filters.type) params.append('type', filters.type);
    
    const url = `/etablissements${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/etablissements/${id}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/etablissements', data);
    return response.data;
  },
};

export default etablissementsService;
