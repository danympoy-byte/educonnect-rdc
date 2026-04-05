# Édu-Connect - PRD (Product Requirements Document)

## Énoncé du problème
Plateforme de gestion éducative pour la République Démocratique du Congo (RDC), permettant la gestion des établissements, enseignants, élèves, notes, documents et communications à l'échelle nationale.

## Architecture
- **Frontend**: React SPA + Tailwind CSS + Recharts + SVG interactif (CarteRDC)
- **Backend**: FastAPI REST API, routes modulaires (routes_stats.py, routes_chat.py, routes_rapports.py, etc.)
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
- [x] Peuplement réaliste des 26 provinces (953 établissements, 126 804 élèves, 4 114 enseignants, 3.3M+ notes)

### Session 3 (corrections + comptes éphémères) - 05/04/2026
- [x] Fix URL API: toutes les URLs frontend utilisent des chemins relatifs (/api) au lieu d'URLs absolues
- [x] Fix CORS: configuration compatible avec credentials
- [x] Fix accents français: Édu-Connect, Élèves, Établissements, Viabilité, Présences, Partage de Données, Déconnexion
- [x] Déplacement onglet Rapports: de la navigation principale vers la page Documents (sous-onglet)
- [x] Fix erreur chargement Rapports: ajout credentials aux appels fetch
- [x] Fix recherche contacts Chat: fonctionne correctement avec URL relative
- [x] Carte RDC fidèle: SVG avec vrais contours des 26 provinces (simplifié de 400KB → 29KB)
- [x] Fix préfixes /api manquants: EntitesExternes.jsx, ListesDistribution.jsx
- [x] Comptes éphémères Test01-Test10 (rôle ministre, 24h)

## Backlog

### P1 - Priorité haute
- [ ] Génération de bulletins scolaires en PDF
- [ ] Saisie manuelle de notes par les enseignants (formulaire CRUD)

### P2 - Priorité moyenne
- [ ] Connexion API SECOPE réelle (quand disponible)
- [ ] Notifications push hors ligne

### Refactoring
- [ ] Extraction routes utilisateurs de server.py si nécessaire
- [ ] Nettoyage des variables API_URL='' inutilisées dans les composants

## Données en base
- 26 provinces administratives
- 60 provinces éducationnelles
- 567 sous-divisions
- 953 établissements
- 4 114 enseignants
- 126 804 élèves
- 3 319 185 notes
- 3 276 classes
- 16 comptes utilisateurs (dont 10 éphémères)
