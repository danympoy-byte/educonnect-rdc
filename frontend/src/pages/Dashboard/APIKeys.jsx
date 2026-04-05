import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import toast from 'react-hot-toast';


const APIKeys = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyData, setNewKeyData] = useState({
    name: '',
    description: '',
    expires_in_days: 365,
    permissions: {
      documents: 'none',
      enseignants: 'none',
      eleves: 'none',
      etablissements: 'none',
      stats: 'none',
      rapports: 'none',
      dinacope: 'none',
      provinces: 'none',
      classes: 'none',
      presences: 'none'
    }
  });
  const [generatedKey, setGeneratedKey] = useState(null);
  const [stats, setStats] = useState(null);

  const fetchAPIKeys = useCallback(async () => {
    try {
            const response = await api.get(`/api-keys`, {
        
      });
      setApiKeys(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des clés API');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
            const response = await api.get(`/api-keys/stats/usage`, {
        
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load API stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchAPIKeys();
    fetchStats();
  }, [fetchAPIKeys, fetchStats]);

  const generateAPIKey = async () => {
    try {
            // Filtrer les permissions "none"
      const filteredPermissions = {};
      Object.entries(newKeyData.permissions).forEach(([module, permission]) => {
        if (permission !== 'none') {
          filteredPermissions[module] = permission;
        }
      });

      if (Object.keys(filteredPermissions).length === 0) {
        toast.error('Veuillez sélectionner au moins une permission');
        return;
      }

      const response = await api.post(
        `/api-keys/generate`,
        {
          ...newKeyData,
          permissions: filteredPermissions
        },
        {  }
      );

      setGeneratedKey(response.data);
      toast.success('Clé API générée avec succès !');
      fetchAPIKeys();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la génération');
    }
  };

  const revokeAPIKey = async (keyId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir révoquer cette clé ? Cette action est irréversible.')) {
      return;
    }

    try {
            await api.delete(`/api-keys/${keyId}`, {
        
      });
      toast.success('Clé révoquée avec succès');
      fetchAPIKeys();
      fetchStats();
    } catch (error) {
      toast.error('Erreur lors de la révocation');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copié dans le presse-papier !');
  };

  const handlePermissionChange = (module, value) => {
    setNewKeyData({
      ...newKeyData,
      permissions: {
        ...newKeyData.permissions,
        [module]: value
      }
    });
  };

  const modules = [
    { key: 'documents', label: '📄 Documents (GED)' },
    { key: 'enseignants', label: '👨‍🏫 Enseignants (SIRH)' },
    { key: 'eleves', label: '👨‍🎓 Élèves' },
    { key: 'etablissements', label: '🏫 Établissements' },
    { key: 'stats', label: '📊 Statistiques' },
    { key: 'rapports', label: '📋 Rapports' },
    { key: 'dinacope', label: '🔍 DINACOPE' },
    { key: 'provinces', label: '🗺️ Provinces' },
    { key: 'classes', label: '🎓 Classes' },
    { key: 'presences', label: '📊 Présences' }
  ];

  if (loading) {
    return <div className="flex justify-center items-center h-64"><div className="text-gray-500">Chargement...</div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clés API</h1>
          <p className="text-sm text-gray-600 mt-1">Gérez les clés d'authentification pour les développeurs externes</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          + Générer une nouvelle clé
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-sm text-gray-600">Total clés</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_keys}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-sm text-gray-600">Clés actives</div>
            <div className="text-2xl font-bold text-green-600">{stats.active_keys}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-sm text-gray-600">Clés révoquées</div>
            <div className="text-2xl font-bold text-red-600">{stats.revoked_keys}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border">
            <div className="text-sm text-gray-600">Appels API</div>
            <div className="text-2xl font-bold text-indigo-600">{stats.total_api_calls}</div>
          </div>
        </div>
      )}

      {/* Liste des clés */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Mes clés API</h2>
          {apiKeys.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Aucune clé API créée. Cliquez sur "Générer une nouvelle clé" pour commencer.
            </div>
          ) : (
            <div className="space-y-4">
              {apiKeys.map((key) => (
                <div key={key.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-gray-900">{key.name}</h3>
                        {key.is_active ? (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span>
                        ) : (
                          <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Révoquée</span>
                        )}
                      </div>
                      {key.description && (
                        <p className="text-sm text-gray-600 mt-1">{key.description}</p>
                      )}
                      <div className="mt-2 space-y-1 text-sm text-gray-500">
                        <div>
                          <span className="font-medium">Préfixe:</span> 
                          <code className="ml-2 bg-gray-100 px-2 py-1 rounded">{key.key_prefix}</code>
                          <button
                            onClick={() => copyToClipboard(key.key_prefix)}
                            className="ml-2 text-indigo-600 hover:text-indigo-700"
                          >
                            📋 Copier
                          </button>
                        </div>
                        <div><span className="font-medium">Créée le:</span> {new Date(key.created_at).toLocaleDateString('fr-FR')}</div>
                        {key.expires_at && (
                          <div><span className="font-medium">Expire le:</span> {new Date(key.expires_at).toLocaleDateString('fr-FR')}</div>
                        )}
                        <div><span className="font-medium">Utilisations:</span> {key.usage_count}</div>
                        {key.last_used_at && (
                          <div><span className="font-medium">Dernière utilisation:</span> {new Date(key.last_used_at).toLocaleDateString('fr-FR')}</div>
                        )}
                      </div>
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-700 mb-2">Permissions:</div>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(key.permissions).map(([module, permission]) => (
                            <span
                              key={module}
                              className={`px-2 py-1 text-xs rounded ${
                                permission === 'read' ? 'bg-blue-100 text-blue-700' :
                                permission === 'write' ? 'bg-purple-100 text-purple-700' :
                                'bg-orange-100 text-orange-700'
                              }`}
                            >
                              {module}: {permission}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div>
                      {key.is_active && (
                        <button
                          onClick={() => revokeAPIKey(key.id)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition text-sm"
                        >
                          Révoquer
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal création */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">Générer une nouvelle clé API</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nom de la clé *</label>
                  <input
                    type="text"
                    value={newKeyData.name}
                    onChange={(e) => setNewKeyData({ ...newKeyData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="Ex: Application Mobile RDC"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    value={newKeyData.description}
                    onChange={(e) => setNewKeyData({ ...newKeyData, description: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    rows="2"
                    placeholder="Description optionnelle"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expiration (jours)</label>
                  <input
                    type="number"
                    value={newKeyData.expires_in_days}
                    onChange={(e) => setNewKeyData({ ...newKeyData, expires_in_days: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                    min="1"
                    max="365"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Permissions par module *</label>
                  <div className="space-y-2">
                    {modules.map((module) => (
                      <div key={module.key} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                        <span className="text-sm">{module.label}</span>
                        <select
                          value={newKeyData.permissions[module.key]}
                          onChange={(e) => handlePermissionChange(module.key, e.target.value)}
                          className="px-3 py-1 border rounded focus:ring-2 focus:ring-indigo-500 text-sm"
                        >
                          <option value="none">Aucune</option>
                          <option value="read">Lecture</option>
                          <option value="write">Écriture</option>
                          <option value="admin">Admin</option>
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex space-x-3">
                <button
                  onClick={generateAPIKey}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  Générer la clé
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal clé générée */}
      {generatedKey && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="text-center mb-4">
              <div className="text-4xl mb-2">🔐</div>
              <h2 className="text-xl font-bold text-gray-900">Clé API générée avec succès !</h2>
              <p className="text-sm text-red-600 mt-2">⚠️ Cette clé ne sera affichée qu'une seule fois. Copiez-la maintenant !</p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Votre clé API :</label>
              <div className="flex items-center space-x-2">
                <code className="flex-1 bg-white px-4 py-3 rounded border text-sm break-all">
                  {generatedKey.key}
                </code>
                <button
                  onClick={() => copyToClipboard(generatedKey.key)}
                  className="px-4 py-3 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition whitespace-nowrap"
                >
                  📋 Copier
                </button>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-blue-900 mb-2">📚 Utilisation</h3>
              <p className="text-sm text-blue-800 mb-2">Incluez cette clé dans le header de vos requêtes HTTP :</p>
              <code className="block bg-white px-3 py-2 rounded text-sm">
                X-API-Key: {generatedKey.key}
              </code>
              <p className="text-xs text-blue-700 mt-2">
                Documentation complète : <a href={`/docs`} target="_blank" rel="noopener noreferrer" className="underline">{API_URL}/api/docs</a>
              </p>
            </div>

            <button
              onClick={() => {
                setGeneratedKey(null);
                setShowCreateModal(false);
                setNewKeyData({
                  name: '',
                  description: '',
                  expires_in_days: 365,
                  permissions: {
                    documents: 'none',
                    enseignants: 'none',
                    eleves: 'none',
                    etablissements: 'none',
                    stats: 'none',
                    rapports: 'none',
                    dinacope: 'none',
                    provinces: 'none',
                    classes: 'none',
                    presences: 'none'
                  }
                });
              }}
              className="w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition"
            >
              J'ai copié la clé, fermer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIKeys;
