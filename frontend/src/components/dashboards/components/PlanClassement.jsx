import React, { useState, useEffect } from 'react';
import { Folder, FileText } from 'lucide-react';
import toast from 'react-hot-toast';
import TreeNodePlanClassement from '../../common/TreeNodePlanClassement';

const PlanClassement = () => {
  const [arborescence, setArborescence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [selectedNode, setSelectedNode] = useState(null);

  const API_URL = process.env.REACT_APP_BACKEND_URL;
    useEffect(() => {
    loadArborescence();
  }, []);

  const loadArborescence = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/plan-classement/arborescence`, {
        
      });

      if (response.ok) {
        const data = await response.json();
        setArborescence(data.arborescence || []);
        // Expand root nodes by default
        const rootIds = new Set(data.arborescence.map(node => node.id));
        setExpandedNodes(rootIds);
      } else {
        toast.error('Erreur lors du chargement du plan de classement');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const selectNode = (node) => {
    setSelectedNode(node);
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          📁 Plan de classement hiérarchique DRC
        </h2>
        <p className="text-gray-600">
          Structure officielle de classification des documents du MINEPST
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Arborescence */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Arborescence</h3>
              <button
                onClick={loadArborescence}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                🔄 Actualiser
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : arborescence.length === 0 ? (
              <div className="text-center py-12">
                <Folder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Aucune catégorie trouvée</p>
                <p className="text-sm text-gray-500 mt-2">
                  Le plan de classement n'a pas encore été initialisé
                </p>
              </div>
            ) : (
              <div className="space-y-1 max-h-[600px] overflow-y-auto">
                {arborescence.map((node) => (
                  <TreeNodePlanClassement 
                    key={node.id} 
                    node={node}
                    expandedNodes={expandedNodes}
                    toggleNode={toggleNode}
                    selectNode={selectNode}
                    selectedNode={selectedNode}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Détails du nœud sélectionné */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sticky top-6">
            {selectedNode ? (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Détails de la catégorie
                </h3>

                <div className="space-y-4">
                  <div>
                    <span className="text-4xl">{selectedNode.icone || '📁'}</span>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Nom</label>
                    <p className="text-lg font-semibold text-gray-900">{selectedNode.nom}</p>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Code</label>
                    <p className="text-gray-900 font-mono">{selectedNode.code}</p>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase">Niveau</label>
                    <p className="text-gray-900">Niveau {selectedNode.niveau}</p>
                  </div>

                  {selectedNode.description && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Description</label>
                      <p className="text-gray-700 text-sm">{selectedNode.description}</p>
                    </div>
                  )}

                  {selectedNode.chemin_complet && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">Chemin</label>
                      <p className="text-gray-700 text-sm">{selectedNode.chemin_complet}</p>
                    </div>
                  )}

                  {selectedNode.duree_conservation_mois && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">
                        Durée de conservation
                      </label>
                      <p className="text-gray-900">
                        {selectedNode.duree_conservation_mois} mois
                      </p>
                    </div>
                  )}

                  {selectedNode.types_documents_acceptes && selectedNode.types_documents_acceptes.length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">
                        Types acceptés
                      </label>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {selectedNode.types_documents_acceptes.map((type, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                          >
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedNode.enfants && selectedNode.enfants.length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase">
                        Sous-catégories
                      </label>
                      <p className="text-gray-900">{selectedNode.enfants.length} sous-catégorie(s)</p>
                    </div>
                  )}

                  {/* Indicateur de statut */}
                  <div className="pt-4 border-t">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${selectedNode.est_actif ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                      <span className="text-sm text-gray-600">
                        {selectedNode.est_actif ? 'Actif' : 'Inactif'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">
                  Sélectionnez une catégorie pour voir les détails
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Légende */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 À propos du plan de classement</h4>
        <p className="text-sm text-blue-800 mb-3">
          Le plan de classement hiérarchique permet d'organiser les documents selon la structure officielle du MINEPST.
          Chaque document doit être classé dans une catégorie appropriée pour faciliter la recherche et la gestion.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <span>🏛️</span>
            <span className="text-blue-700">Administration</span>
          </div>
          <div className="flex items-center gap-2">
            <span>📚</span>
            <span className="text-blue-700">Pédagogie</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🏗️</span>
            <span className="text-blue-700">Infrastructure</span>
          </div>
          <div className="flex items-center gap-2">
            <span>⚖️</span>
            <span className="text-blue-700">Juridique</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanClassement;
