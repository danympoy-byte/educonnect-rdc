# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Plateforme de gestion éducative pour la RDC intégrant données SECOPE/DINACOPE, gestion documentaire, messagerie, et analytics.

## Architecture
- **Frontend**: React 18 + Tailwind CSS + Recharts
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB (db: educonnect_rdc)
- **Authentication**: JWT avec cookies httpOnly

## Core Requirements
- Authentification sécurisée avec rôles multiples
- GED (Gestion Électronique des Documents) - Zones Bleue/Verte
- Évaluation de viabilité des établissements
- Messagerie interne
- Dashboard avec graphiques dynamiques + évolution temporelle
- Page Provinces (60 provinces éducationnelles)
- Page Évaluations (notes, bulletins, statistiques)
- Inscription multi-étapes avec rôles provinciaux/établissement
- Partage de Données (sources, endpoints, clés API)

## Rôles et Accès
| Rôle | Accès |
|------|-------|
| Ministre / Ministre Provincial / PROVED / Admin Tech | Tous les onglets |
| IPP | Tout sauf Paie, Partage de Données |
| DIPROCOPE | Tout sauf Partage de Données |
| Chef Étab / Directeur École / CPE | Tout sauf Documents, Rapports, Paie, Partage de Données |
| Enseignant | Tout sauf Documents, Rapports, Partage de Données (mais avec Paie) |

## What's Been Implemented

### Bugs corrigés
- GED Zone Verte, Graphique Viabilité, Recherche Chat, Sélection Service

### Data Seeding
- 558 établissements, 467 enseignants, 15 494 élèves, 330 classes
- 59 238 notes, 6 000 bulletins (15 matières, 3 trimestres)
- Dates réparties sur 12 mois pour l'évolution temporelle

### Fonctionnalités complètes
- Page Provinces (60 P.E., 26 P.A., navigation 3 niveaux)
- Graphiques d'évolution temporelle (AreaChart + BarChart)
- Page Évaluations (radar, distribution, table par matière)
- Inscription étape 2 avec 3 catégories (Provincial, Établissement, Central)
- Navigation basée sur les rôles (Layout.jsx)
- Page unifiée "Partage de Données" (Sources, Endpoints, Clés API)

## Prioritized Backlog

### P1 (Important) - Future
- [ ] Saisie manuelle de notes par les enseignants (formulaire CRUD)
- [ ] Génération et téléchargement de bulletins PDF
- [ ] Meilleure distribution des données entre provinces
- [ ] Endpoints d'ingestion réels (POST /api/externe/*)

### P2 (Nice to have)
- [ ] Connexion API SECOPE réelle
- [ ] Carte interactive RDC
- [ ] Mode hors ligne

## Key API Endpoints
- GET /api/stats/global, /stats/sexe, /stats/evolution, /stats/notes
- POST /api/auth/login, /api/inscription/etape1, /api/inscription/etape2
- GET /api/notes, /api/bulletins
