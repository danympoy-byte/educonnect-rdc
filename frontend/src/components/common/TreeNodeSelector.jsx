import React from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';

const TreeNodeSelectorComponent = ({ node, level = 0, expandedNodes, toggleNode, handleSelect }) => {
  const hasChildren = node.enfants && node.enfants.length > 0;
  const isExpanded = expandedNodes.has(node.id);

  return (
    <div>
      <div
        className="flex items-center gap-2 py-2 px-3 hover:bg-gray-100 rounded cursor-pointer transition-colors"
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
        onClick={() => handleSelect(node)}
      >
        {hasChildren ? (
          <button
            onClick={(e) => toggleNode(node.id, e)}
            className="p-1 hover:bg-gray-200 rounded"
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-gray-600" />
            ) : (
              <ChevronRight className="w-3 h-3 text-gray-600" />
            )}
          </button>
        ) : (
          <div className="w-5" />
        )}

        <span className="text-base">{node.icone || '📁'}</span>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900 text-sm truncate">
              {node.nom}
            </span>
            <span className="text-xs text-gray-500 font-mono flex-shrink-0">
              {node.code}
            </span>
          </div>
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.enfants.map((child) => (
            <TreeNodeSelector 
              key={child.id} 
              node={child} 
              level={level + 1}
              expandedNodes={expandedNodes}
              toggleNode={toggleNode}
              handleSelect={handleSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Use React.memo to break Babel recursion
const TreeNodeSelector = React.memo(TreeNodeSelectorComponent);

export default TreeNodeSelector;
