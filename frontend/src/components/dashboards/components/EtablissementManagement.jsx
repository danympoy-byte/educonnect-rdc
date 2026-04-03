import React from 'react';
import api from '../../../services/api';
import toast from 'react-hot-toast';
import etablissementsService from '../../../services/etablissements.service';
import provincesService from '../../../services/provinces.service';

const EtablissementManagement = ({
  etablissements,
  provinces,
  sousDivisions,
  showForm,
  form,
  setForm,
  setShowForm,
  setSousDivisions,
  loadData,
  canManage,
  onOpenCarte
}) => {

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await etablissementsService.create(form);
      toast.success('Établissement créé avec succès');
      setShowForm(false);
      setForm({ 
        nom: '', 
        type: 'ecole_primaire', 
        categorie: 'publique', 
        adresse: '', 
        province_id: '', 
        sous_division_id: '' 
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleProvinceChange = async (e) => {
    const provinceId = e.target.value;
    setForm({ ...form, province_id: provinceId });
    const sousDivs = await provincesService.getSousDivisions(provinceId);
    setSousDivisions(sousDivs);
  };

  const handleExport = async () => {
    try {
            const response = await api.get(`/exports/etablissements`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `educonnect_etablissements_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Export Excel téléchargé avec succès !');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'export');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Gestion des Établissements</h2>
        <div className="flex gap-3">
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
          >
            <span>📊</span>
            Exporter Excel
          </button>
          <button
            onClick={onOpenCarte}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <span>🗺️</span>
            Carte Scolaire Numérique
          </button>
          {canManage && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              + Nouvel Établissement
            </button>
          )}
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom</label>
              <input
                type="text"
                value={form.nom}
                onChange={(e) => setForm({ ...form, nom: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="ecole_primaire">École Primaire</option>
                <option value="college">Collège</option>
                <option value="lycee">Lycée</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
              <select
                value={form.categorie}
                onChange={(e) => setForm({ ...form, categorie: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="publique">Publique</option>
                <option value="privee">Privée</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Adresse</label>
              <input
                type="text"
                value={form.adresse}
                onChange={(e) => setForm({ ...form, adresse: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Province</label>
              <select
                value={form.province_id}
                onChange={handleProvinceChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {provinces.map((p) => (
                  <option key={p.id} value={p.id}>{p.nom}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sous-division</label>
              <select
                value={form.sous_division_id}
                onChange={(e) => setForm({ ...form, sous_division_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {sousDivisions.map((sd) => (
                  <option key={sd.id} value={sd.id}>{sd.nom}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-4 flex space-x-3">
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg">Créer</button>
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-200 rounded-lg">Annuler</button>
          </div>
        </form>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Catégorie</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Adresse</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {etablissements.map((etab) => (
              <tr key={etab.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{etab.code_etablissement}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{etab.nom}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{etab.type}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    etab.categorie === 'publique' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-purple-100 text-purple-800'
                  }`}>
                    {etab.categorie === 'publique' ? 'Publique' : 'Privée'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{etab.adresse}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EtablissementManagement;
