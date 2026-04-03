import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import inscriptionService from '../../services/inscription.service';
import servicesService from '../../services/services.service';
import EtapeInformations from './EtapeInformations';
import EtapeService from './EtapeService';

const InscriptionMultiEtapes = () => {
  const navigate = useNavigate();
  const [etapeActuelle, setEtapeActuelle] = useState(1);
  const [userId, setUserId] = useState(null);
  const [servicesHierarchie, setServicesHierarchie] = useState([]);
  const [serviceSelectionne, setServiceSelectionne] = useState(null);
  const [niveauActuel, setNiveauActuel] = useState(1);
  const [cheminHierarchique, setCheminHierarchique] = useState([]);

  const [formEtape1, setFormEtape1] = useState({
    nom: '', postnom: '', prenom: '', sexe: 'masculin', etat_civil: 'celibataire',
    date_naissance: '', lieu_naissance: '', telephone: '', adresse: '',
    password: '', confirm_password: ''
  });

  const [formEtape2, setFormEtape2] = useState({
    dg_id: '', direction_id: '', service_id: '', poste: ''
  });

  React.useEffect(() => {
    if (etapeActuelle === 2) {
      servicesService.getDropdownCascade().then(setServicesHierarchie).catch(() => {
        toast.error('Erreur lors du chargement des services');
      });
    }
  }, [etapeActuelle]);

  const findServiceById = (services, id) => {
    for (const service of services) {
      if (service.id === id) return service;
      if (service.directions?.length > 0) {
        const found = findServiceById(service.directions, id);
        if (found) return found;
      }
      if (service.services?.length > 0) {
        const found = findServiceById(service.services, id);
        if (found) return found;
      }
    }
    return null;
  };

  const selectionnerService = (service) => {
    setServiceSelectionne(service);
    const nouveauForm = { ...formEtape2, poste: formEtape2.poste };

    if (service.niveau === 'niveau_3') {
      nouveauForm.dg_id = service.id; nouveauForm.direction_id = ''; nouveauForm.service_id = '';
    } else if (service.niveau === 'niveau_4') {
      nouveauForm.dg_id = service.parent_id; nouveauForm.direction_id = service.id; nouveauForm.service_id = '';
    } else if (service.niveau === 'niveau_5') {
      let current = service;
      const hierarchy = [current];
      while (current.parent_id) {
        const parent = findServiceById(servicesHierarchie, current.parent_id);
        if (parent) { hierarchy.unshift(parent); current = parent; } else break;
      }
      const dg = hierarchy.find(s => s.niveau === 'niveau_3');
      const direction = hierarchy.find(s => s.niveau === 'niveau_4');
      if (dg) nouveauForm.dg_id = dg.id;
      if (direction) nouveauForm.direction_id = direction.id;
      nouveauForm.service_id = service.id;
    }
    setFormEtape2(nouveauForm);
  };

  const handleSubmitEtape1 = async (e) => {
    e.preventDefault();
    if (formEtape1.password !== formEtape1.confirm_password) { toast.error('Les mots de passe ne correspondent pas'); return; }
    if (formEtape1.password.length < 6) { toast.error('Le mot de passe doit contenir au moins 6 caractères'); return; }
    try {
      const response = await inscriptionService.etape1({
        nom: formEtape1.nom, postnom: formEtape1.postnom, prenom: formEtape1.prenom,
        sexe: formEtape1.sexe, etat_civil: formEtape1.etat_civil,
        date_naissance: formEtape1.date_naissance, lieu_naissance: formEtape1.lieu_naissance,
        telephone: formEtape1.telephone, adresse: formEtape1.adresse,
        password: formEtape1.password, diplomes: [], experiences: []
      });
      setUserId(response.user_id);
      toast.success(response.message);
      setEtapeActuelle(2);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erreur lors de l'inscription");
    }
  };

  const handleSubmitEtape2 = async (e) => {
    e.preventDefault();
    if (!serviceSelectionne) { toast.error("Veuillez sélectionner un service dans l'organigramme"); return; }
    const serviceFinalId = formEtape2.service_id || formEtape2.direction_id || formEtape2.dg_id;
    if (!serviceFinalId) { toast.error('Veuillez sélectionner au moins une Direction Générale'); return; }
    if (!formEtape2.poste) { toast.error('Veuillez indiquer votre poste'); return; }
    try {
      const response = await inscriptionService.etape2({ user_id: userId, service_id: serviceFinalId, poste: formEtape2.poste });
      toast.success(response.message);
      setTimeout(() => navigate('/login'), 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la sélection du service');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 py-12 px-4 sm:px-6 lg:px-8" data-testid="inscription-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-32 h-32 mb-4 flex items-center justify-center">
            <img src="https://customer-assets.emergentagent.com/job_education-connect-5/artifacts/bqswgbm9_Seal_of_the_DR_Congo_Government.svg.png"
              alt="Sceau de la République Démocratique du Congo" className="w-full h-full object-contain" />
          </div>
          <h1 className="text-3xl font-bold text-black">Édu-Connect</h1>
          <p className="text-gray-700 mt-2">Plateforme Éducative Nationale</p>
          <p className="text-sm text-gray-600 mt-1">Ministère de l'Éducation Nationale et de la Nouvelle Citoyenneté</p>
          <h2 className="text-2xl font-semibold text-gray-800 mt-6 mb-2">Inscription</h2>
        </div>

        {/* Indicateur d'étapes */}
        <div className="mb-8">
          <div className="flex justify-center items-center space-x-4">
            <div className={`flex items-center ${etapeActuelle >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${etapeActuelle >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>1</div>
              <span className="ml-2 font-medium hidden sm:block">Informations</span>
            </div>
            <div className="w-12 h-1 bg-gray-300"></div>
            <div className={`flex items-center ${etapeActuelle >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${etapeActuelle >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>2</div>
              <span className="ml-2 font-medium hidden sm:block">Service</span>
            </div>
          </div>
        </div>

        {/* Formulaires */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {etapeActuelle === 1 && (
            <EtapeInformations formEtape1={formEtape1} setFormEtape1={setFormEtape1} onSubmit={handleSubmitEtape1} />
          )}
          {etapeActuelle === 2 && (
            <EtapeService formEtape2={formEtape2} setFormEtape2={setFormEtape2}
              servicesHierarchie={servicesHierarchie} serviceSelectionne={serviceSelectionne}
              setServiceSelectionne={setServiceSelectionne}
              cheminHierarchique={cheminHierarchique} setCheminHierarchique={setCheminHierarchique}
              niveauActuel={niveauActuel} setNiveauActuel={setNiveauActuel}
              selectionnerService={selectionnerService} onSubmit={handleSubmitEtape2}
              onRetour={() => setEtapeActuelle(1)} />
          )}
        </div>

        <div className="text-center mt-6">
          <button onClick={() => navigate('/login')} className="text-indigo-600 hover:text-indigo-800 font-medium" data-testid="btn-retour-login">
            Retour à la connexion
          </button>
        </div>
      </div>
    </div>
  );
};

export default InscriptionMultiEtapes;
