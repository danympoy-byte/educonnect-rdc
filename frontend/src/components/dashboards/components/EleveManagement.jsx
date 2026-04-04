import React from 'react';
import api from '../../../services/api';
import toast from 'react-hot-toast';
import elevesService from '../../../services/eleves.service';

const EleveManagement = ({
  eleves,
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
      // D'abord créer l'utilisateur
      const userResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'},
        body: JSON.stringify({
          email: form.email,
          nom: form.nom,
          prenom: form.prenom,
          password: form.password,
          role: form.niveau.includes('primaire') ? 'eleve_primaire' : 'eleve_secondaire',
          etablissement_id: form.etablissement_id
        })
      });
      
      const userData = await userResponse.json();
      
      // Ensuite créer le profil élève
      await elevesService.create({
        user_id: userData.id,
        etablissement_id: form.etablissement_id,
        niveau: form.niveau,
        sexe: form.sexe,
        date_naissance: form.date_naissance,
        lieu_naissance: form.lieu_naissance,
        parents_ids: []
      });
      
      toast.success('Élève créé avec succès');
      setShowForm(false);
      setForm({ 
        nom: '', 
        prenom: '', 
        email: '', 
        password: '', 
        etablissement_id: '', 
        niveau: '1ere_annee_primaire', 
        sexe: 'masculin', 
        date_naissance: '', 
        lieu_naissance: '' 
      });
      loadData();
    } catch (error) {
      toast.error('Erreur lors de la création de l\'élève');
    }
  };

  const handleExport = async () => {
    try {
            const response = await api.get(`/exports/eleves`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `educonnect_eleves_${new Date().toISOString().slice(0, 10)}.xlsx`);
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
        <h2 className="text-2xl font-bold text-gray-900">Gestion des Élèves</h2>
        <div className="flex space-x-2">
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
          >
            <span>📊</span>
            <span>Exporter Excel</span>
          </button>
          {canManage && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              + Nouvel Élève
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Prénom</label>
              <input
                type="text"
                value={form.prenom}
                onChange={(e) => setForm({ ...form, prenom: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Sexe</label>
              <select
                value={form.sexe}
                onChange={(e) => setForm({ ...form, sexe: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value="masculin">Masculin</option>
                <option value="feminin">Féminin</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date de naissance</label>
              <input
                type="date"
                value={form.date_naissance}
                onChange={(e) => setForm({ ...form, date_naissance: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Lieu de naissance</label>
              <input
                type="text"
                value={form.lieu_naissance}
                onChange={(e) => setForm({ ...form, lieu_naissance: e.target.value })}
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">INE</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Niveau</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date naissance</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {eleves.map((eleve) => (
              <tr key={eleve.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{eleve.ine}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{eleve.nom_complet || `${eleve.prenom || ''} ${eleve.nom || ''}`}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{eleve.niveau}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{eleve.date_naissance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EleveManagement;
