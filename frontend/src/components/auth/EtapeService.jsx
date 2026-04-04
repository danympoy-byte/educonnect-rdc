import React, { useState } from 'react';
import { PROVINCES_EDUCATIONNELLES } from '../../data/provincesEducationnelles';

const POSTES_PROVINCIAUX = [
  { value: 'proved', label: 'PROVED (Chef Provincial Education)', description: 'Representant du Ministre au niveau provincial' },
  { value: 'ipp', label: 'IPP (Inspecteur Provincial Principal)', description: 'Charge des epreuves certificatives' },
  { value: 'diprocope', label: 'DIPROCOPE (Dir. Prov. Controle et Paie)', description: 'Paie des enseignants et agents' },
  { value: 'ministre_provincial', label: 'Ministre Provincial de l\'Education', description: 'Gouvernement provincial' },
];

const POSTES_ETABLISSEMENT = [
  { value: 'chef_etablissement', label: 'Chef d\'Etablissement (Secondaire)', description: 'Responsable d\'un etablissement secondaire' },
  { value: 'directeur_ecole', label: 'Directeur d\'Ecole (Primaire)', description: 'Responsable d\'une ecole primaire' },
  { value: 'conseiller_principal_education', label: 'Conseiller Principal d\'Education (CPE)', description: 'Vie scolaire et discipline' },
  { value: 'enseignant', label: 'Enseignant', description: 'Enseignant dans un etablissement' },
];

const POSTES_CENTRAUX = [
  { value: 'personnel_administratif', label: 'Personnel Administratif', description: 'Agent du ministere' },
  { value: 'inspecteur_pedagogique', label: 'Inspecteur Pedagogique', description: 'Inspection et controle qualite' },
  { value: 'agent_dinacope', label: 'Agent DINACOPE', description: 'Controle et paie nationale' },
];

// Provinces administratives avec leurs provinces éducationnelles
const provincesOptions = PROVINCES_EDUCATIONNELLES.map(p => ({
  admin: p.provinceAdmin,
  educationnelles: p.provincesEdu.map(pe => ({ nom: pe.nom, chefLieu: pe.chefLieu }))
}));

