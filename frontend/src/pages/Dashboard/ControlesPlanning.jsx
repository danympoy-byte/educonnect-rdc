import React from 'react';
import { useAuth } from '../../context/AuthContext';
import PlanningControles from '../../components/dashboards/components/PlanningControles';

const ControlesPlanning = () => {
  const { user } = useAuth();
  return <PlanningControles user={user} />;
};

export default ControlesPlanning;
