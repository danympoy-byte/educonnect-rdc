# Module 3 - Scolarité : Documentation des APIs Externes

## Vue d'ensemble

Le Module 3 - Scolarité permet aux systèmes externes de gestion scolaire d'envoyer des données vers la plateforme RIE-RDC. Le système supporte l'envoi de :
- **Notes des élèves**
- **Présences/Absences quotidiennes**
- **Inscriptions d'élèves**
- **Affectations d'enseignants**

## Formats Supportés

✅ **JSON** - Format recommandé pour les API modernes  
✅ **XML** - Pour les systèmes legacy  
✅ **CSV** - Pour les uploads manuels via fichiers Excel  

---

## Authentification

Toutes les APIs externes utilisent **Basic Auth** (username + password).

### Obtenir des credentials

Les credentials sont créés par un **Administrateur Technique** via l'interface "🔌 APIs Externes" :

1. Connectez-vous en tant qu'administrateur
2. Allez sur l'onglet "🔌 APIs Externes"
3. Cliquez sur "Nouveau Client API"
4. Remplissez le formulaire et sélectionnez les permissions
5. Sauvegardez les credentials (ils ne seront affichés qu'une seule fois)

**Exemple de credentials :**
```
Username: api_ecole_kinshasa_001
Password: Abc123@Secure!xyz
```

---

## API 1 : Envoi de Notes

### Endpoint
```
POST /api/externe/notes
```

### Authentification
```
Basic Auth: username + password
```

### Format JSON (Recommandé)

**Headers :**
```
Content-Type: application/json
```

**Body :**
```json
[
  {
    "eleve_id": "uuid-de-l-eleve",
    "classe_id": "uuid-de-la-classe",
    "matiere": "Mathématiques",
    "note": 15.5,
    "coefficient": 2,
    "trimestre": "trimestre_1",
    "annee_scolaire": "2024-2025",
    "enseignant_id": "uuid-enseignant",
    "commentaire": "Bon travail"
  },
  {
    "eleve_id": "uuid-de-l-eleve",
    "classe_id": "uuid-de-la-classe",
    "matiere": "Français",
    "note": 14.0,
    "coefficient": 2,
    "trimestre": "trimestre_1",
    "annee_scolaire": "2024-2025",
    "enseignant_id": "uuid-enseignant"
  }
]
```

### Format XML

**Headers :**
```
Content-Type: application/xml
```

**Body :**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<data>
  <note>
    <eleve_id>uuid-de-l-eleve</eleve_id>
    <classe_id>uuid-de-la-classe</classe_id>
    <matiere>Mathématiques</matiere>
    <note>15.5</note>
    <coefficient>2</coefficient>
    <trimestre>trimestre_1</trimestre>
    <annee_scolaire>2024-2025</annee_scolaire>
    <enseignant_id>uuid-enseignant</enseignant_id>
    <commentaire>Bon travail</commentaire>
  </note>
</data>
```

### Format CSV (Upload fichier)

**Headers :**
```
Content-Type: multipart/form-data
```

**Fichier CSV :**
```csv
eleve_id,classe_id,matiere,note,coefficient,trimestre,annee_scolaire,enseignant_id,commentaire
uuid-eleve-1,uuid-classe-1,Mathématiques,15.5,2,trimestre_1,2024-2025,uuid-enseignant,Bon travail
uuid-eleve-1,uuid-classe-1,Français,14.0,2,trimestre_1,2024-2025,uuid-enseignant,
```

### Valeurs pour "trimestre"
- `trimestre_1` - Trimestre 1
- `trimestre_2` - Trimestre 2
- `trimestre_3` - Trimestre 3

### Réponse Success
```json
{
  "success": true,
  "nb_notes_inserees": 2,
  "nb_erreurs": 0,
  "erreurs": [],
  "message": "2 notes insérées avec succès"
}
```

---

## API 2 : Envoi de Présences/Absences

### Endpoint
```
POST /api/externe/presences
```

### Format JSON

**Body :**
```json
[
  {
    "eleve_id": "uuid-de-l-eleve",
    "classe_id": "uuid-de-la-classe",
    "etablissement_id": "uuid-etablissement",
    "date": "2025-01-15",
    "present": true
  },
  {
    "eleve_id": "uuid-de-l-eleve-2",
    "classe_id": "uuid-de-la-classe",
    "etablissement_id": "uuid-etablissement",
    "date": "2025-01-15",
    "present": false,
    "justifie": true,
    "motif": "Maladie avec certificat médical"
  }
]
```

### Champs

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `eleve_id` | string | ✅ | ID unique de l'élève |
| `classe_id` | string | ✅ | ID de la classe |
| `etablissement_id` | string | ✅ | ID de l'établissement |
| `date` | string | ✅ | Date au format YYYY-MM-DD |
| `present` | boolean | ✅ | `true` = présent, `false` = absent |
| `justifie` | boolean | ❌ | Si absence justifiée (défaut: `false`) |
| `motif` | string | ❌ | Motif de l'absence |

### Réponse Success
```json
{
  "success": true,
  "nb_presences_inserees": 2,
  "nb_erreurs": 0,
  "erreurs": [],
  "message": "2 présences traitées avec succès"
}
```

---

## API 3 : Inscriptions d'Élèves

### Endpoint
```
POST /api/externe/inscriptions
```

### Authentification
```
Basic Auth: username + password
Permission requise: "inscriptions"
```

### Format JSON

**Body :**
```json
[
  {
    "nom": "Mukendi",
    "prenom": "Jean",
    "email": "jean.mukendi@ecole.cd",
    "etablissement_id": "uuid-etablissement",
    "niveau": "1ere_annee_secondaire",
    "sexe": "masculin",
    "date_naissance": "2010-05-15",
    "lieu_naissance": "Kinshasa",
    "classe_id": "uuid-classe",
    "password": "MotDePasse123"
  }
]
```

### Champs

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `nom` | string | ✅ | Nom de famille |
| `prenom` | string | ✅ | Prénom |
| `email` | string | ✅ | Email unique (sera l'identifiant) |
| `etablissement_id` | string | ✅ | ID de l'établissement |
| `niveau` | string | ✅ | Niveau scolaire (ex: "1ere_annee_secondaire") |
| `sexe` | string | ✅ | "masculin" ou "feminin" |
| `date_naissance` | string | ✅ | Format YYYY-MM-DD |
| `lieu_naissance` | string | ❌ | Lieu de naissance |
| `classe_id` | string | ❌ | ID de la classe (optionnel) |
| `password` | string | ❌ | Mot de passe (défaut: "password123") |

### Comportement
- Génération automatique de l'INE (Identifiant National Élève)
- Création du compte utilisateur avec rôle "eleve_primaire" ou "eleve_secondaire"
- Vérification que l'email n'existe pas déjà
- Attribution automatique du rôle selon le niveau

### Réponse Success
```json
{
  "success": true,
  "nb_inscriptions_inserees": 1,
  "nb_erreurs": 0,
  "erreurs": [],
  "message": "1 inscriptions traitées avec succès"
}
```

---

## API 4 : Affectations d'Enseignants

### Endpoint
```
POST /api/externe/affectations
```

### Authentification
```
Basic Auth: username + password
Permission requise: "affectations"
```

### Format JSON

**Body :**
```json
[
  {
    "enseignant_id": "uuid-enseignant",
    "etablissement_id": "uuid-etablissement",
    "date_debut": "2025-09-01",
    "date_fin": "2026-06-30",
    "poste": "Enseignant de Mathématiques",
    "charge_horaire": 20,
    "matieres": ["Mathématiques", "Physique"],
    "commentaire": "Affectation annuelle 2025-2026"
  }
]
```

### Champs

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `enseignant_id` | string | ✅ | ID de l'enseignant (doit exister) |
| `etablissement_id` | string | ✅ | ID de l'établissement (doit exister) |
| `date_debut` | string | ✅ | Date de début (YYYY-MM-DD) |
| `date_fin` | string | ❌ | Date de fin (YYYY-MM-DD) |
| `poste` | string | ❌ | Intitulé du poste |
| `charge_horaire` | number | ❌ | Nombre d'heures par semaine |
| `matieres` | array | ❌ | Liste des matières enseignées |
| `commentaire` | string | ❌ | Commentaire additionnel |

### Comportement
- Vérifie que l'enseignant et l'établissement existent
- Crée un historique d'affectation
- Met à jour l'établissement_id de l'enseignant
- Permet le suivi des mutations/affectations

### Réponse Success
```json
{
  "success": true,
  "nb_affectations_inserees": 1,
  "nb_erreurs": 0,
  "erreurs": [],
  "message": "1 affectations traitées avec succès"
}
```

---

## API 5 : Génération Automatique de Bulletins

Cette API est accessible uniquement via l'interface web RIE (pas d'API externe pour le moment).

### Comment ça marche ?

1. Les systèmes externes envoient les notes via `/api/externe/notes`
2. Les notes sont validées et stockées dans RIE
3. Un administrateur ou directeur peut générer les bulletins automatiquement pour une classe
4. Le système calcule automatiquement :
   - La moyenne générale de chaque élève
   - L'appréciation générale
   - Le classement dans la classe

---

## Exemples de Code

### Python avec `requests`

```python
import requests

# Configuration
api_url = "https://edu-connect-drc.preview.emergentagent.com"
username = "api_ecole_kinshasa_001"
password = "Abc123@Secure!xyz"

# Envoi de notes
notes = [
    {
        "eleve_id": "abc-123",
        "classe_id": "classe-456",
        "matiere": "Mathématiques",
        "note": 15.5,
        "coefficient": 2,
        "trimestre": "trimestre_1",
        "annee_scolaire": "2024-2025",
        "enseignant_id": "ens-789"
    }
]

response = requests.post(
    f"{api_url}/api/externe/notes",
    json=notes,
    auth=(username, password)
)

print(response.json())
```

### cURL

```bash
curl -X POST \
  https://edu-connect-drc.preview.emergentagent.com/api/externe/notes \
  -u "api_ecole_kinshasa_001:Abc123@Secure!xyz" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "eleve_id": "abc-123",
      "classe_id": "classe-456",
      "matiere": "Mathématiques",
      "note": 15.5,
      "coefficient": 2,
      "trimestre": "trimestre_1",
      "annee_scolaire": "2024-2025",
      "enseignant_id": "ens-789"
    }
  ]'
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const apiUrl = 'https://edu-connect-drc.preview.emergentagent.com';
const username = 'api_ecole_kinshasa_001';
const password = 'Abc123@Secure!xyz';

const notes = [
  {
    eleve_id: 'abc-123',
    classe_id: 'classe-456',
    matiere: 'Mathématiques',
    note: 15.5,
    coefficient: 2,
    trimestre: 'trimestre_1',
    annee_scolaire: '2024-2025',
    enseignant_id: 'ens-789'
  }
];

axios.post(`${apiUrl}/api/externe/notes`, notes, {
  auth: {
    username: username,
    password: password
  }
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

---

## Monitoring et Logs

Les administrateurs peuvent suivre l'activité des APIs externes via l'interface "🔌 APIs Externes" :

- **Clients API actifs** : Liste de tous les systèmes connectés
- **Logs d'activité** : Historique des 50 derniers appels API avec :
  - Date et heure
  - Système qui a fait l'appel
  - Endpoint appelé
  - Format des données (JSON/XML/CSV)
  - Nombre d'enregistrements
  - Statut (success, partial, error)

---

## Support et Contact

Pour toute question ou problème :
- Contactez votre **Administrateur Technique** RIE
- Email support : support@rie.cd
- Documentation complète : https://docs.rie.cd

---

**Version :** 1.0  
**Date :** Mars 2026  
**Ministère de l'Éducation nationale et de la Nouvelle Citoyenneté - RDC**
