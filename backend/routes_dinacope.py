"""
API Routes pour Module DINACOPE Avancé
Paie, Contrôles Physiques Mensuels, Viabilité Établissements
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
import csv
import io

from models import (
    GradeEnseignant, GrileSalariale, FichePaie, ControlePhysiqueMensuel,
    ViabiliteEtablissement, ExportDINACOPE
)
from auth import get_current_user

router = APIRouter(prefix="/api/dinacope", tags=["DINACOPE Avancé"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("user_id", user.get("id", ""))


# ============================================
# GRILLE SALARIALE
# ============================================

GRILLE_SALARIALE_DEFAULT = {
    "stagiaire": {1: 150000, 5: 165000, 10: 180000, 15: 200000},
    "mécanisé": {1: 200000, 5: 220000, 10: 245000, 15: 275000},
    "qualifié": {1: 275000, 5: 305000, 10: 340000, 15: 380000},
    "diplômé": {1: 380000, 5: 420000, 10: 470000, 15: 530000},
    "licencié": {1: 530000, 5: 590000, 10: 660000, 15: 750000},
    "maître_assistant": {1: 750000, 5: 840000, 10: 945000, 15: 1070000},
    "chef_de_travaux": {1: 1070000, 5: 1200000, 10: 1350000, 15: 1530000}
}


def calculer_salaire(grade: str, echelon: int, est_directeur: bool = False) -> dict:
    """Calcule le salaire selon la grille DINACOPE"""
    # Trouver l'échelon le plus proche dans la grille
    echelon_grille = 1
    if echelon >= 15:
        echelon_grille = 15
    elif echelon >= 10:
        echelon_grille = 10
    elif echelon >= 5:
        echelon_grille = 5
    
    salaire_base = GRILLE_SALARIALE_DEFAULT.get(grade, {}).get(echelon_grille, 200000)
    
    # Primes
    prime_fonction = salaire_base * 0.10  # 10% du salaire de base
    prime_anciennete = (echelon - 1) * 5000  # 5000 CDF par an d'ancienneté
    prime_responsabilite = salaire_base * 0.15 if est_directeur else 0
    
    salaire_brut = salaire_base + prime_fonction + prime_anciennete + prime_responsabilite
    retenues = salaire_brut * 0.15  # 15% de retenues (CNSS, impôts)
    salaire_net = salaire_brut - retenues
    
    return {
        "salaire_base": salaire_base,
        "prime_fonction": prime_fonction,
        "prime_anciennete": prime_anciennete,
        "prime_responsabilite": prime_responsabilite,
        "salaire_brut": salaire_brut,
        "retenues": retenues,
        "salaire_net": salaire_net
    }


# ============================================
# PRÉPARATION DE LA PAIE
# ============================================

@router.post("/paie/generer")
async def generer_fichier_paie_mensuel(
    mois: int = Body(..., ge=1, le=12),
    annee: int = Body(..., ge=2024),
    current_user: dict = Depends(get_current_user)
):
    """Générer le fichier de paie mensuel pour tous les enseignants"""
    from dependencies import get_db

    db = get_db()
    
    # Seuls admin et ministre peuvent générer
    if current_user["role"] not in ["administrateur_technique", "ministre"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # user_id = get_user_id(current_user)
    periode = f"{annee}-{mois:02d}"
    
    # Vérifier si déjà généré
    existe = await db.fiches_paie.find_one({"periode": periode}, {"_id": 0})
    if existe:
        raise HTTPException(status_code=400, detail=f"Fichier paie {periode} déjà généré")
    
    # Récupérer tous les enseignants
    enseignants = await db.enseignants.find({}, {"_id": 0}).to_list(10000)
    
    fiches_crees = 0
    for ens in enseignants:
        user = await db.users.find_one({"id": ens["user_id"]}, {"_id": 0})
        etablissement = await db.etablissements.find_one({"id": ens["etablissement_id"]}, {"_id": 0})
        
        if not user or not etablissement:
            continue
        
        province = await db.provinces.find_one({"id": etablissement.get("province_id")}, {"_id": 0})
        
        # Calculer échelon (années depuis engagement)
        echelon = 1
        if user.get("date_creation"):
            try:
                date_engagement = datetime.fromisoformat(user["date_creation"].replace("Z", "+00:00"))
                annees_service = (datetime.now(timezone.utc) - date_engagement).days // 365
                echelon = min(annees_service + 1, 15)
            except Exception:
                pass
        
        # Vérifier si directeur
        est_directeur = user.get("role") in ["directeur_ecole", "chef_etablissement"]
        
        # Calculer salaire
        salaire_data = calculer_salaire(
            ens.get("grade", "mécanisé"),
            echelon,
            est_directeur
        )
        
        # Créer fiche paie
        fiche = FichePaie(
            matricule_secope=ens.get("matricule", ""),
            enseignant_id=ens["id"],
            enseignant_nom=f"{user.get('prenom', '')} {user.get('nom', '')}",
            mois=mois,
            annee=annee,
            periode=periode,
            date_naissance=user.get("date_naissance"),
            sexe=user.get("sexe", "M"),
            grade=ens.get("grade", "mécanisé"),
            echelon=echelon,
            fonction="Directeur" if est_directeur else "Enseignant",
            etablissement_id=ens["etablissement_id"],
            etablissement_nom=etablissement.get("nom", ""),
            province_id=etablissement.get("province_id", ""),
            province_nom=province.get("nom", "") if province else "",
            **salaire_data
        )
        
        await db.fiches_paie.insert_one(fiche.model_dump())
        fiches_crees += 1
    
    return {
        "message": f"Fichier paie {periode} généré avec succès",
        "periode": periode,
        "fiches_crees": fiches_crees
    }


@router.get("/paie")
async def lister_fiches_paie(
    mois: Optional[int] = Query(None),
    annee: Optional[int] = Query(None),
    enseignant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lister les fiches de paie"""
    from dependencies import get_db

    db = get_db()
    
    filtre = {}
    
    # Enseignant voit seulement ses fiches
    if current_user["role"] == "enseignant":
        filtre["enseignant_id"] = current_user["id"]
    elif enseignant_id:
        filtre["enseignant_id"] = enseignant_id
    
    if mois:
        filtre["mois"] = mois
    if annee:
        filtre["annee"] = annee
    
    fiches = await db.fiches_paie.find(filtre, {"_id": 0}).sort("periode", -1).to_list(1000)
    
    return {
        "total": len(fiches),
        "fiches": fiches
    }


