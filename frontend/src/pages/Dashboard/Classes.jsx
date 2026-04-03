import React, { useState, useEffect } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { useAuth } from '../../context/AuthContext';
import ClasseManagement from '../../components/dashboards/components/ClasseManagement';

const Classes = () => {
  const { user } = useAuth();
  const { classes, etablissements, loadClasses, loadEtablissements } = useDashboardData();
  const [showClasseForm, setShowClasseForm] = useState(false);
  const [classeForm, setClasseForm] = useState({
    nom: '',
    niveau: '1ere_annee_primaire',
    etablissement_id: '',
    annee_scolaire: '2024-2025'
  });

  const canManageClasses = ['administrateur_technique', 'directeur_ecole', 'chef_etablissement', 'conseiller_principal_education'].includes(user.role);

  useEffect(() => {
    loadClasses();
    loadEtablissements();
  }, [loadClasses, loadEtablissements]);

  return (
    <ClasseManagement
      classes={classes}
      etablissements={etablissements}
      showForm={showClasseForm}
      form={classeForm}
      setForm={setClasseForm}
      setShowForm={setShowClasseForm}
      loadData={loadClasses}
      canManage={canManageClasses}
    />
  );
};

export default Classes;
