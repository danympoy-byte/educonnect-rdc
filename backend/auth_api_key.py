"""
Authentification par clé API pour les développeurs externes
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import hashlib
import secrets

# Security scheme pour les clés API
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_api_key(key: str) -> str:
    """Hash une clé API pour stockage sécurisé"""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> str:
    """Génère une clé API sécurisée"""
    # Format: educon_[32 caractères alphanumériques]
    random_part = secrets.token_urlsafe(32)
    return f"educon_{random_part}"


async def get_api_key_from_header(
    api_key: str = Security(api_key_header),
    db = None
) -> dict:
    """
    Valide une clé API depuis le header X-API-Key
    Retourne les informations de la clé si valide
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante. Fournissez une clé via le header 'X-API-Key'."
        )
    
    # Hash la clé pour la comparer avec la DB
    key_hash = hash_api_key(api_key)
    
    # Recherche dans la DB
    api_key_doc = await db.api_keys.find_one(
        {"key_hash": key_hash, "is_active": True},
        {"_id": 0}
    )
    
    if not api_key_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou révoquée."
        )
    
    # Vérifier l'expiration
    if api_key_doc.get("expires_at"):
        expires_at = api_key_doc["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clé API expirée."
            )
    
    # Mettre à jour last_used_at et usage_count
    await db.api_keys.update_one(
        {"id": api_key_doc["id"]},
        {
            "$set": {"last_used_at": datetime.now(timezone.utc).isoformat()},
            "$inc": {"usage_count": 1}
        }
    )
    
    return api_key_doc


def check_permission(api_key_doc: dict, module: str, permission: str) -> bool:
    """
    Vérifie si une clé API a la permission requise sur un module
    
    Args:
        api_key_doc: Document de la clé API
        module: Nom du module (ex: "documents", "enseignants")
        permission: Permission requise ("read" ou "write")
    
    Returns:
        True si la permission est accordée, False sinon
    """
    permissions = api_key_doc.get("permissions", {})
    
    # Si la clé a permission "admin", elle a tous les droits
    if permissions.get(module) == "admin":
        return True
    
    # Si demande de lecture et clé a "write", c'est OK
    if permission == "read" and permissions.get(module) in ["read", "write", "admin"]:
        return True
    
    # Sinon, vérification exacte
    return permissions.get(module) == permission


async def require_api_permission(
    module: str,
    permission: str = "read"
):
    """
    Dépendance FastAPI pour vérifier les permissions d'une clé API
    
    Usage:
        @app.get("/api/documents")
        async def get_documents(
            api_key: dict = Depends(require_api_permission("documents", "read"))
        ):
            ...
    """
    async def permission_checker(api_key_doc: dict = Security(get_api_key_from_header)):
        if not check_permission(api_key_doc, module, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission refusée. Cette clé n'a pas l'accès '{permission}' au module '{module}'."
            )
        return api_key_doc
    
    return permission_checker
