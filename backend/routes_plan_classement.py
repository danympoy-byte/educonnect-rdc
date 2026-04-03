"""
API Routes pour le Plan de Classement Hiérarchique
Permet d'organiser les documents selon la structure gouvernementale DRC
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone

from models import PlanClassement
from auth import get_current_user

router = APIRouter(prefix="/api/plan-classement", tags=["Plan de Classement"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


@router.post("/")
async def creer_plan_classement(
    code: str,
    nom: str,
    description: str = None,
    parent_id: str = None,
    duree_conservation_mois: int = None,
    types_documents_acceptes: List[str] = None,
    icone: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un nouveau nœud dans le plan de classement
    Réservé aux administrateurs
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    user_role = current_user.get("role")
    
    # Vérifier les droits (seuls les admins)
    if user_role not in ["ministre", "secretaire_general"]:
        raise HTTPException(
            status_code=403,
            detail="Seuls les administrateurs peuvent créer des plans de classement"
        )
    
    # Vérifier que le code n'existe pas déjà
    existing = await db.plan_classement.find_one({"code": code}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail=f"Le code {code} existe déjà")
    
    # Construire le chemin et le niveau
    niveau = 1
    chemin_complet = nom
    
    if parent_id:
        parent = await db.plan_classement.find_one({"id": parent_id}, {"_id": 0})
        if not parent:
            raise HTTPException(status_code=404, detail="Plan parent non trouvé")
        
        niveau = parent["niveau"] + 1
        chemin_complet = f"{parent['chemin_complet']} > {nom}"
    
    # Créer le plan
    plan = PlanClassement(
        code=code,
        nom=nom,
        description=description,
        niveau=niveau,
        parent_id=parent_id,
        chemin_complet=chemin_complet,
        duree_conservation_mois=duree_conservation_mois,
        types_documents_acceptes=types_documents_acceptes or [],
        icone=icone,
        createur_id=user_id
    )
    
    await db.plan_classement.insert_one(plan.model_dump())
    
    return {
        "message": "Plan de classement créé avec succès",
        "plan": plan.model_dump()
    }


@router.get("/")
async def lister_plans_classement(
    parent_id: Optional[str] = None,
    niveau: Optional[int] = None,
    actif_seulement: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister les plans de classement
    Si parent_id est fourni, liste les enfants de ce parent
    Si niveau est fourni, liste les plans de ce niveau
    """
    from dependencies import get_db

    db = get_db()
    
    filtre = {}
    
    if actif_seulement:
        filtre["est_actif"] = True
    
    if parent_id:
        filtre["parent_id"] = parent_id
    elif niveau:
        filtre["niveau"] = niveau
    
    plans = await db.plan_classement.find(filtre, {"_id": 0}).sort("ordre_affichage", 1).to_list(1000)
    
    return {
        "total": len(plans),
        "plans": plans
    }


