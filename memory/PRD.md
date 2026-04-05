# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Plateforme de gestion éducative pour la RDC intégrant données SECOPE/DINACOPE, gestion documentaire, messagerie, analytics, endpoints d'ingestion, carte interactive et mode hors ligne.

## Architecture
- **Frontend**: React 18 + Tailwind CSS + Recharts + SVG Map
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB (db: educonnect_rdc)
- **Auth**: JWT (utilisateurs) + Basic Auth (clients API)
- **Offline**: Service Worker + Cache API

## What's Been Implemented

### Data Seeding (complet)
- 953 établissements répartis sur **26/26 provinces**
- 4 114 enseignants
- 126 804 élèves (88 968 primaire, 37 836 secondaire)
- 3 276 classes
- 3 319 185 notes (16 matières, 3 trimestres)
- 309 636 bulletins

### Fonctionnalités complètes
- Page Provinces (60 P.E., 26 P.A., navigation 3 niveaux)
- **Carte interactive SVG** des 26 provinces (gradient couleur par nb P.E., cliquable, toggle Carte/Grille)
- Graphiques d'évolution temporelle (12 mois)
- Page Évaluations (radar, distribution, table par matière)
- Inscription étape 2 avec rôles (Provincial, Établissement, Central)
- Navigation basée sur les rôles (PROVED, IPP, DIPROCOPE, Ministre Provincial, etc.)
- Page "Partage de Données" (Sources temps réel, Endpoints, Logs, Clés API)
- **Endpoints d'ingestion réels** (presences, evaluations, effectifs, notes)
- **Mode hors ligne** (Service Worker, cache static + API, bannière offline)

### Refactoring (05/04/2026)
- Extraction des routes statistiques de `server.py` vers `routes_stats.py` (340 lignes)
- `server.py` réduit de 1482 à 1142 lignes

## Rôles et Accès
| Rôle | Accès |
|------|-------|
| Ministre / Ministre Provincial / PROVED / Admin Tech | Tous les onglets |
| IPP | Tout sauf Paie, Partage de Données |
| DIPROCOPE | Tout sauf Partage de Données |
| Chef Étab / Directeur École / CPE | Tout sauf Documents, Rapports, Paie, Partage |
| Enseignant | Tout sauf Documents, Rapports, Partage (avec Paie) |

## Key Files
- `/app/backend/routes_stats.py` - Routes statistiques (extraites de server.py)
- `/app/frontend/src/components/dashboards/components/CarteRDC.jsx` - Carte SVG
- `/app/frontend/public/service-worker.js` - Service Worker offline
- `/app/frontend/src/hooks/useOfflineStatus.js` - Hook détection offline
- `/app/frontend/src/pages/Dashboard/Provinces.jsx` - Page provinces + carte
- `/app/frontend/src/pages/Dashboard/PartageDonnees.jsx` - Sources + endpoints
- `/app/backend/routes_externe.py` - Endpoints d'ingestion

## Key API Endpoints
### Internes (JWT)
- GET /api/stats/global, /stats/sexe, /stats/evolution, /stats/notes, /stats/province/{id}
- GET /api/externe/sources/status, /api/externe/logs

### Externes (Basic Auth)
- POST /api/externe/presences, /evaluations, /effectifs, /notes

## Prioritized Backlog
### P1
- [ ] Saisie manuelle de notes par enseignants (formulaire CRUD)
- [ ] Génération/téléchargement bulletins PDF

### P2
- [ ] Connexion API SECOPE réelle
- [ ] Notifications push hors ligne
