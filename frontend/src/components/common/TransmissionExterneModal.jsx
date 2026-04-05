import React, { useState, useEffect } from 'react';
import { X, Send, Mail } from 'lucide-react';
import toast from 'react-hot-toast';

const TransmissionExterneModal = ({ document, onClose, onSuccess }) => {
  const [entiteId, setEntiteId] = useState('');
  const [email, setEmail] = useState('');
  const [objet, setObjet] = useState(`Document: ${document.titre}`);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [entites, setEntites] = useState([]);

  const API_URL = '';
    useEffect(() => {
    loadEntites();
  }, []);

  const loadEntites = async () => {
    try {
      const response = await fetch('/api/entites-externes', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setEntites(data);
      }
    } catch (error) {
      console.error('Failed to load entites:', error);
    }
  };

  const handleEntiteSelect = (e) => {
    const id = e.target.value;
    setEntiteId(id);
    
    // Pré-remplir l'email si une entité est sélectionnée
    if (id) {
      const entite = entites.find(ent => ent.id === id);
      if (entite && entite.email) {
        setEmail(entite.email);
      }
    }
  };

  const handleTransmission = async () => {
    if (!email.trim() || !objet.trim()) {
      toast.error('Email et objet sont obligatoires');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/documents/${document.id}/transmettre-externe`, {
        method: 'POST',
        headers: {          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          entite_id: entiteId || null,
          email: email,
          objet: objet,
          message: message
        })
      });

      if (response.ok) {
        toast.success('Document transmis par email avec succès');
        onSuccess();
        onClose();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur lors de la transmission');
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
              <Send className="w-6 h-6 text-purple-500" />
              <h3 className="text-xl font-bold text-gray-900">Transmission Externe</h3>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Info */}
          <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-purple-800">
              📄 Document : <span className="font-medium">{document.titre}</span>
            </p>
            <p className="text-xs text-purple-600 mt-1">
              Référence : {document.numero_reference}
            </p>
          </div>

          {/* Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Entité externe (optionnel)
              </label>
              <select
                value={entiteId}
                onChange={handleEntiteSelect}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="">-- Saisir manuellement l'email --</option>
                {entites.map((entite) => (
                  <option key={entite.id} value={entite.id}>
                    {entite.nom} ({entite.type})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Email destinataire *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                placeholder="exemple@organisation.cd"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Objet *
              </label>
              <input
                type="text"
                value={objet}
                onChange={(e) => setObjet(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message (optionnel)
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                rows="3"
                placeholder="Ajoutez un message d'accompagnement..."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleTransmission}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? 'Envoi en cours...' : (
                <>
                  <Send className="w-4 h-4" />
                  Envoyer par email
                </>
              )}
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

export default TransmissionExterneModal;
