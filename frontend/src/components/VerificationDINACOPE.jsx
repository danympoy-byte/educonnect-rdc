import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import sirhService from '../services/sirh.service';

const VerificationDINACOPE = () => {
  const { token } = useParams();
  const [verification, setVerification] = useState(null);
  const [enseignant, setEnseignant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    adresse_personnelle: '',
    telephone_personnel: '',
    email_personnel: '',
    etat_civil: 'celibataire',
    nombre_enfants: 0,
    conjoint_nom: '',
    banque: '',
    numero_compte: '',
    grade: 'mécanisé'
  });

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async () => {
    try {
      const data = await sirhService.getFormulaireVerification(token);
      setVerification(data.verification);
      setEnseignant(data.enseignant);
      setFormData({
        adresse_personnelle: data.enseignant.adresse_personnelle || '',
        telephone_personnel: data.enseignant.telephone_personnel || '',
        email_personnel: data.enseignant.email_personnel || '',
        etat_civil: data.enseignant.etat_civil || 'celibataire',
        nombre_enfants: data.enseignant.nombre_enfants || 0,
        conjoint_nom: data.enseignant.conjoint_nom || '',
        banque: data.enseignant.banque || '',
        numero_compte: data.enseignant.numero_compte || '',
        grade: data.enseignant.grade || 'mécanisé'
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Lien invalide ou expiré');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await sirhService.soumettreVerification(token, formData);
      setSuccess(true);
      toast.success('Vérification effectuée avec succès !');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la soumission');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'nombre_enfants' ? parseInt(value) || 0 : value
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white rounded-xl p-8 shadow-lg">
          <p className="text-lg">Chargement...</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl p-8 shadow-lg max-w-2xl">
          <div className="text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-3xl font-bold text-green-600 mb-4">Vérification Réussie !</h2>
            <p className="text-gray-600 mb-6">
              Vos données ont été mises à jour avec succès dans le système.
            </p>
            <p className="text-sm text-gray-500">
              Merci pour votre collaboration avec la DINACOPE.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!verification || !enseignant) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl p-8 shadow-lg max-w-2xl text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-red-600 mb-4">Lien Invalide</h2>
          <p className="text-gray-600">
            Ce lien de vérification est invalide ou a expiré.
          </p>
        </div>
      </div>
    );
  }

  const dateExpiration = new Date(verification.date_expiration).toLocaleDateString('fr-FR');

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-indigo-600 text-white rounded-t-xl p-6">
          <h1 className="text-3xl font-bold mb-2">🔍 Vérification DINACOPE</h1>
          <p className="text-indigo-100">Contrôle Physique des Enseignants - Mise à jour de vos données</p>
        </div>

        <div className="bg-white rounded-b-xl shadow-lg p-6">
          {/* Infos Enseignant */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-lg mb-2">Vos Informations</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Nom complet</p>
                <p className="font-medium">{enseignant.prenom} {enseignant.nom}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Matricule</p>
                <p className="font-medium">{enseignant.matricule}</p>
              </div>
            </div>
          </div>

          {/* Avertissement expiration */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              ⏰ <strong>Important :</strong> Ce lien expire le {dateExpiration}. Veuillez vérifier et mettre à jour vos données avant cette date.
            </p>
          </div>

          {/* Formulaire */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Adresse */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse personnelle *
                </label>
                <input
                  type="text"
                  name="adresse_personnelle"
                  value={formData.adresse_personnelle}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Numéro, rue, commune, ville"
                />
              </div>

              {/* Téléphone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone personnel *
                </label>
                <input
                  type="tel"
                  name="telephone_personnel"
                  value={formData.telephone_personnel}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="+243 XXX XXX XXX"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email personnel
                </label>
                <input
                  type="email"
                  name="email_personnel"
                  value={formData.email_personnel}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="votre.email@exemple.com"
                />
              </div>

              {/* État civil */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  État civil *
                </label>
                <select
                  name="etat_civil"
                  value={formData.etat_civil}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="celibataire">Célibataire</option>
                  <option value="marie">Marié(e)</option>
                  <option value="divorce">Divorcé(e)</option>
                  <option value="veuf">Veuf/Veuve</option>
                </select>
              </div>

              {/* Nombre d'enfants */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre d'enfants
                </label>
                <input
                  type="number"
                  name="nombre_enfants"
                  value={formData.nombre_enfants}
                  onChange={handleChange}
                  min="0"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Nom conjoint */}
              {(formData.etat_civil === 'marie' || formData.etat_civil === 'veuf') && (
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom du conjoint
                  </label>
                  <input
                    type="text"
                    name="conjoint_nom"
                    value={formData.conjoint_nom}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}

              {/* Banque */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Banque
                </label>
                <input
                  type="text"
                  name="banque"
                  value={formData.banque}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Nom de la banque"
                />
              </div>

              {/* Numéro de compte */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Numéro de compte bancaire
                </label>
                <input
                  type="text"
                  name="numero_compte"
                  value={formData.numero_compte}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Numéro de compte"
                />
              </div>

              {/* Grade */}
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Grade actuel
                </label>
                <select
                  name="grade"
                  value={formData.grade}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="stagiaire">Stagiaire</option>
                  <option value="mécanisé">Mécanisé</option>
                  <option value="qualifié">Qualifié</option>
                  <option value="diplômé">Diplômé</option>
                  <option value="licencié">Licencié</option>
                  <option value="maître_assistant">Maître Assistant</option>
                  <option value="chef_de_travaux">Chef de Travaux</option>
                </select>
              </div>
            </div>

            {/* Boutons */}
            <div className="flex justify-end space-x-4 pt-6 border-t">
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 font-medium"
              >
                {submitting ? 'Enregistrement...' : 'Confirmer et Soumettre'}
              </button>
            </div>
          </form>

          {/* Footer */}
          <div className="mt-6 pt-6 border-t text-center text-sm text-gray-500">
            <p>DINACOPE - Direction Nationale du Contrôle et de la Paie des Enseignants</p>
            <p>Ministère de l'Éducation Nationale - RDC</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerificationDINACOPE;
