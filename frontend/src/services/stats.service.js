import api from './api';

const statsService = {
  async getGlobalStats() {
    const response = await api.get('/stats/global');
    return response.data;
  },

  async getProvinceStats(provinceId) {
    const response = await api.get(`/stats/province/${provinceId}`);
    return response.data;
  },

  async getStatsSexe() {
    const response = await api.get('/stats/sexe');
    return response.data;
  },
};

export default statsService;
