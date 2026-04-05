import React, { useState, useEffect } from 'react';
import { X, FileText, Image as ImageIcon, Download, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const PreviewModal = ({ document, onClose }) => {
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = '';
    useEffect(() => {
    loadPreview();
  }, []);

  const loadPreview = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/preview/document/${document.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors du chargement de la prévisualisation');
      }
    } catch (err) {
      setError('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (previewData?.fichier_url) {
      window.open(`${API_URL}${previewData.fichier_url}`, '_blank');
    }
  };

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
          <p className="text-gray-600">Chargement de la prévisualisation...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <FileText className="w-16 h-16 text-red-400 mb-4" />
          <p className="text-red-600 font-medium mb-2">Impossible de prévisualiser ce document</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      );
    }

    if (!previewData) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <FileText className="w-16 h-16 text-gray-400 mb-4" />
          <p className="text-gray-600">Aucune prévisualisation disponible</p>
        </div>
      );
    }

    // Prévisualisation selon le type
    const type = previewData.type_fichier?.toLowerCase() || '';

    // Images
    if (type.includes('image') || previewData.format_supportes?.includes('image')) {
      return (
        <div className="flex items-center justify-center bg-gray-100 rounded-lg p-4">
          <img 
            src={`${API_URL}${previewData.fichier_url}`}
            alt={document.titre}
            className="max-w-full max-h-[600px] object-contain rounded shadow-lg"
          />
        </div>
      );
    }

    // PDF
    if (type.includes('pdf')) {
      return (
        <div className="bg-gray-100 rounded-lg p-4">
          <iframe
            src={`${API_URL}${previewData.fichier_url}`}
            className="w-full h-[600px] border-0 rounded"
            title={document.titre}
          />
        </div>
      );
    }

    // Texte extrait (pour DOCX et autres)
    if (previewData.texte_extrait) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg p-6 max-h-[600px] overflow-y-auto">
          <div className="prose max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
              {previewData.texte_extrait}
            </pre>
          </div>
        </div>
      );
    }

    // Métadonnées uniquement
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-12 h-12 text-gray-400" />
          <div>
            <h4 className="font-semibold text-gray-900">{document.titre}</h4>
            <p className="text-sm text-gray-600">Type: {previewData.type_fichier}</p>
          </div>
        </div>

        {previewData.metadata && (
          <div className="space-y-2">
            <h5 className="font-medium text-gray-900">Métadonnées :</h5>
            {Object.entries(previewData.metadata).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600">{key}:</span>
                <span className="text-gray-900 font-medium">{value}</span>
              </div>
            ))}
          </div>
        )}

        <p className="text-sm text-gray-600 mt-4">
          ℹ️ La prévisualisation complète n'est pas disponible pour ce type de fichier.
          Vous pouvez télécharger le document pour le consulter.
        </p>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{document.titre}</h3>
              <p className="text-sm text-gray-500 mt-1">Réf: {document.numero_reference}</p>
            </div>
            <div className="flex items-center gap-2">
              {previewData?.fichier_url && (
                <button
                  onClick={handleDownload}
                  className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="Télécharger"
                >
                  <Download className="w-5 h-5" />
                </button>
              )}
              <button 
                onClick={onClose} 
                className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Preview Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {renderPreview()}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {previewData && (
                <span>
                  Type: <span className="font-medium">{previewData.type_fichier}</span>
                  {previewData.taille_fichier && (
                    <> • Taille: <span className="font-medium">{(previewData.taille_fichier / 1024).toFixed(2)} KB</span></>
                  )}
                </span>
              )}
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreviewModal;
