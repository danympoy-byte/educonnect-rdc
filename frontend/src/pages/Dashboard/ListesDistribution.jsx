import React, { useState, useEffect, useCallback } from 'react';
import { Users, Plus, Edit, Trash2, X } from 'lucide-react';
import toast from 'react-hot-toast';
import MultiUserSearchInput from '../../components/common/MultiUserSearchInput';

const ListesDistribution = () => {
  const [listes, setListes] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingListe, setEditingListe] = useState(null);
  const [formData, setFormData] = useState({
    nom: '',
    description: '',
    membres_ids: []
  });

  const API_URL = process.env.REACT_APP_BACKEND_URL;
    const loadListes = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/listes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setListes(data);
      } else {
        toast.error('Erreur lors du chargement des listes');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  }, [API_URL, token]);

  const loadUsers = useCallback(async () => {
    try {
      const response = await fetch(`/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
    }
  }, [API_URL, token]);

  // Charger les listes et utilisateurs au montage
  useEffect(() => {
    loadListes();
    loadUsers();
  }, [loadListes, loadUsers]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.membres_ids.length === 0) {
      toast.error('Veuillez ajouter au moins un membre');
      return;
    }

    const url = editingListe
      ? `/listes/${editingListe.id}`
      : `/listes`;

    const method = editingListe ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: {          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingListe ? 'Liste modifiée' : 'Liste créée');
        loadListes();
        closeForm();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const handleEdit = (liste) => {
    setEditingListe(liste);
    setFormData({
      nom: liste.nom,
      description: liste.description || '',
      membres_ids: liste.membres_ids || []
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette liste ?')) {
      return;
    }

    try {
      const response = await fetch(`/listes/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        toast.success('Liste supprimée');
        loadListes();
      } else {
        toast.error('Erreur lors de la suppression');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingListe(null);
    setFormData({
      nom: '',
      description: '',
      membres_ids: []
    });
  };

  const handleMembersChange = (memberIds) => {
    setFormData({ ...formData, membres_ids: memberIds });
  };

  const getMembresNames = (membresIds) => {
    if (!membresIds || membresIds.length === 0) return 'Aucun membre';
    
    const names = membresIds
      .map(id => {
        const user = users.find(u => u.id === id);
        return user ? `${user.prenom} ${user.nom}` : null;
      })
      .filter(Boolean);
    
    if (names.length === 0) return 'Aucun membre';
    if (names.length <= 3) return names.join(', ');
    return `${names.slice(0, 3).join(', ')} +${names.length - 3} autres`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Users className="w-8 h-8 text-indigo-600" />
              Listes de Distribution
            </h1>
            <p className="text-gray-600 mt-1">Gestion des groupes de destinataires</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <Plus className="w-5 h-5" />
            Nouvelle Liste
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600">Listes totales</p>
            <p className="text-2xl font-bold text-gray-900">{listes.length}</p>
          </div>
          <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
            <p className="text-sm text-indigo-600">Membres uniques</p>
            <p className="text-2xl font-bold text-indigo-900">
              {new Set(listes.flatMap(l => l.membres_ids || [])).size}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <p className="text-sm text-green-600">Moyenne membres/liste</p>
            <p className="text-2xl font-bold text-green-900">
              {listes.length > 0
                ? Math.round(listes.reduce((sum, l) => sum + (l.membres_ids?.length || 0), 0) / listes.length)
                : 0}
            </p>
          </div>
        </div>

        {/* Lists Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <div className="col-span-full text-center py-8 text-gray-500">
              Chargement...
            </div>
          ) : listes.length === 0 ? (
            <div className="col-span-full text-center py-8">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Aucune liste de distribution créée</p>
            </div>
          ) : (
            listes.map((liste) => (
              <div key={liste.id} className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-lg">{liste.nom}</h3>
                    {liste.description && (
                      <p className="text-sm text-gray-600 mt-1">{liste.description}</p>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => handleEdit(liste)}
                      className="p-2 text-indigo-600 hover:bg-indigo-50 rounded transition"
                      title="Modifier"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(liste.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded transition"
                      title="Supprimer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-900">{liste.membres_ids?.length || 0} membre(s)</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-2">{getMembresNames(liste.membres_ids)}</p>
                  {liste.date_creation && (
                    <p className="text-xs text-gray-400 mt-2">
                      Créée le {new Date(liste.date_creation).toLocaleDateString('fr-FR')}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
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
                  {editingListe ? 'Modifier la liste' : 'Nouvelle liste de distribution'}
                </h3>
                <button onClick={closeForm} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nom de la liste *</label>
                  <input
                    type="text"
                    value={formData.nom}
                    onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="Ex: Direction Administrative"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    rows="3"
                    placeholder="Décrivez l'utilité de cette liste..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Membres *</label>
                  <MultiUserSearchInput
                    users={users}
                    selectedUserIds={formData.membres_ids}
                    onChange={handleMembersChange}
                    placeholder="Rechercher et ajouter des membres..."
                    required={true}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.membres_ids.length} membre(s) sélectionné(s)
                  </p>
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
                    {editingListe ? 'Modifier' : 'Créer'}
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

export default ListesDistribution;