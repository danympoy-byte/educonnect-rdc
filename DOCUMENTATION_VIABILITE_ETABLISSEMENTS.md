# 🏫 Fonctionnalité : Évaluation de la Viabilité des Établissements

## 📋 Vue d'Ensemble

La fonctionnalité **"Viabilité des Établissements"** est un système d'évaluation complet qui permet aux autorités éducatives (Directeurs Provinciaux, Ministre, Administrateurs Techniques) d'évaluer la capacité d'un établissement scolaire à fonctionner de manière optimale et durable.

**Objectif** : Identifier les établissements performants, ceux nécessitant un soutien, et ceux en situation critique nécessitant une intervention urgente.

---

## 🎯 Objectifs de la Fonctionnalité

1. **Évaluation Objective** : Score quantitatif sur 100 points basé sur 4 piliers
2. **Diagnostic Complet** : Identification des forces et faiblesses de chaque établissement
3. **Recommandations Automatiques** : Suggestions d'amélioration basées sur les scores
4. **Prise de Décision** : Aide à la décision pour fermeture, soutien ou félicitations
5. **Suivi Longitudinal** : Évolution de la viabilité d'une année à l'autre

---

## 📊 Système de Scoring (100 Points)

L'évaluation repose sur **4 piliers**, chacun valant **25 points** :

### **1️⃣ Score Effectifs (25 points)**

**Critère principal** : Ratio élèves/enseignants

| Ratio élèves/enseignants | Score |
|--------------------------|-------|
| 40 - 50 (idéal) | 25 points |
| 30 - 39 ou 51 - 60 | 20 points |
| 20 - 29 ou 61 - 70 | 15 points |
| < 20 ou > 70 | 10 points |

**Données collectées** :
- Nombre d'élèves
- Nombre d'enseignants
- Nombre de classes
- Ratio calculé automatiquement

**Exemple** : 
- 450 élèves, 10 enseignants = Ratio 45 → **25 points** ✅
- 800 élèves, 10 enseignants = Ratio 80 → **10 points** ⚠️

---

### **2️⃣ Score Infrastructures (25 points)**

**Critères évalués** :

| Critère | Points | Condition |
|---------|--------|-----------|
| Salles de classe fonctionnelles | 10 pts | ≥ 100% des besoins |
| Salles de classe fonctionnelles | 7 pts | ≥ 80% des besoins |
| Latrines fonctionnelles | 5 pts | ≥ 4 latrines |
| Point d'eau disponible | 5 pts | Oui/Non |
| Électricité disponible | 3 pts | Oui/Non |
| Clôture du périmètre | 2 pts | Oui/Non |

**Données collectées** :
- Nombre de salles de classe fonctionnelles
- Nombre de salles de classe nécessaires (calculé selon effectifs)
- Nombre de latrines fonctionnelles
- Disponibilité point d'eau (checkbox)
- Disponibilité électricité (checkbox)
- Clôture du périmètre (checkbox)

**Exemple** :
- 10 salles fonctionnelles / 8 nécessaires = 10 pts
- 6 latrines = 5 pts
- Point d'eau : Oui = 5 pts
- Électricité : Non = 0 pt
- Clôture : Oui = 2 pts
- **Total** : 22/25 points 🟢

---

### **3️⃣ Score Pédagogique (25 points)**

**Critères évalués** :

| Critère | Points | Description |
|---------|--------|-------------|
| Manuels scolaires suffisants | 10 pts | Chaque élève a ses manuels |
| Matériel didactique adéquat | 10 pts | Cartes, globes, matériel scientifique |
| Bibliothèque présente | 5 pts | Bibliothèque fonctionnelle |

**Données collectées** :
- Manuels scolaires suffisants (checkbox)
- Matériel didactique adéquat (checkbox)
- Bibliothèque présente (checkbox)

**Exemple** :
- Manuels : Oui = 10 pts
- Matériel didactique : Non = 0 pt
- Bibliothèque : Oui = 5 pts
- **Total** : 15/25 points 🟡

---

### **4️⃣ Score Financier (25 points)**

**Critères évalués** :

| Critère | Points | Description |
|---------|--------|-------------|
| Frais scolaires conformes | 10 pts | Respect barème officiel |
| Subvention de l'État reçue | 10 pts | Subvention annuelle perçue |
| Budget annuel adéquat | 5 pts | Budget équilibré et transparent |

**Données collectées** :
- Frais scolaires conformes au barème (checkbox)
- Subvention de l'État reçue (checkbox)
- Budget annuel adéquat (checkbox)

**Exemple** :
- Frais conformes : Oui = 10 pts
- Subvention reçue : Non = 0 pt
- Budget adéquat : Oui = 5 pts
- **Total** : 15/25 points 🟡

---

## 🎖️ Niveaux de Viabilité

Le **score total** (somme des 4 piliers) détermine le niveau de viabilité :

