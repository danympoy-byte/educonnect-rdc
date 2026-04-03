# Guide de Déploiement - Édu-Connect

## 📋 Documentation du Projet

**Application** : Édu-Connect - Plateforme Éducative Nationale de la RDC  
**Version** : 2.0.0  
**Stack** : React + FastAPI + MongoDB  
**Ministère** : Éducation Nationale et Nouvelle Citoyenneté (MINEPST)

---

## 🔐 Variables d'Environnement

### Backend (`/app/backend/.env`)

```env
# Base de données MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=educonnect_db

# Sécurité JWT
JWT_SECRET_KEY=votre_clé_secrète_jwt_très_longue_et_sécurisée
JWT_ALGORITHM=HS256

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:3000

# Autres configurations
ENVIRONMENT=production
```

**⚠️ Important** : 
- `MONGO_URL` : URL de connexion à votre base MongoDB (local ou cloud comme MongoDB Atlas)
- `JWT_SECRET_KEY` : Générez une clé aléatoire sécurisée (minimum 32 caractères)
- `DB_NAME` : Nom de votre base de données

### Frontend (`/app/frontend/.env`)

```env
# URL du backend API
REACT_APP_BACKEND_URL=https://votre-domaine.com
```

**⚠️ Important** :
- En développement : `http://localhost:8001`
- En production : URL complète de votre serveur backend (ex: `https://api.educonnect.gouv.cd`)

---

## 📦 Dépendances

### Backend (Python)

Fichier : `/app/backend/requirements.txt`

**Principales dépendances** :
- **FastAPI** : Framework web asynchrone
- **Motor** : Driver MongoDB asynchrone
- **Pydantic** : Validation des données
- **python-jose** : JWT pour authentification
- **passlib** : Hachage des mots de passe
- **reportlab** : Génération PDF
- **openpyxl** : Génération Excel
- **APScheduler** : Tâches planifiées

**Installation** :
```bash
cd /app/backend
pip install -r requirements.txt
```

### Frontend (React)

Fichier : `/app/frontend/package.json`

**Principales dépendances** :
- **React** : Framework UI
- **React Router** : Navigation
- **Axios** : Requêtes HTTP
- **TailwindCSS** : Styles
- **React Hot Toast** : Notifications

**Installation** :
```bash
cd /app/frontend
yarn install
```

---

## 🚀 Déploiement

### Option 1 : Emergent (Natif)

**Avantages** : Infrastructure gérée, MongoDB inclus, SSL automatique

**Coût** : 50 crédits/mois

**Démarrage** :
1. Cliquez sur "Deploy" dans l'interface Emergent
2. Confirmez le déploiement
3. Attendez 10-15 minutes
4. Récupérez votre URL publique

### Option 2 : Serveur Personnel (VPS/Cloud)

**Prérequis** :
- Serveur Linux (Ubuntu 20.04+ recommandé)
- Python 3.9+
- Node.js 18+
- MongoDB 5.0+
- Nginx (reverse proxy)

**Étapes** :

1. **Cloner le dépôt** :
```bash
git clone https://github.com/dmpoy/educonnect-rdc.git
cd educonnect-rdc
```

2. **Configurer MongoDB** :
```bash
# Installer MongoDB
sudo apt install mongodb-org

# Démarrer MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Créer la base de données
mongosh
> use educonnect_db
```

3. **Backend** :
```bash
cd /app/backend

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
nano .env  # Modifier les variables

# Démarrer avec Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

4. **Frontend** :
```bash
cd /app/frontend

# Installer dépendances
yarn install

# Configurer .env
echo "REACT_APP_BACKEND_URL=https://api.votre-domaine.com" > .env

# Build production
yarn build

# Servir avec Nginx
sudo cp -r build/* /var/www/educonnect/
```

5. **Nginx Configuration** :
```nginx
# /etc/nginx/sites-available/educonnect

server {
    listen 80;
    server_name educonnect.gouv.cd;

    # Frontend
    location / {
        root /var/www/educonnect;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **SSL avec Let's Encrypt** :
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d educonnect.gouv.cd
```

---

## 🗄️ Base de Données

### Collections MongoDB

1. **users** : Utilisateurs (enseignants, administrateurs, etc.)
2. **services** : Structure organisationnelle (51 services sur 5 niveaux)
3. **documents** : Documents GED avec circuits de validation
4. **enseignants** : Données SIRH
5. **eleves** : Scolarité
6. **etablissements** : Écoles
7. **classes** : Classes
8. **provinces** : Provinces de la RDC
9. **conversations** : Chat/messagerie interne
10. **messages_chat** : Messages des conversations
11. **api_keys** : Clés API pour développeurs externes

### Sauvegarde MongoDB

**Export** :
```bash
mongodump --db educonnect_db --out /backup/$(date +%Y%m%d)
```

**Import** :
```bash
mongorestore --db educonnect_db /backup/20260401/educonnect_db
```

---

## 🔒 Sécurité

### Recommandations

1. **Mots de passe** :
   - JWT_SECRET_KEY : Minimum 32 caractères aléatoires
   - MongoDB : Activer l'authentification
   - Comptes admin : Mots de passe forts

2. **HTTPS** :
   - Toujours utiliser SSL/TLS en production
   - Rediriger HTTP → HTTPS

3. **Firewall** :
   - Bloquer accès direct MongoDB (port 27017)
   - Autoriser uniquement ports 80/443

4. **Sauvegardes** :
   - Sauvegardes quotidiennes de MongoDB
   - Sauvegardes code sur GitHub
   - Conserver 30 jours d'historique

---

## 📞 Support

**Développement** : Emergent AI  
**Ministère** : MINEPST - République Démocratique du Congo  
**Contact Technique** : support@educonnect.gouv.cd

---

## 📝 Notes de Version

**v2.0.0** (Avril 2026)
- Refonte architecture React Router (18 pages modulaires)
- Organigramme MINEPST complet (51 services, 5 niveaux)
- Profils multi-services
- Circuits de validation hiérarchiques
- Chat/messagerie interne avec règles hiérarchiques
- Exports PDF/Excel
- Documentation OpenAPI/Swagger
- Authentification par clés API
- Interface responsive (mobile/tablette/desktop)

---

**Date de création** : Avril 2026  
**Dernière mise à jour** : Avril 2026
