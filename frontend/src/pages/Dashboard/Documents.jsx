import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import DocumentManagement from '../../components/dashboards/components/DocumentManagement';
import ChatGED from '../../components/chat/ChatGED';
import RapportsTrimestriels from '../../components/dashboards/components/RapportsTrimestriels';

const Documents = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('documents');

  // Rôles autorisés à voir les rapports
  const rapportsRoles = [
    'administrateur_technique', 'ministre', 'ministre_provincial', 'proved',
    'ipp', 'diprocope', 'secretaire_general', 'directeur_provincial',
    'inspecteur_pedagogique', 'agent_dinacope'
  ];
  const showRapports = rapportsRoles.includes(user?.role);

  return (
    <div className="space-y-6">
      {/* Onglets */}
      <div className="flex space-x-4 border-b">
        <button
          onClick={() => setActiveTab('documents')}
          data-testid="tab-documents"
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'documents'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Documents
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          data-testid="tab-conversations"
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'chat'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Conversations
        </button>
        {showRapports && (
          <button
            onClick={() => setActiveTab('rapports')}
            data-testid="tab-rapports"
            className={`px-4 py-2 font-medium transition ${
              activeTab === 'rapports'
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Rapports
          </button>
        )}
      </div>

      {/* Contenu */}
      {activeTab === 'documents' && <DocumentManagement user={user} />}
      {activeTab === 'chat' && <ChatGED />}
      {activeTab === 'rapports' && showRapports && <RapportsTrimestriels user={user} />}
    </div>
  );
};

export default Documents;
