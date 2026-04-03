import React, { useState } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import ProvinceNavigator from '../../components/dashboards/components/ProvinceNavigator';

const Provinces = () => {
  const {
    provinces,
    sousDivisions,
    selectedProvince,
    filteredSousDivisions,
    handleProvinceClick,
    handleProvinceBack,
    loadGlobalStats
  } = useDashboardData();

  const [showProvinceForm, setShowProvinceForm] = useState(false);
  const [provinceForm, setProvinceForm] = useState({ nom: '', code: '' });

  return (
    <ProvinceNavigator
      provinces={provinces}
      sousDivisions={sousDivisions}
      selectedProvince={selectedProvince}
      filteredSousDivisions={filteredSousDivisions}
      showProvinceForm={showProvinceForm}
      provinceForm={provinceForm}
      setProvinceForm={setProvinceForm}
      setShowProvinceForm={setShowProvinceForm}
      onProvinceClick={handleProvinceClick}
      onBack={handleProvinceBack}
      loadData={loadGlobalStats}
    />
  );
};

export default Provinces;
