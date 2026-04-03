import React, { useState, useEffect } from 'react';
import { Key, Plus, Eye, EyeOff, Copy, Check, Activity } from 'lucide-react';
import scolariteService from '@/services/scolarite.service';
import toast from 'react-hot-toast';

const GestionAPIExterne = () => {
  const [clients, setClients] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [newCredentials, setNewCredentials] = useState(null);
  const [copiedField, setCopiedField] = useState(null);

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    nom_systeme: '',
    etablissement_id: '',
    permissions: []
  });

  const permissionsDisponibles = [
    { value: 'notes', label: 'Notes des élèves' },
    { value: 'presences', label: 'Présences/Absences' },
    { value: 'inscriptions', label: 'Inscriptions d\'élèves' },
    { value: 'affectations', label: 'Affectations enseignants' }
  ];

  useEffect(() => {
    chargerClients();
    chargerLogs();
  }, []);

  const chargerClients = async () => {
    setLoading(true);
    try {
      const data = await scolariteService.listerClientsAPI();
      setClients(data.clients);
    } catch (error) {
      toast.error('Erreur lors du chargement des clients API');
    } finally {
      setLoading(false);
    }
  };

  const chargerLogs = async () => {
    try {
      const data = await scolariteService.listerLogsAPI(50);
      setLogs(data.logs);
    } catch (error) {
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const togglePermission = (perm) => {
    setFormData(prev => ({
      ...prev,
      permissions: prev.permissions.includes(perm)
        ? prev.permissions.filter(p => p !== perm)
        : [...prev.permissions, perm]
    }));
  };

  const genererMotDePasse = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    handleInputChange('password', password);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password || !formData.nom_systeme) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    if (formData.permissions.length === 0) {
      toast.error('Veuillez sélectionner au moins une permission');
      return;
    }

    setLoading(true);
    try {
      const result = await scolariteService.creerClientAPI(formData);
      toast.success('Client API créé avec succès !');
      
      // Afficher les credentials
      setNewCredentials({
        username: result.username,
        password: result.password
      });
      
      // Recharger la liste
      await chargerClients();
      
      // Réinitialiser le formulaire
      setFormData({
        username: '',
        password: '',
        nom_systeme: '',
        etablissement_id: '',
        permissions: []
      });
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    } finally {
      setLoading(false);
    }
  };

  const copierTexte = (texte, field) => {
    navigator.clipboard.writeText(texte);
    setCopiedField(field);
    toast.success('Copié !');
    setTimeout(() => setCopiedField(null), 2000);
  };

  const fermerCredentials = () => {
    setNewCredentials(null);
    setShowCreateForm(false);
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Key className="w-8 h-8 text-indigo-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Gestion des APIs Externes</h2>
            <p className="text-sm text-gray-600">Administration des systèmes externes connectés</p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          <Plus className="w-5 h-5" />
          Nouveau Client API
        </button>
      </div>

      {/* Modal Credentials générés */}
      {newCredentials && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              ⚠️ Credentials Générés
            </h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-yellow-800 mb-2">
                <strong>Important :</strong> Conservez ces credentials de manière sécurisée. 
                Ils ne seront plus affichés après la fermeture de cette fenêtre.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newCredentials.username}
                    readOnly
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                  <button
                    onClick={() => copierTexte(newCredentials.username, 'username')}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                  >
                    {copiedField === 'username' ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <div className="flex gap-2">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={newCredentials.password}
                    readOnly
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono"
                  />
                  <button
                    onClick={() => setShowPassword(!showPassword)}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={() => copierTexte(newCredentials.password, 'password')}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                  >
                    {copiedField === 'password' ? <Check className="w-5 h-5 text-green-600" /> : <Copy className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={fermerCredentials}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                J'ai sauvegardé ces credentials
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Formulaire de création */}
      {showCreateForm && !newCredentials && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Créer un nouveau client API</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="api_ecole_kinshasa"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom du système <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.nom_systeme}
                  onChange={(e) => handleInputChange('nom_systeme', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Système Gestion École Primaire Kinshasa"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 font-mono"
                  placeholder="••••••••••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
                <button
                  type="button"
                  onClick={genererMotDePasse}
                  className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200"
                >
                  Générer
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Permissions <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                {permissionsDisponibles.map(perm => (
                  <label key={perm.value} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.permissions.includes(perm.value)}
                      onChange={() => togglePermission(perm.value)}
                      className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                    />
                    <span className="text-sm text-gray-700">{perm.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Création...' : 'Créer le client API'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Annuler
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Liste des clients API */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Clients API Actifs</h3>
        {clients.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Système</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permissions</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dernière utilisation</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {clients.map(client => (
                  <tr key={client.id}>
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{client.username}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{client.nom_systeme}</td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex flex-wrap gap-1">
                        {client.permissions.map(perm => (
                          <span key={perm} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs">
                            {perm}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {client.last_used ? new Date(client.last_used).toLocaleString('fr-FR') : 'Jamais'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        client.actif ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {client.actif ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-600 text-center py-8">Aucun client API créé</p>
        )}
      </div>

      {/* Logs d'activité */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Logs d'Activité (50 derniers)</h3>
        </div>
        {logs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Endpoint</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Enregistrements</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {logs.map(log => (
                  <tr key={log.id}>
                    <td className="px-3 py-2 text-xs text-gray-600">
                      {new Date(log.timestamp).toLocaleString('fr-FR')}
                    </td>
                    <td className="px-3 py-2 text-xs font-mono text-gray-900">
                      {clients.find(c => c.id === log.api_client_id)?.username || log.api_client_id.slice(0, 8)}
                    </td>
                    <td className="px-3 py-2 text-xs text-gray-900">{log.endpoint}</td>
                    <td className="px-3 py-2">
                      <span className="px-2 py-1 bg-gray-100 rounded text-xs uppercase">{log.format_donnees}</span>
                    </td>
                    <td className="px-3 py-2 text-xs text-center">{log.nb_enregistrements}</td>
                    <td className="px-3 py-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        log.statut === 'success' ? 'bg-green-100 text-green-700' :
                        log.statut === 'partial' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {log.statut}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-600 text-center py-8">Aucune activité enregistrée</p>
        )}
      </div>
    </div>
  );
};

export default GestionAPIExterne;
