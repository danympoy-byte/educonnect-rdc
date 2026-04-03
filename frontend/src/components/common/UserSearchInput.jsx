import React, { useState, useRef, useEffect } from 'react';

/**
 * Composant de recherche d'utilisateur avec autocomplétion
 * Permet de rechercher parmi une liste d'utilisateurs par nom, prénom ou téléphone
 */
const UserSearchInput = ({ 
  users, 
  selectedUserId, 
  onSelect, 
  placeholder = "Rechercher un utilisateur...",
  filterRole = null, // Optionnel : filtrer par rôle
  required = false,
  label = "Utilisateur"
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const dropdownRef = useRef(null);

  // Trouver l'utilisateur sélectionné
  const selectedUser = users.find(u => u.id === selectedUserId);

  // Filtrer les utilisateurs en fonction de la recherche
  useEffect(() => {
    if (searchTerm.length > 0) {
      let filtered = users;

      // Filtrer par rôle si spécifié
      if (filterRole) {
        const roles = Array.isArray(filterRole) ? filterRole : [filterRole];
        filtered = filtered.filter(u => u.role && roles.includes(u.role));
      }

      // Recherche par nom, prénom ou téléphone
      filtered = filtered.filter(user => {
        const fullName = `${user.prenom || ''} ${user.nom || ''}`.toLowerCase();
        const telephone = (user.telephone || '').toLowerCase();
        const search = searchTerm.toLowerCase();

        return fullName.includes(search) || telephone.includes(search);
      });

      setFilteredUsers(filtered.slice(0, 10)); // Limiter à 10 résultats
      setShowDropdown(true);
    } else {
      setFilteredUsers([]);
      setShowDropdown(false);
    }
  }, [searchTerm, users, filterRole]);

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

  const handleSelect = (user) => {
    onSelect(user.id, `${user.prenom} ${user.nom}`);
    setSearchTerm('');
    setShowDropdown(false);
  };

  const handleClear = () => {
    onSelect('', '');
    setSearchTerm('');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Utilisateur sélectionné */}
      {selectedUser ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
              {selectedUser.prenom?.charAt(0)}{selectedUser.nom?.charAt(0)}
            </div>
            <div>
              <p className="font-medium text-green-900">
                {selectedUser.prenom} {selectedUser.nom}
              </p>
              <p className="text-sm text-green-600">
                {selectedUser.telephone}
                {selectedUser.role && ` • ${selectedUser.role}`}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClear}
            className="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            ✕ Changer
          </button>
        </div>
      ) : (
        /* Champ de recherche */
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => searchTerm.length > 0 && setShowDropdown(true)}
            placeholder={placeholder}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            required={required}
          />
          
          {/* Icône de recherche */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
            🔍
          </div>

          {/* Dropdown des résultats */}
          {showDropdown && filteredUsers.length > 0 && (
            <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto">
              {filteredUsers.map((user) => (
                <div
                  key={user.id}
                  onClick={() => handleSelect(user)}
                  className="flex items-center space-x-3 p-3 hover:bg-indigo-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                >
                  <div className="w-10 h-10 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
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

          {/* Message si aucun résultat */}
          {showDropdown && searchTerm.length > 0 && filteredUsers.length === 0 && (
            <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-500">
              Aucun utilisateur trouvé pour "{searchTerm}"
            </div>
          )}
        </div>
      )}

      {/* Aide */}
      {!selectedUser && (
        <p className="mt-1 text-xs text-gray-500">
          💡 Tapez le nom, prénom ou numéro de téléphone pour rechercher
        </p>
      )}
    </div>
  );
};

export default UserSearchInput;
