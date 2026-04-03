import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const StatsCharts = ({ stats, statsSexe }) => {
  if (!stats) return null;

  // Préparer les données pour les graphiques
  const provinceData = stats?.repartition_par_province 
    ? Object.entries(stats.repartition_par_province).map(([key, value]) => ({
        name: key,
        count: value
      }))
    : [];

  const niveauData = stats?.repartition_par_niveau
    ? Object.entries(stats.repartition_par_niveau).map(([key, value]) => ({
        name: key.replace(/_/g, ' '),
        value: value
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Répartition par province - GRAND FORMAT */}
      {provinceData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Établissements par Province Administrative</h3>
            <span className="text-sm text-gray-500">{provinceData.length} provinces</span>
          </div>
          <div className="overflow-x-auto">
            <ResponsiveContainer width="100%" height={600}>
              <BarChart data={provinceData} margin={{ top: 20, right: 30, left: 20, bottom: 150 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end" 
                  height={150}
                  interval={0}
                  tick={{ fontSize: 11 }}
                />
                <YAxis label={{ value: 'Nombre d\'établissements', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#4F46E5" name="Établissements" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          {/* Tableau récapitulatif */}
          <div className="mt-6 border-t pt-6">
            <h4 className="text-md font-semibold text-gray-900 mb-4">Détail par Province</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {provinceData.sort((a, b) => b.count - a.count).map((province, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">{province.name}</span>
                    <span className="text-lg font-bold text-indigo-600">{province.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Répartition par niveau */}
      {niveauData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition des élèves par niveau</h3>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={niveauData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {niveauData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Statistiques par Sexe */}
      {statsSexe && (
        <div className="space-y-6 mt-8">
          <h2 className="text-2xl font-bold text-gray-900">Répartition par Sexe</h2>
          
          {/* Stats globales par sexe - ÉLÈVES */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Élèves</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Garçons</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{statsSexe.eleves.global.masculin}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👨‍🎓</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Filles</p>
                    <p className="text-3xl font-bold text-pink-600 mt-2">{statsSexe.eleves.global.feminin}</p>
                  </div>
                  <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👩‍🎓</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Élèves</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{statsSexe.eleves.global.total}</p>
                  </div>
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">🎓</span>
                  </div>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                  <span className="mr-3">Garçons: {((statsSexe.eleves.global.masculin / statsSexe.eleves.global.total) * 100).toFixed(1)}%</span>
                  <span>Filles: {((statsSexe.eleves.global.feminin / statsSexe.eleves.global.total) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Stats globales par sexe - ENSEIGNANTS */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Enseignants</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Hommes</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{statsSexe.enseignants.global.masculin}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👨‍🏫</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Femmes</p>
                    <p className="text-3xl font-bold text-pink-600 mt-2">{statsSexe.enseignants.global.feminin}</p>
                  </div>
                  <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👩‍🏫</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Enseignants</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{statsSexe.enseignants.global.total}</p>
                  </div>
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👥</span>
                  </div>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                  <span className="mr-3">Hommes: {((statsSexe.enseignants.global.masculin / statsSexe.enseignants.global.total) * 100).toFixed(1)}%</span>
                  <span>Femmes: {((statsSexe.enseignants.global.feminin / statsSexe.enseignants.global.total) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Stats globales par sexe - DIRECTEURS */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Directeurs d'Écoles</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Hommes</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{statsSexe.directeurs.global.masculin}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👨‍💼</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Femmes</p>
                    <p className="text-3xl font-bold text-pink-600 mt-2">{statsSexe.directeurs.global.feminin}</p>
                  </div>
                  <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👩‍💼</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Directeurs</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{statsSexe.directeurs.global.total}</p>
                  </div>
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl">👥</span>
                  </div>
                </div>
                <div className="mt-4 text-xs text-gray-500">
                  <span className="mr-3">Hommes: {((statsSexe.directeurs.global.masculin / statsSexe.directeurs.global.total) * 100).toFixed(1)}%</span>
                  <span>Femmes: {((statsSexe.directeurs.global.feminin / statsSexe.directeurs.global.total) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Graphique: Répartition ÉLÈVES par sexe et par niveau */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Élèves: Répartition par Sexe et par Niveau</h3>
            <ResponsiveContainer width="100%" height={500}>
              <BarChart 
                data={Object.entries(statsSexe.eleves.par_niveau).map(([niveau, data]) => ({
                  niveau: niveau.replace(/_/g, ' '),
                  Garçons: data.masculin || 0,
                  Filles: data.feminin || 0
                }))}
                margin={{ top: 20, right: 30, left: 20, bottom: 100 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="niveau" angle={-45} textAnchor="end" height={100} interval={0} tick={{ fontSize: 10 }} />
                <YAxis label={{ value: 'Nombre d\'élèves', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Garçons" fill="#3B82F6" />
                <Bar dataKey="Filles" fill="#EC4899" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Graphique: Répartition ÉLÈVES par sexe et par province */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Élèves: Répartition par Sexe et par Province Administrative (26 provinces)</h3>
            <ResponsiveContainer width="100%" height={600}>
              <BarChart 
                data={(() => {
                  // Liste des 26 provinces administratives
                  const provinces26 = [
                    "Kinshasa", "Kongo Central", "Kwango", "Kwilu", "Mai-Ndombe",
                    "Équateur", "Mongala", "Nord-Ubangi", "Sud-Ubangi", "Tshuapa",
                    "Tshopo", "Bas-Uele", "Haut-Uele", "Ituri", "Nord-Kivu",
                    "Sud-Kivu", "Maniema", "Haut-Katanga", "Lualaba", "Tanganyika",
                    "Haut-Lomami", "Kasaï", "Kasaï-Central", "Kasaï-Oriental", "Lomami", "Sankuru"
                  ];
                  
                  // Créer un objet avec toutes les provinces à 0 par défaut
                  const provinceData = {};
                  provinces26.forEach(prov => {
                    provinceData[prov] = { Garçons: 0, Filles: 0 };
                  });
                  
                  // Remplir avec les vraies données
                  Object.entries(statsSexe.eleves.par_province).forEach(([province, data]) => {
                    if (provinceData[province]) {
                      provinceData[province].Garçons = data.masculin || 0;
                      provinceData[province].Filles = data.feminin || 0;
                    }
                  });
                  
                  // Convertir en array pour le graphique
                  return provinces26.map(province => ({
                    province,
                    Garçons: provinceData[province].Garçons,
                    Filles: provinceData[province].Filles
                  }));
                })()}
                margin={{ top: 20, right: 30, left: 20, bottom: 150 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="province" angle={-45} textAnchor="end" height={150} interval={0} tick={{ fontSize: 10 }} />
                <YAxis label={{ value: 'Nombre d\'élèves', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Garçons" fill="#3B82F6" />
                <Bar dataKey="Filles" fill="#EC4899" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Graphique: Répartition ENSEIGNANTS par sexe et par province */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Enseignants: Répartition par Sexe et par Province Administrative (26 provinces)</h3>
            <ResponsiveContainer width="100%" height={600}>
              <BarChart 
                data={(() => {
                  // Liste des 26 provinces administratives
                  const provinces26 = [
                    "Kinshasa", "Kongo Central", "Kwango", "Kwilu", "Mai-Ndombe",
                    "Équateur", "Mongala", "Nord-Ubangi", "Sud-Ubangi", "Tshuapa",
                    "Tshopo", "Bas-Uele", "Haut-Uele", "Ituri", "Nord-Kivu",
                    "Sud-Kivu", "Maniema", "Haut-Katanga", "Lualaba", "Tanganyika",
                    "Haut-Lomami", "Kasaï", "Kasaï-Central", "Kasaï-Oriental", "Lomami", "Sankuru"
                  ];
                  
                  // Créer un objet avec toutes les provinces à 0 par défaut
                  const provinceData = {};
                  provinces26.forEach(prov => {
                    provinceData[prov] = { Hommes: 0, Femmes: 0 };
                  });
                  
                  // Remplir avec les vraies données
                  Object.entries(statsSexe.enseignants.par_province).forEach(([province, data]) => {
                    if (provinceData[province]) {
                      provinceData[province].Hommes = data.masculin || 0;
                      provinceData[province].Femmes = data.feminin || 0;
                    }
                  });
                  
                  // Convertir en array pour le graphique
                  return provinces26.map(province => ({
                    province,
                    Hommes: provinceData[province].Hommes,
                    Femmes: provinceData[province].Femmes
                  }));
                })()}
                margin={{ top: 20, right: 30, left: 20, bottom: 150 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="province" angle={-45} textAnchor="end" height={150} interval={0} tick={{ fontSize: 10 }} />
                <YAxis label={{ value: 'Nombre d\'enseignants', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="Hommes" fill="#3B82F6" />
                <Bar dataKey="Femmes" fill="#EC4899" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsCharts;
