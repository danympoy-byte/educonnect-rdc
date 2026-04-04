# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Correction de 4 bugs dans la plateforme Édu-Connect + enrichissement avec données réalistes RDC:
1. GED Zone Verte - "Erreur de connexion" lors du clic
2. Page Viabilité - Ajouter graphique camembert répartition niveaux viabilité
3. Page Conversation - Recherche utilisateurs ne fonctionne pas
4. Page Inscription - Impossible de sélectionner un service
5. Intégration données SECOPE/DINACOPE (établissements, enseignants, élèves, paie)
6. Page Provinces - Afficher les 60 provinces éducationnelles officielles

## Architecture
- **Frontend**: React 18 + Tailwind CSS + Recharts
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB
- **Authentication**: JWT avec cookies httpOnly

## User Personas
1. **Administrateur Système** - Accès complet au système
2. **Admin GED** - Gestion documentaire
3. **Admin SIRH** - Ressources humaines
4. **Utilisateurs réguliers** - Agents du ministère

## Core Requirements (Static)
- Authentification sécurisée
- Gestion documentaire (GED) avec zones Bleue/Verte
- Évaluation de viabilité des établissements
- Messagerie interne entre utilisateurs
- Inscription multi-étapes avec sélection de service
- Dashboard avec graphiques dynamiques liés aux données seed
- Page Provinces avec navigation drill-down (26 admin → 60 éducationnelles → sous-divisions)

## What's Been Implemented

### 03/04/2026 - Bug Fixes Session
1. **Bug #1 - GED Zone Verte CORRIGÉ** - ContexteSwitcher.jsx fix
2. **Bug #2 - Graphique Viabilité CORRIGÉ** - EvaluationViabilite.jsx fix
3. **Bug #3 - Recherche Utilisateurs CORRIGÉ** - routes_chat.py fix
4. **Bug #4 - Sélection Service CORRIGÉ** - seed_services.py (51 services)

### 03/04/2026 - Data Seeding & Dashboard
- Retrait onglet "Carte Scolaire" du menu principal
- Dashboard Paie avec stats SECOPE mock
- Seed 558 établissements, 467 enseignants, 15494 élèves, 330 classes
- Graphiques dashboard liés dynamiquement aux collections MongoDB

### 04/04/2026 - Page Provinces Éducationnelles
- **TERMINÉ** : Refonte complète de la page Provinces
- Données statiques des 60 provinces éducationnelles (source: edu-nc.gouv.cd)
- Navigation 3 niveaux : Provinces Admin → Provinces Éducationnelles → Sous-Divisions
- Texte introductif officiel + explication des rôles (PROVED, IPP, DIPROCOPE)
- Barre de recherche fonctionnelle
- Statistiques en haut de page (26 PA, 60 PE, 567 SD)
- Contacts complets pour chaque province éducationnelle
- Tests : 10/10 passés (iteration_8.json)

## Prioritized Backlog

### P0 (Critical) - All Completed
- [x] Zone Verte/Bleue switching
- [x] Viabilité pie chart
- [x] User search in conversations
- [x] Service selection in registration
- [x] Page Provinces avec données DINACOPE

### P1 (Important) - Future
- [ ] Graphiques d'évolution temporelle sur le dashboard
- [ ] Structures de notes/évaluations pour les élèves
- [ ] Meilleure distribution des données de test entre provinces

### P2 (Nice to have)
- [ ] Connexion à l'API SECOPE réelle
- [ ] Export des données en PDF
- [ ] Statistiques avancées
- [ ] Mode hors ligne

## Key Files
- `/app/frontend/src/pages/Dashboard/Provinces.jsx` - Page provinces refaite
- `/app/frontend/src/data/provincesEducationnelles.js` - Données statiques 60 PE
- `/app/frontend/src/components/dashboards/components/DashboardPaie.jsx` - Dashboard paie
- `/app/backend/server.py` - API stats endpoints
- `/app/backend/seed_etablissements.py` - Seed 558 écoles
- `/app/backend/seed_enseignants_eleves.py` - Seed enseignants/élèves/classes
