# Structure des modèles - Édu-Connect (Refonte complète)

## 📋 Nouveaux Enums

### EtatCivil
- `CELIBATAIRE`
- `MARIE`
- `DIVORCE`
- `VEUF`

### NiveauService
- `NIVEAU_1`: Ministre
- `NIVEAU_2`: Cabinet, Inspections, Secrétariat Général
- `NIVEAU_3`: Directions Générales (8 DG)
- `NIVEAU_4`: Directions/Sous-directions
- `NIVEAU_5`: Services

### PrioriteDocument
- `CRITIQUE` (Priorité 1): Urgent - Immédiat
- `ELEVEE` (Priorité 2): Important - Échéance proche
- `NORMALE` (Priorité 3): Nécessaire - Non immédiat
- `FAIBLE` (Priorité 4): Peu important

---

## 🏢 Modèle Service

Représente un service dans l'organigramme du ministère.

```python
Service:
  - id: str
  - nom: str                    # Ex: "Direction Générale de l'Administration"
  - code: str                   # Ex: "DGA", "DGA_FIN"
  - niveau: NiveauService       # 1 à 5
  - parent_id: Optional[str]    # Service parent (None pour Ministre)
  - responsable_id: Optional[str]
  - description: Optional[str]
  - created_at: datetime
```

**Hiérarchie :**
```
Ministre (Niveau 1)
└── Cabinet du Ministre (Niveau 2)
└── Secrétariat Général (Niveau 2)
    └── DG Administration (Niveau 3)
        └── Direction Finances (Niveau 4)
            └── Service Comptabilité (Niveau 5)
```

---

## 👤 Modèle User (Refonte complète)

### Nouveaux champs ajoutés :

**Informations personnelles :**
- `postnom`: Nom de famille complet
- `etat_civil`: EtatCivil
- `date_naissance`: str (YYYY-MM-DD)
- `lieu_naissance`: str

**Contact :**
- `telephone`: str (OBLIGATOIRE dès Étape 1)
- `adresse`: str (OBLIGATOIRE dès Étape 1)
- `email`: Optional[str] (Peut être ajouté en Étape 3)

**Professionnel :**
- `diplomes`: List[Diplome]
- `experiences`: List[ExperienceProfessionnelle]

**Multi-services :**
- `service_profiles`: List[UserServiceProfile]
- `service_actif_id`: Optional[str]

**Financier :**
- `numero_compte_bancaire`: Optional[str]
- `banque`: Optional[str]

**Profil :**
- `photo_url`: Optional[str]
- `profil_complete`: bool (True si photo, email, compte bancaire renseignés)

---

## 📄 Modèle UserServiceProfile

Un utilisateur peut appartenir à plusieurs services (multi-profils).

```python
UserServiceProfile:
  - id: str
  - user_id: str
  - service_id: str
  - service_nom: str            # Dénormalisé
  - service_code: str
  - poste: str                  # Intitulé du poste dans ce service
  - est_responsable: bool       # True si responsable du service
  - date_affectation: datetime
```

---

## 🎓 Modèle Diplome

```python
Diplome:
  - intitule: str
  - etablissement: str
  - annee_obtention: Optional[int]
  - pays: str (défaut: "RDC")
```

---

## 💼 Modèle ExperienceProfessionnelle

```python
ExperienceProfessionnelle:
  - poste: str
  - employeur: str
  - date_debut: str (YYYY-MM)
  - date_fin: Optional[str] (None si poste actuel)
  - description: Optional[str]
```

---

## 📝 Modèle Document (Modifications majeures)

### Nouveaux champs obligatoires :

**Créateur :**
- `createur_service_id`: str
- `createur_service_nom`: str

**Destinataire :**
- `destinataire_service_id`: str
- `destinataire_service_nom`: str

**Circuit de validation (OBLIGATOIRE) :**
- `circuit_validation`: List[str] (PAS de défaut [])
- `circuit_validation_noms`: List[str]
- `circuit_validation_services`: List[str]

**Priorité (NOUVEAU - OBLIGATOIRE) :**
- `priorite`: PrioriteDocument (défaut: NORMALE)

**Affectation (pour Ministre/SG) :**
- `affecte_a_service_id`: Optional[str]
- `affecte_a_service_nom`: Optional[str]
- `commentaire_affectation`: Optional[str]

---

## 🔄 Processus d'inscription (3 étapes)

### Étape 1 : UserCreateStep1
- Informations personnelles complètes
- Diplômes et expériences
- Mot de passe

### Étape 2 : UserCreateStep2
- Sélection du service (liste déroulante 3 niveaux)
- Intitulé du poste dans le service

### Étape 3 : UserCreateStep3 (Optionnel)
- Email
- Numéro compte bancaire
- Photo
- **Note :** L'utilisateur a accès à la plateforme dès l'Étape 2
- Notifications de rappel pour compléter le profil

---

## 🔄 Circuit de validation automatique

**Logique :**
1. Récupérer le service du créateur
2. Remonter la hiérarchie : Service → Direction → DG → SG → Ministre
3. Générer le circuit automatiquement

**Exemple :**
```
Agent (Service Finances, DGA)
  → Chef Finances (N+1)
  → DG Administration
  → Secrétaire Général
  → Ministre
```

**Exceptions :**
- Si Ministre crée : peut valider directement OU affecter à un service
- Si SG crée : peut valider directement OU affecter à un service

---

## 🎯 Prochaines étapes (Phase 2)

1. Créer le fichier de seed pour les 8 Directions Générales
2. Créer les routes backend pour la gestion des services
3. Implémenter la logique d'auto-génération du circuit de validation
4. Créer les routes d'inscription en 3 étapes

---

**Status Phase 1 :** ✅ TERMINÉE
**Date :** 2026-03-31
