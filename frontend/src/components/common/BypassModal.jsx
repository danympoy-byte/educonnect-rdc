import React, { useState } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

const BypassModal = ({ document, onClose, onSuccess }) => {
  const [etapeSelectionnee, setEtapeSelectionnee] = useState('');
  const [motif, setMotif] = useState('');
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.REACT_APP_BACKEND_URL;
    const handleBypass = async () => {
    if (!etapeSelectionnee || !motif.trim()) {
      toast.error('Veuillez sélectionner une étape et fournir un motif');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/documents/${document.id}/bypass-etape`, {
        method: 'POST',
        headers: {          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          etape_numero: parseInt(etapeSelectionnee),
          motif: motif
        })
      });

      if (response.ok) {
        toast.success('Étape contournée avec succès');
        onSuccess();
        onClose();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur lors du bypass');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  // Générer la liste des étapes du circuit
  const etapes = document.circuit_validation?.map((userId, index) => ({
    numero: index + 1,
    userId: userId
  })) || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-lg w-full">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-orange-500" />
              <h3 className="text-xl font-bold text-gray-900">Bypass / Dérogation</h3>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Warning */}
          <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-sm text-orange-800">
              ⚠️ Cette action permet de contourner une étape du circuit de validation. Elle doit être justifiée.
            </p>
          </div>

          {/* Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Étape à contourner *
              </label>
              <select
                value={etapeSelectionnee}
                onChange={(e) => setEtapeSelectionnee(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
              >
                <option value="">-- Sélectionner une étape --</option>
                {etapes.map((etape) => (
                  <option key={etape.numero} value={etape.numero}>
                    Étape {etape.numero}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif de dérogation *
              </label>
              <textarea
                value={motif}
                onChange={(e) => setMotif(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                rows="4"
                placeholder="Expliquez pourquoi cette étape doit être contournée..."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleBypass}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'En cours...' : 'Contourner l\'étape'}
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

export default BypassModal;
