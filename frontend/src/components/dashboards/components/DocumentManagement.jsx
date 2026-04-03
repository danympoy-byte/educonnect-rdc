import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import documentsService from '../../../services/documents.service';
import usersService from '../../../services/users.service';
import DocumentStats from './DocumentStats';
import DetailDocumentModal from './DetailDocumentModal';
import UserSearchInput from '../../common/UserSearchInput';
import MultiUserSearchInput from '../../common/MultiUserSearchInput';
import ContexteSwitcher from '../../common/ContexteSwitcher';
import PlanClassementSelector from '../../common/PlanClassementSelector';
import PreviewModal from '../../common/PreviewModal';
import { Eye, Search } from 'lucide-react';

const INITIAL_FORM = {
  titre: '', description: '', type_document: 'administratif', categorie: '',
  destinataire_final_id: '', destinataire_final_nom: '',
  circuit_validation: [], circuit_validation_roles: {},
  collaborateurs_ids: [], niveau_diffusion: 'prive', mode_livraison: 'interne',
  niveau_confidentialite: 'public', necessite_signature: false, fichier: null,
  template_name: '', template_description: '', plan_classement_id: ''
};

const STATUT_BADGES = {
  'brouillon': { cls: 'bg-gray-100 text-gray-800', label: 'Brouillon' },
  'en_attente': { cls: 'bg-yellow-100 text-yellow-800', label: 'En attente' },
  'en_cours': { cls: 'bg-blue-100 text-blue-800', label: 'En cours' },
  'valide': { cls: 'bg-green-100 text-green-800', label: 'Validé' },
  'rejete': { cls: 'bg-red-100 text-red-800', label: 'Rejeté' },
  'archive': { cls: 'bg-gray-100 text-gray-600', label: 'Archivé' }
};

const getStatutBadge = (statut) => {
  const badge = STATUT_BADGES[statut] || { cls: 'bg-gray-100 text-gray-800', label: statut };
  return <span className={`px-2 py-1 rounded-full text-xs font-medium ${badge.cls}`}>{badge.label}</span>;
};

