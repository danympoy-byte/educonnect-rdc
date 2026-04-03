import React from 'react';
import toast from 'react-hot-toast';
import provincesService from '../../../services/provinces.service';

const ProvinceNavigator = ({ 
  provinces,
  sousDivisions, 
  selectedProvince, 
  filteredSousDivisions,
  showProvinceForm,
  provinceForm,
  setProvinceForm,
  setShowProvinceForm,
  onProvinceClick,
  onBack,
  loadData
}) => {
  
  const handleCreateProvince = async (e) => {
    e.preventDefault();
    try {
      await provincesService.create(provinceForm);
      toast.success('Province créée avec succès');
      setShowProvinceForm(false);
      setProvinceForm({ nom: '', code: '' });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          {selectedProvince 
            ? `Provinces Éducationnelles de ${selectedProvince.nom}` 
            : 'Provinces Administratives (26)'}
        </h2>
        <div className="flex gap-3">
          {selectedProvince && (
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              ← Retour aux provinces
            </button>
          )}
          <button
            onClick={() => setShowProvinceForm(!showProvinceForm)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            + Nouvelle Province
          </button>
        </div>
      </div>

      {showProvinceForm && (
        <form onSubmit={handleCreateProvince} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom de la province</label>
              <input
                type="text"
                value={provinceForm.nom}
                onChange={(e) => setProvinceForm({ ...provinceForm, nom: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Code</label>
              <input
                type="text"
                value={provinceForm.code}
                onChange={(e) => setProvinceForm({ ...provinceForm, code: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          </div>
          <div className="mt-4 flex space-x-3">
            <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
              Créer
            </button>
            <button
              type="button"
              onClick={() => setShowProvinceForm(false)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Annuler
            </button>
          </div>
        </form>
      )}

      {/* Affichage des provinces administratives */}
      {!selectedProvince && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {provinces.map((province) => {
            const nbSousDivisions = sousDivisions.filter(sd => sd.province_id === province.id).length;
            return (
              <div
                key={province.id}
                onClick={() => onProvinceClick(province)}
                className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:border-indigo-500 hover:shadow-lg transition-all cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition">
                    <span className="text-xl font-bold text-indigo-600">{province.code}</span>
                  </div>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                    {nbSousDivisions} {nbSousDivisions > 1 ? 'P.E.' : 'P.E.'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition">
                  {province.nom}
                </h3>
                <p className="text-sm text-gray-500">
                  Cliquez pour voir les provinces éducationnelles
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* Affichage des provinces éducationnelles */}
      {selectedProvince && (
        <div className="space-y-4">
          <div className="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg">
            <p className="text-sm text-indigo-700">
              <span className="font-semibold">{filteredSousDivisions.length}</span> province(s) éducationnelle(s) 
              dans la province administrative de <span className="font-semibold">{selectedProvince.nom}</span>
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Province Administrative</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date création</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSousDivisions.map((sousDivision) => (
                  <tr key={sousDivision.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{sousDivision.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{sousDivision.nom}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-indigo-600 font-medium">{selectedProvince.nom}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(sousDivision.created_at).toLocaleDateString('fr-FR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProvinceNavigator;
