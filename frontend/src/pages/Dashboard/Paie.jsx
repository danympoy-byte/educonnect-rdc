import React from 'react';
import { useAuth } from '../../context/AuthContext';
import DashboardPaie from '../../components/dashboards/components/DashboardPaie';

const Paie = () => {
  const { user } = useAuth();
  return <DashboardPaie user={user} />;
};

export default Paie;
