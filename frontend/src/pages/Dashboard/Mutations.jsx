import React from 'react';
import { useAuth } from '../../context/AuthContext';
import MutationsEnseignant from '../../components/dashboards/components/MutationsEnseignant';

const Mutations = () => {
  const { user } = useAuth();
  return <MutationsEnseignant user={user} />;
};

export default Mutations;
