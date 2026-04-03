"""
Authentification Basic Auth pour les systèmes externes
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from auth import verify_password

security = HTTPBasic()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'rie_education')]


async def verify_api_client(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Vérifie les credentials Basic Auth d'un système externe
    Returns: dict avec les infos du client API
    """
    # Rechercher le client API par username
    api_client = await db.api_clients.find_one(
        {"username": credentials.username, "actif": True},
        {"_id": 0}
    )
    
    if not api_client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Vérifier le mot de passe
    if not verify_password(credentials.password, api_client['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Mettre à jour last_used
    await db.api_clients.update_one(
        {"id": api_client['id']},
        {"$set": {"last_used": datetime.now(timezone.utc).isoformat()}}
    )
    
    return api_client


def require_permission(permission: str):
    """
    Décorateur pour vérifier qu'un client API a une permission spécifique
    """
    async def permission_checker(api_client: dict = Depends(verify_api_client)):
        if permission not in api_client.get('permissions', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' requise"
            )
        return api_client
    
    return permission_checker
