import React from 'react';
import toast from 'react-hot-toast';
import classesService from '../../../services/classes.service';

const ClasseManagement = ({
  classes,
  etablissements,
  showForm,
  form,
  setForm,
  setShowForm,
  loadData,
  canManage
}) => {

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await classesService.create(form);
      toast.success('Classe créée avec succès');
      setShowForm(false);
      setForm({ 
        nom: '', 
        niveau: '1ere_annee_primaire', 
        etablissement_id: '', 
        annee_scolaire: '2024-2025' 
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Gestion des Classes</h2>
        {canManage && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            + Nouvelle Classe
          </button>
        )}
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
                placeholder="Ex: CP1 A"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Niveau</label>
              <select
                value={form.niveau}
                onChange={(e) => setForm({ ...form, niveau: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <optgroup label="Primaire">
                  <option value="1ere_annee_primaire">1ère Année Primaire</option>
                  <option value="2eme_annee_primaire">2ème Année Primaire</option>
                  <option value="3eme_annee_primaire">3ème Année Primaire</option>
                  <option value="4eme_annee_primaire">4ème Année Primaire</option>
                  <option value="5eme_annee_primaire">5ème Année Primaire</option>
                  <option value="6eme_annee_primaire">6ème Année Primaire</option>
                </optgroup>
                <optgroup label="Secondaire">
                  <option value="1ere_annee_secondaire">1ère Année Secondaire</option>
                  <option value="2eme_annee_secondaire">2ème Année Secondaire</option>
                  <option value="3eme_annee_secondaire">3ème Année Secondaire</option>
                  <option value="4eme_annee_secondaire">4ème Année Secondaire</option>
                  <option value="5eme_annee_secondaire">5ème Année Secondaire</option>
                  <option value="6eme_annee_secondaire">6ème Année Secondaire</option>
                </optgroup>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Établissement</label>
              <select
                value={form.etablissement_id}
                onChange={(e) => setForm({ ...form, etablissement_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="">Sélectionner...</option>
                {etablissements.map((etab) => (
                  <option key={etab.id} value={etab.id}>{etab.nom}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Année scolaire</label>
              <input
                type="text"
                value={form.annee_scolaire}
                onChange={(e) => setForm({ ...form, annee_scolaire: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Niveau</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Année scolaire</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {classes.map((classe) => (
              <tr key={classe.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{classe.nom}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{classe.niveau}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{classe.annee_scolaire}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ClasseManagement;
