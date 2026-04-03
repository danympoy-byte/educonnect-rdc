"""
API Routes pour la gestion des listes d'utilisateurs (Distribution, Attribution, E-signataires)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone

from models import ListeUtilisateurs, TypeListe
from auth import get_current_user

router = APIRouter(prefix="/api/listes", tags=["Listes"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


@router.post("/")
async def creer_liste(
    nom: str = Query(...),
    type_liste: str = Query(...),
    user_ids: List[str] = Query(default=[]),
    description: str = Query(default=None),
    est_publique: bool = Query(default=True),
    service_id: str = Query(default=None),
    current_user: dict = Depends(get_current_user)
):
    """
    Créer une nouvelle liste d'utilisateurs
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Vérifier que le type de liste est valide
    if type_liste not in [t.value for t in TypeListe]:
        raise HTTPException(status_code=400, detail="Type de liste invalide")
    
    # Récupérer les noms des utilisateurs
    user_noms = []
    for uid in user_ids:
        user = await db.users.find_one({"id": uid}, {"_id": 0})
        if user:
            user_noms.append(f"{user.get('prenom', '')} {user.get('nom', '')}")
        else:
            user_noms.append(f"Utilisateur inconnu ({uid})")
    
    # Créer la liste
    liste = ListeUtilisateurs(
        nom=nom,
        description=description,
        type_liste=type_liste,
        user_ids=user_ids,
        user_noms=user_noms,
        createur_id=user_id,
        createur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        est_publique=est_publique,
        service_id=service_id
    )
    
    await db.listes_utilisateurs.insert_one(liste.model_dump())
    
    return {
        "message": "Liste créée avec succès",
        "liste": liste.model_dump()
    }


@router.get("/")
async def lister_listes(
    type_liste: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lister les listes accessibles par l'utilisateur
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Construire le filtre
    filtre = {
        "$or": [
            {"est_publique": True},
            {"createur_id": user_id}
        ]
    }
    
    if type_liste:
        filtre["type_liste"] = type_liste
    
    listes = await db.listes_utilisateurs.find(filtre, {"_id": 0}).to_list(1000)
    
    return {
        "total": len(listes),
        "listes": listes
    }


@router.get("/{liste_id}")
async def obtenir_liste(
    liste_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir les détails d'une liste
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    liste = await db.listes_utilisateurs.find_one({"id": liste_id}, {"_id": 0})
    if not liste:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    
    # Vérifier l'accès
    if not liste.get("est_publique") and liste.get("createur_id") != user_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette liste")
    
    return liste


@router.put("/{liste_id}")
async def modifier_liste(
    liste_id: str,
    nom: str = None,
    description: str = None,
    user_ids: List[str] = None,
    est_publique: bool = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Modifier une liste existante
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    liste = await db.listes_utilisateurs.find_one({"id": liste_id}, {"_id": 0})
    if not liste:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    
    # Seul le créateur peut modifier
    if liste.get("createur_id") != user_id:
        raise HTTPException(status_code=403, detail="Seul le créateur peut modifier cette liste")
    
    # Construire les mises à jour
    mises_a_jour = {
        "date_modification": datetime.now(timezone.utc)
    }
    
    if nom is not None:
        mises_a_jour["nom"] = nom
    if description is not None:
        mises_a_jour["description"] = description
    if est_publique is not None:
        mises_a_jour["est_publique"] = est_publique
    
    if user_ids is not None:
        # Récupérer les nouveaux noms
        user_noms = []
        for uid in user_ids:
            user = await db.users.find_one({"id": uid}, {"_id": 0})
            if user:
                user_noms.append(f"{user.get('prenom', '')} {user.get('nom', '')}")
            else:
                user_noms.append(f"Utilisateur inconnu ({uid})")
        
        mises_a_jour["user_ids"] = user_ids
        mises_a_jour["user_noms"] = user_noms
    
    await db.listes_utilisateurs.update_one(
        {"id": liste_id},
        {"$set": mises_a_jour}
    )
    
    return {
        "message": "Liste modifiée avec succès",
        "liste_id": liste_id
    }


@router.delete("/{liste_id}")
async def supprimer_liste(
    liste_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer une liste
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    liste = await db.listes_utilisateurs.find_one({"id": liste_id}, {"_id": 0})
    if not liste:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    
    # Seul le créateur ou un admin peut supprimer
    user_role = current_user.get("role")
    peut_supprimer = (
        liste.get("createur_id") == user_id or
        user_role == "ministre"
    )
    
    if not peut_supprimer:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits pour supprimer cette liste")
    
    await db.listes_utilisateurs.delete_one({"id": liste_id})
    
    return {
        "message": "Liste supprimée avec succès",
        "liste_id": liste_id
    }


@router.post("/{liste_id}/utiliser")
async def incrementer_utilisation(
    liste_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Incrémenter le compteur d'utilisation d'une liste
    Appelé automatiquement quand la liste est utilisée
    """
    from dependencies import get_db

    db = get_db()
    
    liste = await db.listes_utilisateurs.find_one({"id": liste_id}, {"_id": 0})
    if not liste:
        raise HTTPException(status_code=404, detail="Liste non trouvée")
    
    await db.listes_utilisateurs.update_one(
        {"id": liste_id},
        {"$inc": {"nombre_utilisations": 1}}
    )
    
    return {
        "message": "Utilisation enregistrée",
        "liste_id": liste_id
    }
