"""
Routes pour la gestion des clés API
Permet aux administrateurs de générer, lister, et révoquer des clés API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List
import os

from models import APIKey, APIKeyCreate, APIKeyResponse, APIKeyInfo
from auth import get_current_user, require_role
from auth_api_key import generate_api_key, hash_api_key

# Router
router = APIRouter(prefix="/api/api-keys", tags=["API Keys"])

# MongoDB connection
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


@router.post(
    "/generate",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer une nouvelle clé API",
    description="""
    Génère une nouvelle clé API pour l'authentification externe.
    
    ⚠️ **IMPORTANT** : La clé complète est retournée **UNE SEULE FOIS** dans cette réponse.
    Vous devez la sauvegarder immédiatement, elle ne sera plus jamais affichée.
    
    **Permissions disponibles par module** :
    - `read` : Lecture seule
    - `write` : Lecture + Écriture
    - `admin` : Tous les droits
    
    **Modules disponibles** :
    - `documents` : Gestion électronique des documents (GED)
    - `enseignants` : Gestion des enseignants (SIRH)
    - `eleves` : Gestion des élèves
    - `etablissements` : Gestion des établissements
    - `stats` : Statistiques et tableaux de bord
    - `rapports` : Rapports et exports
    - `dinacope` : Contrôles DINACOPE
    - `provinces` : Gestion des provinces
    - `classes` : Gestion des classes
    - `presences` : Gestion des présences
    
    **Exemple de permissions** :
    ```json
    {
      "documents": "read",
      "enseignants": "write",
      "stats": "read"
    }
    ```
    """,
    responses={
        201: {
            "description": "Clé API créée avec succès",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Application Mobile RDC",
                        "key": "educon_abc123xyz789...",
                        "key_prefix": "educon_abc123...",
                        "permissions": {"documents": "read", "enseignants": "write"},
                        "created_at": "2026-03-31T12:00:00Z",
                        "expires_at": "2027-03-31T12:00:00Z",
                        "description": "Clé pour l'application mobile du personnel"
                    }
                }
            }
        },
        403: {"description": "Accès refusé - Réservé aux administrateurs"}
    }
)
async def generate_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Génère une nouvelle clé API avec les permissions spécifiées.
    Réservé aux administrateurs.
    """
    # Vérification des permissions - IDs autorisés
    allowed_user_ids = ["ministre_001", "secretaire_general_001", "dg_admin_001"]
    if current_user.get("sub") not in allowed_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé. Fonctionnalité réservée aux hauts responsables (Ministre, SG, DG)."
        )
    
    # Générer la clé
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    key_prefix = api_key[:20] + "..."  # educon_abc123...
    
    # Calculer la date d'expiration si demandée
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_in_days)
    
    # Créer le document
    api_key_doc = APIKey(
        name=key_data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        permissions=key_data.permissions,
        created_by=current_user["sub"],
        expires_at=expires_at,
        description=key_data.description,
        ip_whitelist=key_data.ip_whitelist
    )
    
    # Sauvegarder dans MongoDB
    doc = api_key_doc.model_dump()
    if doc.get("expires_at"):
        doc["expires_at"] = doc["expires_at"].isoformat()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.api_keys.insert_one(doc)
    
    # Retourner la réponse avec la clé en clair (une seule fois)
    return APIKeyResponse(
        id=api_key_doc.id,
        name=api_key_doc.name,
        key=api_key,  # ⚠️ Clé en clair - une seule fois
        key_prefix=key_prefix,
        permissions=key_data.permissions,
        created_at=api_key_doc.created_at,
        expires_at=expires_at,
        description=key_data.description
    )


@router.get(
    "",
    response_model=List[APIKeyInfo],
    summary="Lister mes clés API",
    description="Récupère la liste de toutes les clés API créées par l'utilisateur connecté."
)
async def list_api_keys(
    current_user: dict = Depends(get_current_user)
):
    """
    Liste toutes les clés API de l'utilisateur connecté.
    """
    keys = await db.api_keys.find(
        {"created_by": current_user["sub"]},
        {"_id": 0, "key_hash": 0}  # Ne pas exposer le hash
    ).to_list(100)
    
    return keys


@router.get(
    "/{key_id}",
    response_model=APIKeyInfo,
    summary="Détails d'une clé API",
    description="Récupère les détails d'une clé API spécifique."
)
async def get_api_key_details(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les détails d'une clé API.
    """
    key = await db.api_keys.find_one(
        {"id": key_id, "created_by": current_user["sub"]},
        {"_id": 0, "key_hash": 0}
    )
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clé API introuvable."
        )
    
    return key


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_200_OK,
    summary="Révoquer une clé API",
    description="Révoque une clé API (la désactive définitivement)."
)
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Révoque (désactive) une clé API.
    """
    result = await db.api_keys.update_one(
        {"id": key_id, "created_by": current_user["sub"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clé API introuvable."
        )
    
    return {"message": "Clé API révoquée avec succès."}


@router.put(
    "/{key_id}/permissions",
    response_model=APIKeyInfo,
    summary="Modifier les permissions d'une clé API",
    description="Met à jour les permissions d'une clé API existante."
)
async def update_api_key_permissions(
    key_id: str,
    permissions: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Modifie les permissions d'une clé API existante.
    """
    result = await db.api_keys.update_one(
        {"id": key_id, "created_by": current_user["sub"]},
        {"$set": {"permissions": permissions}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clé API introuvable."
        )
    
    # Récupérer la clé mise à jour
    updated_key = await db.api_keys.find_one(
        {"id": key_id},
        {"_id": 0, "key_hash": 0}
    )
    
    return updated_key


@router.get(
    "/stats/usage",
    summary="Statistiques d'utilisation des clés API",
    description="Récupère les statistiques d'utilisation de toutes les clés API de l'utilisateur."
)
async def get_api_keys_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les statistiques d'utilisation des clés API.
    """
    keys = await db.api_keys.find(
        {"created_by": current_user["sub"]},
        {"_id": 0}
    ).to_list(100)
    
    total_keys = len(keys)
    active_keys = len([k for k in keys if k.get("is_active", False)])
    total_usage = sum(k.get("usage_count", 0) for k in keys)
    
    return {
        "total_keys": total_keys,
        "active_keys": active_keys,
        "revoked_keys": total_keys - active_keys,
        "total_api_calls": total_usage,
        "keys": keys
    }
