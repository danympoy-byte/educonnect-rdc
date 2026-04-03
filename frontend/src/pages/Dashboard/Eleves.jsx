import React, { useState, useEffect } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { useAuth } from '../../context/AuthContext';
import EleveManagement from '../../components/dashboards/components/EleveManagement';

const Eleves = () => {
  const { user } = useAuth();
  const { eleves, etablissements, loadEleves, loadEtablissements } = useDashboardData();
  const [showEleveForm, setShowEleveForm] = useState(false);
  const [eleveForm, setEleveForm] = useState({
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

  const canManageEleves = ['administrateur_technique', 'directeur_ecole', 'chef_etablissement', 'conseiller_principal_education'].includes(user.role);

  useEffect(() => {
    loadEleves();
    loadEtablissements();
  }, [loadEleves, loadEtablissements]);

  return (
    <EleveManagement
      eleves={eleves}
      etablissements={etablissements}
      showForm={showEleveForm}
      form={eleveForm}
      setForm={setEleveForm}
      setShowForm={setShowEleveForm}
      loadData={loadEleves}
      canManage={canManageEleves}
    />
  );
};

export default Eleves;
