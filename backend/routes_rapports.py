"""
API Routes pour les Rapports Trimestriels GED
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from auth import get_current_user
from dependencies import get_db

router = APIRouter(prefix="/api/rapports", tags=["Rapports Trimestriels"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("user_id", user.get("id", ""))


@router.get("/")
async def lister_rapports_trimestriels(
    annee: int = Query(None, description="Filtrer par année"),
    current_user: dict = Depends(get_current_user)
):
    """Lister tous les rapports trimestriels générés"""
    db = get_db()
    
    # Seuls les décideurs peuvent consulter les rapports
    if current_user["role"] not in ["ministre", "secretaire_general", "directeur_provincial", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux décideurs")
    
    filtre = {}
    if annee:
        filtre["annee"] = annee
    
    rapports = await db.rapports_trimestriels.find(
        filtre,
        {"_id": 0}
    ).sort([("annee", -1), ("trimestre", -1)]).to_list(100)
    
    return {
        "total": len(rapports),
        "rapports": rapports
    }


@router.get("/{rapport_id}")
async def obtenir_rapport_detaille(
    rapport_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les détails d'un rapport trimestriel"""
    db = get_db()
    
    # Seuls les décideurs peuvent consulter les rapports
    if current_user["role"] not in ["ministre", "secretaire_general", "directeur_provincial", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux décideurs")
    
    rapport = await db.rapports_trimestriels.find_one({"id": rapport_id}, {"_id": 0})
    
    if not rapport:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    
    return rapport


@router.post("/generer")
async def generer_rapport_manuel(
    trimestre: int = Query(..., ge=1, le=4, description="Numéro du trimestre (1-4)"),
    annee: int = Query(..., ge=2020, description="Année"),
    current_user: dict = Depends(get_current_user)
):
    """Générer manuellement un rapport trimestriel (pour test ou rattrapage)"""
    from generer_rapport_trimestriel import generer_rapport_trimestriel
    
    # Seuls les administrateurs peuvent générer manuellement
    if current_user["role"] not in ["ministre", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    
    user_id = get_user_id(current_user)
    
    try:
        rapport = await generer_rapport_trimestriel(trimestre, annee, genere_par=user_id)
        return {
            "message": f"Rapport T{trimestre} {annee} généré avec succès",
            "rapport": rapport
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération rapport: {str(e)}")
