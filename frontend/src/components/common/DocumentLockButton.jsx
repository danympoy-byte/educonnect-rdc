import React, { useState } from 'react';
import { Lock, Unlock, AlertCircle } from 'lucide-react';
import api from '../../services/api';

const DocumentLockButton = ({ document, onLockChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLock = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post(`/documents/${document.id}/verrouiller`);

      if (response.data) {
        // Rafraîchir le document
        if (onLockChange) {
          onLockChange({ ...document, est_verrouille: true, ...response.data });
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du verrouillage');
    } finally {
      setLoading(false);
    }
  };

  const handleUnlock = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post(`/documents/${document.id}/deverrouiller`);

      if (response.data) {
        if (onLockChange) {
          onLockChange({ ...document, est_verrouille: false, ...response.data });
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du déverrouillage');
    } finally {
      setLoading(false);
    }
  };

  const isLocked = document.est_verrouille;
  
  // Get current user from localStorage
  const userStr = localStorage.getItem('user');
  const currentUser = userStr ? JSON.parse(userStr) : null;
  const lockedByMe = currentUser && document.verrouille_par_user_id === currentUser.id;

  return (
    <div className="space-y-2">
      {/* Bouton de verrouillage */}
      {!isLocked ? (
        <button
          onClick={handleLock}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Lock className="w-4 h-4" />
          {loading ? 'Verrouillage...' : 'Verrouiller le document'}
        </button>
      ) : (
        <div className="space-y-2">
          {/* Badge de statut verrouillé */}
          <div className={`flex items-center gap-2 px-4 py-3 rounded-lg ${
            lockedByMe ? 'bg-yellow-50 border border-yellow-200' : 'bg-red-50 border border-red-200'
          }`}>
            <Lock className={`w-5 h-5 ${lockedByMe ? 'text-yellow-600' : 'text-red-600'}`} />
            <div className="flex-1">
              <p className={`font-medium ${lockedByMe ? 'text-yellow-900' : 'text-red-900'}`}>
                {lockedByMe ? '🔒 Vous avez verrouillé ce document' : '🔒 Document verrouillé'}
              </p>
              {!lockedByMe && document.verrouille_par_user_nom && (
                <p className="text-sm text-red-700">
                  Par {document.verrouille_par_user_nom}
                </p>
              )}
              {document.date_verrouillage && (
                <p className="text-xs text-gray-600 mt-1">
                  Le {new Date(document.date_verrouillage).toLocaleString('fr-FR')}
                </p>
              )}
            </div>
          </div>

          {/* Bouton de déverrouillage (seulement si verrouillé par moi) */}
          {lockedByMe && (
            <button
              onClick={handleUnlock}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              <Unlock className="w-4 h-4" />
              {loading ? 'Déverrouillage...' : 'Déverrouiller le document'}
            </button>
          )}
        </div>
      )}

      {/* Message d'erreur */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Avertissement si document verrouillé par autre utilisateur */}
      {isLocked && !lockedByMe && (
        <div className="flex items-center gap-2 px-4 py-3 bg-orange-50 border border-orange-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-orange-600" />
          <p className="text-sm text-orange-700">
            Vous ne pouvez pas modifier ce document tant qu'il est verrouillé.
          </p>
        </div>
      )}
    </div>
  );
};

export default DocumentLockButton;
