import api from './api';

const chatService = {
  // Créer une conversation
  createConversation: async (data) => {
    const response = await api.post('/chat/conversations', data);
    return response.data;
  },

  // Lister les conversations
  listConversations: async (archive = null) => {
    const params = archive !== null ? { archive } : {};
    const response = await api.get('/chat/conversations', { params });
    return response.data;
  },

  // Détails d'une conversation
  getConversation: async (conversationId) => {
    const response = await api.get(`/chat/conversations/${conversationId}`);
    return response.data;
  },

  // Archiver/Désarchiver
  archiveConversation: async (conversationId, archive) => {
    const response = await api.put(
      `/chat/conversations/${conversationId}/archive`,
      null,
      { params: { archive } }
    );
    return response.data;
  },

  // Envoyer un message
  sendMessage: async (conversationId, contenu) => {
    const response = await api.post(
      `/chat/conversations/${conversationId}/messages`,
      { contenu }
    );
    return response.data;
  },

  // Récupérer les messages
  getMessages: async (conversationId) => {
    const response = await api.get(
      `/chat/conversations/${conversationId}/messages`
    );
    return response.data;
  },

  // Rechercher
  search: async (query) => {
    const response = await api.get('/chat/search', {
      params: { q: query }
    });
    return response.data;
  },

  // Terminer une conversation (supérieur uniquement)
  terminerConversation: async (conversationId) => {
    const response = await api.put(
      `/chat/conversations/${conversationId}/terminer`
    );
    return response.data;
  },

  // Récupérer les utilisateurs contactables (selon hiérarchie)
  getUtilisateursContactables: async () => {
    const response = await api.get('/chat/utilisateurs-contactables');
    return response.data;
  },

  // Exporter une conversation
  exportConversation: async (conversationId) => {
    const response = await api.get(`/chat/conversations/${conversationId}/export`);
    return response.data;
  }
};

export default chatService;
