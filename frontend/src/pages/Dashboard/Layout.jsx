import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import NotificationProfilIncomplet from '../../components/notifications/NotificationProfilIncomplet';

const UserMenu = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
      >
        <div className="text-right hidden sm:block">
          <p className="text-sm font-medium text-gray-900">{user.prenom} {user.nom}</p>
          <p className="text-xs text-gray-500">{user.role?.replace(/_/g, ' ')}</p>
        </div>
        <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-20">
            <div className="p-4 border-b border-gray-200">
              <p className="text-sm font-semibold text-gray-900">{user.prenom} {user.nom}</p>
              <p className="text-xs text-gray-500 mt-1">{user.email || user.telephone}</p>
            </div>
            <div className="py-2">
              <button onClick={() => { navigate('/dashboard/profil'); setIsOpen(false); }}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
                <span>Mon profil</span>
              </button>
              <button onClick={() => { navigate('/dashboard/completion-profil'); setIsOpen(false); }}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
                <span>Compléter mon profil</span>
              </button>
            </div>
            <div className="border-t border-gray-200">
              <button onClick={() => { onLogout(); setIsOpen(false); }}
                className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
                </svg>
                <span>Déconnexion</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Définition centralisée des accès par rôle
const getNavItems = (role) => {
  // Rôles avec accès complet (comme Ministre)
  const acces_ministre = [
    'administrateur_technique', 'ministre', 'ministre_provincial', 'proved'
  ];

  // IPP : tout sauf Paie, Partage de Données
  const acces_ipp = ['ipp'];

  // DIPROCOPE : tout sauf Partage de Données
  const acces_diprocope = ['diprocope'];

  // Chef d'établissement / Directeur école / CPE : sans Documents, Rapports, Paie, Partage de Données
  const acces_etablissement = ['chef_etablissement', 'directeur_ecole', 'conseiller_principal_education'];

  // Enseignant : sans Documents, Rapports, Partage de Données (mais avec Paie)
  const acces_enseignant = ['enseignant'];

  const items = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/documents',
      label: 'Documents',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/provinces',
      label: 'Provinces',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/enseignants',
      label: 'Enseignants',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/eleves',
      label: 'Élèves',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/etablissements',
      label: 'Établissements',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/viabilite',
      label: 'Viabilité',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope,
        'secretaire_general', 'directeur_provincial', 'inspecteur_pedagogique', 'agent_dinacope']
    },
    {
      path: '/dashboard/classes',
      label: 'Classes',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division', 'inspecteur_pedagogique', 'agent_dinacope', 'personnel_administratif']
    },
    {
      path: '/dashboard/presences',
      label: 'Présences',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'chef_sous_division']
    },
    {
      path: '/dashboard/paie',
      label: 'Paie',
      roles: [...acces_ministre, ...acces_diprocope, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'agent_dinacope']
    },
    {
      path: '/dashboard/tests',
      label: 'Tests',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial', 'inspecteur_pedagogique']
    },
    {
      path: '/dashboard/partage-donnees',
      label: 'Partage de Données',
      roles: [...acces_ministre, 'secretaire_general']
    },
    {
      path: '/dashboard/dinacope',
      label: 'Contrôle DINACOPE',
      roles: ['agent_dinacope', 'administrateur_technique']
    },
    {
      path: '/dashboard/mutations',
      label: 'Mutations',
      roles: [...acces_ministre, ...acces_ipp, ...acces_diprocope, ...acces_etablissement, ...acces_enseignant,
        'secretaire_general', 'directeur_provincial']
    },
    {
      path: '/dashboard/controles-planning',
      label: 'Planning Controles',
      roles: ['agent_dinacope', 'administrateur_technique']
    }
  ];

  return items.filter(item => item.roles.includes(role));
};

const DashboardLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = getNavItems(user.role);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <Link to="/dashboard" className="cursor-pointer flex-shrink-0">
                <img
                  src="https://customer-assets.emergentagent.com/job_education-connect-5/artifacts/bqswgbm9_Seal_of_the_DR_Congo_Government.svg.png"
                  alt="Logo Republique Democratique du Congo"
                  className="h-10 sm:h-14 w-auto hover:opacity-80 transition"
                />
              </Link>
              <div className="min-w-0">
                <h1 className="text-lg sm:text-2xl font-bold text-black">Édu-Connect</h1>
                <p className="text-xs sm:text-sm text-gray-700 mt-0.5 hidden sm:block">Plateforme Éducative Nationale</p>
                <p className="text-xs sm:text-sm text-gray-700 hidden md:block">Ministère de l'Éducation Nationale et de la Nouvelle Citoyenneté</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
              <UserMenu user={user} onLogout={handleLogout} />
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-1 overflow-x-auto pb-px" data-testid="main-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/dashboard'}
                className={({ isActive }) =>
                  `px-4 py-2 font-medium text-sm whitespace-nowrap transition ${
                    isActive
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`
                }
                data-testid={`nav-${item.path.split('/').pop() || 'dashboard'}`}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      <NotificationProfilIncomplet />
    </div>
  );
};

export default DashboardLayout;
