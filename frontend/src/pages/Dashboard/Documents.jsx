import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import DocumentManagement from '../../components/dashboards/components/DocumentManagement';
import ChatGED from '../../components/chat/ChatGED';

const Documents = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('documents'); // 'documents' ou 'chat'

  return (
    <div className="space-y-6">
      {/* Onglets */}
      <div className="flex space-x-4 border-b">
        <button
          onClick={() => setActiveTab('documents')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'documents'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📄 Documents
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-4 py-2 font-medium transition ${
            activeTab === 'chat'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          💬 Conversations
        </button>
      </div>

      {/* Contenu */}
      {activeTab === 'documents' ? (
        <DocumentManagement user={user} />
      ) : (
        <ChatGED />
      )}
    </div>
  );
};

export default Documents;
