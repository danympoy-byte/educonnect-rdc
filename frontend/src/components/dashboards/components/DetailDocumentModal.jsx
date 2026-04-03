import React, { useState } from 'react';
import toast from 'react-hot-toast';
import documentsService from '../../../services/documents.service';
import DocumentLockButton from '../../common/DocumentLockButton';
import BypassModal from '../../common/BypassModal';
import DelegationModal from '../../common/DelegationModal';
import TransmissionExterneModal from '../../common/TransmissionExterneModal';
import { Send, UserPlus, AlertTriangle } from 'lucide-react';

const DetailDocumentModal = ({ document, user, onClose }) => {
  const [localDocument, setLocalDocument] = useState(document);
  const [commentaire, setCommentaire] = useState('');
  const [raisonRefus, setRaisonRefus] = useState('');
  const [showRefusForm, setShowRefusForm] = useState(false);
  const [showBypassModal, setShowBypassModal] = useState(false);
  const [showDelegationModal, setShowDelegationModal] = useState(false);
  const [showTransmissionModal, setShowTransmissionModal] = useState(false);

  const handleLockChange = (updatedDocument) => {
    setLocalDocument({ ...localDocument, document: updatedDocument });
  };

  const handlePrendreEnCharge = async () => {
    try {
      await documentsService.prendreEnCharge(document.document.id, true);
      toast.success('Document pris en charge');
      onClose();
    } catch {
      toast.error('Erreur lors de la prise en charge');
    }
  };

  const handleRefuser = async () => {
    if (!raisonRefus.trim()) {
      toast.error('La raison du refus est obligatoire');
      return;
    }
    try {
      await documentsService.prendreEnCharge(document.document.id, false, raisonRefus);
      toast.success('Document refusé');
      onClose();
    } catch {
      toast.error('Erreur lors du refus');
    }
  };

  const handleAjouterCommentaire = async () => {
    if (!commentaire.trim()) return;
    try {
      await documentsService.ajouterCommentaire(document.document.id, commentaire);
      toast.success('Commentaire ajouté');
      setCommentaire('');
      onClose();
    } catch {
      toast.error("Erreur lors de l'ajout du commentaire");
    }
  };

  const estProprietaire = document.document.proprietaire_actuel_id === user.id;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 data-testid="detail-doc-title" className="text-2xl font-bold text-gray-900">{document.document.titre}</h3>
              <p className="text-sm text-gray-500 mt-1">Réf: {document.document.numero_reference}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600" data-testid="close-detail-modal">
              <span className="text-2xl">&times;</span>
            </button>
          </div>

          {/* Infos document */}
          <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
            <div><p className="text-sm text-gray-600">Type</p><p className="font-medium">{document.document.type_document}</p></div>
            <div><p className="text-sm text-gray-600">Statut</p><p className="font-medium">{document.document.statut}</p></div>
            <div><p className="text-sm text-gray-600">Créateur</p><p className="font-medium">{document.document.createur_nom}</p></div>
            <div><p className="text-sm text-gray-600">Propriétaire actuel</p><p className="font-medium">{document.document.proprietaire_actuel_nom}</p></div>
            <div><p className="text-sm text-gray-600">Destinataire final</p><p className="font-medium">{document.document.destinataire_final_nom}</p></div>
            <div><p className="text-sm text-gray-600">Date de création</p><p className="font-medium">{new Date(document.document.date_creation).toLocaleString('fr-FR')}</p></div>
          </div>

          {/* Description */}
          {document.document.description && (
            <div className="mb-6">
              <h4 className="font-semibold text-gray-900 mb-2">Description</h4>
              <p className="text-gray-700">{document.document.description}</p>
            </div>
          )}

          {/* Actions si propriétaire */}
          {estProprietaire && document.document.statut === 'en_attente' && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">Actions requises</h4>
              <div className="flex space-x-3">
                <button onClick={handlePrendreEnCharge} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700" data-testid="btn-prendre-en-charge">
                  Prendre en charge
                </button>
                <button onClick={() => setShowRefusForm(!showRefusForm)} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700" data-testid="btn-refuser">
                  Refuser
                </button>
              </div>
              {showRefusForm && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Raison du refus (obligatoire)</label>
                  <textarea value={raisonRefus} onChange={(e) => setRaisonRefus(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg" rows="3" placeholder="Expliquez pourquoi vous refusez ce document..." />
                  <button onClick={handleRefuser} className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700" data-testid="btn-confirmer-refus">Confirmer le refus</button>
                </div>
              )}
            </div>
          )}

          {/* Section Verrouillage */}
          <div className="border-t pt-4 mb-6">
            <h4 className="font-semibold text-gray-900 mb-3">Verrouillage du document</h4>
            <DocumentLockButton document={localDocument.document} onLockChange={handleLockChange} />
          </div>

          {/* Section Actions avancées */}
          <div className="border-t pt-4 mb-6">
            <h4 className="font-semibold text-gray-900 mb-3">Actions avancées</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <button onClick={() => setShowBypassModal(true)} className="flex items-center justify-center gap-2 px-4 py-3 bg-orange-50 text-orange-700 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors" data-testid="btn-bypass">
                <AlertTriangle className="w-4 h-4" /><span className="font-medium">Bypass</span>
              </button>
              <button onClick={() => setShowDelegationModal(true)} className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors" data-testid="btn-deleguer">
                <UserPlus className="w-4 h-4" /><span className="font-medium">Déléguer</span>
              </button>
              <button onClick={() => setShowTransmissionModal(true)} className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors" data-testid="btn-transmettre">
                <Send className="w-4 h-4" /><span className="font-medium">Transmettre</span>
              </button>
            </div>
          </div>

          {/* Historique */}
          <div className="mb-6">
            <h4 className="font-semibold text-gray-900 mb-3">Historique des actions</h4>
            <div className="space-y-2">
              {document.historique.map((action, index) => (
                <div key={action.id || `${action.date_action}-${index}`} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{action.user_nom}</p>
                    <p className="text-sm text-gray-600">{action.type_action}</p>
                    {action.commentaire && <p className="text-sm text-gray-500 mt-1">{action.commentaire}</p>}
                    {action.raison_rejet && <p className="text-sm text-red-600 mt-1">Raison: {action.raison_rejet}</p>}
                  </div>
                  <span className="text-xs text-gray-400">{new Date(action.date_action).toLocaleString('fr-FR')}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Ajouter commentaire */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Ajouter un commentaire</h4>
            <textarea value={commentaire} onChange={(e) => setCommentaire(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg" rows="3" placeholder="Votre commentaire..." />
            <button onClick={handleAjouterCommentaire} className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700" data-testid="btn-ajouter-commentaire">Ajouter</button>
          </div>
        </div>
      </div>

      {/* Modals d'action */}
      {showBypassModal && (
        <BypassModal document={localDocument.document} onClose={() => setShowBypassModal(false)} onSuccess={() => { setShowBypassModal(false); onClose(); }} />
      )}
      {showDelegationModal && (
        <DelegationModal document={localDocument.document} onClose={() => setShowDelegationModal(false)} onSuccess={() => { setShowDelegationModal(false); onClose(); }} />
      )}
      {showTransmissionModal && (
        <TransmissionExterneModal document={localDocument.document} onClose={() => setShowTransmissionModal(false)} onSuccess={() => { setShowTransmissionModal(false); onClose(); }} />
      )}
    </div>
  );
};

export default DetailDocumentModal;