| Score Total | Niveau | Badge | Décision |
|-------------|--------|-------|----------|
| 90 - 100 | **Excellent** | 🟢 Vert | **Viable** - Établissement modèle |
| 80 - 89 | **Bon** | 🔵 Bleu | **Viable** - Très bon fonctionnement |
| 60 - 79 | **Moyen** | 🟡 Jaune | **Sous surveillance** - Amélioration nécessaire |
| 40 - 59 | **Faible** | 🟠 Orange | **Besoin d'amélioration** - Intervention requise |
| 0 - 39 | **Critique** | 🔴 Rouge | **Fermeture recommandée** - Situation alarmante |

---

## 💡 Recommandations Automatiques

Le système génère automatiquement des recommandations selon les scores :

### **Si Score Effectifs < 20 points** :
- ✅ **Ratio optimal** → "Ratio élèves/enseignants optimal" (Point fort)
- ⚠️ **Ratio > 60** → "Recruter des enseignants supplémentaires"
- ⚠️ **Ratio < 30** → "Optimiser la répartition des classes"

### **Si Score Infrastructures < 15 points** :
- ⚠️ "Améliorer les infrastructures" (Point d'amélioration)
- 🛠️ "Construire/réhabiliter salles de classe et latrines"

### **Si Score Pédagogique < 15 points** :
- ⚠️ "Renforcer le matériel pédagogique" (Point d'amélioration)
- 📚 "Acquérir manuels scolaires et matériel didactique"

---

## 🖥️ Interface Utilisateur

### **A) Onglet "💰 Viabilité"**

Accessible depuis le dashboard principal pour les rôles autorisés.

### **B) Liste des Évaluations**

Affiche toutes les évaluations de viabilité avec :

```
┌─────────────────────────────────────────────────────┐
│ 🏫 École Primaire de Kinshasa                       │
│ Kinshasa - 2024-2025                        [Bon] 82/100 │
│                                                     │
│ ┌──────────┬──────────┬──────────┬──────────┐      │
│ │Effectifs │Infrastructure│Pédagogique│Financier│  │
│ │  22/25   │    20/25     │   15/25   │  25/25  │  │
│ └──────────┴──────────────┴──────────┴──────────┘  │
│                                                     │
│ 📋 Recommandations :                                │
│  • Renforcer le matériel pédagogique               │
│  • Acquérir manuels scolaires                      │
└─────────────────────────────────────────────────────┘
```

### **C) Formulaire de Nouvelle Évaluation**

**Champs du formulaire** :

**Section 1 : Identification**
- Établissement (dropdown)
- Année scolaire (ex: 2024-2025)

**Section 2 : Effectifs**
- Nombre d'élèves (nombre)
- Nombre d'enseignants (nombre)
- Nombre de classes (nombre)
- *Ratio élèves/enseignants calculé automatiquement*

**Section 3 : Infrastructures**
- Salles de classe fonctionnelles (nombre)
- Salles de classe nécessaires (nombre)
- Latrines fonctionnelles (nombre)
- ✅ Point d'eau disponible (checkbox)
- ✅ Électricité disponible (checkbox)
- ✅ Clôture du périmètre (checkbox)

**Section 4 : Pédagogique**
- ✅ Manuels scolaires suffisants (checkbox)
- ✅ Matériel didactique adéquat (checkbox)
- ✅ Bibliothèque présente (checkbox)

**Section 5 : Financier**
- ✅ Frais scolaires conformes (checkbox - coché par défaut)
- ✅ Subvention de l'État reçue (checkbox)
- ✅ Budget annuel adéquat (checkbox)

---

## 🔐 Contrôle d'Accès

**Rôles autorisés** :
- ✅ Administrateur Technique (accès complet)
- ✅ Ministre de l'Éducation (accès complet)
- ✅ Directeur Provincial de l'Éducation (accès aux établissements de sa province)

**Rôles non autorisés** :
- ❌ Chefs d'établissement (ne peuvent pas s'auto-évaluer)
- ❌ Enseignants
- ❌ Personnel administratif

---

## 📊 Cas d'Usage Pratiques

### **Cas 1 : Établissement Excellent (Score 95/100)**

**École Primaire Modèle - Kinshasa**

| Pilier | Score |
|--------|-------|
| Effectifs | 25/25 (ratio 45) |
| Infrastructures | 25/25 (tout disponible) |
| Pédagogique | 25/25 (tout disponible) |
| Financier | 20/25 (pas de subvention État) |

**Décision** : ✅ **Viable** - Établissement modèle  
**Points forts** :
- Ratio élèves/enseignants optimal
- Infrastructures complètes
- Matériel pédagogique complet

**Recommandations** : Aucune intervention nécessaire

---

### **Cas 2 : Établissement Moyen (Score 68/100)**

**École Secondaire Rurale - Bandundu**

| Pilier | Score |
|--------|-------|
| Effectifs | 20/25 (ratio 55) |
| Infrastructures | 12/25 (manque eau et électricité) |
| Pédagogique | 15/25 (pas de bibliothèque) |
| Financier | 21/25 (budget adéquat mais pas de subvention) |

**Décision** : 🟡 **Sous surveillance** - Amélioration nécessaire  
**Points d'amélioration** :
- Améliorer les infrastructures
- Renforcer le matériel pédagogique

**Recommandations** :
- Construire un point d'eau
- Installer panneaux solaires
- Créer une bibliothèque

---

### **Cas 3 : Établissement Critique (Score 32/100)**

**École Primaire Isolée - Province du Kasaï**

| Pilier | Score |
|--------|-------|
| Effectifs | 10/25 (ratio 85 - surchargé) |
| Infrastructures | 7/25 (salles insuffisantes, pas d'eau ni électricité) |
| Pédagogique | 5/25 (manuels insuffisants) |
| Financier | 10/25 (pas de subvention) |

**Décision** : 🔴 **Fermeture recommandée** - Situation alarmante  
**Points d'amélioration** :
- Tous les domaines nécessitent intervention urgente

**Recommandations** :
- Recruter 5 enseignants supplémentaires
- Construire/réhabiliter salles de classe et latrines
- Acquérir manuels scolaires et matériel didactique
- **ACTION PRIORITAIRE** : Intervention ministérielle urgente

---

## 🗄️ Base de Données

**Collection** : `viabilite_etablissements`

**Champs stockés** :
```json
{
  "id": "uuid",
  "etablissement_id": "uuid",
  "etablissement_nom": "École Primaire...",
  "province_id": "uuid",
  "province_nom": "Kinshasa",
  "date_evaluation": "2024-03-30T12:00:00Z",
  "annee_scolaire": "2024-2025",
  
  // Effectifs
  "nombre_eleves": 450,
  "nombre_enseignants": 10,
  "nombre_classes": 12,
  "ratio_eleves_enseignants": 45.0,
  
  // Infrastructures
  "salles_classes_fonctionnelles": 12,
  "salles_classes_necessaires": 12,
  "latrines_fonctionnelles": 6,
  "point_eau_disponible": true,
  "electricite_disponible": false,
  "cloture_perimetre": true,
  
  // Pédagogique
  "manuels_scolaires_suffisants": true,
  "materiel_didactique_adequat": false,
  "bibliotheque_presente": true,
  
  // Financier
  "frais_scolaires_conformes": true,
  "subvention_etat_recue": false,
  "budget_annuel_adequat": true,
  
  // Scores calculés
  "score_effectifs": 25,
  "score_infrastructures": 20,
  "score_pedagogique": 15,
  "score_financier": 15,
  "score_total": 75,
  
  // Résultats
  "niveau_viabilite": "moyen",
  "decision": "sous_surveillance",
  "recommandations": ["...", "..."],
  "points_forts": ["..."],
  "points_amelioration": ["..."],
  
  // Métadonnées
  "decision_prise_par": "user_id",
  "date_decision": "2024-03-30T12:00:00Z"
}
```

---

## 📈 Statistiques et Rapports

Le système peut générer :

1. **Rapport provincial** : Nombre d'établissements par niveau de viabilité
2. **Rapport national** : Vue d'ensemble de la viabilité des établissements RDC
3. **Évolution temporelle** : Comparaison année par année
4. **Classement** : Top 10 meilleurs / 10 plus faibles établissements

---

## 🎯 Bénéfices de la Fonctionnalité

### **Pour le Ministère de l'Éducation** :
- 📊 Vision claire de l'état des établissements
- 🎯 Priorisation des interventions et investissements
- 📈 Suivi de l'évolution de la qualité éducative
- 💰 Allocation optimale des ressources budgétaires

### **Pour les Directeurs Provinciaux** :
- 🔍 Identification rapide des établissements en difficulté
- 📋 Recommandations concrètes pour améliorer
- 🏆 Valorisation des établissements performants

### **Pour les Établissements** :
- 🎯 Diagnostic objectif de leur situation
- 📝 Plan d'action clair pour s'améliorer
- 🏅 Reconnaissance officielle pour les bons résultats

---

## 🚀 Évolutions Futures Possibles

1. **Export PDF** : Générer rapport PDF de l'évaluation
2. **Comparaison** : Comparer avec établissements similaires
3. **Suivi longitudinal** : Graphiques d'évolution pluriannuelle
4. **Planification** : Créer plans d'action avec échéances
5. **Alertes automatiques** : Notification si score < 40
6. **Tableau de bord national** : Vue agrégée de toutes les évaluations

---

## 📝 Conclusion

La fonctionnalité **"Viabilité des Établissements"** est un outil puissant de pilotage de la qualité éducative qui permet :

✅ Une évaluation objective et standardisée  
✅ Des recommandations automatiques actionnables  
✅ Un suivi dans le temps de l'amélioration  
✅ Une aide à la décision pour les autorités  
✅ Une transparence dans l'allocation des ressources  

**C'est un levier essentiel pour améliorer progressivement la qualité de l'éducation en RDC.** 🇨🇩

---

**Document préparé par** : Agent E1  
**Date** : 30 Mars 2026  
**Version** : 1.0
