import React from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';

const TreeNodePlanClassementComponent = ({ node, level = 0, expandedNodes, toggleNode, selectNode, selectedNode }) => {
  const hasChildren = node.enfants && node.enfants.length > 0;
  const isExpanded = expandedNodes.has(node.id);
  const isSelected = selectedNode?.id === node.id;

  return (
    <div className="select-none">
      <div
        className={`flex items-center gap-2 py-2 px-3 rounded-lg cursor-pointer transition-colors ${
          isSelected 
            ? 'bg-blue-100 border-l-4 border-blue-600' 
            : 'hover:bg-gray-50'
        }`}
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
        onClick={() => selectNode(node)}
      >
        {/* Toggle chevron */}
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              toggleNode(node.id);
            }}
            className="p-1 hover:bg-gray-200 rounded transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            )}
          </button>
        ) : (
          <div className="w-6" />
        )}

        {/* Icon */}
        <span className="text-xl">
          {node.icone || (hasChildren ? (isExpanded ? '📂' : '📁') : '📄')}
        </span>

        {/* Label */}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className={`font-medium ${isSelected ? 'text-blue-900' : 'text-gray-900'}`}>
              {node.nom}
            </span>
            <span className="text-xs text-gray-500 font-mono">
              {node.code}
            </span>
          </div>
          {node.description && (
            <p className="text-xs text-gray-600 mt-0.5">{node.description}</p>
          )}
        </div>

        {/* Badge nombre d'enfants */}
        {hasChildren && (
          <span className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded-full">
            {node.enfants.length}
          </span>
        )}
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div className="ml-2">
          {node.enfants.map((child) => (
            <TreeNodePlanClassement 
              key={child.id} 
              node={child} 
              level={level + 1}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
              selectNode={selectNode}
              selectedNode={selectedNode}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Use React.memo to break Babel recursion
const TreeNodePlanClassement = React.memo(TreeNodePlanClassementComponent);

export default TreeNodePlanClassement;