@router.get("/paie/statistiques")
async def statistiques_paie(
    mois: int = Query(...),
    annee: int = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Statistiques comparatives de la paie (mois actuel vs précédent)"""
    from dependencies import get_db

    db = get_db()
    
    periode_actuelle = f"{annee}-{mois:02d}"
    
    # Mois précédent
    date_actuelle = datetime(annee, mois, 1)
    date_precedente = date_actuelle - relativedelta(months=1)
    periode_precedente = date_precedente.strftime("%Y-%m")
    
    # Stats période actuelle
    fiches_actuelles = await db.fiches_paie.find({"periode": periode_actuelle}, {"_id": 0}).to_list(10000)
    total_actuel = len(fiches_actuelles)
    masse_salariale_actuelle = sum(f.get("salaire_net", 0) for f in fiches_actuelles)
    payes_actuels = len([f for f in fiches_actuelles if f.get("statut_paiement") == "paye"])
    
    # Stats période précédente
    fiches_precedentes = await db.fiches_paie.find({"periode": periode_precedente}, {"_id": 0}).to_list(10000)
    total_precedent = len(fiches_precedentes)
    masse_salariale_precedente = sum(f.get("salaire_net", 0) for f in fiches_precedentes)
    payes_precedents = len([f for f in fiches_precedentes if f.get("statut_paiement") == "paye"])
    
    return {
        "periode_actuelle": {
            "periode": periode_actuelle,
            "total_enseignants": total_actuel,
            "enseignants_payes": payes_actuels,
            "taux_paiement": round((payes_actuels / total_actuel * 100) if total_actuel > 0 else 0, 2),
            "masse_salariale": masse_salariale_actuelle
        },
        "periode_precedente": {
            "periode": periode_precedente,
            "total_enseignants": total_precedent,
            "enseignants_payes": payes_precedents,
            "taux_paiement": round((payes_precedents / total_precedent * 100) if total_precedent > 0 else 0, 2),
            "masse_salariale": masse_salariale_precedente
        },
        "evolution": {
            "enseignants": total_actuel - total_precedent,
            "masse_salariale": masse_salariale_actuelle - masse_salariale_precedente,
            "taux_evolution": round(
                ((total_actuel - total_precedent) / total_precedent * 100) if total_precedent > 0 else 0,
                2
            )
        }
    }


# ============================================
# CONTRÔLES PHYSIQUES MENSUELS
# ============================================

@router.post("/controles/planifier")
async def planifier_controles_mensuels(
    mois: int = Body(...),
    annee: int = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Planifier les contrôles physiques mensuels pour tous les établissements"""
    from dependencies import get_db

    db = get_db()
    
    if current_user["role"] not in ["agent_dinacope", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents DINACOPE")
    
    user_id = get_user_id(current_user)
    periode = f"{annee}-{mois:02d}"
    
    # Récupérer tous les établissements
    etablissements = await db.etablissements.find({}, {"_id": 0}).to_list(10000)
    
    controles_crees = 0
    for etab in etablissements:
        province = await db.provinces.find_one({"id": etab.get("province_id")}, {"_id": 0})
        
        # Compter les enseignants
        enseignants_count = await db.enseignants.count_documents({"etablissement_id": etab["id"]})
        
        controle = ControlePhysiqueMensuel(
            etablissement_id=etab["id"],
            etablissement_nom=etab.get("nom", ""),
            province_id=etab.get("province_id", ""),
            province_nom=province.get("nom", "") if province else "",
            mois=mois,
            annee=annee,
            periode=periode,
            agent_dinacope_id=user_id,
            agent_dinacope_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
            date_controle=datetime.now(timezone.utc).isoformat(),
            enseignants_total=enseignants_count
        )
        
        await db.controles_physiques.insert_one(controle.model_dump())
        controles_crees += 1
    
    return {
        "message": f"Contrôles mensuels {periode} planifiés avec succès",
        "periode": periode,
        "controles_crees": controles_crees
    }


@router.get("/controles")
async def lister_controles(
    mois: Optional[int] = Query(None),
    annee: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lister les contrôles physiques mensuels"""
    from dependencies import get_db

    db = get_db()
    
    filtre = {}
    if mois:
        filtre["mois"] = mois
    if annee:
        filtre["annee"] = annee
    if statut:
        filtre["statut"] = statut
    
    controles = await db.controles_physiques.find(filtre, {"_id": 0}).sort("date_controle", -1).to_list(1000)
    
    return {
        "total": len(controles),
        "controles": controles
    }


@router.post("/controles/{controle_id}/effectuer")
async def effectuer_controle(
    controle_id: str,
    enseignants_presents: List[str] = Body(...),
    enseignants_absents: List[str] = Body(...),
    observations: str = Body(""),
    current_user: dict = Depends(get_current_user)
):
    """Effectuer un contrôle physique"""
    from dependencies import get_db

    db = get_db()
    
    if current_user["role"] not in ["agent_dinacope", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents DINACOPE")
    
    controle = await db.controles_physiques.find_one({"id": controle_id}, {"_id": 0})
    if not controle:
        raise HTTPException(status_code=404, detail="Contrôle non trouvé")
    
    # Construire liste vérification
    enseignants_verifies = []
    for ens_id in enseignants_presents:
        ens = await db.enseignants.find_one({"id": ens_id}, {"_id": 0})
        if ens:
            user = await db.users.find_one({"id": ens["user_id"]}, {"_id": 0})
            enseignants_verifies.append({
                "enseignant_id": ens_id,
                "nom": f"{user.get('prenom', '')} {user.get('nom', '')}",
                "present": True,
                "observations": ""
            })
    
    for ens_id in enseignants_absents:
        ens = await db.enseignants.find_one({"id": ens_id}, {"_id": 0})
        if ens:
            user = await db.users.find_one({"id": ens["user_id"]}, {"_id": 0})
            enseignants_verifies.append({
                "enseignant_id": ens_id,
                "nom": f"{user.get('prenom', '')} {user.get('nom', '')}",
                "present": False,
                "observations": "Absent lors du contrôle"
            })
    
    total = len(enseignants_presents) + len(enseignants_absents)
    taux_presence = round((len(enseignants_presents) / total * 100) if total > 0 else 0, 2)
    
    # Mettre à jour contrôle
    await db.controles_physiques.update_one(
        {"id": controle_id},
        {
            "$set": {
                "statut": "termine",
                "enseignants_presents": len(enseignants_presents),
                "enseignants_absents": len(enseignants_absents),
                "taux_presence": taux_presence,
                "enseignants_verifies": enseignants_verifies,
                "observations": observations
            }
        }
    )
    
    # Mettre à jour les fiches de paie (marquer contrôle effectué)
    periode = controle["periode"]
    for ens_id in enseignants_presents:
        await db.fiches_paie.update_many(
            {"enseignant_id": ens_id, "periode": periode},
            {
                "$set": {
                    "controle_physique_effectue": True,
                    "date_controle_physique": datetime.now(timezone.utc).isoformat(),
                    "agent_controle_id": get_user_id(current_user)
                }
            }
        )
    
    return {
        "message": "Contrôle effectué avec succès",
        "taux_presence": taux_presence
    }


# ============================================
# VIABILITÉ DES ÉTABLISSEMENTS
# ============================================

@router.post("/viabilite/evaluer")
async def evaluer_viabilite_etablissement(
    etablissement_id: str = Body(...),
    annee_scolaire: str = Body(...),
    donnees: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Évaluer la viabilité d'un établissement"""
    from dependencies import get_db

    db = get_db()
    
    if current_user["role"] not in ["directeur_provincial", "ministre", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    etablissement = await db.etablissements.find_one({"id": etablissement_id}, {"_id": 0})
    if not etablissement:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    
    province = await db.provinces.find_one({"id": etablissement.get("province_id")}, {"_id": 0})
    
    # Calcul scoring
    # 1. Score effectifs (25 points)
    ratio = donnees.get("ratio_eleves_enseignants", 0)
    score_effectifs = 0
    if 40 <= ratio <= 50:
        score_effectifs = 25
    elif 30 <= ratio < 40 or 50 < ratio <= 60:
        score_effectifs = 20
    elif 20 <= ratio < 30 or 60 < ratio <= 70:
        score_effectifs = 15
    else:
        score_effectifs = 10
    
    # 2. Score infrastructures (25 points)
    score_infra = 0
    if donnees.get("salles_classes_fonctionnelles", 0) >= donnees.get("salles_classes_necessaires", 1):
        score_infra += 10
    elif donnees.get("salles_classes_fonctionnelles", 0) >= donnees.get("salles_classes_necessaires", 1) * 0.8:
        score_infra += 7
    
    if donnees.get("latrines_fonctionnelles", 0) >= 4:
        score_infra += 5
    if donnees.get("point_eau_disponible", False):
        score_infra += 5
    if donnees.get("electricite_disponible", False):
        score_infra += 3
    if donnees.get("cloture_perimetre", False):
        score_infra += 2
    
    # 3. Score pédagogique (25 points)
    score_peda = 0
    if donnees.get("manuels_scolaires_suffisants", False):
        score_peda += 10
    if donnees.get("materiel_didactique_adequat", False):
        score_peda += 10
    if donnees.get("bibliotheque_presente", False):
        score_peda += 5
    
    # 4. Score financier (25 points)
    score_financier = 0
    if donnees.get("frais_scolaires_conformes", False):
        score_financier += 10
    if donnees.get("subvention_etat_recue", False):
        score_financier += 10
    if donnees.get("budget_annuel_adequat", False):
        score_financier += 5
    
    score_total = score_effectifs + score_infra + score_peda + score_financier
    
    # Niveau viabilité
    if score_total >= 90:
        niveau = "excellent"
        decision = "viable"
    elif score_total >= 80:
        niveau = "bon"
        decision = "viable"
    elif score_total >= 60:
        niveau = "moyen"
        decision = "sous_surveillance"
    elif score_total >= 40:
        niveau = "faible"
        decision = "besoin_amelioration"
    else:
        niveau = "critique"
        decision = "fermeture_recommandee"
    
    # Générer recommandations
    recommandations = []
    points_forts = []
    points_amelioration = []
    
    if score_effectifs >= 20:
        points_forts.append("Ratio élèves/enseignants optimal")
    else:
        points_amelioration.append("Ajuster le ratio élèves/enseignants")
        recommandations.append("Recruter des enseignants supplémentaires" if ratio > 60 else "Optimiser la répartition des classes")
    
    if score_infra < 15:
        points_amelioration.append("Améliorer les infrastructures")
        recommandations.append("Construire/réhabiliter salles de classe et latrines")
    
    if score_peda < 15:
        points_amelioration.append("Renforcer le matériel pédagogique")
        recommandations.append("Acquérir manuels scolaires et matériel didactique")
    
    # Créer évaluation
    evaluation = ViabiliteEtablissement(
        etablissement_id=etablissement_id,
        etablissement_nom=etablissement.get("nom", ""),
        province_id=etablissement.get("province_id", ""),
        province_nom=province.get("nom", "") if province else "",
        date_evaluation=datetime.now(timezone.utc).isoformat(),
        annee_scolaire=annee_scolaire,
        **donnees,
        score_effectifs=score_effectifs,
        score_infrastructures=score_infra,
        score_pedagogique=score_peda,
        score_financier=score_financier,
        score_total=score_total,
        niveau_viabilite=niveau,
        recommandations=recommandations,
        points_forts=points_forts,
        points_amelioration=points_amelioration,
        decision=decision,
        decision_prise_par=get_user_id(current_user),
        date_decision=datetime.now(timezone.utc).isoformat()
    )
    
    await db.viabilite_etablissements.insert_one(evaluation.model_dump())
    
    return {
        "message": "Évaluation de viabilité créée avec succès",
        "evaluation": evaluation.model_dump()
    }


@router.get("/viabilite")
async def lister_evaluations_viabilite(
    etablissement_id: Optional[str] = Query(None),
    niveau: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lister les évaluations de viabilité"""
    from dependencies import get_db

    db = get_db()
    
    filtre = {}
    if etablissement_id:
        filtre["etablissement_id"] = etablissement_id
    if niveau:
        filtre["niveau_viabilite"] = niveau
    
    evaluations = await db.viabilite_etablissements.find(filtre, {"_id": 0}).sort("date_evaluation", -1).to_list(500)
    
    return {
        "total": len(evaluations),
        "evaluations": evaluations
    }


# ============================================
# EXPORTS DINACOPE
# ============================================

@router.post("/exports/generer")
async def generer_export_dinacope(
    type_export: str = Body(...),
    mois: int = Body(...),
    annee: int = Body(...),
    format_fichier: str = Body("csv"),
    current_user: dict = Depends(get_current_user)
):
    """Générer un export au format DINACOPE"""
    from dependencies import get_db

    db = get_db()
    
    if current_user["role"] not in ["administrateur_technique", "ministre"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    periode = f"{annee}-{mois:02d}"
    
    # Selon type export
    if type_export == "fichier_paie":
        fiches = await db.fiches_paie.find({"periode": periode}, {"_id": 0}).to_list(10000)
        
        if format_fichier == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "matricule_secope", "enseignant_nom", "grade", "echelon",
                "etablissement_nom", "province_nom", "salaire_net", "statut_paiement"
            ])
            writer.writeheader()
            for fiche in fiches:
                writer.writerow({
                    "matricule_secope": fiche.get("matricule_secope"),
                    "enseignant_nom": fiche.get("enseignant_nom"),
                    "grade": fiche.get("grade"),
                    "echelon": fiche.get("echelon"),
                    "etablissement_nom": fiche.get("etablissement_nom"),
                    "province_nom": fiche.get("province_nom"),
                    "salaire_net": fiche.get("salaire_net"),
                    "statut_paiement": fiche.get("statut_paiement")
                })
            
            contenu = output.getvalue()
            fichier_nom = f"fichier_paie_{periode}.csv"
            
            # Sauvegarder export
            export = ExportDINACOPE(
                type_export=type_export,
                mois=mois,
                annee=annee,
                periode=periode,
                nombre_enregistrements=len(fiches),
                format_fichier=format_fichier,
                fichier_nom=fichier_nom,
                statut="termine",
                genere_par=get_user_id(current_user)
            )
            
            await db.exports_dinacope.insert_one(export.model_dump())
            
            return {
                "message": "Export généré avec succès",
                "export": export.model_dump(),
                "contenu": contenu
            }
    
    return {"message": "Type d'export non supporté"}
