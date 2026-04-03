import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import statsService from '../services/stats.service';
import etablissementsService from '../services/etablissements.service';
import elevesService from '../services/eleves.service';
import enseignantsService from '../services/enseignants.service';
import classesService from '../services/classes.service';
import provincesService from '../services/provinces.service';
import toast from 'react-hot-toast';

/**
 * Hook personnalisé pour charger et gérer les données du dashboard
 */
export const useDashboardData = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [statsSexe, setStatsSexe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [etablissements, setEtablissements] = useState([]);
  const [eleves, setEleves] = useState([]);
  const [enseignants, setEnseignants] = useState([]);
  const [classes, setClasses] = useState([]);
  const [provinces, setProvinces] = useState([]);
  const [sousDivisions, setSousDivisions] = useState([]);
  const [selectedProvince, setSelectedProvince] = useState(null);
  const [filteredSousDivisions, setFilteredSousDivisions] = useState([]);

  const loadGlobalStats = useCallback(async () => {
    try {
      const [statsData, statsSexeData, provincesData, sousDivisionsData] = await Promise.all([
        statsService.getGlobalStats(),
        statsService.getStatsSexe(),
        provincesService.getAll(),
        provincesService.getSousDivisions()
      ]);
      
      setStats(statsData);
      setStatsSexe(statsSexeData);
      setProvinces(provincesData);
      setSousDivisions(sousDivisionsData);
    } catch (error) {
      toast.error('Erreur lors du chargement des statistiques');
    }
  }, []);

  const loadEtablissements = useCallback(async () => {
    try {
      const filters = user?.etablissement_id ? { etablissement_id: user.etablissement_id } : {};
      const data = await etablissementsService.getAll(filters);
      setEtablissements(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des établissements');
    }
  }, [user?.etablissement_id]);

  const loadEleves = useCallback(async () => {
    try {
      const filters = user?.etablissement_id ? { etablissement_id: user.etablissement_id } : {};
      const data = await elevesService.getAll(filters);
      setEleves(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des élèves');
    }
  }, [user?.etablissement_id]);

  const loadEnseignants = useCallback(async () => {
    try {
      const filters = user?.etablissement_id ? { etablissement_id: user.etablissement_id } : {};
      const data = await enseignantsService.getAll(filters);
      setEnseignants(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des enseignants');
    }
  }, [user?.etablissement_id]);

  const loadClasses = useCallback(async () => {
    try {
      const filters = user?.etablissement_id ? { etablissement_id: user.etablissement_id } : {};
      const data = await classesService.getAll(filters);
      setClasses(data);
    } catch (error) {
      toast.error('Erreur lors du chargement des classes');
    }
  }, [user?.etablissement_id]);

  const handleProvinceClick = (province) => {
    setSelectedProvince(province);
    const filtered = sousDivisions.filter(sd => sd.province_id === province.id);
    setFilteredSousDivisions(filtered);
  };

  const handleProvinceBack = () => {
    setSelectedProvince(null);
    setFilteredSousDivisions([]);
  };

  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      await loadGlobalStats();
      setLoading(false);
    };
    loadInitialData();
  }, [loadGlobalStats]);

  return {
    stats,
    statsSexe,
    loading,
    etablissements,
    eleves,
    enseignants,
    classes,
    provinces,
    sousDivisions,
    selectedProvince,
    filteredSousDivisions,
    setEtablissements,
    setEleves,
    setEnseignants,
    setClasses,
    setSousDivisions,
    loadGlobalStats,
    loadEtablissements,
    loadEleves,
    loadEnseignants,
    loadClasses,
    handleProvinceClick,
    handleProvinceBack
  };
};
