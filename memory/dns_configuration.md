# 🌐 Configuration DNS pour edu-connect-rdc.net

**Date** : 2 avril 2026  
**Domaine** : edu-connect-rdc.net  
**Application** : Édu-Connect - Plateforme Éducative RDC

---

## 📋 Étapes de configuration DNS

### ✅ Étape 1 : Déploiement sur Emergent (À FAIRE EN PREMIER)

1. **Cliquez sur le bouton "Deploy"** dans l'interface Emergent
2. Attendez la fin du déploiement (5-10 minutes)
3. **Notez l'URL de production** que Emergent vous donne (exemple : `educonnect-prod-xyz.emergentagent.com`)

> ⚠️ **IMPORTANT** : Vous devez d'abord déployer pour obtenir l'URL cible !

---

### ✅ Étape 2 : Configuration DNS chez votre registrar

Une fois l'URL de production Emergent obtenue, configurez votre DNS :

#### **Accédez au panneau de contrôle DNS**
Connectez-vous au site web où vous avez acheté **edu-connect-rdc.net** (votre registrar).  
Exemples de registrars : Namecheap, GoDaddy, Gandi, OVH, Cloudflare, etc.

#### **Ajoutez les enregistrements DNS suivants** :

##### Option A : Utiliser un CNAME (Recommandé pour Emergent)

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| CNAME | @ | `[URL_EMERGENT_SANS_HTTPS]` | 3600 |
| CNAME | www | `[URL_EMERGENT_SANS_HTTPS]` | 3600 |

**Exemple** (remplacez par votre vraie URL Emergent) :
```
Type: CNAME
Nom: @
Valeur: educonnect-prod-xyz.emergentagent.com
TTL: 3600
```

> 💡 **Note** : Certains registrars n'autorisent pas les CNAME sur le domaine racine (@). Dans ce cas, utilisez l'Option B.

##### Option B : Utiliser des enregistrements A (si CNAME @ non supporté)

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| A | @ | `[IP_FOURNIE_PAR_EMERGENT]` | 3600 |
| A | www | `[IP_FOURNIE_PAR_EMERGENT]` | 3600 |

> ⚠️ Emergent vous fournira l'adresse IP lors du déploiement.

---

### ✅ Étape 3 : Configuration SSL/HTTPS

**Emergent gère automatiquement le SSL/TLS** pour votre domaine via Let's Encrypt.

Après avoir configuré le DNS :
1. Attendez la propagation DNS (15 min à 48h, souvent 1-2h)
2. Emergent détectera automatiquement votre domaine
3. Un certificat SSL sera généré automatiquement
4. Votre site sera accessible en HTTPS

---

### ✅ Étape 4 : Vérification

#### **Vérifier la propagation DNS** :
Utilisez ces outils en ligne :
- https://dnschecker.org
- https://www.whatsmydns.net

Entrez `edu-connect-rdc.net` et vérifiez que :
- Le domaine pointe vers l'URL/IP Emergent
- La propagation est effective dans plusieurs régions

#### **Tester l'application** :
Une fois le DNS propagé :
1. Accédez à https://edu-connect-rdc.net/login
2. Connectez-vous avec les identifiants admin
3. Vérifiez que tout fonctionne

---

## 🔧 Variables d'environnement configurées

Les variables suivantes ont déjà été mises à jour dans l'application :

### Backend (`/app/backend/.env`)
```
FRONTEND_URL=https://edu-connect-rdc.net
```

### Frontend (`/app/frontend/.env`)
```
REACT_APP_BACKEND_URL=https://edu-connect-rdc.net
```

> ✅ Ces variables seront automatiquement utilisées lors du déploiement.

---

## 📞 Identifiants Admin (Rappel)

Une fois déployé sur edu-connect-rdc.net, utilisez :

- **Super Admin** : admin@educonnect.cd / Admin@EduConnect2026!
- **Admin GED** : ged.admin@educonnect.cd / GED@Admin2026!
- **Admin SIRH** : sirh.admin@educonnect.cd / SIRH@Admin2026!

---

## ⏱️ Timeline estimé

| Étape | Durée |
|-------|-------|
| Déploiement Emergent | 5-10 minutes |
| Configuration DNS | 5 minutes |
| Propagation DNS | 15 min - 48h (souvent 1-2h) |
| Génération SSL automatique | 5-10 minutes après propagation |
| **TOTAL** | **30 min - 48h** (en moyenne 1-3h) |

---

## 🆘 Problèmes courants

### Le site n'est pas accessible après configuration DNS
- ✅ Vérifiez la propagation DNS avec dnschecker.org
- ✅ Videz le cache DNS de votre ordinateur : `ipconfig /flushdns` (Windows) ou `sudo dscacheutil -flushcache` (Mac)
- ✅ Essayez en navigation privée
- ✅ Attendez 1-2h pour la propagation complète

### Erreur de certificat SSL
- ✅ Attendez 10-15 minutes après la propagation DNS
- ✅ Emergent génère le certificat automatiquement
- ✅ Si le problème persiste après 1h, contactez le support Emergent

### Le domaine affiche une page vide ou erreur 404
- ✅ Vérifiez que le déploiement Emergent est terminé
- ✅ Vérifiez que les variables d'environnement sont correctes
- ✅ Redéployez si nécessaire

---

## 📝 Checklist finale

- [ ] Déployer sur Emergent (bouton "Deploy")
- [ ] Noter l'URL de production Emergent fournie
- [ ] Se connecter au registrar de edu-connect-rdc.net
- [ ] Ajouter les enregistrements DNS (CNAME ou A)
- [ ] Attendre la propagation DNS (vérifier avec dnschecker.org)
- [ ] Vérifier que https://edu-connect-rdc.net/login fonctionne
- [ ] Tester la connexion admin
- [ ] Vérifier toutes les fonctionnalités

---

**🎉 Une fois terminé, votre application Édu-Connect sera accessible sur votre domaine personnalisé !**
