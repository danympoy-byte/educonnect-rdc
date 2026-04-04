# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Plateforme de gestion éducative pour la RDC intégrant données SECOPE/DINACOPE, gestion documentaire, messagerie, analytics, et endpoints d'ingestion de données externes.

## Architecture
- **Frontend**: React 18 + Tailwind CSS + Recharts
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB (db: educonnect_rdc)
- **Authentication**: JWT (utilisateurs) + Basic Auth (clients API externes)

## Rôles et Accès
| Rôle | Accès |
|------|-------|
| Ministre / Ministre Provincial / PROVED / Admin Tech | Tous les onglets |
| IPP | Tout sauf Paie, Partage de Données |
| DIPROCOPE | Tout sauf Partage de Données |
| Chef Étab / Directeur École / CPE | Tout sauf Documents, Rapports, Paie, Partage de Données |
| Enseignant | Tout sauf Documents, Rapports, Partage de Données (avec Paie) |

## What's Been Implemented

### Bugs corrigés (03/04)
- GED Zone Verte, Viabilité, Recherche Chat, Sélection Service

### Data Seeding
- 558 établissements, 467 enseignants, 15 494 élèves, 330 classes
- 59 238 notes, 6 000 bulletins (15 matières, 3 trimestres)

### Fonctionnalités
- Page Provinces (60 P.E., 26 P.A., navigation 3 niveaux)
- Graphiques d'évolution temporelle (AreaChart + BarChart, 12 mois)
- Page Évaluations (radar, distribution, table par matière)
- Inscription étape 2 avec rôles (Provincial, Établissement, Central)
- Navigation basée sur les rôles
- Page "Partage de Données" unifiée (Sources, Endpoints, Logs, Clés API)
- **Endpoints d'ingestion réels** : presences, evaluations, effectifs, notes
  - Basic Auth via api_clients
  - Support JSON/XML/CSV
  - Logging automatique de tous les appels
  - Validation des données (notes 0-20, etablissement_id existant)
  - GET /api/externe/sources/status + /api/externe/logs

## Key API Endpoints
### Internes (JWT)
- GET /api/stats/global, /stats/sexe, /stats/evolution, /stats/notes
- POST /api/auth/login, /api/inscription/etape1, /api/inscription/etape2
- GET /api/externe/sources/status, /api/externe/logs

### Externes (Basic Auth)
- POST /api/externe/presences
- POST /api/externe/evaluations
- POST /api/externe/effectifs
- POST /api/externe/notes

## Test Client API
- username: gestion_scolaire_test
- password: TestApiKey2026!
- permissions: notes, presences, inscriptions, affectations

## Prioritized Backlog
### P1
- [ ] Saisie manuelle de notes par enseignants (CRUD)
- [ ] Génération/téléchargement bulletins PDF
- [ ] Meilleure distribution données entre provinces

### P2
- [ ] Connexion API SECOPE réelle
- [ ] Carte interactive RDC
- [ ] Mode hors ligne
