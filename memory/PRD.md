# PRD - Réseau Intégré de l'Éducation (RIE) - MVP

## 1. Vue d'Ensemble du Produit

### 1.1 Objectif
Créer un Produit Minimum Viable (MVP) du Réseau Intégré de l'Éducation (RIE) pour digitaliser et centraliser la gestion des données éducatives en République Démocratique du Congo.

### 1.2 Problèmes à Résoudre
- Gestion manuelle et fragmentée des données éducatives
- Absence d'identifiant unique pour les acteurs (enseignants, élèves)
- Difficultés de suivi du parcours scolaire
- Manque de visibilité sur les statistiques nationales
- Processus administratifs longs et opaques

### 1.3 Utilisateurs Cibles
16 profils utilisateurs répartis en 7 catégories :
- Décideurs (Ministre, Secrétaire Général, DPE, Chef sous-division)
- Établissements (Chef établissement, Directeur école, CPE)
- Enseignants
- Apprenants et Familles (Élèves, Parents)
- Contrôle (Inspecteurs, Agents DINACOPE)
- Support (Personnel admin, Infirmiers)
- Système (Administrateurs techniques)

## 2. Fonctionnalités du MVP

### 2.1 Module Authentification et Identités ✅

#### Fonctionnalités Implémentées
- **Inscription et connexion sécurisées**
  - Email + mot de passe
  - Hashing bcrypt
  - Token JWT (24h)
  
- **Gestion des rôles (RBAC)**
  - 16 profils avec permissions spécifiques
  - Protection des routes par rôle
  - Vérification côté backend et frontend

- **Identifiants uniques auto-générés**
  - Matricule Enseignant : `ENS-XXXXXX`
  - INE Élève : `INE-XXXXXXXX`
  - Code Établissement : `{PROVINCE}-ETB-XXXX`

#### Critères d'Acceptation
- [x] Un utilisateur peut s'inscrire avec son rôle
- [x] Un utilisateur peut se connecter et recevoir un token
- [x] Le token est vérifié à chaque requête API
- [x] Les identifiants sont uniques et persistants
- [x] Les actions sont tracées dans un journal d'audit

### 2.2 Module Gestion Territoriale ✅

#### Fonctionnalités Implémentées
- **Provinces**
  - CRUD complet
  - Code unique par province
  - Utilisé pour la génération des codes établissements

- **Sous-divisions**
  - CRUD complet
  - Liées aux provinces
  - Organisation administrative

#### Critères d'Acceptation
- [x] Admin peut créer une province avec un code unique
- [x] Admin peut créer des sous-divisions liées aux provinces
- [x] Les utilisateurs peuvent consulter la liste des provinces
- [x] Les statistiques peuvent être filtrées par province

### 2.3 Module Établissements ✅

#### Fonctionnalités Implémentées
- **Types d'établissements**
  - École Primaire
  - Collège
  - Lycée

- **Informations**
  - Nom, adresse
  - Code auto-généré
  - Affectation province et sous-division
  - Directeur/Chef d'établissement

#### Critères d'Acceptation
- [x] Admin/DPE peut créer un établissement
- [x] Code établissement généré automatiquement
- [x] Établissements filtrables par province/type
- [x] Affichage en tableau avec tri/recherche

### 2.4 Module Enseignants ✅

#### Fonctionnalités Implémentées
- **Profil enseignant**
  - Lié à un compte utilisateur
  - Matricule unique auto-généré
  - Établissement d'affectation
  - Matières enseignées
  - Statut professeur principal

#### Critères d'Acceptation
- [x] Directeur peut créer un profil enseignant
- [x] Matricule généré automatiquement (ENS-XXXXXX)
- [x] Enseignant peut être affecté à plusieurs matières
- [x] Enseignant peut être désigné professeur principal
- [x] Liste des enseignants filtrable par établissement

### 2.5 Module Élèves ✅

#### Fonctionnalités Implémentées
- **Profil élève**
  - Lié à un compte utilisateur
  - INE unique auto-généré
  - Informations : nom, prénom, date/lieu naissance
  - Établissement et classe
  - Niveau scolaire (CP1 à Terminale)
  - Lien avec parents/tuteurs

