# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Correction de bugs + enrichissement avec données réalistes RDC pour la plateforme Édu-Connect:
1. GED Zone Verte - "Erreur de connexion" lors du clic
2. Page Viabilité - Ajouter graphique camembert répartition niveaux viabilité
3. Page Conversation - Recherche utilisateurs ne fonctionne pas
4. Page Inscription - Impossible de sélectionner un service
5. Intégration données SECOPE/DINACOPE (établissements, enseignants, élèves, paie)
6. Page Provinces - Afficher les 60 provinces éducationnelles officielles
7. Graphiques d'évolution temporelle sur le dashboard
8. Structure de notes/évaluations pour les élèves

## Architecture
- **Frontend**: React 18 + Tailwind CSS + Recharts
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB (db: educonnect_rdc)
- **Authentication**: JWT avec cookies httpOnly

## What's Been Implemented

### 03/04/2026 - Bug Fixes Session
1. GED Zone Verte CORRIGÉ - ContexteSwitcher.jsx fix
2. Graphique Viabilité CORRIGÉ - EvaluationViabilite.jsx fix
3. Recherche Utilisateurs CORRIGÉ - routes_chat.py fix
4. Sélection Service CORRIGÉ - seed_services.py (51 services)

### 03/04/2026 - Data Seeding & Dashboard
- Retrait onglet "Carte Scolaire" du menu principal
- Dashboard Paie avec stats SECOPE mock
- Seed 558 établissements, 467 enseignants, 15494 élèves, 330 classes
- Graphiques dashboard liés dynamiquement aux collections MongoDB

### 04/04/2026 - Page Provinces Éducationnelles
- Refonte complète de la page Provinces (60 P.E., 26 P.A., 567 S.D.)
- Navigation 3 niveaux avec contacts PROVED/IPP/DIPROCOPE
- Tests : 10/10 passés (iteration_8.json)

### 04/04/2026 - Evolution Temporelle + Evaluations
- **Graphiques d'évolution temporelle** sur le dashboard :
  - AreaChart des effectifs cumulés (élèves, enseignants, établissements) sur 12 mois
  - BarChart des nouvelles inscriptions mensuelles
  - Endpoint GET /api/stats/evolution
  - Dates réparties sur 12 mois pour un rendu réaliste
- **Page Évaluations et Notes** (/dashboard/evaluations) :
  - Accessible via bouton sur page Élèves (pas d'onglet menu)
  - Bannière d'avertissement : données indicatives, seul le bulletin fait foi
  - 59 238 notes + 6 000 bulletins générés (seed_notes.py)
  - Stats : Moyenne générale (11.74/20), 15 matières, 3 trimestres
  - Radar chart, bar charts, distribution des notes, table détaillée
  - 3 onglets : Vue Générale, Par Matière, Distribution
  - Endpoint GET /api/stats/notes
- Tests : 100% passés (iteration_9.json) - backend 13/13, frontend complet

## Prioritized Backlog

### P0 (Critical) - All Completed
- [x] Zone Verte/Bleue switching
- [x] Viabilité pie chart
- [x] User search in conversations
- [x] Service selection in registration
- [x] Page Provinces avec données DINACOPE
- [x] Graphiques d'évolution temporelle
- [x] Structure de notes/évaluations

### P1 (Important) - Future
- [ ] Meilleure distribution des données de test entre provinces
- [ ] Saisie manuelle de notes par les enseignants (formulaire CRUD)
- [ ] Génération et téléchargement de bulletins PDF individuels

### P2 (Nice to have)
- [ ] Connexion à l'API SECOPE réelle
- [ ] Export des données en PDF
- [ ] Statistiques avancées par établissement
- [ ] Mode hors ligne
- [ ] Carte interactive RDC pour la page Provinces

## Key Files
- `/app/frontend/src/pages/Dashboard/Overview.jsx` - Dashboard principal
- `/app/frontend/src/components/dashboards/components/StatsCharts.jsx` - Graphiques (+ evolution)
- `/app/frontend/src/pages/Dashboard/Eleves.jsx` - Page élèves (bouton evaluations)
- `/app/frontend/src/pages/Dashboard/Evaluations.jsx` - Page evaluations/notes
- `/app/frontend/src/pages/Dashboard/Provinces.jsx` - Page provinces refaite
- `/app/frontend/src/data/provincesEducationnelles.js` - Données 60 P.E.
- `/app/backend/server.py` - API (stats/evolution, stats/notes, etc.)
- `/app/backend/seed_notes.py` - Seed 59k notes + 6k bulletins
- `/app/backend/seed_etablissements.py` - Seed 558 écoles
- `/app/backend/seed_enseignants_eleves.py` - Seed enseignants/élèves/classes

## Key API Endpoints
- `GET /api/stats/global` - Métriques globales dashboard
- `GET /api/stats/sexe` - Répartition par sexe
- `GET /api/stats/evolution` - Évolution temporelle 12 mois
- `GET /api/stats/notes` - Statistiques notes/évaluations
- `POST /api/auth/login` - Authentification
- `GET /api/notes` - Liste des notes
- `GET /api/bulletins` - Liste des bulletins
