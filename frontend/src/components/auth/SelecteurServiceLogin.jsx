import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const SelecteurServiceLogin = ({ user, onServiceSelected }) => {
  const navigate = useNavigate();
  const [selectedServiceId, setSelectedServiceId] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedServiceId) {
      toast.error('Veuillez sélectionner un service');
      return;
    }

    const selectedProfile = user.service_profiles.find(p => p.service_id === selectedServiceId);
    
    // Mettre à jour le service actif dans le contexte
    onServiceSelected(selectedServiceId, selectedProfile);
    
    toast.success(`Service ${selectedProfile.service_nom} activé`);
    navigate('/dashboard');
  };

  if (!user || !user.service_profiles || user.service_profiles.length <= 1) {
    // Si l'utilisateur n'a qu'un seul service, rediriger directement
    if (user?.service_profiles?.length === 1) {
      onServiceSelected(user.service_profiles[0].service_id, user.service_profiles[0]);
      navigate('/dashboard');
    }
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="flex justify-center items-center space-x-3 mb-4">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Coat_of_arms_of_the_Democratic_Republic_of_the_Congo.svg/180px-Coat_of_arms_of_the_Democratic_Republic_of_the_Congo.svg.png"
                alt="Logo MINEPST"
                className="h-12 w-auto"
              />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                Édu-Connect
              </h1>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Sélectionnez votre service
            </h2>
            <p className="text-gray-600 text-sm">
              Bonjour {user.prenom} {user.nom}
            </p>
          </div>

          {/* Formulaire */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Vous appartenez à plusieurs services. Choisissez celui que vous souhaitez utiliser :
              </label>
              <div className="space-y-3">
                {user.service_profiles.map((profile) => (
                  <label
                    key={profile.service_id}
                    className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition ${
                      selectedServiceId === profile.service_id
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="service"
                      value={profile.service_id}
                      checked={selectedServiceId === profile.service_id}
                      onChange={(e) => setSelectedServiceId(e.target.value)}
                      className="mt-1 h-4 w-4 text-indigo-600"
                    />
                    <div className="ml-3">
                      <div className="font-medium text-gray-900">
                        {profile.service_nom}
                      </div>
                      <div className="text-sm text-gray-600">
                        {profile.poste}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Code: {profile.service_code}
                      </div>
                      {profile.est_responsable && (
                        <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          Responsable
                        </span>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={!selectedServiceId}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continuer
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              💡 Vous pourrez changer de service à tout moment depuis votre profil
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SelecteurServiceLogin;
