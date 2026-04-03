"""
API Routes pour la gestion des Entités Externes
Permet de gérer les contacts externes (entreprises, ONG, citoyens, etc.)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone

from models import EntiteExterne, TypeEntiteExterne
from auth import get_current_user

router = APIRouter(prefix="/api/entites-externes", tags=["Entités Externes"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


@router.post("/")
async def creer_entite_externe(
    nom: str = Query(...),
    type_entite: str = Query(...),
    email: str = Query(default=None),
    telephone: str = Query(default=None),
    adresse: str = Query(default=None),
    ville: str = Query(default=None),
    province: str = Query(default=None),
    numero_identification: str = Query(default=None),
    secteur_activite: str = Query(default=None),
    description: str = Query(default=None),
    contact_principal_nom: str = Query(default=None),
    contact_principal_fonction: str = Query(default=None),
    contact_principal_email: str = Query(default=None),
    contact_principal_telephone: str = Query(default=None),
    est_partenaire: bool = Query(default=False),
    tags: List[str] = Query(default=[]),
    current_user: dict = Depends(get_current_user)
):
    """
    Créer une nouvelle entité externe
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Vérifier que le type est valide
    if type_entite not in [t.value for t in TypeEntiteExterne]:
        raise HTTPException(status_code=400, detail="Type d'entité invalide")
    
    # Vérifier que l'entité n'existe pas déjà (même nom + type)
    existing = await db.entites_externes.find_one({
        "nom": nom,
        "type_entite": type_entite,
        "est_actif": True
    }, {"_id": 0})
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Une entité '{nom}' de type '{type_entite}' existe déjà"
        )
    
    entite = EntiteExterne(
        nom=nom,
        type_entite=type_entite,
        email=email,
        telephone=telephone,
        adresse=adresse,
        ville=ville,
        province=province,
        numero_identification=numero_identification,
        secteur_activite=secteur_activite,
        description=description,
        contact_principal_nom=contact_principal_nom,
        contact_principal_fonction=contact_principal_fonction,
        contact_principal_email=contact_principal_email,
        contact_principal_telephone=contact_principal_telephone,
        est_partenaire=est_partenaire,
        tags=tags or [],
        createur_id=user_id,
        createur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}"
    )
    
    await db.entites_externes.insert_one(entite.model_dump())
    
    return {
        "message": "Entité externe créée avec succès",
        "entite": entite.model_dump()
    }