const EtapeService = ({
  formEtape2, setFormEtape2,
  servicesHierarchie, serviceSelectionne, setServiceSelectionne,
  cheminHierarchique, setCheminHierarchique,
  niveauActuel, setNiveauActuel,
  selectionnerService, onSubmit, onRetour
}) => {
  const [typePoste, setTypePoste] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedProvinceAdmin, setSelectedProvinceAdmin] = useState('');
  const [selectedProvinceEdu, setSelectedProvinceEdu] = useState('');
  const [showOrganigramme, setShowOrganigramme] = useState(false);

  const naviguerVersService = (service) => {
    setCheminHierarchique([...cheminHierarchique, service]);
    setNiveauActuel(niveauActuel + 1);
  };

  const remonterHierarchie = () => {
    if (cheminHierarchique.length > 0) {
      setCheminHierarchique(cheminHierarchique.slice(0, -1));
      setNiveauActuel(Math.max(1, niveauActuel - 1));
    }
  };

  const getServicesNiveauActuel = () => {
    if (cheminHierarchique.length === 0) return servicesHierarchie;
    const dernier = cheminHierarchique[cheminHierarchique.length - 1];
    if (dernier.directions?.length > 0) return dernier.directions;
    if (dernier.services?.length > 0) return dernier.services;
    return [];
  };

  const servicesAffiches = getServicesNiveauActuel();

  const handleTypePosteChange = (type) => {
    setTypePoste(type);
    setSelectedRole('');
    setSelectedProvinceAdmin('');
    setSelectedProvinceEdu('');
    setShowOrganigramme(type === 'central');
    if (type !== 'central') {
      setServiceSelectionne(null);
    }
  };

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setFormEtape2({ ...formEtape2, poste: role });
  };

  const getProvincesEdu = () => {
    const found = provincesOptions.find(p => p.admin === selectedProvinceAdmin);
    return found?.educationnelles || [];
  };

  const isProvinceRole = ['proved', 'ipp', 'diprocope', 'ministre_provincial'].includes(selectedRole);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!typePoste) {
      return;
    }

    if (typePoste === 'provincial') {
      if (!selectedRole) return;
      if (!selectedProvinceAdmin) return;
      // For PROVED/IPP/DIPROCOPE, province éducationnelle is mandatory
      if (['proved', 'ipp', 'diprocope'].includes(selectedRole) && !selectedProvinceEdu) return;
    }

    if (typePoste === 'etablissement') {
      if (!selectedRole) return;
    }

    if (typePoste === 'central') {
      if (!serviceSelectionne && !selectedRole) return;
    }

    // Build the poste string
    let posteLabel = selectedRole;
    if (isProvinceRole && selectedProvinceEdu) {
      posteLabel = `${selectedRole} - ${selectedProvinceEdu}`;
    } else if (isProvinceRole && selectedProvinceAdmin) {
      posteLabel = `${selectedRole} - ${selectedProvinceAdmin}`;
    }

    setFormEtape2({ ...formEtape2, poste: posteLabel });

    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" data-testid="form-etape-2">
      <h3 className="text-xl font-bold text-gray-900 mb-2">Etape 2 : Selection de votre poste</h3>
      <p className="text-gray-600 mb-6">Selectionnez votre categorie de poste et vos informations d'affectation.</p>

      {/* Sélection du type de poste */}
      <div data-testid="type-poste-selector">
        <label className="block text-sm font-semibold text-gray-800 mb-3">Categorie de poste *</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { key: 'provincial', label: 'Poste Provincial', desc: 'PROVED, IPP, DIPROCOPE, Ministre Prov.', icon: 'M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9' },
            { key: 'etablissement', label: 'Poste en Etablissement', desc: 'Chef Etab., Directeur, CPE, Enseignant', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
            { key: 'central', label: 'Administration Centrale', desc: 'Agent MINEPST, Inspecteur, DINACOPE', icon: 'M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z' }
          ].map(type => (
            <button
              key={type.key}
              type="button"
              onClick={() => handleTypePosteChange(type.key)}
              className={`p-4 rounded-xl border-2 text-left transition ${
                typePoste === type.key
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
              data-testid={`type-${type.key}`}
            >
              <svg className={`w-6 h-6 mb-2 ${typePoste === type.key ? 'text-indigo-600' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={type.icon} />
              </svg>
              <p className={`font-semibold text-sm ${typePoste === type.key ? 'text-indigo-700' : 'text-gray-800'}`}>{type.label}</p>
              <p className="text-xs text-gray-500 mt-0.5">{type.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* POSTE PROVINCIAL */}
      {typePoste === 'provincial' && (
        <div className="space-y-4 p-5 bg-gray-50 rounded-xl border border-gray-200" data-testid="section-provincial">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">Poste provincial *</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {POSTES_PROVINCIAUX.map(poste => (
                <button
                  key={poste.value}
                  type="button"
                  onClick={() => handleRoleSelect(poste.value)}
                  className={`p-3 rounded-lg border text-left transition ${
                    selectedRole === poste.value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                  data-testid={`role-${poste.value}`}
                >
                  <p className="font-semibold text-sm text-gray-900">{poste.label}</p>
                  <p className="text-xs text-gray-500">{poste.description}</p>
                </button>
              ))}
            </div>
          </div>

          {selectedRole && (
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">Province administrative *</label>
              <select
                value={selectedProvinceAdmin}
                onChange={(e) => { setSelectedProvinceAdmin(e.target.value); setSelectedProvinceEdu(''); }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white"
                data-testid="select-province-admin"
              >
                <option value="">-- Selectionnez une province --</option>
                {provincesOptions.map((p, i) => (
                  <option key={i} value={p.admin}>{p.admin}</option>
                ))}
              </select>
            </div>
          )}

          {selectedProvinceAdmin && ['proved', 'ipp', 'diprocope'].includes(selectedRole) && (
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">Province educationnelle *</label>
              <select
                value={selectedProvinceEdu}
                onChange={(e) => setSelectedProvinceEdu(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white"
                data-testid="select-province-edu"
              >
                <option value="">-- Selectionnez une province educationnelle --</option>
                {getProvincesEdu().map((pe, i) => (
                  <option key={i} value={pe.nom}>{pe.nom} (Chef-lieu: {pe.chefLieu})</option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* POSTE EN ETABLISSEMENT */}
      {typePoste === 'etablissement' && (
        <div className="space-y-4 p-5 bg-gray-50 rounded-xl border border-gray-200" data-testid="section-etablissement">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-2">Fonction *</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {POSTES_ETABLISSEMENT.map(poste => (
                <button
                  key={poste.value}
                  type="button"
                  onClick={() => handleRoleSelect(poste.value)}
                  className={`p-3 rounded-lg border text-left transition ${
                    selectedRole === poste.value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                  data-testid={`role-${poste.value}`}
                >
                  <p className="font-semibold text-sm text-gray-900">{poste.label}</p>
                  <p className="text-xs text-gray-500">{poste.description}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ADMINISTRATION CENTRALE */}
      {typePoste === 'central' && (
        <div className="space-y-4" data-testid="section-central">
          {/* Sélection rapide du rôle */}
          <div className="p-5 bg-gray-50 rounded-xl border border-gray-200">
            <label className="block text-sm font-semibold text-gray-800 mb-2">Fonction *</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-4">
              {POSTES_CENTRAUX.map(poste => (
                <button
                  key={poste.value}
                  type="button"
                  onClick={() => handleRoleSelect(poste.value)}
                  className={`p-3 rounded-lg border text-left transition ${
                    selectedRole === poste.value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                  data-testid={`role-${poste.value}`}
                >
                  <p className="font-semibold text-sm text-gray-900">{poste.label}</p>
                  <p className="text-xs text-gray-500">{poste.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Organigramme du MINEPST */}
          <div className="border border-gray-200 rounded-xl bg-white">
            <div className="px-5 py-3 bg-gray-50 border-b border-gray-200">
              <h4 className="font-semibold text-gray-900 text-sm">Organigramme du MINEPST (optionnel)</h4>
              <p className="text-xs text-gray-500">Selectionnez votre service d'affectation si applicable</p>
            </div>

            {/* Breadcrumb */}
            {cheminHierarchique.length > 0 && (
              <div className="flex items-center space-x-2 p-3 bg-gray-50 flex-wrap border-b border-gray-100" data-testid="breadcrumb-services">
                <button type="button" onClick={() => { setCheminHierarchique([]); setNiveauActuel(1); }}
                  className="text-sm text-blue-600 hover:text-blue-800 hover:underline">Ministere</button>
                {cheminHierarchique.map((service, index) => (
                  <React.Fragment key={service.id}>
                    <span className="text-gray-400">&rsaquo;</span>
                    <button type="button" onClick={() => { setCheminHierarchique(cheminHierarchique.slice(0, index + 1)); setNiveauActuel(index + 2); }}
                      className="text-sm text-blue-600 hover:text-blue-800 hover:underline truncate max-w-xs">{service.nom}</button>
                  </React.Fragment>
                ))}
              </div>
            )}

            {/* Service sélectionné */}
            {serviceSelectionne && (
              <div className="p-4 bg-green-50 border-b border-green-200" data-testid="service-selectionne">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-700 font-medium">Service selectionne :</p>
                    <p className="text-base font-bold text-green-900">{serviceSelectionne.nom}</p>
                    <p className="text-sm text-green-600">Code : {serviceSelectionne.code}</p>
                  </div>
                  <button type="button" onClick={() => setServiceSelectionne(null)} className="text-red-600 hover:text-red-800 text-sm">Annuler</button>
                </div>
              </div>
            )}

            <div className="p-4" data-testid="grille-services">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-72 overflow-y-auto">
                {servicesAffiches.map((service) => {
                  const estSelectionne = serviceSelectionne?.id === service.id;
                  const aDesEnfants = (service.directions?.length > 0) || (service.services?.length > 0);
                  return (
                    <div key={service.id}
                      className={`border rounded-lg p-3 transition cursor-pointer ${estSelectionne ? 'border-green-500 bg-green-50 shadow-md' : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'}`}
                      onClick={() => { if (!estSelectionne) selectionnerService(service); }} data-testid={`service-card-${service.code}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm text-gray-900 truncate mb-1">{service.nom}</p>
                          <p className="text-xs text-gray-500">Code : {service.code}</p>
                        </div>
                        {aDesEnfants && (
                          <button type="button" onClick={(e) => { e.stopPropagation(); naviguerVersService(service); }}
                            className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200 flex-shrink-0">Ouvrir</button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              {servicesAffiches.length === 0 && <p className="text-center text-gray-500 py-4 text-sm">Aucun service disponible</p>}
            </div>

            {cheminHierarchique.length > 0 && (
              <div className="px-4 pb-4">
                <button type="button" onClick={remonterHierarchie} className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm" data-testid="btn-retour-niveau">
                  Retour au niveau precedent
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Boutons de navigation */}
      <div className="flex justify-between pt-4">
        <button type="button" onClick={onRetour} className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 font-medium" data-testid="btn-retour-etape1">Retour</button>
        <button
          type="submit"
          disabled={!typePoste || !selectedRole}
          className={`px-6 py-3 rounded-lg font-medium transition ${
            typePoste && selectedRole
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          data-testid="btn-terminer-inscription"
        >
          Terminer l'inscription
        </button>
      </div>

      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Note :</strong> Apres validation, vous pourrez vous connecter immediatement avec votre telephone et votre mot de passe.
          Votre role determinera vos acces aux differents modules de la plateforme.
        </p>
      </div>
    </form>
  );
};

export default EtapeService;
