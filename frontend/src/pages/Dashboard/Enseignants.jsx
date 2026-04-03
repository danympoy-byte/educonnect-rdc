import React, { useEffect } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import EnseignantManagement from '../../components/dashboards/components/EnseignantManagement';

const Enseignants = () => {
  const { enseignants, loadEnseignants } = useDashboardData();

  useEffect(() => {
    loadEnseignants();
  }, [loadEnseignants]);

  return <EnseignantManagement enseignants={enseignants} />;
};

export default Enseignants;
