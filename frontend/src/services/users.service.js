import api from './api';

const usersService = {
  async getAll(role = null) {
    const url = role ? `/users?role=${role}` : '/users';
    const response = await api.get(url);
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },
};

export default usersService;
