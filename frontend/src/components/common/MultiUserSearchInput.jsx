import React, { useState, useRef, useEffect } from 'react';

/**
 * Composant de recherche multi-utilisateurs avec autocomplétion ET sélection de rôle
 * Permet de sélectionner plusieurs utilisateurs via recherche et d'assigner un rôle à chacun
 */
const MultiUserSearchInput = ({ 
  users, 
  selectedUserIds = [],
  selectedUserRoles = {}, // NOUVEAU - {userId: role}
  onSelectionChange,
  onRoleChange, // NOUVEAU - Callback pour changer le rôle
  placeholder = "Rechercher un utilisateur...",
  maxSelection = null,
  label = "Utilisateurs",
  color = "indigo",
  withRoles = false, // NOUVEAU - Active la sélection de rôles
  availableRoles = [] // NOUVEAU - Liste des rôles disponibles
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [selectedRoleForAdd, setSelectedRoleForAdd] = useState(availableRoles[0]?.value || '');
  const dropdownRef = useRef(null);

  // Trouver les utilisateurs sélectionnés
  const selectedUsers = users.filter(u => selectedUserIds.includes(u.id));

  // Filtrer les utilisateurs en fonction de la recherche
  useEffect(() => {
    if (searchTerm.length > 0) {
      let filtered = users;

      // Exclure les utilisateurs déjà sélectionnés
      filtered = filtered.filter(u => !selectedUserIds.includes(u.id));

      // Recherche par nom, prénom ou téléphone
      filtered = filtered.filter(user => {
        const fullName = `${user.prenom || ''} ${user.nom || ''}`.toLowerCase();
        const telephone = (user.telephone || '').toLowerCase();
        const search = searchTerm.toLowerCase();

        return fullName.includes(search) || telephone.includes(search);
      });

      setFilteredUsers(filtered.slice(0, 10));
      setShowDropdown(true);
    } else {
      setFilteredUsers([]);
      setShowDropdown(false);
    }
  }, [searchTerm, users, selectedUserIds]);

  // Fermer le dropdown si on clique à l'extérieur
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAdd = (user) => {
    if (maxSelection && selectedUserIds.length >= maxSelection) {
      return;
    }

    const newSelection = [...selectedUserIds, user.id];
    onSelectionChange(newSelection);
    
    // Si withRoles, définir le rôle par défaut
    if (withRoles && onRoleChange) {
      onRoleChange(user.id, selectedRoleForAdd);
    }
    
    setSearchTerm('');
    setShowDropdown(false);
  };

  const handleRemove = (userId) => {
    const newSelection = selectedUserIds.filter(id => id !== userId);
    onSelectionChange(newSelection);
  };

  const handleRoleChangeForUser = (userId, newRole) => {
    if (onRoleChange) {
      onRoleChange(userId, newRole);
    }
  };

  // Couleurs selon le thème
  const colorClasses = {
    indigo: {
      bg: 'bg-indigo-50',
      border: 'border-indigo-200',
      text: 'text-indigo-900',
      badge: 'bg-indigo-600',
      hover: 'hover:bg-indigo-50'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-900',
      badge: 'bg-blue-600',
      hover: 'hover:bg-blue-50'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-900',
      badge: 'bg-green-600',
      hover: 'hover:bg-green-50'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-900',
      badge: 'bg-purple-600',
      hover: 'hover:bg-purple-50'
    }
  };

  const colors = colorClasses[color] || colorClasses.indigo;

  return (
    <div className="space-y-3">
      {/* Utilisateurs sélectionnés */}
      {selectedUsers.length > 0 && (
        <div className="space-y-2">
          {selectedUsers.map((user, index) => (
            <div
              key={user.id}
              className={`flex items-center justify-between p-3 ${colors.bg} border ${colors.border} rounded-lg`}
            >
              <div className="flex items-center space-x-3 flex-1">
                {/* Numéro d'ordre */}
                {maxSelection === 5 && (
                  <div className={`w-8 h-8 ${colors.badge} text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0`}>
                    {index + 1}
                  </div>
                )}
                
                {/* Avatar */}
                <div className={`w-10 h-10 ${colors.badge} text-white rounded-full flex items-center justify-center font-bold flex-shrink-0`}>
                  {user.prenom?.charAt(0)}{user.nom?.charAt(0)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className={`font-medium ${colors.text} truncate`}>
                    {user.prenom} {user.nom}
                  </p>
                  <p className="text-sm text-gray-600 truncate">
                    {user.telephone}
                    {user.role && ` • ${user.role}`}
                  </p>
                </div>
                
                {/* Sélection de rôle */}
                {withRoles && (
                  <select
                    value={selectedUserRoles[user.id] || availableRoles[0]?.value || ''}
                    onChange={(e) => handleRoleChangeForUser(user.id, e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded text-sm bg-white focus:ring-2 focus:ring-indigo-500"
                  >
                    {availableRoles.map(role => (
                      <option key={role.value} value={role.value}>
                        {role.icon} {role.label}
                      </option>
                    ))}
                  </select>
                )}
              </div>
              
              <button
                type="button"
                onClick={() => handleRemove(user.id)}
                className="text-red-600 hover:text-red-800 text-sm font-medium px-3 py-1 hover:bg-red-50 rounded ml-2 flex-shrink-0"
              >
                ✕ Retirer
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Champ de recherche avec sélection de rôle */}
      {(!maxSelection || selectedUserIds.length < maxSelection) && (
        <div className="space-y-2">
          {/* Sélection du rôle avant ajout (si withRoles) */}
          {withRoles && (
            <div className="flex items-center space-x-2 bg-gray-50 p-2 rounded border border-gray-200">
              <span className="text-sm text-gray-600 font-medium">Rôle :</span>
              <select
                value={selectedRoleForAdd}
                onChange={(e) => setSelectedRoleForAdd(e.target.value)}
                className="flex-1 px-3 py-1 border border-gray-300 rounded text-sm bg-white"
              >
                {availableRoles.map(role => (
                  <option key={role.value} value={role.value}>
                    {role.icon} {role.label}
                  </option>
                ))}
              </select>
            </div>
          )}
          
          <div className="relative" ref={dropdownRef}>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onFocus={() => searchTerm.length > 0 && setShowDropdown(true)}
              placeholder={placeholder}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              🔍
            </div>

            {/* Dropdown des résultats */}
            {showDropdown && filteredUsers.length > 0 && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
                {filteredUsers.map((user) => (
                  <div
                    key={user.id}
                    onClick={() => handleAdd(user)}
                    className={`flex items-center space-x-3 p-3 ${colors.hover} cursor-pointer border-b border-gray-100 last:border-b-0`}
                  >
                    <div className={`w-10 h-10 ${colors.badge} text-white rounded-full flex items-center justify-center font-bold text-sm`}>
                      {user.prenom?.charAt(0)}{user.nom?.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {user.prenom} {user.nom}
                      </p>
                      <p className="text-sm text-gray-500">
                        {user.telephone}
                        {user.role && ` • ${user.role}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {showDropdown && searchTerm.length > 0 && filteredUsers.length === 0 && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-500">
                Aucun utilisateur trouvé pour "{searchTerm}"
              </div>
            )}
          </div>
        </div>
      )}

      {/* Limite atteinte */}
      {maxSelection && selectedUserIds.length >= maxSelection && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800 font-medium">
            ⚠️ Limite atteinte : {maxSelection} {label.toLowerCase()} maximum
          </p>
        </div>
      )}

      {/* Aide */}
      {(!maxSelection || selectedUserIds.length < maxSelection) && (
        <p className="text-xs text-gray-500">
          💡 Tapez le nom, prénom ou numéro de téléphone pour rechercher
          {maxSelection && ` (max ${maxSelection})`}
        </p>
      )}
    </div>
  );
};

export default MultiUserSearchInput;
