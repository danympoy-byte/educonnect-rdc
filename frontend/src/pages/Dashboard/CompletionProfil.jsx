import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import inscriptionService from '../../services/inscription.service';
import toast from 'react-hot-toast';

const CompletionProfil = () => {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    email: user?.email || '',
    numero_compte_bancaire: user?.numero_compte_bancaire || '',
    banque: user?.banque || ''
  });
  
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(user?.photo_url || null);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('La photo ne doit pas dépasser 5 MB');
        return;
      }
      
      setPhotoFile(file);
      
      // Créer un aperçu
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Étape 1 : Upload de la photo si fournie
      if (photoFile) {
        await inscriptionService.uploadPhoto(user.id, photoFile);
        toast.success('Photo uploadée avec succès');
      }

      // Étape 2 : Mise à jour des autres informations
      if (formData.email || formData.numero_compte_bancaire || formData.banque) {
        const dataToSend = {
          user_id: user.id
        };
        
        if (formData.email) dataToSend.email = formData.email;
        if (formData.numero_compte_bancaire) dataToSend.numero_compte_bancaire = formData.numero_compte_bancaire;
        if (formData.banque) dataToSend.banque = formData.banque;

        const response = await inscriptionService.etape3(dataToSend);
        toast.success(response.message);
      }

      // Rafraîchir les données utilisateur
      if (refreshUser) {
        await refreshUser();
      }

      // Rediriger vers le dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la mise à jour');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Compléter votre profil
          </h2>
          <p className="text-gray-600">
            Ajoutez les informations manquantes pour finaliser votre profil
          </p>
        </div>

        {/* Informations actuelles */}
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">Vos informations</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-700">Nom :</span>
              <span className="ml-2 font-medium text-blue-900">{user?.prenom} {user?.nom}</span>
            </div>
            <div>
              <span className="text-blue-700">Téléphone :</span>
              <span className="ml-2 font-medium text-blue-900">{user?.telephone}</span>
            </div>
            {user?.service_profiles?.[0] && (
              <div className="col-span-2">
                <span className="text-blue-700">Service :</span>
                <span className="ml-2 font-medium text-blue-900">
                  {user.service_profiles[0].service_nom} - {user.service_profiles[0].poste}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Photo de profil */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Photo de profil
              {user?.photo_url && <span className="ml-2 text-green-600">✓ Déjà ajoutée</span>}
            </label>
            
            <div className="flex items-center space-x-4">
              {photoPreview && (
                <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-indigo-200">
                  <img src={photoPreview} alt="Aperçu" className="w-full h-full object-cover" />
                </div>
              )}
              
              <div className="flex-1">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoChange}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-lg file:border-0
                    file:text-sm file:font-semibold
                    file:bg-indigo-50 file:text-indigo-700
                    hover:file:bg-indigo-100"
                />
                <p className="mt-1 text-xs text-gray-500">PNG, JPG jusqu'à 5 MB</p>
              </div>
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Adresse email
              {user?.email && <span className="ml-2 text-green-600">✓ Déjà ajoutée</span>}
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="votre.email@educonnect.gouv.cd"
            />
          </div>

          {/* Compte bancaire */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Numéro de compte bancaire
                {user?.numero_compte_bancaire && <span className="ml-2 text-green-600">✓ Déjà ajouté</span>}
              </label>
              <input
                type="text"
                value={formData.numero_compte_bancaire}
                onChange={(e) => setFormData({ ...formData, numero_compte_bancaire: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="000123456789"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Banque
                {user?.banque && <span className="ml-2 text-green-600">✓ Déjà ajoutée</span>}
              </label>
              <input
                type="text"
                value={formData.banque}
                onChange={(e) => setFormData({ ...formData, banque: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Ex: Rawbank"
              />
            </div>
          </div>

          {/* Boutons */}
          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
            >
              Plus tard
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </div>
        </form>

        {/* Info */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">
            💡 <strong>Note :</strong> Ces informations sont optionnelles mais recommandées pour une utilisation complète de la plateforme. Vous pouvez les ajouter à tout moment.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CompletionProfil;
