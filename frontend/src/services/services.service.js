import api from './api';

const servicesService = {
  async getAll() {
    const response = await api.get('/services/all');
    return response.data;
  },

  async getByNiveau(niveau) {
    const response = await api.get(`/services/niveau/${niveau}`);
    return response.data;
  },

  async getDropdownCascade() {
    const response = await api.get('/services/dropdown-cascade');
    return response.data;
  },

  async getHierarchie(serviceId) {
    const response = await api.get(`/services/hierarchie/${serviceId}`);
    return response.data;
  },

  async getById(serviceId) {
    const response = await api.get(`/services/${serviceId}`);
    return response.data;
  }
};

export default servicesService;
