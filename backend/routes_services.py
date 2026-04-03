"""
Routes pour la gestion des services et organigramme
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models import Service, ServiceCreate, NiveauService
from auth import get_current_user

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/all", response_model=List[Service])
async def get_all_services(current_user: dict = Depends(get_current_user)):
    """Récupérer tous les services"""
    from dependencies import get_db

    db = get_db()
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    return services


@router.get("/niveau/{niveau}", response_model=List[Service])
async def get_services_by_niveau(
    niveau: NiveauService,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les services d'un niveau hiérarchique donné"""
    from dependencies import get_db

    db = get_db()
    services = await db.services.find(
        {"niveau": niveau.value},
        {"_id": 0}
    ).to_list(1000)
    return services


@router.get("/parent/{parent_id}", response_model=List[Service])
async def get_services_by_parent(
    parent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les services enfants d'un service parent"""
    from dependencies import get_db

    db = get_db()
    services = await db.services.find(
        {"parent_id": parent_id},
        {"_id": 0}
    ).to_list(1000)
    return services


@router.get("/hierarchie/{service_id}")
async def get_service_hierarchy(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer la hiérarchie complète d'un service (de lui jusqu'au Ministre)
    Utile pour générer le circuit de validation
    """
    from dependencies import get_db

    db = get_db()
    
    hierarchy = []
    current_service_id = service_id
    
    # Remonter la hiérarchie jusqu'au Ministre
    while current_service_id:
        service = await db.services.find_one({"id": current_service_id}, {"_id": 0})
        if not service:
            break
        
        hierarchy.append(service)
        current_service_id = service.get("parent_id")
    
    return {
        "service_depart": hierarchy[0] if hierarchy else None,
        "hierarchie": hierarchy,  # De bas en haut (service → ... → Ministre)
        "nombre_niveaux": len(hierarchy)
    }


@router.get("/enfants-recursif/{service_id}")
async def get_service_children_recursive(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer tous les services enfants (récursif)
    Utile pour afficher l'organigramme complet sous un service
    """
    from dependencies import get_db

    db = get_db()
    
    async def get_children(parent_id: str):
        """Fonction récursive pour obtenir tous les enfants"""
        children = await db.services.find({"parent_id": parent_id}, {"_id": 0}).to_list(1000)
        
        for child in children:
            child["enfants"] = await get_children(child["id"])
        
        return children
    
    # Récupérer le service de départ
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    
    # Ajouter ses enfants récursivement
    service["enfants"] = await get_children(service_id)
    
    return service


@router.get("/dropdown-cascade")
async def get_services_for_dropdown():
    """
    Récupérer les services organisés pour une liste déroulante en cascade (3 niveaux)
    Format: Niveau 3 (DG) → Niveau 4 (Directions) → Niveau 5 (Services)
    
    ⚠️ Endpoint public (utilisé pour l'inscription)
    """
    from dependencies import get_db

    db = get_db()
    
    # Récupérer les DG (Niveau 3)
    dg_list = await db.services.find(
        {"niveau": "niveau_3"},
        {"_id": 0}
    ).sort("nom", 1).to_list(100)
    
    result = []
    for dg in dg_list:
        # Récupérer les directions (Niveau 4) sous cette DG
        directions = await db.services.find(
            {"parent_id": dg["id"], "niveau": "niveau_4"},
            {"_id": 0}
        ).sort("nom", 1).to_list(100)
        
        directions_with_services = []
        for direction in directions:
            # Récupérer les services (Niveau 5) sous cette direction
            services = await db.services.find(
                {"parent_id": direction["id"], "niveau": "niveau_5"},
                {"_id": 0}
            ).sort("nom", 1).to_list(100)
            
            directions_with_services.append({
                **direction,
                "services": services
            })
        
        result.append({
            **dg,
            "directions": directions_with_services
        })
    
    return result


@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer un service par son ID"""
    from dependencies import get_db

    db = get_db()
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service non trouvé")
    return service


@router.post("/", response_model=Service)
async def create_service(
    service: ServiceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau service (Admin uniquement)"""
    from dependencies import get_db

    db = get_db()
    
    new_service = Service(**service.model_dump())
    await db.services.insert_one(new_service.model_dump())
    return new_service