@router.get("/")
async def lister_entites_externes(
    type_entite: Optional[str] = None,
    est_partenaire: Optional[bool] = None,
    actif_seulement: bool = True,
    province: Optional[str] = None,
    q: Optional[str] = None,  # Recherche texte
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister les entités externes avec filtres
    """
    from dependencies import get_db

    db = get_db()
    
    filtre = {}
    
    if actif_seulement:
        filtre["est_actif"] = True
    
    if type_entite:
        filtre["type_entite"] = type_entite
    
    if est_partenaire is not None:
        filtre["est_partenaire"] = est_partenaire
    
    if province:
        filtre["province"] = province
    
    # Recherche textuelle
    if q:
        filtre["$or"] = [
            {"nom": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"secteur_activite": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}}
        ]
    
    entites = await db.entites_externes.find(filtre, {"_id": 0}).sort("nom", 1).to_list(limit)
    
    return {
        "total": len(entites),
        "entites": entites
    }


@router.get("/{entite_id}")
async def obtenir_entite_externe(
    entite_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir les détails d'une entité externe
    """
    from dependencies import get_db

    db = get_db()
    
    entite = await db.entites_externes.find_one({"id": entite_id}, {"_id": 0})
    if not entite:
        raise HTTPException(status_code=404, detail="Entité externe non trouvée")
    
    return entite


@router.put("/{entite_id}")
async def modifier_entite_externe(
    entite_id: str,
    nom: str = None,
    email: str = None,
    telephone: str = None,
    adresse: str = None,
    ville: str = None,
    province: str = None,
    numero_identification: str = None,
    secteur_activite: str = None,
    description: str = None,
    contact_principal_nom: str = None,
    contact_principal_fonction: str = None,
    contact_principal_email: str = None,
    contact_principal_telephone: str = None,
    est_partenaire: bool = None,
    tags: List[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Modifier une entité externe existante
    """
    from dependencies import get_db

    db = get_db()
    
    entite = await db.entites_externes.find_one({"id": entite_id}, {"_id": 0})
    if not entite:
        raise HTTPException(status_code=404, detail="Entité externe non trouvée")
    
    mises_a_jour = {}
    
    if nom is not None:
        mises_a_jour["nom"] = nom
    if email is not None:
        mises_a_jour["email"] = email
    if telephone is not None:
        mises_a_jour["telephone"] = telephone
    if adresse is not None:
        mises_a_jour["adresse"] = adresse
    if ville is not None:
        mises_a_jour["ville"] = ville
    if province is not None:
        mises_a_jour["province"] = province
    if numero_identification is not None:
        mises_a_jour["numero_identification"] = numero_identification
    if secteur_activite is not None:
        mises_a_jour["secteur_activite"] = secteur_activite
    if description is not None:
        mises_a_jour["description"] = description
    if contact_principal_nom is not None:
        mises_a_jour["contact_principal_nom"] = contact_principal_nom
    if contact_principal_fonction is not None:
        mises_a_jour["contact_principal_fonction"] = contact_principal_fonction
    if contact_principal_email is not None:
        mises_a_jour["contact_principal_email"] = contact_principal_email
    if contact_principal_telephone is not None:
        mises_a_jour["contact_principal_telephone"] = contact_principal_telephone
    if est_partenaire is not None:
        mises_a_jour["est_partenaire"] = est_partenaire
    if tags is not None:
        mises_a_jour["tags"] = tags
    
    if mises_a_jour:
        await db.entites_externes.update_one(
            {"id": entite_id},
            {"$set": mises_a_jour}
        )
    
    return {
        "message": "Entité externe modifiée avec succès",
        "entite_id": entite_id
    }


@router.post("/{entite_id}/desactiver")
async def desactiver_entite_externe(
    entite_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Désactiver une entité externe (soft delete)
    """
    from dependencies import get_db

    db = get_db()
    
    entite = await db.entites_externes.find_one({"id": entite_id}, {"_id": 0})
    if not entite:
        raise HTTPException(status_code=404, detail="Entité externe non trouvée")
    
    await db.entites_externes.update_one(
        {"id": entite_id},
        {"$set": {"est_actif": False}}
    )
    
    return {
        "message": "Entité externe désactivée",
        "entite_id": entite_id
    }


@router.post("/{entite_id}/interaction")
async def enregistrer_interaction(
    entite_id: str,
    type_interaction: str,  # "document_recu" ou "document_envoye"
    current_user: dict = Depends(get_current_user)
):
    """
    Enregistrer une interaction avec l'entité externe
    Appelé automatiquement lors de transmission/réception de documents
    """
    from dependencies import get_db

    db = get_db()
    
    entite = await db.entites_externes.find_one({"id": entite_id}, {"_id": 0})
    if not entite:
        raise HTTPException(status_code=404, detail="Entité externe non trouvée")
    
    champ_increment = "nombre_documents_recus" if type_interaction == "document_recu" else "nombre_documents_envoyes"
    
    await db.entites_externes.update_one(
        {"id": entite_id},
        {
            "$inc": {champ_increment: 1},
            "$set": {"derniere_interaction": datetime.now(timezone.utc)}
        }
    )
    
    return {
        "message": "Interaction enregistrée",
        "entite_id": entite_id
    }


@router.get("/stats/partenaires")
async def statistiques_partenaires(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques sur les partenaires et entités externes
    """
    from dependencies import get_db

    db = get_db()
    
    # Compter par type
    stats_par_type = {}
    for type_entite in TypeEntiteExterne:
        count = await db.entites_externes.count_documents({
            "type_entite": type_entite.value,
            "est_actif": True
        })
        stats_par_type[type_entite.value] = count
    
    # Partenaires actifs
    partenaires = await db.entites_externes.count_documents({
        "est_partenaire": True,
        "est_actif": True
    })
    
    # Top 10 des entités avec le plus d'interactions
    top_entites = await db.entites_externes.find(
        {"est_actif": True},
        {"_id": 0, "nom": 1, "type_entite": 1, "nombre_documents_recus": 1, "nombre_documents_envoyes": 1}
    ).sort([
        ("nombre_documents_recus", -1),
        ("nombre_documents_envoyes", -1)
    ]).to_list(10)
    
    return {
        "total_actif": sum(stats_par_type.values()),
        "par_type": stats_par_type,
        "partenaires": partenaires,
        "top_interactions": top_entites
    }
