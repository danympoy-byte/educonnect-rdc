# Édu-Connect

> Plateforme Éducative Nationale - République Démocratique du Congo

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-Gouvernement%20RDC-green.svg)
![Stack](https://img.shields.io/badge/stack-React%20%2B%20FastAPI%20%2B%20MongoDB-orange.svg)

## 📋 À propos

**Édu-Connect** est la plateforme intégrée de gestion de l'éducation pour le **Ministère de l'Éducation Nationale et de la Nouvelle Citoyenneté (MINEPST)** de la République Démocratique du Congo.

### Objectifs

- 🎯 Digitaliser la gestion administrative du MINEPST
- 📊 Centraliser les données éducatives nationales
- 🏫 Gérer les établissements, enseignants et élèves
- 📄 Système de Gestion Électronique des Documents (GED)
- 💬 Communication interne hiérarchique
- 📈 Tableaux de bord et analyses statistiques

## 🚀 Fonctionnalités

### Modules Principaux

- **📄 GED** : Gestion Électronique des Documents avec circuits de validation hiérarchiques
- **👨‍🏫 SIRH** : Système d'Information des Ressources Humaines (enseignants, mutations, promotions)
- **👨‍🎓 Scolarité** : Gestion des élèves, classes, notes, bulletins
- **🏫 Établissements** : Gestion des écoles (primaire, collèges, lycées)
- **🔍 DINACOPE** : Contrôles, viabilité, détection de fraudes
- **💬 Chat** : Messagerie interne respectant la hiérarchie organisationnelle
- **📊 Statistiques** : Tableaux de bord et analyses
- **🗺️ Provinces** : Organisation territoriale administrative
- **📋 Exports** : Génération PDF/Excel pour rapports
- **🔐 API Keys** : Gestion des clés d'authentification pour développeurs externes

### Caractéristiques Techniques

- ✅ Architecture modulaire React Router (18 pages)
- ✅ Organigramme MINEPST complet (51 services sur 5 niveaux hiérarchiques)
- ✅ Profils multi-services avec inscription en 3 étapes
- ✅ Authentification JWT + API Keys
- ✅ Documentation OpenAPI/Swagger complète
- ✅ Interface responsive (mobile/tablette/desktop)
- ✅ Exports PDF/Excel
- ✅ Recherche avancée dans documents et conversations
- ✅ Respect de la hiérarchie organisationnelle

## 🛠️ Stack Technique

### Frontend
- **React** 18 - Framework UI
- **React Router** v6 - Navigation
- **TailwindCSS** - Styles
- **Axios** - Requêtes HTTP
- **React Hot Toast** - Notifications

### Backend
- **FastAPI** - Framework Python asynchrone
- **Motor** - Driver MongoDB asynchrone
- **Pydantic** - Validation des données
- **python-jose** - JWT
- **passlib[bcrypt]** - Hachage des mots de passe
- **reportlab** - Génération PDF
- **openpyxl** - Génération Excel

### Base de Données
- **MongoDB** - Base NoSQL

## 📦 Installation

### Prérequis

- Python 3.9+
- Node.js 18+
- MongoDB 5.0+
- yarn

### Backend

```bash
cd /app/backend

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Configurer variables d'environnement
cp .env.example .env
nano .env  # Modifier selon vos besoins

# Démarrer le serveur
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd /app/frontend

# Installer dépendances
yarn install

# Configurer variables d'environnement
cp .env.example .env
nano .env  # Modifier REACT_APP_BACKEND_URL

# Démarrer le serveur de développement
yarn start
```

L'application sera accessible sur `http://localhost:3000`

## 🔐 Configuration

### Variables d'Environnement

**Backend (`.env`)** :
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=educonnect_db
JWT_SECRET_KEY=votre_clé_secrète_très_longue
JWT_ALGORITHM=HS256
FRONTEND_URL=http://localhost:3000
```

**Frontend (`.env`)** :
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

Voir le fichier [DEPLOYMENT.md](./DEPLOYMENT.md) pour plus de détails.

## 📚 Documentation

- **Guide de déploiement** : [DEPLOYMENT.md](./DEPLOYMENT.md)
- **API Documentation** : `http://localhost:8001/docs` (Swagger UI)
- **API ReDoc** : `http://localhost:8001/redoc`

## 🏗️ Architecture

### Structure du Projet

```
/app/
├── backend/                 # API FastAPI
│   ├── server.py           # Point d'entrée principal
│   ├── models.py           # Modèles Pydantic
│   ├── auth.py             # Authentification JWT
│   ├── routes_*.py         # Routes par module
│   └── requirements.txt    # Dépendances Python
│
├── frontend/               # Application React
│   ├── src/
│   │   ├── pages/         # Pages (18 modules)
│   │   ├── components/    # Composants réutilisables
│   │   ├── services/      # Services API
│   │   └── context/       # Context React
│   └── package.json       # Dépendances Node
│
└── DEPLOYMENT.md          # Guide de déploiement
```

### Organisation Hiérarchique (MINEPST)

**5 niveaux hiérarchiques** :
1. Niveau 1 : Ministre
2. Niveau 2 : Secrétaire Général
3. Niveau 3 : Directions Générales (8 DG)
4. Niveau 4 : Directions
5. Niveau 5 : Services et Subdivisions

**51 services** couvrant l'ensemble de l'organigramme du MINEPST.

## 🔒 Sécurité

- 🔐 Authentification JWT avec refresh tokens
- 🔑 API Keys pour intégrations externes
- 🛡️ Validation des données avec Pydantic
- 🔒 Hachage bcrypt pour les mots de passe
- ✅ CORS configuré
- 🚫 Aucune suppression de données (traçabilité totale)

## 🌐 Déploiement

### Option 1 : Emergent (Natif)

Infrastructure gérée, MongoDB inclus, SSL automatique.

**Coût** : 50 crédits/mois

### Option 2 : Serveur Personnel

Voir le guide complet dans [DEPLOYMENT.md](./DEPLOYMENT.md)

Plateformes supportées :
- VPS (Ubuntu, Debian)
- Cloud (AWS, Azure, Google Cloud)
- Heroku, Railway, Render

## 📊 Base de Données

### Collections MongoDB

- `users` - Utilisateurs du système
- `services` - Structure organisationnelle (51 services)
- `documents` - Documents GED
- `enseignants` - SIRH
- `eleves` - Scolarité
- `etablissements` - Écoles
- `classes` - Classes
- `provinces` - 26 provinces RDC
- `conversations` - Chat interne
- `messages_chat` - Messages
- `api_keys` - Clés API externes

## 👥 Profils Utilisateurs

16 profils distincts avec RBAC :
- Ministre
- Secrétaire Général
- Directeurs Généraux
- Directeurs de services
- Agents administratifs
- Enseignants
- Chefs d'établissement
- Agents DINACOPE
- Et plus...

## 🎓 Cas d'Usage

### Enseignant
- Consulter son dossier
- Soumettre demande de mutation
- Accéder aux documents pédagogiques
- Communiquer avec sa hiérarchie

### Directeur d'École
- Gérer les élèves et classes
- Soumettre rapports trimestriels
- Consulter statistiques établissement
- Communiquer avec la direction provinciale

### Ministre / DG
- Tableaux de bord nationaux
- Validation de documents importants
- Suivi des établissements
- Analyse des données éducatives

## 📄 Licence

© 2026 Gouvernement de la République Démocratique du Congo  
Ministère de l'Éducation Nationale et de la Nouvelle Citoyenneté

**Tous droits réservés**

## 🤝 Contribution

Ce projet est développé pour le compte du MINEPST. Pour toute question ou suggestion :

📧 **Contact** : support@educonnect.gouv.cd

## 🙏 Remerciements

- **MINEPST** - Ministère de l'Éducation Nationale et de la Nouvelle Citoyenneté
- **Emergent AI** - Plateforme de développement
- Tous les contributeurs et testeurs

---

**Fait avec ❤️ pour l'éducation en RDC** 🇨🇩
