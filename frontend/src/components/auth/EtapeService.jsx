import React from 'react';

const EtapeService = ({
  formEtape2, setFormEtape2,
  servicesHierarchie, serviceSelectionne, setServiceSelectionne,
  cheminHierarchique, setCheminHierarchique,
  niveauActuel, setNiveauActuel,
  selectionnerService, onSubmit, onRetour
}) => {

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

  return (
    <form onSubmit={onSubmit} className="space-y-6" data-testid="form-etape-2">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Étape 2 : Sélection de votre service</h3>
      <p className="text-gray-600 mb-6">Naviguez dans l'organigramme du MINEPST et sélectionnez le service auquel vous appartenez.</p>

      {/* Breadcrumb */}
      {cheminHierarchique.length > 0 && (
        <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg flex-wrap" data-testid="breadcrumb-services">
          <button type="button" onClick={() => { setCheminHierarchique([]); setNiveauActuel(1); }}
            className="text-sm text-blue-600 hover:text-blue-800 hover:underline">Ministère</button>
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
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg" data-testid="service-selectionne">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700 font-medium">Service sélectionné :</p>
              <p className="text-lg font-bold text-green-900">{serviceSelectionne.nom}</p>
              <p className="text-sm text-green-600">Code : {serviceSelectionne.code} | Niveau {serviceSelectionne.niveau}</p>
            </div>
            <button type="button" onClick={() => setServiceSelectionne(null)} className="text-red-600 hover:text-red-800 text-sm">Annuler</button>
          </div>
        </div>
      )}

      {/* Grille des services */}
      <div className="border border-gray-200 rounded-lg p-4 bg-white" data-testid="grille-services">
        <h4 className="font-semibold text-gray-900 mb-4">
          {cheminHierarchique.length === 0 ? 'Directions Générales' : `Services sous : ${cheminHierarchique[cheminHierarchique.length - 1].nom}`}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
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
                    <p className="text-xs text-gray-500 mb-2">Code : {service.code}</p>
                    {service.responsable_nom && <p className="text-xs text-gray-600">{service.responsable_nom}</p>}
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
        {servicesAffiches.length === 0 && <p className="text-center text-gray-500 py-8">Aucun service disponible à ce niveau</p>}
      </div>

      {cheminHierarchique.length > 0 && (
        <button type="button" onClick={remonterHierarchie} className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition" data-testid="btn-retour-niveau">
          Retour au niveau précédent
        </button>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Intitulé de votre poste *</label>
        <input type="text" value={formEtape2.poste} onChange={(e) => setFormEtape2({ ...formEtape2, poste: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg" required placeholder="Ex: Chef de division, Agent administratif..." data-testid="input-poste" />
      </div>

      <div className="flex justify-between pt-4">
        <button type="button" onClick={onRetour} className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 font-medium" data-testid="btn-retour-etape1">Retour</button>
        <button type="submit" className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium" data-testid="btn-terminer-inscription">Terminer l'inscription</button>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Note :</strong> Après validation, vous pourrez vous connecter immédiatement avec votre téléphone et votre mot de passe.
          Vous pourrez compléter votre profil (email, photo, compte bancaire) plus tard depuis votre tableau de bord.
        </p>
      </div>
    </form>
  );
};

export default EtapeService;
