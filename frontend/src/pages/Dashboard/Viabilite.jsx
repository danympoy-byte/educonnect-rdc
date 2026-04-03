import React from 'react';
import { useAuth } from '../../context/AuthContext';
import EvaluationViabilite from '../../components/dashboards/components/EvaluationViabilite';

const Viabilite = () => {
  const { user } = useAuth();
  return <EvaluationViabilite user={user} />;
};

export default Viabilite;
