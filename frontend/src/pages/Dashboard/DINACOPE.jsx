import React from 'react';
import { useAuth } from '../../context/AuthContext';
import ControleDINACOPE from '../../components/dashboards/components/ControleDINACOPE';

const DINACOPE = () => {
  const { user } = useAuth();
  return <ControleDINACOPE user={user} />;
};

export default DINACOPE;
