import api from './api';

const notesService = {
  async getAll(filters = {}) {
    const params = new URLSearchParams();
    if (filters.eleve_id) params.append('eleve_id', filters.eleve_id);
    if (filters.classe_id) params.append('classe_id', filters.classe_id);
    if (filters.trimestre) params.append('trimestre', filters.trimestre);
    if (filters.annee_scolaire) params.append('annee_scolaire', filters.annee_scolaire);
    
    const url = `/notes${params.toString() ? '?' + params.toString() : ''}`;
    const response = await api.get(url);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/notes', data);
    return response.data;
  },

  async update(noteId, noteValue) {
    const response = await api.put(`/notes/${noteId}`, null, {
      params: { note_value: noteValue }
    });
    return response.data;
  },
};

export default notesService;
