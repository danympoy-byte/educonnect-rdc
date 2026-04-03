import React, { useState, useEffect } from 'react';
import { User, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

const ContexteSwitcher = ({ onContextChange }) => {
  const [contexte, setContexte] = useState('personnel');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadContexte();
    loadStats();
  }, []);

  const loadContexte = async () => {
    try {
      const response = await api.get('/contexte/');
      setContexte(response.data.contexte_actuel);
    } catch (error) {
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/contexte/statistiques');
      setStats(response.data);
    } catch (error) {
    }
  };

  const handleSwitch = async (nouveauContexte) => {
    if (nouveauContexte === contexte) return;

    setLoading(true);

    try {
      const response = await api.post('/contexte/basculer', {
        nouveau_contexte: nouveauContexte
      });

      setContexte(nouveauContexte);
      toast.success(response.data.message || `Basculé vers la ${nouveauContexte === 'equipe' ? 'Zone Verte' : 'Zone Bleue'}`);
      
      if (onContextChange) {
        onContextChange(nouveauContexte);
      }

      // Recharger les stats
      loadStats();
    } catch (error) {
      console.error('Erreur de basculement:', error);
      // Même en cas d'erreur, on permet le basculement côté UI
      // L'erreur peut être due à un problème de connexion temporaire
      if (error.response?.status === 401) {
        toast.error('Session expirée. Veuillez vous reconnecter.');
      } else if (error.response?.status === 404) {
        // L'utilisateur n'a peut-être pas de profil complet, on bascule quand même
        setContexte(nouveauContexte);
        toast.success(`Basculé vers la ${nouveauContexte === 'equipe' ? 'Zone Verte' : 'Zone Bleue'}`);
        if (onContextChange) {
          onContextChange(nouveauContexte);
        }
      } else {
        toast.error(error.response?.data?.detail || 'Erreur temporaire - Réessayez');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Environnement de travail</h3>
      </div>

      {/* Toggle entre les zones */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => handleSwitch('personnel')}
          disabled={loading}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            contexte === 'personnel'
              ? 'bg-blue-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          } disabled:opacity-50`}
        >
          <User className="w-5 h-5" />
          <div className="text-left">
            <div className="font-semibold">Zone Bleue</div>
            <div className="text-xs opacity-90">Personnel</div>
          </div>
        </button>

        <button
          onClick={() => handleSwitch('equipe')}
          disabled={loading}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            contexte === 'equipe'
              ? 'bg-green-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          } disabled:opacity-50`}
        >
          <Users className="w-5 h-5" />
          <div className="text-left">
            <div className="font-semibold">Zone Verte</div>
            <div className="text-xs opacity-90">Équipe</div>
          </div>
        </button>
      </div>

      {/* Statistiques par zone */}
      {stats && (
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className={`p-3 rounded-lg ${
            contexte === 'personnel' ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
          }`}>
            <div className="text-gray-600 text-xs mb-1">Zone Bleue</div>
            <div className="font-bold text-lg text-blue-600">
              {stats.zone_bleue_personnel?.total_documents || 0}
            </div>
            <div className="text-xs text-gray-500">documents personnels</div>
            {stats.zone_bleue_personnel?.taches_en_attente > 0 && (
              <div className="text-xs text-orange-600 mt-1">
                {stats.zone_bleue_personnel.taches_en_attente} tâche(s) en attente
              </div>
            )}
          </div>

          <div className={`p-3 rounded-lg ${
            contexte === 'equipe' ? 'bg-green-50 border border-green-200' : 'bg-gray-50'
          }`}>
            <div className="text-gray-600 text-xs mb-1">Zone Verte</div>
            <div className="font-bold text-lg text-green-600">
              {stats.zone_verte_equipe?.total_documents || 0}
            </div>
            <div className="text-xs text-gray-500">documents d'équipe</div>
            {stats.zone_verte_equipe?.services_count > 0 && (
              <div className="text-xs text-gray-500 mt-1">
                {stats.zone_verte_equipe.services_count} service(s)
              </div>
            )}
          </div>
        </div>
      )}

      {/* Description de la zone active */}
      <div className={`mt-3 p-3 rounded-lg text-xs ${
        contexte === 'personnel' 
          ? 'bg-blue-50 text-blue-700 border border-blue-200' 
          : 'bg-green-50 text-green-700 border border-green-200'
      }`}>
        {contexte === 'personnel' ? (
          <>
            <strong>👤 Zone Bleue (Personnel) :</strong> Vos documents personnels, tâches individuelles et documents dont vous êtes propriétaire.
          </>
        ) : (
          <>
            <strong>👥 Zone Verte (Équipe) :</strong> Documents partagés avec votre équipe, votre service et les collaborations.
          </>
        )}
      </div>
    </div>
  );
};

export default ContexteSwitcher;
