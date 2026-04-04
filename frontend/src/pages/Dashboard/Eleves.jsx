import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDashboardData } from '../../hooks/useDashboardData';
import { useAuth } from '../../context/AuthContext';
import EleveManagement from '../../components/dashboards/components/EleveManagement';

const Eleves = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { eleves, etablissements, loadEleves, loadEtablissements } = useDashboardData();
  const [showEleveForm, setShowEleveForm] = useState(false);
  const [eleveForm, setEleveForm] = useState({
    nom: '',
    prenom: '',
    email: '',
    password: '',
    etablissement_id: '',
    niveau: '1ere_annee_primaire',
    sexe: 'masculin',
    date_naissance: '',
    lieu_naissance: ''
  });

  const canManageEleves = ['administrateur_technique', 'directeur_ecole', 'chef_etablissement', 'conseiller_principal_education'].includes(user.role);

  useEffect(() => {
    loadEleves();
    loadEtablissements();
  }, [loadEleves, loadEtablissements]);

  return (
    <div className="space-y-4">
      {/* Bouton Evaluations */}
      <div className="flex justify-end">
        <button
          onClick={() => navigate('/dashboard/evaluations')}
          className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2 shadow-sm"
          data-testid="btn-evaluations"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Evaluations et Notes
        </button>
      </div>

      <EleveManagement
        eleves={eleves}
        etablissements={etablissements}
        showForm={showEleveForm}
        form={eleveForm}
        setForm={setEleveForm}
        setShowForm={setShowEleveForm}
        loadData={loadEleves}
        canManage={canManageEleves}
      />
    </div>
  );
};

export default Eleves;
