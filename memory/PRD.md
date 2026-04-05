# Édu-Connect - PRD (Product Requirements Document)

## Énoncé du problème
Plateforme de gestion éducative pour la République Démocratique du Congo (RDC), permettant la gestion des établissements, enseignants, élèves, notes, documents et communications à l'échelle nationale.

## Architecture
- **Frontend**: React SPA + Tailwind CSS + Recharts + SVG interactif (CarteRDC)
- **Backend**: FastAPI REST API, routes modulaires (routes_stats.py, routes_chat.py, routes_rapports.py, routes_sirh.py, etc.)
- **Base de données**: MongoDB (educonnect_rdc)
- **Auth**: JWT + cookies httpOnly
- **PWA**: Service Worker pour mode hors ligne

## Ce qui a été implémenté

### Session initiale
- [x] Authentification multi-rôles (JWT + httpOnly cookies)
- [x] Inscription en 3 étapes
- [x] Dashboard avec statistiques globales et graphiques
- [x] Gestion des documents (GED) avec circuit de validation
- [x] Chat interne (conversations, contacts)
- [x] Carte interactive SVG des 26 provinces
- [x] Gestion SIRH (enseignants, mutations)
- [x] Module DINACOPE (contrôle, viabilité, paie)
- [x] Ingestion de données externes (API SECOPE mockée)
- [x] Mode PWA hors ligne

### Session 2 (refactoring + données)
- [x] Refactoring server.py: extraction routes stats → routes_stats.py
- [x] Peuplement réaliste des 26 provinces

### Session 3 (corrections URL + accents + comptes éphémères) - 05/04/2026
- [x] Fix URL API: chemins relatifs (/api)
- [x] Fix CORS
- [x] Fix accents français (Édu-Connect, Élèves, etc.)
- [x] Déplacement onglet Rapports → sous-onglet Documents
- [x] Fix erreur chargement Rapports
- [x] Carte RDC fidèle (400KB → 29KB)
- [x] Comptes éphémères Test01-Test10

### Session 4 (corrections #2) - 05/04/2026
- [x] Fix page Mutations: get_db() manquant dans routes_sirh.py
- [x] Fix texte Partage de Données: accents corrigés
- [x] Fix carte 0 P.E.: alignement prop/noms
- [x] Fix préfixes /api manquants

### Session 5 (code quality review) - 05/04/2026
- [x] #1 Secrets hardcodés → os.getenv() dans 4 fichiers de tests
- [x] #2 Hook dependencies: NotificationProfilIncomplet.jsx useCallback
- [x] #3 `is` comparisons → faux positifs (tous `is None`, correct)
- [x] #5 Array index keys → remplacés par des identifiants uniques (8 fichiers)
- [x] #6 Empty catch blocks → ajout console.error (6 fichiers)
- [x] #7 Undefined `token` → remplacé par credentials:'include' (6 fichiers)
- [x] #8 Nested ternaries → refactorisés en helper functions (Evaluations, DashboardPaie, RapportsTrimestriels)
- [x] Undefined email functions → commentées dans routes_sirh.py
- [x] Python lint: All checks passed
- [x] Unused API_URL variables nettoyées

## Backlog

### P1 - Priorité haute
- [ ] Génération de bulletins scolaires en PDF
- [ ] Saisie manuelle de notes par les enseignants (formulaire CRUD)

### P2 - Priorité moyenne
- [ ] Connexion API SECOPE réelle (quand disponible)
- [ ] Notifications push hors ligne

## Données en base
- 26 provinces administratives, 60 provinces éducationnelles, 567 sous-divisions
- 953 établissements, 4 114 enseignants, 126 804 élèves, 3 276 classes
- 3 319 185 notes
- 16 comptes utilisateurs (dont 10 éphémères)
