"""
API Routes pour l'environnement double zone (Personnel vs Équipe)
Permet aux utilisateurs de basculer entre leur espace personnel et l'espace d'équipe
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

from auth import get_current_user

router = APIRouter(prefix="/api/contexte", tags=["Contexte de Travail"])


class ContexteSwitch(BaseModel):
    nouveau_contexte: str


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


@router.get("/")
async def obtenir_contexte_actuel(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir le contexte de travail actuel de l'utilisateur
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Récupérer le contexte depuis la session utilisateur
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    contexte = user.get("contexte_travail", "personnel")  # Défaut: personnel
    
    return {
        "contexte_actuel": contexte,
        "user_id": user_id,
        "contextes_disponibles": [
            {
                "id": "personnel",
                "nom": "Zone Bleue - Personnel",
                "description": "Documents et tâches personnels",
                "icone": "👤",
                "couleur": "#3B82F6"  # Bleu
            },
            {
                "id": "equipe",
                "nom": "Zone Verte - Équipe",
                "description": "Documents et tâches de l'équipe/service",
                "icone": "👥",
                "couleur": "#10B981"  # Vert
            }
        ]
    }


@router.post("/basculer")
async def basculer_contexte(
    data: ContexteSwitch,
    current_user: dict = Depends(get_current_user)
):
    """
    Basculer entre le contexte personnel et équipe
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    if data.nouveau_contexte not in ["personnel", "equipe"]:
        raise HTTPException(
            status_code=400,
            detail="Contexte invalide. Utilisez 'personnel' ou 'equipe'"
        )
    
    # Mettre à jour le contexte de l'utilisateur
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"contexte_travail": data.nouveau_contexte}}
    )
    
    return {
        "message": f"Contexte basculé vers '{data.nouveau_contexte}'",
        "contexte_actuel": data.nouveau_contexte,
        "zone_affichage": "Zone Bleue - Personnel" if data.nouveau_contexte == "personnel" else "Zone Verte - Équipe"
    }


@router.get("/documents")
async def lister_documents_par_contexte(
    contexte: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister les documents selon le contexte de travail
    
    - Personnel (Zone Bleue): Documents créés par moi, en attente de ma validation
    - Équipe (Zone Verte): Documents partagés avec l'équipe, niveau diffusion service
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Si contexte non spécifié, utiliser le contexte actuel de l'utilisateur
    if not contexte:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        contexte = user.get("contexte_travail", "personnel")
    
    if contexte not in ["personnel", "equipe"]:
        raise HTTPException(status_code=400, detail="Contexte invalide")
    
    filtre = {}
    
    if contexte == "personnel":
        # Zone Bleue - Documents personnels
        filtre["$or"] = [
            {"createur_id": user_id},
            {"proprietaire_actuel_id": user_id},
            {"circuit_validation": user_id}
        ]
    
    elif contexte == "equipe":
        # Zone Verte - Documents de l'équipe
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        service_profiles = user.get("service_profiles", [])
        
        if service_profiles:
            # Récupérer tous les services de l'utilisateur
            service_ids = [sp.get("service_id") for sp in service_profiles if sp.get("service_id")]
            
            filtre["$or"] = [
                {"niveau_diffusion": "service"},
                {"createur_service_id": {"$in": service_ids}},
                {"destinataire_service_id": {"$in": service_ids}},
                {"collaborateurs_ids": {"$exists": True, "$ne": []}}
            ]
        else:
            # Pas de service - retourner documents publics
            filtre["niveau_diffusion"] = "public"
    
    documents = await db.documents.find(
        filtre,
        {"_id": 0}
    ).sort("date_creation", -1).to_list(limit)
    
    return {
        "contexte": contexte,
        "zone": "Zone Bleue - Personnel" if contexte == "personnel" else "Zone Verte - Équipe",
        "total": len(documents),
        "documents": documents
    }


@router.get("/statistiques")
async def statistiques_par_contexte(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques des documents par contexte (Personnel vs Équipe)
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Zone Bleue - Personnel
    docs_personnels = await db.documents.count_documents({
        "$or": [
            {"createur_id": user_id},
            {"proprietaire_actuel_id": user_id},
            {"circuit_validation": user_id}
        ]
    })
    
    # Tâches en attente personnelles
    taches_personnelles = await db.documents.count_documents({
        "proprietaire_actuel_id": user_id,
        "statut": {"$in": ["en_attente", "brouillon"]}
    })
    
    # Zone Verte - Équipe
    service_profiles = user.get("service_profiles", [])
    service_ids = [sp.get("service_id") for sp in service_profiles if sp.get("service_id")]
    
    docs_equipe = 0
    if service_ids:
        docs_equipe = await db.documents.count_documents({
            "$or": [
                {"niveau_diffusion": "service"},
                {"createur_service_id": {"$in": service_ids}},
                {"destinataire_service_id": {"$in": service_ids}}
            ]
        })
    
    # Contexte actuel
    contexte_actuel = user.get("contexte_travail", "personnel")
    
    return {
        "contexte_actuel": contexte_actuel,
        "zone_bleue_personnel": {
            "total_documents": docs_personnels,
            "taches_en_attente": taches_personnelles,
            "description": "Mes documents et tâches personnels"
        },
        "zone_verte_equipe": {
            "total_documents": docs_equipe,
            "services_count": len(service_ids),
            "description": "Documents partagés avec mon équipe"
        },
        "recommandation": "Zone Verte" if docs_equipe > docs_personnels else "Zone Bleue"
    }


@router.get("/conversations")
async def lister_conversations_par_contexte(
    contexte: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister les conversations selon le contexte
    
    - Personnel: Conversations 1-to-1
    - Équipe: Conversations de groupe/service
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    if not contexte:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        contexte = user.get("contexte_travail", "personnel")
    
    if contexte not in ["personnel", "equipe"]:
        raise HTTPException(status_code=400, detail="Contexte invalide")
    
    filtre = {
        "$or": [
            {"user_id": user_id},
            {"destinataire_id": user_id}
        ]
    }
    
    if contexte == "equipe":
        # Uniquement les conversations avec plusieurs participants ou niveau service
        filtre["$and"] = [
            filtre,
            {
                "$or": [
                    {"est_groupe": True},
                    {"niveau": "service"}
                ]
            }
        ]
    else:
        # Personnel - conversations 1-to-1
        filtre["est_groupe"] = {"$ne": True}
    
    conversations = await db.conversations.find(
        filtre,
        {"_id": 0}
    ).sort("date_dernier_message", -1).to_list(limit)
    
    return {
        "contexte": contexte,
        "zone": "Zone Bleue - Personnel" if contexte == "personnel" else "Zone Verte - Équipe",
        "total": len(conversations),
        "conversations": conversations
    }
