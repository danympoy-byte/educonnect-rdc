import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDashboardData } from '../../hooks/useDashboardData';
import { useAuth } from '../../context/AuthContext';
import EtablissementManagement from '../../components/dashboards/components/EtablissementManagement';

const Etablissements = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { 
    etablissements, 
    provinces, 
    sousDivisions, 
    setSousDivisions,
    loadEtablissements 
  } = useDashboardData();

  const [showEtablissementForm, setShowEtablissementForm] = useState(false);
  const [etablissementForm, setEtablissementForm] = useState({
    nom: '',
    type: 'ecole_primaire',
    categorie: 'publique',
    adresse: '',
    province_id: '',
    sous_division_id: ''
  });

  const canManageEtablissements = ['administrateur_technique', 'directeur_provincial', 'chef_sous_division'].includes(user.role);

  useEffect(() => {
    loadEtablissements();
  }, [loadEtablissements]);

  const handleOpenCarte = () => {
    navigate('/dashboard/carte-scolaire');
  };

  return (
    <EtablissementManagement
      etablissements={etablissements}
      provinces={provinces}
      sousDivisions={sousDivisions}
      showForm={showEtablissementForm}
      form={etablissementForm}
      setForm={setEtablissementForm}
      setShowForm={setShowEtablissementForm}
      setSousDivisions={setSousDivisions}
      loadData={loadEtablissements}
      canManage={canManageEtablissements}
      onOpenCarte={handleOpenCarte}
    />
  );
};

export default Etablissements;
