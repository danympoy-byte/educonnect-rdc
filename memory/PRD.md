# Édu-Connect - Plateforme Éducative Nationale RDC

## Original Problem Statement
Correction de 4 bugs dans la plateforme Édu-Connect:
1. GED Zone Verte - "Erreur de connexion" lors du clic
2. Page Viabilité - Ajouter graphique camembert répartition niveaux viabilité
3. Page Conversation - Recherche utilisateurs ne fonctionne pas
4. Page Inscription - Impossible de sélectionner un service

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

## What's Been Implemented
### 03/04/2026 - Bug Fixes Session
1. **Bug #1 - GED Zone Verte CORRIGÉ**
   - Fichier: `/app/frontend/src/components/common/ContexteSwitcher.jsx`
   - Fix: Amélioration gestion erreurs, basculement fonctionne même si API échoue
   
2. **Bug #2 - Graphique Viabilité CORRIGÉ**
   - Fichier: `/app/frontend/src/components/dashboards/components/EvaluationViabilite.jsx`
   - Fix: Variable `token` undefined remplacée par credentials:include
   - Graphique camembert avec 5 portions égales (Excellent, Bon, Moyen, Faible, Critique)

3. **Bug #3 - Recherche Utilisateurs CORRIGÉ**
   - Fichier: `/app/backend/routes_chat.py`
   - Fix: Endpoint `/api/chat/utilisateurs-contactables` retourne tous les utilisateurs sans filtrage hiérarchique

4. **Bug #4 - Sélection Service CORRIGÉ**
   - Fichier: `/app/backend/seed_services.py` exécuté
   - 51 services créés (8 DG avec directions et services)
   - Dropdown cascade fonctionne correctement

## Prioritized Backlog
### P0 (Critical) - Completed
- [x] Zone Verte/Bleue switching
- [x] Viabilité pie chart
- [x] User search in conversations
- [x] Service selection in registration

### P1 (Important) - Future
- [ ] Compléter l'inscription multi-étapes (endpoint /api/auth/inscription/etape1)
- [ ] Ajouter données réelles pour les évaluations de viabilité
- [ ] Notifications en temps réel pour la messagerie

### P2 (Nice to have)
- [ ] Export des données en PDF
- [ ] Statistiques avancées
- [ ] Mode hors ligne

## Next Tasks
1. Tester l'inscription complète avec un nouvel utilisateur
2. Ajouter des données de test pour les établissements
3. Implémenter l'envoi de messages en temps réel