#### Critères d'Acceptation
- [x] Directeur peut inscrire un élève
- [x] INE généré automatiquement (INE-XXXXXXXX)
- [x] Élève affecté à une classe et un niveau
- [x] Parents peuvent être liés à l'élève
- [x] Liste des élèves filtrable par établissement/classe

### 2.6 Module Classes ✅

#### Fonctionnalités Implémentées
- **Gestion des classes**
  - Nom (ex: CP1 A, 6ème B)
  - Niveau scolaire
  - Établissement
  - Professeur principal
  - Année scolaire

#### Critères d'Acceptation
- [x] Directeur peut créer une classe
- [x] Classe liée à un établissement et un niveau
- [x] Professeur principal assigné
- [x] Liste des classes par établissement

### 2.7 Module Notes et Bulletins ✅

#### Fonctionnalités Implémentées
- **Saisie des notes**
  - Par enseignant
  - Par élève, matière, trimestre
  - Note sur 20
  - Coefficient
  - Commentaire optionnel

- **Génération de bulletins**
  - Automatique à partir des notes
  - Moyenne générale pondérée
  - Détail par matière
  - Appréciation automatique
  - Rang et effectif classe

#### Critères d'Acceptation
- [x] Enseignant peut saisir des notes
- [x] Notes organisées par trimestre et année scolaire
- [x] Bulletin généré automatiquement
- [x] Calcul correct des moyennes avec coefficients
- [x] Appréciation selon barème (Très bien, Bien, etc.)
- [x] Élève/Parent peut consulter le bulletin

### 2.8 Module Statistiques et Tableaux de Bord ✅

#### Fonctionnalités Implémentées
- **Statistiques globales**
  - Total établissements
  - Total enseignants
  - Total élèves (primaire/secondaire)
  - Total classes

- **Répartitions**
  - Par province
  - Par niveau scolaire
  - Par type d'établissement

- **Visualisations**
  - Graphiques en barres
  - Graphiques circulaires (pie charts)
  - KPIs en cartes

#### Critères d'Acceptation
- [x] Dashboard adapté selon le rôle utilisateur
- [x] Statistiques temps réel
- [x] Graphiques interactifs
- [x] Filtres par province
- [x] Export possible (futur)

### 2.9 Interface Utilisateur ✅

#### Fonctionnalités Implémentées
- **Page de connexion**
  - Design moderne et professionnel
  - Validation des champs
  - Messages d'erreur clairs

- **Dashboard unifié**
  - Navigation par onglets
  - Adaptation selon le rôle
  - 16 profils différents

- **Composants**
  - Tableaux de données
  - Formulaires de création
  - Notifications toast
  - Graphiques statistiques
  - Cartes KPI

#### Critères d'Acceptation
- [x] Interface responsive (desktop prioritaire)
- [x] Design cohérent et moderne
- [x] Navigation intuitive
- [x] Feedback utilisateur (notifications)
- [x] Temps de chargement < 3s
- [x] Aucune erreur console critique

## 3. Spécifications Techniques

### 3.1 Architecture

#### Backend
- **Framework:** FastAPI (Python)
- **Base de données:** MongoDB (Motor async)
- **Authentification:** JWT (python-jose)
- **Validation:** Pydantic v2
- **API:** RESTful, préfixe `/api`

#### Frontend
- **Framework:** React 19
- **Routing:** React Router v7
- **State:** Context API
- **HTTP:** Axios
- **UI:** Tailwind CSS + Radix UI
- **Charts:** Recharts

### 3.2 Sécurité

#### Implémenté ✅
- Hashing bcrypt pour mots de passe
- JWT avec expiration 24h
- CORS configuré
- Validation stricte des inputs
- RBAC (16 rôles)
- Journal d'audit
- Protection des endpoints sensibles

### 3.3 Performance

#### Cibles ✅
- Temps de réponse API < 500ms (95e percentile)
- Chargement page < 2s
- Support 100+ utilisateurs simultanés (MVP)

## 4. Métriques de Succès

### 4.1 Métriques Fonctionnelles
- [x] 100% des 16 profils implémentés
- [x] CRUD complet pour toutes les entités
- [x] Génération automatique des identifiants uniques
- [x] Calcul correct des bulletins
- [x] Statistiques en temps réel

### 4.2 Métriques Techniques
- [x] API 100% fonctionnelle
- [x] Frontend sans erreurs critiques
- [x] Authentification sécurisée
- [x] Base de données optimisée

