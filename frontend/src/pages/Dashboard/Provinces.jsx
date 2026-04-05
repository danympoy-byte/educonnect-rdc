import React, { useState } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import CarteRDC from '../../components/dashboards/components/CarteRDC';
import { 
  INTRO_TEXT, 
  COMITE_PROVINCIAL, 
  PROVINCES_EDUCATIONNELLES, 
  STATS 
} from '../../data/provincesEducationnelles';

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
  const [selectedAdminProvince, setSelectedAdminProvince] = useState(null);
  const [selectedEduProvince, setSelectedEduProvince] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('carte'); // 'carte' ou 'liste'

  const handleSelectAdmin = (province) => {
    setSelectedAdminProvince(province);
    setSelectedEduProvince(null);
  };

  const handleSelectEdu = (eduProvince) => {
    setSelectedEduProvince(eduProvince);
  };

  const handleBack = () => {
    if (selectedEduProvince) {
      setSelectedEduProvince(null);
    } else {
      setSelectedAdminProvince(null);
    }
  };

  const filteredProvinces = searchTerm
    ? PROVINCES_EDUCATIONNELLES.filter(p =>
        p.provinceAdmin.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.provincesEdu.some(pe => pe.nom.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : PROVINCES_EDUCATIONNELLES;

  return (
    <div className="space-y-6" data-testid="provinces-page">
      {/* Header avec statistiques */}
      {!selectedAdminProvince && (
        <div className="space-y-6">
          {/* Bandeau de stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-xl p-5 text-white" data-testid="stat-provinces-admin">
              <p className="text-indigo-200 text-sm font-medium">Provinces Administratives</p>
              <p className="text-3xl font-bold mt-1">{STATS.totalProvincesAdmin}</p>
            </div>
            <div className="bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl p-5 text-white" data-testid="stat-provinces-edu">
              <p className="text-emerald-200 text-sm font-medium">Provinces Educationnelles</p>
              <p className="text-3xl font-bold mt-1">{STATS.totalProvincesEdu}</p>
            </div>
            <div className="bg-gradient-to-br from-amber-600 to-amber-700 rounded-xl p-5 text-white" data-testid="stat-sous-divisions">
              <p className="text-amber-200 text-sm font-medium">Sous-Divisions</p>
              <p className="text-3xl font-bold mt-1">{STATS.totalSousDivisions}</p>
            </div>
          </div>

          {/* Texte introductif */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6" data-testid="intro-section">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Provinces Educationnelles de la RDC</h2>
            <p className="text-gray-600 leading-relaxed text-sm">{INTRO_TEXT}</p>
            
            {/* Comité provincial */}
            <div className="mt-5">
              <h3 className="text-base font-semibold text-gray-800 mb-3">
                Comité provincial de l'EDU-NC
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {COMITE_PROVINCIAL.map((membre) => (
                  <div key={membre.role} className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold">
                        {membre.numero}
                      </span>
                      <span className="font-semibold text-gray-900 text-sm">{membre.role}</span>
                    </div>
                    <p className="text-xs text-gray-600 leading-relaxed">{membre.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Carte interactive + Toggle */}
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900">
              Les 26 Provinces Administratives
            </h2>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1" data-testid="view-toggle">
              <button
                onClick={() => setViewMode('carte')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${viewMode === 'carte' ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
                data-testid="btn-view-carte"
              >
                <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" /></svg>
                Carte
              </button>
              <button
                onClick={() => setViewMode('liste')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${viewMode === 'liste' ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700'}`}
                data-testid="btn-view-liste"
              >
                <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                Grille
              </button>
            </div>
          </div>

          {/* Vue Carte */}
          {viewMode === 'carte' && (
            <CarteRDC
              provincesData={PROVINCES_EDUCATIONNELLES}
              onSelectProvince={handleSelectAdmin}
            />
          )}

          {/* Vue Grille */}
          {viewMode === 'liste' && (
            <>
              {/* Barre de recherche */}
              <div className="relative" data-testid="search-provinces">
                <input
                  type="text"
                  placeholder="Rechercher une province administrative ou éducationnelle..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-3 pl-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  data-testid="search-input"
                />
                <svg className="absolute left-3 top-3.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              {/* Grille des provinces administratives */}
              <div>
                {searchTerm && (
                  <p className="text-sm text-gray-500 mb-3">{filteredProvinces.length} resultat(s)</p>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="provinces-grid">
              {filteredProvinces.map((province, idx) => {
                const totalSD = province.provincesEdu.reduce((a, pe) => a + pe.sousDivisions.length, 0);
                return (
                  <div
                    key={province.provinceAdmin}
                    onClick={() => handleSelectAdmin(province)}
                    className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-5 hover:border-indigo-500 hover:shadow-lg transition-all cursor-pointer group"
                    data-testid={`province-card-${idx}`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition">
                        <span className="text-sm font-bold text-indigo-600">{idx + 1}</span>
                      </div>
                      <div className="flex gap-1.5">
                        <span className="text-xs bg-emerald-100 px-2 py-1 rounded-full text-emerald-700 font-medium">
                          {province.provincesEdu.length} P.E.
                        </span>
                        <span className="text-xs bg-amber-100 px-2 py-1 rounded-full text-amber-700 font-medium">
                          {totalSD} S.D.
                        </span>
                      </div>
                    </div>
                    <h3 className="text-base font-semibold text-gray-900 mb-1 group-hover:text-indigo-600 transition">
                      {province.provinceAdmin}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {province.provincesEdu.map(pe => pe.chefLieu).join(', ')}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
            </>
          )}
        </div>
      )}

      {/* Vue détaillée d'une province administrative */}
      {selectedAdminProvince && !selectedEduProvince && (
        <div className="space-y-5" data-testid="admin-province-detail">
          <div className="flex justify-between items-center">
            <div>
              <button
                onClick={handleBack}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium mb-2 flex items-center gap-1"
                data-testid="back-button"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Retour aux provinces
              </button>
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedAdminProvince.provinceAdmin}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {selectedAdminProvince.provincesEdu.length} province(s) éducationnelle(s)
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {selectedAdminProvince.provincesEdu.map((eduProv, idx) => (
              <div
                key={eduProv.nom}
                onClick={() => handleSelectEdu(eduProv)}
                className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-indigo-500 hover:shadow-lg transition-all cursor-pointer group"
                data-testid={`edu-province-card-${idx}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition">
                      {eduProv.nom}
                    </h3>
                    <p className="text-sm text-gray-500 mt-0.5">
                      Chef-lieu : <span className="font-medium text-gray-700">{eduProv.chefLieu}</span>
                    </p>
                  </div>
                  <span className="text-xs bg-indigo-100 px-2.5 py-1 rounded-full text-indigo-700 font-medium">
                    {eduProv.sousDivisions.length} sous-divisions
                  </span>
                </div>

                {/* Contacts résumés */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold flex-shrink-0">P</span>
                    <span className="text-gray-700 truncate">{eduProv.contacts.proved.nom}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="w-6 h-6 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold flex-shrink-0">I</span>
                    <span className="text-gray-700 truncate">{eduProv.contacts.ipp.nom}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="w-6 h-6 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center text-xs font-bold flex-shrink-0">D</span>
                    <span className="text-gray-700 truncate">{eduProv.contacts.diprocope.nom}</span>
                  </div>
                </div>

                <p className="text-xs text-indigo-500 mt-4 font-medium group-hover:underline">
                  Voir les details et sous-divisions →
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vue détaillée d'une province éducationnelle */}
      {selectedEduProvince && (
        <div className="space-y-5" data-testid="edu-province-detail">
          <div>
            <button
              onClick={handleBack}
              className="text-sm text-indigo-600 hover:text-indigo-800 font-medium mb-2 flex items-center gap-1"
              data-testid="back-to-admin-button"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Retour a {selectedAdminProvince.provinceAdmin}
            </button>
            <h2 className="text-2xl font-bold text-gray-900">
              {selectedEduProvince.nom}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Chef-lieu : <span className="font-medium text-gray-700">{selectedEduProvince.chefLieu}</span>
              {' | '}{selectedAdminProvince.provinceAdmin}
            </p>
          </div>

          {/* Contacts détaillés */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6" data-testid="contacts-section">
            <h3 className="text-base font-bold text-gray-900 mb-4">Comite Provincial</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* PROVED */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">P</span>
                  <span className="font-semibold text-gray-900 text-sm">PROVED</span>
                </div>
                <p className="text-sm text-gray-800 font-medium">{selectedEduProvince.contacts.proved.nom}</p>
                {selectedEduProvince.contacts.proved.tel && (
                  <p className="text-xs text-gray-500 mt-1">Tel: {selectedEduProvince.contacts.proved.tel}</p>
                )}
                <p className="text-xs text-indigo-600 mt-1 break-all">{selectedEduProvince.contacts.proved.email}</p>
              </div>
              {/* IPP */}
              <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-8 h-8 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">I</span>
                  <span className="font-semibold text-gray-900 text-sm">IPP</span>
                </div>
                <p className="text-sm text-gray-800 font-medium">{selectedEduProvince.contacts.ipp.nom}</p>
                {selectedEduProvince.contacts.ipp.tel && (
                  <p className="text-xs text-gray-500 mt-1">Tel: {selectedEduProvince.contacts.ipp.tel}</p>
                )}
                <p className="text-xs text-indigo-600 mt-1 break-all">{selectedEduProvince.contacts.ipp.email}</p>
              </div>
              {/* DIPROCOPE */}
              <div className="bg-orange-50 rounded-lg p-4 border border-orange-100">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-8 h-8 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center text-xs font-bold">D</span>
                  <span className="font-semibold text-gray-900 text-sm">DIPROCOPE</span>
                </div>
                <p className="text-sm text-gray-800 font-medium">{selectedEduProvince.contacts.diprocope.nom}</p>
                {selectedEduProvince.contacts.diprocope.tel && (
                  <p className="text-xs text-gray-500 mt-1">Tel: {selectedEduProvince.contacts.diprocope.tel}</p>
                )}
                <p className="text-xs text-indigo-600 mt-1 break-all">{selectedEduProvince.contacts.diprocope.email}</p>
              </div>
            </div>
          </div>

          {/* Tableau des sous-divisions */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" data-testid="sous-divisions-table">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h3 className="text-base font-bold text-gray-900">
                Sous-Divisions ({selectedEduProvince.sousDivisions.length})
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lieu d'implantation</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {selectedEduProvince.sousDivisions.map((sd, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-3 whitespace-nowrap text-sm text-gray-400 font-medium">{idx + 1}</td>
                      <td className="px-6 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{sd.nom}</td>
                      <td className="px-6 py-3 whitespace-nowrap text-sm text-gray-600">{sd.lieu}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Provinces;
