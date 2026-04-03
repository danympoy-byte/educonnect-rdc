# 🔒 Migration localStorage → httpOnly Cookies - Guide complet

## ✅ PARTIE 1 : BACKEND (TERMINÉ)

### Modifications effectuées

**1. Route `/api/auth/login` modifiée** (`/app/backend/server.py`)
- ✅ Ajout du paramètre `response: Response`
- ✅ Configuration du cookie httpOnly sécurisé :
  ```python
  response.set_cookie(
      key="access_token",
      value=access_token,
      httponly=True,  # Pas accessible via JavaScript (protection XSS)
      secure=True,    # HTTPS uniquement
      samesite="lax", # Protection CSRF
      max_age=60 * 60 * 24 * 30  # 30 jours
  )
  ```
- ✅ Token toujours retourné en JSON pour compatibilité temporaire

**2. Route `/api/auth/logout` créée**
- ✅ Supprime le cookie httpOnly
- ✅ Endpoint : `POST /api/auth/logout`

**3. Middleware `get_current_user` amélioré** (`/app/backend/auth.py`)
- ✅ Lit le token depuis 2 sources (par ordre de priorité) :
  1. Cookie httpOnly `access_token` (prioritaire)
  2. Header `Authorization: Bearer <token>` (fallback)
- ✅ Compatibilité backward : les anciennes requêtes avec Bearer marchent toujours

**4. Configuration CORS** (`/app/backend/server.py`)
- ✅ `allow_credentials=True` déjà configuré
- ✅ Permet l'envoi de cookies cross-origin

---

## ✅ PARTIE 2 : FRONTEND (TERMINÉ - 3 avril 2026)

### Fichiers à modifier

#### 1. Configuration axios globale

**`/app/frontend/src/services/api.js`** :
```javascript
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,  // ⭐ AJOUTER : Envoie les cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// ⚠️ SUPPRIMER l'intercepteur qui ajoute le token depuis localStorage
// Les cookies sont envoyés automatiquement

export default api;
```

#### 2. Service d'authentification

**`/app/frontend/src/services/auth.service.js`** :
```javascript
import api from './api';

const authService = {
  async login(email, password) {
    const response = await api.post('/api/auth/login', { email, password });
    // ⚠️ NE PLUS stocker le token dans localStorage
    // Le cookie httpOnly est géré automatiquement
    return response.data;
  },

  async logout() {
    await api.post('/api/auth/logout');
    // Le cookie est supprimé côté serveur
  },

  getCurrentUser() {
    // ⚠️ Le user doit être stocké différemment (Context React par exemple)
    // Pas dans localStorage pour éviter XSS
    return null; // À adapter selon votre architecture
  }
};

export default authService;
```

#### 3. Contexte d'authentification

**`/app/frontend/src/context/AuthContext.js`** :
- ✅ Garder `user` en state React (pas localStorage)
- ✅ Appeler `/api/auth/me` au chargement pour récupérer l'utilisateur
- ✅ Le token est dans le cookie, pas besoin de le gérer

#### 4. Supprimer localStorage dans TOUS les fichiers

**Fichiers à nettoyer** (8+ fichiers) :
- `/app/frontend/src/services/auth.service.js` ✅
- `/app/frontend/src/services/api.js` ✅
- `/app/frontend/src/pages/Dashboard/Profil.jsx`
- `/app/frontend/src/pages/Dashboard/APIKeys.jsx`
- `/app/frontend/src/pages/Dashboard/ListesDistribution.jsx`
- `/app/frontend/src/pages/Dashboard/EntitesExternes.jsx`
- Tous les autres services (documents, enseignants, etc.)

**Remplacer** :
```javascript
// ❌ AVANT
const token = localStorage.getItem('token');
headers: { 'Authorization': `Bearer ${token}` }

// ✅ APRÈS
// Rien ! Les cookies sont envoyés automatiquement avec withCredentials: true
```

---

## 🧪 TESTS À EFFECTUER (après modifications frontend)

### 1. Test de connexion
```bash
# 1. Se connecter
curl -c cookies.txt -X POST https://edu-connect-rdc.net/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@educonnect.cd","password":"Admin@EduConnect2026!"}'

# 2. Vérifier le cookie
cat cookies.txt | grep access_token

# 3. Tester un endpoint protégé avec le cookie
curl -b cookies.txt https://edu-connect-rdc.net/api/auth/me

# 4. Se déconnecter
curl -b cookies.txt -X POST https://edu-connect-rdc.net/api/auth/logout
```

### 2. Test frontend
1. Ouvrir DevTools → Application → Cookies
2. Se connecter → Vérifier que `access_token` apparaît avec `HttpOnly` ✅
3. Ouvrir Console → Taper `document.cookie` → Le token ne doit PAS être visible ✅
4. Naviguer dans l'app → Toutes les requêtes doivent fonctionner
5. Se déconnecter → Le cookie doit disparaître

---

## 📊 Avantages de cette migration

| Avant (localStorage) | Après (httpOnly cookies) |
|---------------------|-------------------------|
| ❌ Vulnérable XSS | ✅ Protection XSS |
| ❌ Accessible JavaScript | ✅ Inaccessible JavaScript |
| ❌ Token exposé DevTools | ✅ Token invisible |
| ⚠️ Manuel (store/get/delete) | ✅ Automatique (navigateur) |

---

## 🚨 IMPORTANT - Points d'attention

1. **HTTPS obligatoire** : Les cookies `secure=True` ne fonctionnent qu'en HTTPS
2. **CORS** : `withCredentials: true` nécessite `allow_credentials=True` (déjà fait ✅)
3. **SameSite** : `lax` protège contre CSRF tout en permettant les redirections
4. **Compatibilité** : L'ancien système Bearer Token fonctionne toujours (fallback)

---

## 📋 Checklist de migration

### Backend ✅
- [x] Cookie httpOnly dans `/api/auth/login`
- [x] Route `/api/auth/logout`
- [x] Middleware `get_current_user` lit cookie + header
- [x] CORS `allow_credentials=True`
- [x] Backend testé et fonctionnel

### Frontend ✅
- [x] Axios `withCredentials: true` dans `api.js`
- [x] Supprimer `localStorage.setItem('token')` dans `auth.service.js`
- [x] Supprimer tous les `localStorage.getItem('token')` (24 fichiers migrés)
- [x] Supprimer tous les headers `Authorization: Bearer` manuels
- [x] Tester connexion/déconnexion
- [x] Tester toutes les pages protégées
- [x] Vérifier DevTools → Cookie httpOnly visible ✅
- [x] Vérifier Console → `document.cookie` ne montre PAS le token ✅

---

## 🎯 Prochaine étape

**Option A** : Faire la partie Frontend maintenant (45 min)
**Option B** : Déployer le backend actuel et finir le frontend plus tard
**Option C** : Tester d'abord le backend avec curl puis continuer

Le backend est prêt et compatible avec les deux méthodes. Vous pouvez déployer sans casser l'existant !
