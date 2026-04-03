import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import etablissementsService from '../../../services/etablissements.service';
import provincesService from '../../../services/provinces.service';
import toast from 'react-hot-toast';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Icône personnalisée pour les écoles
const schoolIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Composant pour centrer la carte automatiquement
function MapBoundsUpdater({ etablissements }) {
  const map = useMap();
  
  useEffect(() => {
    if (etablissements.length > 0) {
      const bounds = etablissements
        .filter(etab => etab.coordonnees?.latitude && etab.coordonnees?.longitude)
        .map(etab => [etab.coordonnees.latitude, etab.coordonnees.longitude]);
      
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [etablissements, map]);
  
  return null;
}

const CarteScolaireNumerique = () => {
  const [etablissements, setEtablissements] = useState([]);
  const [provinces, setProvinces] = useState([]);
  const [selectedProvince, setSelectedProvince] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [filteredEtablissements, setFilteredEtablissements] = useState([]);

  // Centre de la RDC
  const rdcCenter = [-4.0383, 21.7587];

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterEtablissements();
  }, [etablissements, selectedProvince, searchTerm]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [etablissementsData, provincesData] = await Promise.all([
        etablissementsService.getAll(),
        provincesService.getAll()
      ]);
      
      // Ajouter des coordonnées simulées pour la démonstration
      // En production, ces coordonnées viendront de votre base de données
      const etablissementsAvecCoordonnees = etablissementsData.map((etab, index) => ({
        ...etab,
        coordonnees: etab.coordonnees || generateMockCoordinates(index)
      }));
      
      setEtablissements(etablissementsAvecCoordonnees);
      setProvinces(provincesData);
    } catch (error) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  // Coordonnées géographiques réelles des principales villes/provinces de la RDC
  const coordonneesVillesRDC = [
    // Kinshasa
    { lat: -4.3276, lng: 15.3136, nom: 'Kinshasa' },
    // Bas-Congo / Kongo Central
    { lat: -5.8333, lng: 13.2833, nom: 'Matadi' },
    { lat: -5.7931, lng: 13.4622, nom: 'Mbanza-Ngungu' },
    // Bandundu / Kwilu / Kwango / Mai-Ndombe
    { lat: -3.3167, lng: 17.3833, nom: 'Bandundu' },
    { lat: -5.0333, lng: 18.8167, nom: 'Kikwit' },
    { lat: -4.9833, lng: 16.1833, nom: 'Kenge' },
    { lat: -1.9833, lng: 18.6167, nom: 'Inongo' },
    // Equateur / Mongala / Nord-Ubangi / Sud-Ubangi / Tshuapa
    { lat: 0.0333, lng: 18.2667, nom: 'Mbandaka' },
    { lat: 2.1500, lng: 21.5000, nom: 'Gbadolite' },
    { lat: 3.4667, lng: 18.5833, nom: 'Gemena' },
    { lat: 2.1500, lng: 19.8167, nom: 'Lisala' },
    { lat: -1.8667, lng: 20.8500, nom: 'Boende' },
    // Province Orientale / Tshopo / Bas-Uele / Haut-Uele / Ituri
    { lat: 0.5167, lng: 25.2000, nom: 'Kisangani' },
    { lat: 2.2667, lng: 27.4333, nom: 'Isiro' },
    { lat: 4.3500, lng: 28.6167, nom: 'Aru' },
    { lat: 1.5667, lng: 30.0833, nom: 'Bunia' },
    // Nord-Kivu
    { lat: -1.6833, lng: 29.2333, nom: 'Goma' },
    { lat: 0.1167, lng: 29.2667, nom: 'Butembo' },
    // Sud-Kivu
    { lat: -2.5083, lng: 28.8608, nom: 'Bukavu' },
    { lat: -3.3667, lng: 29.1500, nom: 'Uvira' },
    // Maniema
    { lat: -2.9500, lng: 25.9167, nom: 'Kindu' },
    // Katanga / Haut-Katanga / Lualaba / Tanganyika / Haut-Lomami
    { lat: -11.6667, lng: 27.4667, nom: 'Lubumbashi' },
    { lat: -10.7167, lng: 25.4667, nom: 'Kolwezi' },
    { lat: -5.9167, lng: 29.1833, nom: 'Kalemie' },
    { lat: -8.7333, lng: 25.4833, nom: 'Kamina' },
    // Kasaï / Kasaï-Central / Kasaï-Oriental / Lomami / Sankuru
    { lat: -5.8833, lng: 22.4167, nom: 'Kananga' },
    { lat: -6.1333, lng: 23.6000, nom: 'Mbuji-Mayi' },
    { lat: -6.1333, lng: 24.4833, nom: 'Kabinda' },
    { lat: -3.4500, lng: 23.6167, nom: 'Lodja' },
    { lat: -6.0000, lng: 20.8000, nom: 'Tshikapa' }
  ];

  // Générer des coordonnées réalistes pour la RDC basées sur les vraies villes
  const generateMockCoordinates = (index) => {
    // Sélectionner une ville de manière pseudo-aléatoire mais déterministe
    const villeIndex = index % coordonneesVillesRDC.length;
    const ville = coordonneesVillesRDC[villeIndex];
    
    // Ajouter une petite variance (±0.05 degrés ~5-6 km) pour distribuer les écoles autour de la ville
    const variance = 0.05;
    const randomLat = ((index * 7) % 100) / 100; // Pseudo-random 0-1
    const randomLng = ((index * 13) % 100) / 100; // Pseudo-random 0-1
    
    const lat = ville.lat + (randomLat - 0.5) * variance * 2;
    const lng = ville.lng + (randomLng - 0.5) * variance * 2;
    
    return { latitude: lat, longitude: lng };
  };

  const filterEtablissements = () => {
    let filtered = [...etablissements];
    
    if (selectedProvince) {
      filtered = filtered.filter(etab => etab.province_id === selectedProvince);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(etab => 
        etab.nom.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredEtablissements(filtered);
  };

  const getTypeLabel = (type) => {
    const labels = {
      'ecole_primaire': 'École Primaire',
      'college': 'Collège',
      'lycee': 'Lycée',
      'institut': 'Institut'
    };
    return labels[type] || type;
  };

  const getCategorieLabel = (categorie) => {
    const labels = {
      'publique': 'Public',
      'prive': 'Privé',
      'conventionne': 'Conventionné'
    };
    return labels[categorie] || categorie;
  };

  const getProvinceName = (provinceId) => {
    const province = provinces.find(p => p.id === provinceId);
    return province?.nom || 'N/A';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement de la carte...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header avec filtres */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">🗺️ Carte Scolaire Numérique</h2>
              <p className="text-sm text-gray-600 mt-1">
                Géolocalisation des établissements scolaires en République Démocratique du Congo
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-indigo-600">{filteredEtablissements.length}</p>
              <p className="text-sm text-gray-600">Établissements</p>
            </div>
          </div>

          {/* Filtres */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Recherche par province */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🗺️ Province Éducationnelle
              </label>
              <select
                value={selectedProvince}
                onChange={(e) => setSelectedProvince(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">TOUS LES ÉTABLISSEMENTS</option>
                {provinces.map(province => (
                  <option key={province.id} value={province.id}>
                    {province.nom}
                  </option>
                ))}
              </select>
            </div>

            {/* Recherche par nom */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🔍 Recherche par nom d'établissement
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Rechercher par nom établissement..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Carte */}
      <div className="flex-1 relative">
        <MapContainer
          center={rdcCenter}
          zoom={6}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          {/* Utilisation de Google Maps comme sur SECOPE */}
          <TileLayer
            attribution='&copy; Google Maps'
            url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
            maxZoom={20}
          />
          
          {/* Marqueurs temporairement désactivés en attente des vraies coordonnées */}
          {/* 
          {filteredEtablissements.map((etablissement) => {
            if (!etablissement.coordonnees?.latitude || !etablissement.coordonnees?.longitude) {
              return null;
            }
            
            return (
              <Marker
                key={etablissement.id}
                position={[etablissement.coordonnees.latitude, etablissement.coordonnees.longitude]}
                icon={schoolIcon}
              >
                <Popup>
                  <div className="p-2 min-w-[250px]">
                    <h3 className="font-bold text-lg text-indigo-700 mb-2">
                      {etablissement.nom}
                    </h3>
                    <div className="space-y-1 text-sm">
                      <p>
                        <span className="font-semibold">Type:</span> {getTypeLabel(etablissement.type)}
                      </p>
                      <p>
                        <span className="font-semibold">Catégorie:</span> {getCategorieLabel(etablissement.categorie)}
                      </p>
                      <p>
                        <span className="font-semibold">Province:</span> {getProvinceName(etablissement.province_id)}
                      </p>
                      <p>
                        <span className="font-semibold">Adresse:</span> {etablissement.adresse || 'N/A'}
                      </p>
                      {etablissement.code && (
                        <p>
                          <span className="font-semibold">Code:</span> {etablissement.code}
                        </p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        📍 {etablissement.coordonnees.latitude.toFixed(4)}, {etablissement.coordonnees.longitude.toFixed(4)}
                      </p>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
          */}
          
          <MapBoundsUpdater etablissements={[]} />
        </MapContainer>
      </div>

      {/* Légende */}
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 z-[1000] border border-gray-200">
        <h4 className="font-bold text-sm mb-2 text-gray-900">Légende</h4>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Établissement Scolaire</span>
          </div>
          <div className="text-gray-600 mt-2 pt-2 border-t">
            <p className="font-semibold text-amber-600">⚠️ En Attente</p>
            <p className="mt-1">Coordonnées géographiques en cours d'intégration</p>
          </div>
          <div className="text-gray-600 pt-2 border-t">
            <p className="font-semibold">Sources:</p>
            <p>RIE-RDC & SECOPE</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarteScolaireNumerique;
