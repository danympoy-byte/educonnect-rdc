import React from 'react';
import { useAuth } from '../../context/AuthContext';
import RapportsTrimestriels from '../../components/dashboards/components/RapportsTrimestriels';

const Rapports = () => {
  const { user } = useAuth();
  return <RapportsTrimestriels user={user} />;
};

export default Rapports;