const DocumentManagement = ({ user }) => {
  const [documents, setDocuments] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [users, setUsers] = useState([]);
  const [showSearchFilters, setShowSearchFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatut, setFilterStatut] = useState('');
  const [ocrSearchQuery, setOcrSearchQuery] = useState('');
  const [ocrResults, setOcrResults] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewDocument, setPreviewDocument] = useState(null);
  const [saveAsTemplate, setSaveAsTemplate] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [formData, setFormData] = useState(INITIAL_FORM);

  useEffect(() => { loadDocuments(); loadUsers(); loadTemplates(); }, []);

  const loadDocuments = async () => {
    try {
      let data;
      if (searchQuery || filterType || filterStatut) {
        data = await documentsService.search(searchQuery, { type_document: filterType, statut: filterStatut });
        setDocuments(data.documents || data);
      } else {
        data = await documentsService.getAll();
        setDocuments(data);
      }
    } catch {
      toast.error('Erreur lors du chargement des documents');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try { setUsers(await usersService.getAll()); } catch { /* silenced */ }
  };

  const loadTemplates = async () => {
    try { setTemplates(await documentsService.getTemplates()); } catch { /* silenced */ }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplateId(templateId);
    if (templateId) {
      const template = templates.find(t => t.id === templateId);
      if (template) {
        setFormData({
          ...formData, titre: template.titre || '', description: template.description || '',
          type_document: template.type_document || 'administratif', categorie: template.categorie || '',
          circuit_validation: template.circuit_validation || [],
          niveau_diffusion: template.niveau_diffusion || 'prive',
          mode_livraison: template.mode_livraison || 'interne',
          niveau_confidentialite: template.niveau_confidentialite || 'public',
          necessite_signature: template.necessite_signature || false
        });
        toast.success(`Modèle "${template.template_name}" chargé`);
      }
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.size > 50 * 1024 * 1024) { toast.error('Fichier trop volumineux (max 50MB)'); return; }
    setFormData({ ...formData, fichier: file });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (saveAsTemplate && !formData.template_name) { toast.error('Veuillez saisir un nom pour le modèle'); return; }

    const fd = new FormData();
    fd.append('titre', formData.titre);
    fd.append('description', formData.description || '');
    fd.append('type_document', formData.type_document);
    fd.append('categorie', formData.categorie || '');
    fd.append('destinataire_final_id', formData.destinataire_final_id);
    fd.append('destinataire_final_nom', formData.destinataire_final_nom);
    fd.append('circuit_validation', formData.circuit_validation.join(','));
    const roles = formData.circuit_validation.map(uid => formData.circuit_validation_roles[uid] || 'contributeur');
    fd.append('circuit_validation_roles', roles.join(','));
    fd.append('collaborateurs_ids', formData.collaborateurs_ids.join(','));
    fd.append('niveau_diffusion', formData.niveau_diffusion);
    fd.append('mode_livraison', formData.mode_livraison);
    fd.append('niveau_confidentialite', formData.niveau_confidentialite);
    fd.append('necessite_signature', formData.necessite_signature);
    if (formData.plan_classement_id) fd.append('plan_classement_id', formData.plan_classement_id);
    fd.append('save_as_template', saveAsTemplate);
    if (saveAsTemplate) { fd.append('template_name', formData.template_name); fd.append('template_description', formData.template_description || ''); }
    if (selectedTemplateId) fd.append('load_from_template_id', selectedTemplateId);
    if (formData.fichier) fd.append('fichier', formData.fichier);

    try {
      const response = await documentsService.create(fd);
      const msg = saveAsTemplate ? `Modèle "${formData.template_name}" créé avec succès` : 'Document créé avec succès';
      if (response.validation_n_plus_1_requise && response.n_plus_1) {
        toast.success(`${msg}\nValidation N+1 requise : ${response.n_plus_1.prenom} ${response.n_plus_1.nom}`, { duration: 6000 });
      } else {
        toast.success(msg);
      }
      setShowCreateForm(false);
      setSaveAsTemplate(false);
      setSelectedTemplateId('');
      setFormData(INITIAL_FORM);
      loadDocuments();
      if (saveAsTemplate) loadTemplates();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleOCRSearch = async () => {
    if (!ocrSearchQuery.trim()) { toast.error('Veuillez saisir un terme de recherche'); return; }
    setOcrLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/recherche/texte-integral?query=${encodeURIComponent(ocrSearchQuery)}`, { headers: {} });
      if (response.ok) {
        const data = await response.json();
        setOcrResults(data);
        toast.success(`${data.resultats?.length || 0} résultat(s) trouvé(s)`);
      } else { toast.error('Erreur lors de la recherche'); }
    } catch { toast.error('Erreur de connexion'); } finally { setOcrLoading(false); }
  };

  const handleViewDetail = async (doc) => {
    try {
      setSelectedDocument(await documentsService.getById(doc.id));
      setShowDetail(true);
    } catch { toast.error('Erreur lors du chargement des détails'); }
  };

  if (loading) return <div className="text-center py-8">Chargement...</div>;

  return (
    <div className="space-y-6" data-testid="document-management">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Gestion Documentaire</h2>
        <button onClick={() => setShowSearchFilters(!showSearchFilters)} className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition" data-testid="btn-rechercher">
          Rechercher
        </button>
      </div>

      {/* Recherche OCR */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <Search className="w-5 h-5 text-purple-600 flex-shrink-0" />
          <div className="flex-1 flex gap-2">
            <input type="text" value={ocrSearchQuery} onChange={(e) => setOcrSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleOCRSearch()}
              placeholder="Recherche plein texte dans les documents (OCR)..."
              className="flex-1 px-4 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              data-testid="ocr-search-input" />
            <button onClick={handleOCRSearch} disabled={ocrLoading}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              data-testid="btn-ocr-search">
              {ocrLoading ? 'Recherche...' : 'Rechercher'}
            </button>
            {ocrResults && (
              <button onClick={() => { setOcrSearchQuery(''); setOcrResults(null); }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition">Effacer</button>
            )}
          </div>
        </div>
        {ocrResults && (
          <div className="mt-3 p-3 bg-white rounded-lg border border-purple-200">
            <p className="text-sm font-medium text-purple-900">{ocrResults.resultats?.length || 0} document(s) trouvé(s) contenant "{ocrSearchQuery}"</p>
            {ocrResults.resultats?.length > 0 && (
              <div className="mt-2 space-y-1">
                {ocrResults.resultats.map((result, idx) => (
                  <div key={result.id || idx} className="text-sm text-gray-700">
                    {result.titre || result.document_titre} - <span className="text-purple-600">{result.correspondances || 0} occurrence(s)</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Contexte */}
      <ContexteSwitcher onContextChange={() => loadDocuments()} />
      <DocumentStats />

      {/* Bouton Nouveau */}
      <div className="flex justify-center">
        <button onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition shadow-md text-base font-medium"
          data-testid="btn-nouveau-document">+ Nouveau Document</button>
      </div>

      {/* Filtres */}
      {showSearchFilters && (
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="grid grid-cols-4 gap-4">
            <div className="col-span-2">
              <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher par titre, référence, mots-clés..." className="w-full px-4 py-2 border border-gray-300 rounded-lg" data-testid="filter-search-input" />
            </div>
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg" data-testid="filter-type">
              <option value="">Tous les types</option>
              <option value="administratif">Administratif</option><option value="rh">RH</option>
              <option value="financier">Financier</option><option value="pedagogique">Pédagogique</option>
            </select>
            <select value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg" data-testid="filter-statut">
              <option value="">Tous les statuts</option>
              <option value="brouillon">Brouillon</option><option value="en_attente">En attente</option>
              <option value="en_cours">En cours</option><option value="valide">Validé</option><option value="rejete">Rejeté</option>
            </select>
          </div>
          <div className="mt-3 flex space-x-2">
            <button onClick={loadDocuments} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700" data-testid="btn-appliquer-filtres">Rechercher</button>
            <button onClick={() => { setSearchQuery(''); setFilterType(''); setFilterStatut(''); loadDocuments(); }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">Réinitialiser</button>
          </div>
        </div>
      )}

      {/* Formulaire création */}
      {showCreateForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200" data-testid="create-document-form">
          {templates.length > 0 && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <label className="block text-sm font-medium text-blue-900 mb-2">Utiliser un modèle existant (optionnel)</label>
              <select value={selectedTemplateId} onChange={(e) => handleTemplateSelect(e.target.value)} className="w-full px-4 py-2 border border-blue-300 rounded-lg bg-white">
                <option value="">-- Partir de zéro --</option>
                {templates.map((t) => <option key={t.id} value={t.id}>{t.template_name} - {t.type_document}</option>)}
              </select>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Titre *</label>
              <input type="text" value={formData.titre} onChange={(e) => setFormData({ ...formData, titre: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg" required data-testid="input-titre" />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg" rows="3" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type de document *</label>
              <select value={formData.type_document} onChange={(e) => setFormData({ ...formData, type_document: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg" data-testid="select-type-doc">
                <option value="administratif">Administratif</option><option value="rh">Ressources Humaines</option>
                <option value="financier">Financier</option><option value="pedagogique">Pédagogique</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
              <input type="text" value={formData.categorie} onChange={(e) => setFormData({ ...formData, categorie: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="Ex: Note de service" />
            </div>
            <div className="col-span-2">
              <PlanClassementSelector selectedId={formData.plan_classement_id}
                onSelect={(planData) => setFormData({ ...formData, plan_classement_id: planData.id })}
                onClear={() => setFormData({ ...formData, plan_classement_id: '' })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Destinataire final *</label>
              <UserSearchInput users={users} selectedUserId={formData.destinataire_final_id}
                onSelect={(userId, userNom) => setFormData({ ...formData, destinataire_final_id: userId, destinataire_final_nom: userNom })}
                placeholder="Rechercher par nom, prénom ou téléphone..." required={true} label="Destinataire final" />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Circuit de validation (optionnel, max 5 étapes)</label>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-300">
                <p className="text-xs text-gray-600 mb-3">Recherchez et ajoutez jusqu'à 5 validateurs avec leur rôle dans le circuit</p>
                <MultiUserSearchInput users={users} selectedUserIds={formData.circuit_validation}
                  selectedUserRoles={formData.circuit_validation_roles}
                  onSelectionChange={(s) => setFormData({ ...formData, circuit_validation: s })}
                  onRoleChange={(userId, role) => setFormData({ ...formData, circuit_validation_roles: { ...formData.circuit_validation_roles, [userId]: role } })}
                  placeholder="Rechercher un validateur..." maxSelection={5} label="validateurs" color="indigo" withRoles={true}
                  availableRoles={[
                    { value: 'contributeur', label: 'Contributeur', icon: '' },
                    { value: 'visa_correction', label: 'Visa/Relecture', icon: '' },
                    { value: 'signature', label: 'Signature', icon: '' },
                    { value: 'expedition', label: 'Expédition', icon: '' }
                  ]} />
              </div>
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Collaborateurs (optionnel)</label>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-xs text-blue-700 mb-3">
                  Recherchez et ajoutez les personnes qui travailleront avec vous
                  {formData.niveau_diffusion === 'service' && (
                    <span className="block mt-1 text-blue-800 font-medium">Document partagé au service - Validation N+1 requise</span>
                  )}
                </p>
                <MultiUserSearchInput users={users} selectedUserIds={formData.collaborateurs_ids}
                  onSelectionChange={(s) => setFormData({ ...formData, collaborateurs_ids: s })}
                  placeholder="Rechercher un collaborateur..." maxSelection={null} label="collaborateurs" color="blue" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Niveau de diffusion</label>
              <select value={formData.niveau_diffusion} onChange={(e) => setFormData({ ...formData, niveau_diffusion: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="prive">Privé (moi et destinataire)</option><option value="service">Service</option><option value="tous">Tous les services</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mode de livraison</label>
              <select value={formData.mode_livraison} onChange={(e) => setFormData({ ...formData, mode_livraison: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="interne">Usage interne</option><option value="email">Email</option>
                <option value="physique">Dépôt physique</option><option value="citoyen">Remise à un citoyen</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confidentialité</label>
              <select value={formData.niveau_confidentialite} onChange={(e) => setFormData({ ...formData, niveau_confidentialite: e.target.value })} className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option value="public">Public</option><option value="confidentiel">Confidentiel</option><option value="secret">Secret</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Fichier joint (max 50MB)</label>
              <input type="file" onChange={handleFileChange} className="w-full px-4 py-2 border border-gray-300 rounded-lg" accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.xml" />
              {formData.fichier && <p className="text-sm text-gray-500 mt-2">Fichier : {formData.fichier.name} ({(formData.fichier.size / 1024 / 1024).toFixed(2)} MB)</p>}
            </div>
            <div className="col-span-2">
              <label className="flex items-center space-x-2">
                <input type="checkbox" checked={formData.necessite_signature} onChange={(e) => setFormData({ ...formData, necessite_signature: e.target.checked })} className="rounded" />
                <span className="text-sm text-gray-700">Nécessite une signature du ministre</span>
              </label>
            </div>
            <div className="col-span-2 mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <label className="flex items-center space-x-2 mb-3">
                <input type="checkbox" checked={saveAsTemplate} onChange={(e) => setSaveAsTemplate(e.target.checked)} className="rounded text-green-600" />
                <span className="text-sm font-medium text-green-900">Sauvegarder comme modèle réutilisable</span>
              </label>
              {saveAsTemplate && (
                <div className="space-y-3 ml-6">
                  <div>
                    <label className="block text-sm font-medium text-green-900 mb-1">Nom du modèle *</label>
                    <input type="text" value={formData.template_name} onChange={(e) => setFormData({ ...formData, template_name: e.target.value })}
                      className="w-full px-3 py-2 border border-green-300 rounded-lg bg-white" placeholder="Ex: Circulaire administrative type" required={saveAsTemplate} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-green-900 mb-1">Description du modèle</label>
                    <textarea value={formData.template_description} onChange={(e) => setFormData({ ...formData, template_description: e.target.value })}
                      className="w-full px-3 py-2 border border-green-300 rounded-lg bg-white" rows="2" placeholder="Décrivez quand utiliser ce modèle..." />
                  </div>
                </div>
              )}
            </div>
          </div>
          <div className="mt-6 flex space-x-3">
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700" data-testid="btn-submit-document">
              {saveAsTemplate ? 'Créer le modèle' : 'Créer le document'}
            </button>
            <button type="button" onClick={() => setShowCreateForm(false)} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">Annuler</button>
          </div>
        </form>
      )}

      {/* Liste des documents */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" data-testid="documents-table">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Référence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Titre</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Propriétaire</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-indigo-600">{doc.numero_reference}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{doc.titre}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{doc.type_document}</td>
                <td className="px-6 py-4 text-sm">{getStatutBadge(doc.statut)}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{doc.proprietaire_actuel_nom}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(doc.date_creation).toLocaleDateString('fr-FR')}</td>
                <td className="px-6 py-4 text-sm">
                  <div className="flex gap-2">
                    <button onClick={() => handleViewDetail(doc)} className="text-indigo-600 hover:text-indigo-900 font-medium" data-testid={`btn-detail-${doc.id}`}>Voir détails</button>
                    <button onClick={() => { setPreviewDocument(doc); setShowPreview(true); }} className="flex items-center gap-1 text-purple-600 hover:text-purple-900 font-medium" data-testid={`btn-preview-${doc.id}`}>
                      <Eye className="w-4 h-4" /> Preview
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {documents.length === 0 && <div className="text-center py-8 text-gray-500">Aucun document trouvé</div>}
      </div>

      {/* Modals */}
      {showDetail && selectedDocument && (
        <DetailDocumentModal document={selectedDocument} user={user}
          onClose={() => { setShowDetail(false); setSelectedDocument(null); loadDocuments(); }} />
      )}
      {showPreview && previewDocument && (
        <PreviewModal document={previewDocument} onClose={() => { setShowPreview(false); setPreviewDocument(null); }} />
      )}
    </div>
  );
};

export default DocumentManagement;
