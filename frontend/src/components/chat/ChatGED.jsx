import React, { useState, useEffect, useRef, useMemo } from 'react';
import toast from 'react-hot-toast';
import chatService from '../../services/chat.service';
import authService from '../../services/auth.service';

const ChatGED = () => {
  const [conversations, setConversations] = useState([]);
  const [conversationActive, setConversationActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [nouveauMessage, setNouveauMessage] = useState('');
  const [showNewConv, setShowNewConv] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [utilisateursContactables, setUtilisateursContactables] = useState([]);
  const [searchUser, setSearchUser] = useState(''); // Pour la recherche d'utilisateurs
  
  // Nouvelle conversation
  const [newConvData, setNewConvData] = useState({
    titre: '',
    participants_ids: [],
    premier_message: ''
  });

  const messagesEndRef = useRef(null);
  const currentUser = authService.getCurrentUser();
  const currentUserId = currentUser?.id;

  // Utilisateurs filtrés avec useMemo pour la performance
  const filteredUsers = useMemo(() => {
    if (!searchUser) return utilisateursContactables;
    
    const search = searchUser.toLowerCase();
    return utilisateursContactables.filter(user => 
      user.nom.toLowerCase().includes(search) ||
      user.prenom.toLowerCase().includes(search) ||
      user.service.toLowerCase().includes(search) ||
      (user.email && user.email.toLowerCase().includes(search)) ||
      (user.telephone && user.telephone.includes(search))
    );
  }, [utilisateursContactables, searchUser]);

  useEffect(() => {
    loadConversations();
    loadUtilisateursContactables(); // Charger les utilisateurs au démarrage
    // Polling toutes les 10 secondes pour les nouveaux messages
    const interval = setInterval(loadConversations, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (conversationActive) {
      loadMessages(conversationActive.id);
    }
  }, [conversationActive]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Charger les utilisateurs quand le formulaire s'ouvre
  useEffect(() => {
    if (showNewConv && utilisateursContactables.length === 0) {
      loadUtilisateursContactables();
    }
  }, [showNewConv]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const data = await chatService.listConversations();
      setConversations(data);
    } catch (error) {
    }
  };

  const loadMessages = async (convId) => {
    try {
      const data = await chatService.getMessages(convId);
      setMessages(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des messages');
    }
  };

  const loadUtilisateursContactables = async () => {
    try {
      const data = await chatService.getUtilisateursContactables();
      setUtilisateursContactables(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des utilisateurs');
    }
  };

  const handleCreateConversation = async (e) => {
    e.preventDefault();
    
    // Validation
    if (newConvData.participants_ids.length === 0) {
      toast.error('Veuillez sélectionner au moins un participant');
      return;
    }
    
    try {
      const result = await chatService.createConversation(newConvData);
      toast.success('Conversation créée !');
      setShowNewConv(false);
      setNewConvData({ titre: '', participants_ids: [], premier_message: '' });
      setSearchUser(''); // Réinitialiser la recherche
      loadConversations();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleTerminerConversation = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir terminer cette conversation ? Cette action est irréversible et bloquera l\'envoi de messages.')) {
      return;
    }

    try {
      await chatService.terminerConversation(conversationActive.id);
      toast.success('Conversation terminée');
      loadConversations();
      setConversationActive({ ...conversationActive, statut: 'terminee' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la terminaison');
    }
  };

  const isSuperieurInConversation = () => {
    if (!conversationActive || !conversationActive.participants_info) return false;
    
    // Trouver le niveau le plus bas (= hiérarchiquement le plus haut)
    const niveaux = conversationActive.participants_info.map(p => ({ id: p.id, niveau: p.niveau || 999 }));
    niveaux.sort((a, b) => a.niveau - b.niveau);
    
    // Je suis supérieur si mon ID correspond au plus haut niveau
    return niveaux.length > 0 && niveaux[0].id === currentUserId;
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!nouveauMessage.trim()) return;

    try {
      await chatService.sendMessage(conversationActive.id, nouveauMessage);
      setNouveauMessage('');
      loadMessages(conversationActive.id);
      loadConversations(); // Rafraîchir la liste
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    }
  };

  const handleSearch = async () => {
    if (searchQuery.length < 3) {
      toast.error('Entrez au moins 3 caractères');
      return;
    }

    try {
      const results = await chatService.search(searchQuery);
      setSearchResults(results);
      toast.success(`${results.total_resultats} résultat(s) trouvé(s)`);
    } catch (error) {
      toast.error('Erreur de recherche');
    }
  };

  const handlePrint = async () => {
    if (!conversationActive) return;

    try {
      const data = await chatService.exportConversation(conversationActive.id);
      
      // Créer une fenêtre d'impression de manière sécurisée (sans document.write)
      const printWindow = window.open('', '_blank');
      
      // Créer le contenu HTML de manière sécurisée
      const htmlContent = document.createElement('html');
      
      // Head
      const head = document.createElement('head');
      const title = document.createElement('title');
      title.textContent = `Conversation - ${data.conversation.titre}`;
      const style = document.createElement('style');
      style.textContent = `
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .message { margin: 15px 0; padding: 10px; background: #f5f5f5; border-radius: 8px; }
        .meta { font-size: 12px; color: #666; margin-bottom: 5px; }
        .content { margin-top: 5px; }
      `;
      head.appendChild(title);
      head.appendChild(style);
      
      // Body
      const body = document.createElement('body');
      
      // Header
      const header = document.createElement('div');
      header.className = 'header';
      const h1 = document.createElement('h1');
      h1.textContent = 'Édu-Connect - Conversation';
      const h2 = document.createElement('h2');
      h2.textContent = data.conversation.titre;
      const pParticipants = document.createElement('p');
      pParticipants.textContent = `Participants: ${data.conversation.participants_info.map(p => `${p.prenom} ${p.nom} (${p.service})`).join(', ')}`;
      const pExport = document.createElement('p');
      pExport.textContent = `Exporté le ${new Date(data.date_export).toLocaleString('fr-FR')} par ${data.exporte_par}`;
      header.appendChild(h1);
      header.appendChild(h2);
      header.appendChild(pParticipants);
      header.appendChild(pExport);
      body.appendChild(header);
      
      // Messages
      data.messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        const metaDiv = document.createElement('div');
        metaDiv.className = 'meta';
        const strong = document.createElement('strong');
        strong.textContent = msg.expediteur_nom;
        metaDiv.appendChild(strong);
        metaDiv.appendChild(document.createTextNode(` (${msg.expediteur_service}) - ${new Date(msg.date_envoi).toLocaleString('fr-FR')}`));
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.textContent = msg.contenu;
        
        messageDiv.appendChild(metaDiv);
        messageDiv.appendChild(contentDiv);
        body.appendChild(messageDiv);
      });
      
      htmlContent.appendChild(head);
      htmlContent.appendChild(body);
      
      // Injecter le contenu de manière sécurisée
      printWindow.document.documentElement.replaceWith(htmlContent);
      printWindow.print();
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  return (
    <div className="flex h-[calc(100vh-300px)] bg-white rounded-lg shadow-sm border">
      {/* Liste des conversations */}
      <div className="w-1/3 border-r flex flex-col">
        <div className="p-4 border-b">
          <button
            onClick={() => {
              setShowNewConv(true);
              loadUtilisateursContactables();
            }}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mb-3"
          >
            💬 Nouvelle Conversation
          </button>
          
          {/* Recherche */}
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher..."
              className="flex-1 px-3 py-2 border rounded-lg text-sm"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              className="px-3 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              🔍
            </button>
          </div>
        </div>

        {/* Liste */}
        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => setConversationActive(conv)}
              className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
                conversationActive?.id === conv.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-sm truncate">{conv.titre}</span>
                {conv.messages_non_lus > 0 && (
                  <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {conv.messages_non_lus}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-600 truncate">{conv.dernier_message}</p>
              <p className="text-xs text-gray-400 mt-1">
                {conv.dernier_message_date && new Date(conv.dernier_message_date).toLocaleDateString('fr-FR')}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Zone de messages */}
      <div className="flex-1 flex flex-col">
        {conversationActive ? (
          <>
            {/* Header conversation */}
            <div className="p-4 border-b flex justify-between items-center">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-bold">{conversationActive.titre}</h3>
                  {conversationActive.statut === 'terminee' && (
                    <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                      Terminée
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  {conversationActive.participants_info.map(p => `${p.prenom} ${p.nom}`).join(', ')}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handlePrint}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm"
                >
                  🖨️ Imprimer
                </button>
                {conversationActive.statut !== 'terminee' && isSuperieurInConversation() && (
                  <button
                    onClick={handleTerminerConversation}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
                  >
                    ✕ Terminer
                  </button>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((msg) => (
                <div key={msg.id} className="flex flex-col">
                  <div className="text-xs text-gray-500 mb-1">
                    <strong>{msg.expediteur_nom}</strong> ({msg.expediteur_service}) • 
                    {new Date(msg.date_envoi).toLocaleString('fr-FR')}
                  </div>
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    {msg.contenu}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input message */}
            {conversationActive.statut === 'terminee' ? (
              <div className="p-4 border-t bg-gray-50 text-center text-gray-600">
                Cette conversation a été terminée par le supérieur. Aucun message ne peut être envoyé.
              </div>
            ) : (
              <form onSubmit={handleSendMessage} className="p-4 border-t flex gap-2">
                <input
                  type="text"
                  value={nouveauMessage}
                  onChange={(e) => setNouveauMessage(e.target.value)}
                  placeholder="Tapez votre message..."
                  className="flex-1 px-4 py-2 border rounded-lg"
                />
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Envoyer
                </button>
              </form>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            Sélectionnez une conversation pour commencer
          </div>
        )}
      </div>

      {/* Modal nouvelle conversation */}
      {showNewConv && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Nouvelle Conversation</h3>
            <form onSubmit={handleCreateConversation} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Titre</label>
                <input
                  type="text"
                  value={newConvData.titre}
                  onChange={(e) => setNewConvData({ ...newConvData, titre: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Participants</label>
                
                {/* Barre de recherche */}
                <input
                  type="text"
                  value={searchUser}
                  onChange={(e) => setSearchUser(e.target.value)}
                  placeholder="🔍 Rechercher un utilisateur (nom, prénom, service)..."
                  className="w-full px-3 py-2 border rounded-lg mb-2"
                />
                
                {/* Liste des utilisateurs filtrés */}
                <div className="border rounded-lg max-h-48 overflow-y-auto">
                  {filteredUsers.map(user => {
                      const isSelected = newConvData.participants_ids.includes(user.id);
                      return (
                        <div
                          key={user.id}
                          onClick={() => {
                            if (isSelected) {
                              setNewConvData({
                                ...newConvData,
                                participants_ids: newConvData.participants_ids.filter(id => id !== user.id)
                              });
                            } else {
                              setNewConvData({
                                ...newConvData,
                                participants_ids: [...newConvData.participants_ids, user.id]
                              });
                            }
                          }}
                          className={`p-3 cursor-pointer border-b last:border-b-0 hover:bg-gray-50 ${
                            isSelected ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => {}} // Géré par le onClick du parent
                              className="cursor-pointer"
                            />
                            <div className="flex-1">
                              <p className="font-medium text-gray-900">
                                {user.prenom} {user.nom}
                              </p>
                              <p className="text-xs text-gray-600">
                                {user.service} {user.email && `• ${user.email}`}
                              </p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  
                  {filteredUsers.length === 0 && (
                    <div className="p-4 text-center text-gray-500 text-sm">
                      {searchUser ? 'Aucun utilisateur trouvé' : 'Aucun utilisateur disponible'}
                    </div>
                  )}
                </div>
                
                {/* Participants sélectionnés */}
                {newConvData.participants_ids.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {newConvData.participants_ids.map(userId => {
                      const user = utilisateursContactables.find(u => u.id === userId);
                      return user ? (
                        <span key={userId} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs flex items-center gap-1">
                          {user.prenom} {user.nom}
                          <button
                            type="button"
                            onClick={() => setNewConvData({
                              ...newConvData,
                              participants_ids: newConvData.participants_ids.filter(id => id !== userId)
                            })}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            ✕
                          </button>
                        </span>
                      ) : null;
                    })}
                  </div>
                )}
                
                <p className="text-xs text-gray-500 mt-2">
                  {newConvData.participants_ids.length} participant(s) sélectionné(s). 
                  Seuls vos pairs et subordonnés sont affichés.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Premier message</label>
                <textarea
                  value={newConvData.premier_message}
                  onChange={(e) => setNewConvData({ ...newConvData, premier_message: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                  required
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Créer
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewConv(false)}
                  className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Résultats de recherche */}
      {searchResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Résultats de recherche</h3>
              <button
                onClick={() => setSearchResults(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Conversations ({searchResults.conversations.length})</h4>
                {searchResults.conversations.map(conv => (
                  <div
                    key={conv.id}
                    onClick={() => {
                      setConversationActive(conv);
                      setSearchResults(null);
                    }}
                    className="p-3 bg-gray-50 rounded-lg mb-2 cursor-pointer hover:bg-gray-100"
                  >
                    {conv.titre}
                  </div>
                ))}
              </div>

              <div>
                <h4 className="font-semibold mb-2">Messages ({searchResults.messages.length})</h4>
                {searchResults.messages.map(msg => (
                  <div key={msg.id} className="p-3 bg-gray-50 rounded-lg mb-2">
                    <div className="text-xs text-gray-500 mb-1">
                      {msg.expediteur_nom} • {new Date(msg.date_envoi).toLocaleDateString()}
                    </div>
                    <div className="text-sm">{msg.contenu}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatGED;
