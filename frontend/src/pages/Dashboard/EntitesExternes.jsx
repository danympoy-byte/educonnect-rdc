import React, { useState, useEffect, useCallback } from 'react';
import { Building2, Plus, Edit, Trash2, X } from 'lucide-react';
import toast from 'react-hot-toast';

const EntitesExternes = () => {
  const [entites, setEntites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingEntite, setEditingEntite] = useState(null);
  const [formData, setFormData] = useState({
    nom: '',
    type: 'ministere',
    adresse: '',
    telephone: '',
    email: '',
    contact_principal: '',
    description: ''
  });

  const API_URL = '';
    const loadEntites = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/entites-externes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setEntites(data);
      } else {
        toast.error('Erreur lors du chargement des entités');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  }, [API_URL, token]);

  useEffect(() => {
    loadEntites();
  }, [loadEntites]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const url = editingEntite
      ? `/entites-externes/${editingEntite.id}`
      : `/entites-externes`;

    const method = editingEntite ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingEntite ? 'Entité modifiée' : 'Entité créée');
        loadEntites();
        closeForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const handleEdit = (entite) => {
    setEditingEntite(entite);
    setFormData({
      nom: entite.nom,
      type: entite.type,
      adresse: entite.adresse || '',
      telephone: entite.telephone || '',
      email: entite.email || '',
      contact_principal: entite.contact_principal || '',
      description: entite.description || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette entité ?')) {
      return;
    }

    try {
      const response = await fetch(`/entites-externes/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Entité supprimée');
        loadEntites();
      } else {
        toast.error('Erreur lors de la suppression');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingEntite(null);
    setFormData({
      nom: '',
      type: 'ministere',
      adresse: '',
      telephone: '',
      email: '',
      contact_principal: '',
      description: ''
    });
  };

  const getTypeBadge = (type) => {
    const badges = {
      'ministere': 'bg-blue-100 text-blue-800',
      'organisme': 'bg-green-100 text-green-800',
      'entreprise': 'bg-purple-100 text-purple-800',
      'ong': 'bg-orange-100 text-orange-800',
      'partenaire': 'bg-pink-100 text-pink-800'
    };

    const labels = {
      'ministere': 'Ministère',
      'organisme': 'Organisme',
      'entreprise': 'Entreprise',
      'ong': 'ONG',
      'partenaire': 'Partenaire'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badges[type] || 'bg-gray-100 text-gray-800'}`}>
        {labels[type] || type}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Building2 className="w-8 h-8 text-indigo-600" />
              Entités Externes
            </h1>
            <p className="text-gray-600 mt-1">Gestion des organismes, ministères et partenaires</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <Plus className="w-5 h-5" />
            Nouvelle Entité
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-gray-900">{entites.length}</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-600">Ministères</p>
            <p className="text-2xl font-bold text-blue-900">
              {entites.filter(e => e.type === 'ministere').length}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <p className="text-sm text-green-600">Organismes</p>
            <p className="text-2xl font-bold text-green-900">
              {entites.filter(e => e.type === 'organisme').length}
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <p className="text-sm text-purple-600">Entreprises</p>
            <p className="text-2xl font-bold text-purple-900">
              {entites.filter(e => e.type === 'entreprise').length}
            </p>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Téléphone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    Chargement...
                  </td>
                </tr>
              ) : entites.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                    Aucune entité externe enregistrée
                  </td>
                </tr>
              ) : (
                entites.map((entite) => (
                  <tr key={entite.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{entite.nom}</div>
                      {entite.description && (
                        <div className="text-sm text-gray-500">{entite.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4">{getTypeBadge(entite.type)}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{entite.contact_principal || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{entite.email || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{entite.telephone || '-'}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(entite)}
                          className="p-2 text-indigo-600 hover:bg-indigo-50 rounded transition"
                          title="Modifier"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(entite.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded transition"
                          title="Supprimer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingEntite ? 'Modifier l\'entité' : 'Nouvelle entité externe'}
                </h3>
                <button onClick={closeForm} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Nom *</label>
                    <input
                      type="text"
                      value={formData.nom}
                      onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Type *</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      required
                    >
                      <option value="ministere">Ministère</option>
                      <option value="organisme">Organisme</option>
                      <option value="entreprise">Entreprise</option>
                      <option value="ong">ONG</option>
                      <option value="partenaire">Partenaire</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Contact principal</label>
                    <input
                      type="text"
                      value={formData.contact_principal}
                      onChange={(e) => setFormData({ ...formData, contact_principal: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Téléphone</label>
                    <input
                      type="text"
                      value={formData.telephone}
                      onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Adresse</label>
                    <input
                      type="text"
                      value={formData.adresse}
                      onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows="3"
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={closeForm}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                  >
                    {editingEntite ? 'Modifier' : 'Créer'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntitesExternes;