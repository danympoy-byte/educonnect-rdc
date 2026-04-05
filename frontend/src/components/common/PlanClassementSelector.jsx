import React, { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import TreeNodeSelector from './TreeNodeSelector';

const PlanClassementSelector = ({ selectedId, onSelect, onClear }) => {
  const [arborescence, setArborescence] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);

  const API_URL = '';
    useEffect(() => {
    if (showDropdown && arborescence.length === 0) {
      loadArborescence();
    }
  }, [showDropdown]);

  useEffect(() => {
    if (selectedId && arborescence.length > 0) {
      // Find the selected node
      const findNode = (nodes) => {
        for (const node of nodes) {
          if (node.id === selectedId) return node;
          if (node.enfants) {
            const found = findNode(node.enfants);
            if (found) return found;
          }
        }
        return null;
      };
      const node = findNode(arborescence);
      setSelectedNode(node);
    }
  }, [selectedId, arborescence]);

  const loadArborescence = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/plan-classement/arborescence`, {
        
      });

      if (response.ok) {
        const data = await response.json();
        setArborescence(data.arborescence || []);
        // Expand root by default
        const rootIds = new Set(data.arborescence.map(n => n.id));
        setExpandedNodes(rootIds);
      }
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const toggleNode = (nodeId, e) => {
    e.stopPropagation();
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const handleSelect = (node) => {
    setSelectedNode(node);
    if (onSelect) {
      onSelect({
        id: node.id,
        code: node.code,
        nom: node.nom,
        chemin_complet: node.chemin_complet
      });
    }
    setShowDropdown(false);
  };

  const handleClear = () => {
    setSelectedNode(null);
    if (onClear) {
      onClear();
    }
  };

  const filterNodes = (nodes, query) => {
    if (!query) return nodes;
    const lowerQuery = query.toLowerCase();
    
    return nodes.filter(node => {
      const matches = 
        node.nom.toLowerCase().includes(lowerQuery) ||
        node.code.toLowerCase().includes(lowerQuery) ||
        (node.chemin_complet && node.chemin_complet.toLowerCase().includes(lowerQuery));
      
      const childMatches = node.enfants && filterNodes(node.enfants, query).length > 0;
      
      return matches || childMatches;
    }).map(node => ({
      ...node,
      enfants: node.enfants ? filterNodes(node.enfants, query) : []
    }));
  };

  const filteredArborescence = searchQuery 
    ? filterNodes(arborescence, searchQuery)
    : arborescence;

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Plan de classement (optionnel)
      </label>

      {/* Selected value or placeholder */}
      <div
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center justify-between px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:border-gray-400 transition-colors bg-white"
      >
        {selectedNode ? (
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <span className="text-lg">{selectedNode.icone || '📁'}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900 text-sm truncate">
                  {selectedNode.nom}
                </span>
                <span className="text-xs text-gray-500 font-mono flex-shrink-0">
                  {selectedNode.code}
                </span>
              </div>
              {selectedNode.chemin_complet && (
                <p className="text-xs text-gray-500 truncate">
                  {selectedNode.chemin_complet}
                </p>
              )}
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              className="p-1 hover:bg-gray-200 rounded transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        ) : (
          <span className="text-gray-500">Sélectionner une catégorie...</span>
        )}
      </div>

      {/* Dropdown */}
      {showDropdown && (
        <div className="absolute z-50 mt-2 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Rechercher une catégorie..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>

          {/* Tree */}
          <div className="overflow-y-auto max-h-80 p-2">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
            ) : filteredArborescence.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                {searchQuery ? 'Aucune catégorie trouvée' : 'Aucune catégorie disponible'}
              </div>
            ) : (
              <div className="space-y-1">
                {filteredArborescence.map((node) => (
                  <TreeNodeSelector 
                    key={node.id} 
                    node={node}
                    expandedNodes={expandedNodes}
                    toggleNode={toggleNode}
                    handleSelect={handleSelect}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Close dropdown on outside click */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </div>
  );
};

export default PlanClassementSelector;
