import React, { useEffect } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import SuiviPresences from '../../components/dashboards/components/SuiviPresences';

const Presences = () => {
  const { etablissements, classes, loadEtablissements, loadClasses } = useDashboardData();

  useEffect(() => {
    loadEtablissements();
    loadClasses();
  }, [loadEtablissements, loadClasses]);

  return <SuiviPresences etablissements={etablissements} classes={classes} />;
};

export default Presences;