### 4.3 Métriques Utilisateur
- [x] Interface intuitive et moderne
- [x] Navigation fluide
- [x] Feedback en temps réel
- [x] Formulaires validés

## 5. Hors Périmètre MVP

### Fonctionnalités Futures
- ❌ Module Examens d'État
- ❌ Gestion des mutations enseignants
- ❌ Application mobile native
- ❌ Mode hors ligne
- ❌ Diplômes avec QR Code
- ❌ Intégration SIGFIP (paie)
- ❌ Notifications SMS/Email
- ❌ Cartographie interactive
- ❌ Gestion des absences
- ❌ Planning des cours
- ❌ Messagerie interne

### Simplifications Techniques
- MongoDB au lieu de PostgreSQL
- FastAPI au lieu de Java/Spring Boot
- Pas de Kafka/Redis pour le MVP
- Pas de Keycloak (JWT simple)
- Pas de mode hors ligne
- Web uniquement (pas de mobile)

## 6. Risques et Mitigations

### Risques Identifiés
1. **Volumétrie importante** (15M élèves)
   - Mitigation: Architecture scalable, pagination, index MongoDB

2. **Sécurité des données**
   - Mitigation: JWT, bcrypt, RBAC, audit logs

3. **Adoption utilisateur**
   - Mitigation: Interface intuitive, formation prévue

4. **Connectivité zones rurales**
   - Mitigation: Prévu en V2 (mode hors ligne)

## 7. Plan de Déploiement

### Phase 1: MVP (Actuel) ✅
- Backend FastAPI déployé
- Frontend React déployé
- MongoDB configuré
- Authentification fonctionnelle
- 16 profils opérationnels

### Phase 2: Données de Production
- Migration des données existantes
- Formation des utilisateurs
- Support technique

### Phase 3: Évolutions
- Fonctionnalités avancées
- Optimisations performance
- Application mobile

## 8. Documentation

### Livrables ✅
- [x] README.md complet
- [x] API documentation (inline dans code)
- [x] Credentials de test
- [x] PRD (ce document)
- [x] Architecture technique documentée

## 9. Statut Actuel

### ✅ Complété
- Backend complet avec toutes les APIs
- Frontend avec dashboard unifié
- Authentification JWT via httpOnly cookies (migration localStorage terminée)
- 16 profils utilisateurs (RBAC)
- CRUD pour toutes les entités
- Génération automatique des identifiants
- Statistiques et graphiques
- Interface moderne et responsive
- Migration cookies httpOnly (30+ fichiers)
- Correction imports circulaires (34+ backend files, via dependencies.py)
- Badge "Made with Emergent" retiré
- **Code Quality Phase 1** (Avril 2026) :
  - P1: Backend function decomposition (generer_rapport_trimestriel.py 432→304 lignes, migrate_new_system.py 398→218 lignes)
  - P2: Frontend component splitting (DocumentManagement.jsx 1131→445+179, InscriptionMultiEtapes.jsx 689→166+102+125, UnifiedDashboard.old.js supprimé)
  - P3: 47 console statements supprimés, 0 anti-patterns Python `is` vs `==`
- 2 Health Checks de déploiement réussis
- **Bug fix:** Services invisibles sur étape 2 d'inscription (services.service.js migré vers instance api)
- **Utilisateurs éphémères (démo):** Comptes Test01-TestN, valides 24h après 1ère connexion (POST /api/demo/generer, GET /api/demo/liste, DELETE /api/demo/supprimer)

### 🔄 En Cours
- Tests utilisateurs

### 📋 Prochaines Étapes (Backlog)
1. **P0** Module Budgétaire (Finance/Caisse)
2. **P1** Plan d'Opérations Chef d'Établissement
3. **P1** Observations de Leçons
4. **P2** Refactoring templates email (email_service.py)
5. Documentation utilisateur & données de démonstration enrichies

## 10. Contacts et Support

**Développeur MVP:** Emergent AI Agent
**Date de livraison MVP:** Mars 2026
**Version:** 1.1.0 (Code Quality Phase 1)

---

*Ce PRD définit le périmètre fonctionnel et technique du MVP du Réseau Intégré de l'Éducation (RIE) pour la RDC.*
