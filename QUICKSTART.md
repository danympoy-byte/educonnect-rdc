# 🚀 Guide de Démarrage Rapide - RIE

## Accès Immédiat

### 🌐 URL de l'Application
**https://bulletin-pdf-preview.preview.emergentagent.com**

### 🔐 Compte de Test
```
Email: admin@rie.cd
Mot de passe: admin123
Rôle: Administrateur Technique (accès complet)
```

## 📋 Premiers Pas

### 1. Connexion
1. Accédez à l'URL ci-dessus
2. Entrez les credentials de test
3. Cliquez sur "Se connecter"

### 2. Navigation
Une fois connecté, vous verrez un dashboard avec plusieurs onglets :
- **📊 Tableau de bord** - Vue d'ensemble des statistiques
- **🗺️ Provinces** - Gestion des provinces
- **🏫 Établissements** - Gestion des écoles
- **👨‍🎓 Élèves** - Gestion des élèves
- **👨‍🏫 Enseignants** - Gestion des enseignants
- **📚 Classes** - Gestion des classes

### 3. Créer une Province (Premier pas recommandé)
1. Cliquez sur l'onglet "🗺️ Provinces"
2. Cliquez sur "+ Nouvelle Province"
3. Remplissez :
   - Nom : "Kinshasa"
   - Code : "KIN"
4. Cliquez sur "Créer"

> **Note :** Si la province existe déjà, vous verrez un message d'erreur. C'est normal si des données de test existent déjà.

### 4. Créer une Sous-division
1. Depuis l'onglet Provinces
2. Créez une sous-division :
   - Nom : "Kinshasa Centre"
   - Code : "KIN-C"
   - Sélectionnez la province "Kinshasa"

### 5. Créer un Établissement
1. Allez dans l'onglet "🏫 Établissements"
2. Cliquez sur "+ Nouvel Établissement"
3. Remplissez les informations :
   - Nom : "École Primaire Lumumba"
   - Type : "École Primaire"
   - Adresse : "Avenue Lumumba, Kinshasa"
   - Province : "Kinshasa"
   - Sous-division : "Kinshasa Centre"
4. Cliquez sur "Créer"
5. **Un code unique sera automatiquement généré** (ex: KIN-ETB-1234)

### 6. Créer un Élève
1. Allez dans l'onglet "👨‍🎓 Élèves"
2. Cliquez sur "+ Nouvel Élève"
3. Remplissez :
   - Nom : "Kabila"
   - Prénom : "Jean"
   - Email : "jean.kabila@exemple.cd"
   - Mot de passe : "eleve123"
   - Établissement : Sélectionnez un établissement
   - Niveau : "CP1"
   - Date de naissance : 2018-01-15
   - Lieu de naissance : "Kinshasa"
4. Cliquez sur "Créer"
5. **Un INE unique sera automatiquement généré** (ex: INE-12345678)

### 7. Créer une Classe
1. Allez dans "📚 Classes"
2. Cliquez sur "+ Nouvelle Classe"
3. Remplissez :
   - Nom : "CP1 A"
   - Niveau : "CP1"
   - Établissement : Sélectionnez un établissement
   - Année scolaire : "2024-2025"
4. Cliquez sur "Créer"

## 🎯 Scénarios d'Utilisation

### Scénario 1 : Vue Directeur d'École
Pour tester la vue d'un directeur :
1. Créez un nouvel utilisateur avec le rôle "Directeur d'école"
2. Connectez-vous avec ce compte
3. Vous verrez uniquement les données de votre établissement

### Scénario 2 : Gestion Complète des Notes
1. Créez un enseignant
2. Créez des élèves et assignez-les à une classe
3. L'enseignant peut saisir des notes
4. Générez un bulletin automatiquement

### Scénario 3 : Vue Statistiques (Ministre/DPE)
1. Créez plusieurs établissements et élèves
2. Connectez-vous en tant qu'admin ou ministre
3. Consultez les statistiques globales avec graphiques

## 🔍 Exploration de l'API

### Test avec cURL
```bash
# 1. Connexion
curl -X POST https://bulletin-pdf-preview.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@rie.cd","password":"admin123"}'

# 2. Récupérer les statistiques (remplacez TOKEN)
curl -X GET https://bulletin-pdf-preview.preview.emergentagent.com/api/stats/global \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Lister les provinces
curl -X GET https://bulletin-pdf-preview.preview.emergentagent.com/api/provinces \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📱 Les 16 Profils Disponibles

Vous pouvez créer des utilisateurs avec ces rôles :

### Décisionnel
- `ministre` - Ministre de l'Éducation
- `secretaire_general` - Secrétaire Général
- `directeur_provincial` - DPE
- `chef_sous_division` - Chef de Sous-division

### Établissement
- `chef_etablissement` - Chef d'Établissement (secondaire)
- `directeur_ecole` - Directeur d'École (primaire)
- `conseiller_principal_education` - CPE

### Enseignement
- `enseignant` - Enseignant

### Apprenants
- `eleve_primaire` - Élève Primaire
- `eleve_secondaire` - Élève Secondaire
- `parent` - Parent

### Contrôle
- `inspecteur_pedagogique` - Inspecteur
- `agent_dinacope` - Agent DINACOPE

### Support
- `personnel_administratif` - Personnel Admin
- `infirmier_scolaire` - Infirmier

### Système
- `administrateur_technique` - Admin Technique

## 🎓 Identifiants Uniques Automatiques

Le système génère automatiquement :
- **Matricule Enseignant :** ENS-XXXXXX (ex: ENS-123456)
- **INE Élève :** INE-XXXXXXXX (ex: INE-12345678)
- **Code Établissement :** {PROVINCE}-ETB-XXXX (ex: KIN-ETB-1234)

Ces identifiants sont **uniques et permanents** pour chaque acteur.

## 📊 Fonctionnalités Clés à Tester

### ✅ Authentification
- [x] Connexion/Déconnexion
- [x] Token JWT (valide 24h)
- [x] Protection des routes

### ✅ Gestion Administrative
- [x] Provinces et sous-divisions
- [x] Établissements (3 types)
- [x] Classes par établissement

### ✅ Acteurs Éducatifs
- [x] Enseignants avec matricule
- [x] Élèves avec INE
- [x] Parents

### ✅ Pédagogie
- [x] Saisie des notes
- [x] Génération des bulletins
- [x] Calcul automatique des moyennes

### ✅ Statistiques
- [x] Tableau de bord global
- [x] Graphiques interactifs
- [x] Filtres par province

## ❓ Questions Fréquentes

**Q: Puis-je modifier un identifiant (INE, Matricule) ?**
R: Non, ces identifiants sont uniques et permanents une fois générés.

**Q: Comment créer un enseignant ?**
R: D'abord créez un utilisateur avec le rôle "enseignant", puis créez un profil enseignant lié à ce compte.

**Q: Les données sont-elles persistées ?**
R: Oui, toutes les données sont stockées dans MongoDB.

**Q: Puis-je tester plusieurs rôles ?**
R: Oui, créez plusieurs comptes avec des rôles différents et alternez entre eux.

**Q: Y a-t-il des données de démonstration ?**
R: Un compte admin existe. Vous pouvez créer vos propres données de test.

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans le navigateur (Console F12)
2. Vérifiez que vous êtes bien connecté
3. Assurez-vous d'avoir les permissions pour l'action

## 📚 Documentation Complète

Pour plus de détails, consultez :
- `/app/README.md` - Documentation technique complète
- `/app/memory/PRD.md` - Spécifications fonctionnelles
- `/app/memory/test_credentials.md` - Liste des endpoints API

---

**Bon test ! 🎉**
