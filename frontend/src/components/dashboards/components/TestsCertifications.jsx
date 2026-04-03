import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';
import testsService from '../../../services/tests.service';

const COLORS_PIE = ['#10B981', '#3B82F6', '#EF4444'];
const COLORS_BAR = { masculin: '#3B82F6', feminin: '#EC4899' };

const TestsCertifications = () => {
  const [stats, setStats] = useState(null);
  const [resultats, setResultats] = useState([]);
  const [categories, setCategories] = useState([]);
  const [etablissementsEligibles, setEtablissementsEligibles] = useState([]);
  const [selectedCategorie, setSelectedCategorie] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, categoriesData, eligiblesData] = await Promise.all([
        testsService.getStats(),
        testsService.getCategories(),
        testsService.getEtablissementsEligibles()
      ]);
      
      setStats(statsData);
      setCategories(categoriesData);
      setEtablissementsEligibles(eligiblesData);
      
      // Charger tous les résultats
      const resultatsData = await testsService.getResultats();
      setResultats(resultatsData);
    } catch (error) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const filterResultatsByCategorie = async (categorie) => {
    setSelectedCategorie(categorie);
    try {
      const resultatsData = await testsService.getResultats(categorie);
      setResultats(resultatsData);
    } catch (error) {
      toast.error('Erreur lors du filtrage');
    }
  };

  const getEligibilityPieData = () => {
    if (!stats) return [];
    
    const eligibles = stats.etablissements_eligibles;
    return [
      { name: 'Excellent (90-100%)', value: eligibles.excellent, color: '#10B981' },
      { name: 'Bon (80-89%)', value: eligibles.bon, color: '#3B82F6' },
      { name: 'Non éligibles', value: eligibles.total_etablissements - eligibles.total_eligibles, color: '#EF4444' }
    ];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des tests et certifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-8 text-white">
        <h2 className="text-3xl font-bold mb-2">🎓 Tests et Certifications</h2>
        <p className="text-indigo-100">
          Plateforme de tests en ligne pour l'éducation, la technologie, la santé, la finance et plus encore
        </p>
      </div>

      {/* Stats Globales */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Tests</p>
                <p className="text-3xl font-bold text-indigo-600 mt-2">{stats.total_tests}</p>
              </div>
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">📝</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Participants</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{stats.total_participants}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">👥</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Moyenne Générale</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">{stats.moyenne_generale.toFixed(1)}%</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Établissements Éligibles</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{stats.etablissements_eligibles.pourcentage.toFixed(1)}%</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl">🏫</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Graphique Camembert - Établissements Éligibles */}
      {stats && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            🏫 Répartition des Établissements pour les Tests en Ligne
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={getEligibilityPieData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {getEligibilityPieData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-4">
              <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                <p className="font-semibold text-green-900">🟢 Excellent (90-100%)</p>
                <p className="text-2xl font-bold text-green-700">{stats.etablissements_eligibles.excellent}</p>
                <p className="text-sm text-green-600">Établissements modèles - Infrastructures complètes</p>
              </div>

              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                <p className="font-semibold text-blue-900">🔵 Bon (80-89%)</p>
                <p className="text-2xl font-bold text-blue-700">{stats.etablissements_eligibles.bon}</p>
                <p className="text-sm text-blue-600">Très bon fonctionnement</p>
              </div>

              <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded">
                <p className="font-semibold text-gray-900">📊 Total Éligibles</p>
                <p className="text-2xl font-bold text-indigo-700">
                  {stats.etablissements_eligibles.total_eligibles} / {stats.etablissements_eligibles.total_etablissements}
                </p>
                <p className="text-sm text-gray-600">
                  {stats.etablissements_eligibles.pourcentage.toFixed(1)}% des établissements peuvent accueillir des tests
                </p>
              </div>
            </div>
          </div>

          {/* Critères d'éligibilité */}
          <div className="mt-6 bg-indigo-50 rounded-lg p-6">
            <h4 className="font-bold text-indigo-900 mb-3">✅ Critères d'Éligibilité pour les Tests en Ligne</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>Score de viabilité ≥ 80%</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>Salle informatique équipée</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>Connexion Internet stable</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>Électricité régulière</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-600">✓</span>
                <span>Agrément du Ministère</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Catégories de Tests */}
      {categories.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4">📚 Catégories de Tests</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {categories.map((cat) => (
              <div
                key={cat.categorie}
                className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200 hover:shadow-md transition cursor-pointer"
                onClick={() => filterResultatsByCategorie(cat.categorie)}
              >
                <h4 className="font-bold text-gray-900 mb-2 capitalize">{cat.label}</h4>
                <div className="space-y-1 text-sm text-gray-600">
                  <p>Tests: {cat.nombre_tests}</p>
                  <p>Participants: {cat.total_participants}</p>
                  <p>Moyenne: {cat.moyenne.toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conditions Générales */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-xl font-bold text-gray-900 mb-4">📋 Conditions Générales et d'Utilisation</h3>
        <div className="prose max-w-none text-gray-700">
          <h4 className="font-semibold text-lg mb-2">1. Accès à la Plateforme</h4>
          <p className="mb-4">
            Les tests et certifications sont accessibles via une plateforme externe dédiée. 
            Les résultats sont automatiquement synchronisés avec le RIE pour un suivi national.
          </p>

          <h4 className="font-semibold text-lg mb-2">2. Établissements Agréés</h4>
          <p className="mb-4">
            Seuls les établissements avec un score de viabilité supérieur ou égal à 80% (Excellent ou Bon) 
            peuvent accueillir des sessions de tests en ligne. Ces établissements disposent des infrastructures 
            nécessaires (salle informatique, Internet, électricité).
          </p>

          <h4 className="font-semibold text-lg mb-2">3. Types de Tests Disponibles</h4>
          <ul className="list-disc list-inside mb-4 space-y-1">
            <li><strong>Éducation :</strong> Concours enseignants, validation des acquis</li>
            <li><strong>Technologie :</strong> Certifications informatiques et numériques</li>
            <li><strong>Santé :</strong> Tests de connaissances médicales</li>
            <li><strong>Finance :</strong> Certifications comptables et financières</li>
            <li><strong>Gouvernement :</strong> Concours administratifs</li>
            <li><strong>Associations :</strong> Évaluations sectorielles</li>
          </ul>

          <h4 className="font-semibold text-lg mb-2">4. Confidentialité des Données</h4>
          <p className="mb-4">
            Les résultats sont traités de manière anonymisée pour les statistiques nationales. 
            Les données personnelles sont protégées conformément aux lois en vigueur en RDC.
          </p>

          <h4 className="font-semibold text-lg mb-2">5. Partenariat Externe</h4>
          <p>
            La plateforme de tests est gérée par un partenaire externe agréé par le Ministère de l'Éducation. 
            Le RIE reçoit uniquement les données statistiques agrégées pour le pilotage national.
          </p>
        </div>
      </div>
    </div>
  );
};

export default TestsCertifications;
