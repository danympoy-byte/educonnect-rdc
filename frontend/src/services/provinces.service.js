import api from './api';

const provincesService = {
  async getAll() {
    const response = await api.get('/provinces');
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/provinces/${id}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/provinces', data);
    return response.data;
  },

  async getSousDivisions(provinceId = null) {
    const url = provinceId ? `/sous-divisions?province_id=${provinceId}` : '/sous-divisions';
    const response = await api.get(url);
    return response.data;
  },

  async createSousDivision(data) {
    const response = await api.post('/sous-divisions', data);
    return response.data;
  },
};

export default provincesService;
