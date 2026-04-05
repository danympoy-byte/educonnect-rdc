import React, { useState, useEffect } from 'react';
import { X, UserPlus } from 'lucide-react';
import toast from 'react-hot-toast';
import UserSearchInput from './UserSearchInput';

const DelegationModal = ({ document, onClose, onSuccess }) => {
  const [destinataireId, setDestinataireId] = useState('');
  const [motif, setMotif] = useState('');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);

  const API_URL = '';
    useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
    }
  };

  const handleDelegation = async () => {
    if (!destinataireId || !motif.trim()) {
      toast.error('Veuillez sélectionner un utilisateur et fournir un motif');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/documents/${document.id}/deleguer`, {
        method: 'POST',
        headers: {          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          destinataire_id: destinataireId,
          motif: motif
        })
      });

      if (response.ok) {
        toast.success('Tâche déléguée avec succès');
        onSuccess();
        onClose();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur lors de la délégation');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-2">
              <UserPlus className="w-6 h-6 text-blue-500" />
              <h3 className="text-xl font-bold text-gray-900">Déléguer la tâche</h3>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Info */}
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              📄 Document : <span className="font-medium">{document.titre}</span>
            </p>
          </div>

          {/* Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Déléguer à *
              </label>
              <UserSearchInput
                users={users}
                selectedUserId={destinataireId}
                onSelect={(user) => setDestinataireId(user.id)}
                placeholder="Rechercher un utilisateur..."
                required={true}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif de délégation *
              </label>
              <textarea
                value={motif}
                onChange={(e) => setMotif(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                rows="4"
                placeholder="Expliquez pourquoi vous déléguez cette tâche..."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleDelegation}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'En cours...' : 'Déléguer'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DelegationModal;
