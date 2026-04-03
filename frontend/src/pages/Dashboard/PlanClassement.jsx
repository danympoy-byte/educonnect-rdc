import React from 'react';
import PlanClassementComponent from '../../components/dashboards/components/PlanClassement';

const PlanClassementPage = ({ user }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <PlanClassementComponent />
    </div>
  );
};

export default PlanClassementPage;