@router.get("/arborescence")
async def obtenir_arborescence_complete(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir l'arborescence complète du plan de classement sous forme hiérarchique
    """
    from dependencies import get_db

    db = get_db()
    
    # Récupérer tous les plans actifs
    tous_plans = await db.plan_classement.find(
        {"est_actif": True}, 
        {"_id": 0}
    ).sort("ordre_affichage", 1).to_list(1000)
    
    # Construire l'arborescence
    def construire_arbre(parent_id=None):
        enfants = [p for p in tous_plans if p.get("parent_id") == parent_id]
        arbre = []
        for enfant in enfants:
            noeud = {
                **enfant,
                "enfants": construire_arbre(enfant["id"])
            }
            arbre.append(noeud)
        return arbre
    
    arborescence = construire_arbre(None)
    
    return {
        "total_noeuds": len(tous_plans),
        "arborescence": arborescence
    }


@router.get("/{plan_id}")
async def obtenir_plan_classement(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir les détails d'un plan de classement
    """
    from dependencies import get_db

    db = get_db()
    
    plan = await db.plan_classement.find_one({"id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de classement non trouvé")
    
    # Récupérer les enfants
    enfants = await db.plan_classement.find(
        {"parent_id": plan_id, "est_actif": True},
        {"_id": 0}
    ).sort("ordre_affichage", 1).to_list(100)
    
    return {
        **plan,
        "enfants": enfants
    }


@router.put("/{plan_id}")
async def modifier_plan_classement(
    plan_id: str,
    nom: str = None,
    description: str = None,
    duree_conservation_mois: int = None,
    types_documents_acceptes: List[str] = None,
    icone: str = None,
    ordre_affichage: int = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Modifier un plan de classement existant
    """
    from dependencies import get_db

    db = get_db()
    
    user_role = current_user.get("role")
    
    if user_role not in ["ministre", "secretaire_general"]:
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    
    plan = await db.plan_classement.find_one({"id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de classement non trouvé")
    
    mises_a_jour = {}
    
    if nom is not None:
        mises_a_jour["nom"] = nom
        # Recalculer le chemin complet
        if plan.get("parent_id"):
            parent = await db.plan_classement.find_one({"id": plan["parent_id"]}, {"_id": 0})
            if parent:
                mises_a_jour["chemin_complet"] = f"{parent['chemin_complet']} > {nom}"
        else:
            mises_a_jour["chemin_complet"] = nom
    
    if description is not None:
        mises_a_jour["description"] = description
    if duree_conservation_mois is not None:
        mises_a_jour["duree_conservation_mois"] = duree_conservation_mois
    if types_documents_acceptes is not None:
        mises_a_jour["types_documents_acceptes"] = types_documents_acceptes
    if icone is not None:
        mises_a_jour["icone"] = icone
    if ordre_affichage is not None:
        mises_a_jour["ordre_affichage"] = ordre_affichage
    
    if mises_a_jour:
        await db.plan_classement.update_one(
            {"id": plan_id},
            {"$set": mises_a_jour}
        )
    
    return {
        "message": "Plan de classement modifié avec succès",
        "plan_id": plan_id
    }


@router.post("/{plan_id}/desactiver")
async def desactiver_plan_classement(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Désactiver un plan de classement (ne le supprime pas, le masque)
    """
    from dependencies import get_db

    db = get_db()
    
    user_role = current_user.get("role")
    
    if user_role not in ["ministre", "secretaire_general"]:
        raise HTTPException(status_code=403, detail="Droits insuffisants")
    
    plan = await db.plan_classement.find_one({"id": plan_id}, {"_id": 0})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de classement non trouvé")
    
    await db.plan_classement.update_one(
        {"id": plan_id},
        {"$set": {"est_actif": False}}
    )
    
    return {
        "message": "Plan de classement désactivé",
        "plan_id": plan_id
    }


@router.post("/initialiser-drc")
async def initialiser_plan_classement_drc(
    current_user: dict = Depends(get_current_user)
):
    """
    Initialiser le plan de classement avec la structure standard DRC
    À n'utiliser qu'une seule fois lors de la configuration initiale
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    user_role = current_user.get("role")
    
    if user_role != "ministre":
        raise HTTPException(status_code=403, detail="Réservé au Ministre")
    
    # Vérifier si déjà initialisé
    existing = await db.plan_classement.count_documents({})
    if existing > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Plan de classement déjà initialisé ({existing} entrées). Utilisez les endpoints CRUD pour modifier."
        )
    
    # Structure standard DRC MINEPST
    structure = [
        {"code": "ADM", "nom": "Administration", "niveau": 1, "icone": "🏛️", "ordre": 1},
        {"code": "ADM.FIN", "nom": "Finances et Comptabilité", "niveau": 2, "parent": "ADM", "icone": "💰", "ordre": 1},
        {"code": "ADM.RH", "nom": "Ressources Humaines", "niveau": 2, "parent": "ADM", "icone": "👥", "ordre": 2},
        {"code": "ADM.LOG", "nom": "Logistique", "niveau": 2, "parent": "ADM", "icone": "📦", "ordre": 3},
        
        {"code": "PED", "nom": "Pédagogie", "niveau": 1, "icone": "📚", "ordre": 2},
        {"code": "PED.PROG", "nom": "Programmes Scolaires", "niveau": 2, "parent": "PED", "icone": "📖", "ordre": 1},
        {"code": "PED.EXAM", "nom": "Examens et Évaluations", "niveau": 2, "parent": "PED", "icone": "✍️", "ordre": 2},
        {"code": "PED.FORM", "nom": "Formation Continue", "niveau": 2, "parent": "PED", "icone": "🎓", "ordre": 3},
        
        {"code": "INF", "nom": "Infrastructure", "niveau": 1, "icone": "🏗️", "ordre": 3},
        {"code": "INF.CONST", "nom": "Construction et Rénovation", "niveau": 2, "parent": "INF", "icone": "🔨", "ordre": 1},
        {"code": "INF.MAINT", "nom": "Maintenance", "niveau": 2, "parent": "INF", "icone": "🔧", "ordre": 2},
        
        {"code": "JUR", "nom": "Juridique", "niveau": 1, "icone": "⚖️", "ordre": 4},
        {"code": "JUR.REG", "nom": "Réglementation", "niveau": 2, "parent": "JUR", "icone": "📜", "ordre": 1},
        {"code": "JUR.CONT", "nom": "Contentieux", "niveau": 2, "parent": "JUR", "icone": "⚠️", "ordre": 2},
    ]
    
    # Créer les plans
    plans_crees = {}
    
    for item in structure:
        parent_id = None
        chemin = item["nom"]
        
        if "parent" in item:
            parent_code = item["parent"]
            if parent_code in plans_crees:
                parent_id = plans_crees[parent_code]["id"]
                chemin = f"{plans_crees[parent_code]['chemin_complet']} > {item['nom']}"
        
        plan = PlanClassement(
            code=item["code"],
            nom=item["nom"],
            niveau=item["niveau"],
            parent_id=parent_id,
            chemin_complet=chemin,
            icone=item.get("icone"),
            ordre_affichage=item.get("ordre", 0),
            createur_id=user_id
        )
        
        await db.plan_classement.insert_one(plan.model_dump())
        plans_crees[item["code"]] = {
            "id": plan.id,
            "chemin_complet": chemin
        }
    
    return {
        "message": "Plan de classement DRC initialisé avec succès",
        "total_cree": len(structure),
        "structure": structure
    }
