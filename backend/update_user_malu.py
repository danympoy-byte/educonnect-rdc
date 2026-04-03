#!/usr/bin/env python3
"""
Script pour supprimer Felix Tshisekedi et créer Raïssa Malu
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def update_user():
    """Supprimer Felix Tshisekedi et créer Raïssa Malu"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🗑️  Suppression de l'ancien utilisateur...")
    
    # Supprimer l'utilisateur avec le téléphone +243 820 000 001
    result = await db.users.delete_one({"telephone": "+243 820 000 001"})
    
    if result.deleted_count > 0:
        print(f"✅ Utilisateur Felix Tshisekedi supprimé (téléphone: +243 820 000 001)")
    else:
        print("⚠️  Aucun utilisateur trouvé avec ce téléphone")
    
    print("\n👤 Création du nouveau compte pour Raïssa Malu...")
    
    # Créer le nouveau compte
    nouveau_user = {
        "id": str(uuid4()),
        "nom": "Malu",
        "prenom": "Raïssa",
        "telephone": "+243 820 000 010",
        "email": None,  # Pas d'email pour l'instant
        "role": "ministre",
        "hashed_password": get_password_hash("Ministre2026!"),
        "is_active": True,
        "service_id": "MINISTERE",
        "niveau_hierarchique": 2,
        "permissions": [
            "dashboard_access",
            "reports_view",
            "statistics_view"
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(nouveau_user)
    print("✅ Compte créé pour Raïssa Malu")
    
    print("\n📋 Résumé du nouveau compte :")
    print(f"   Nom : {nouveau_user['prenom']} {nouveau_user['nom']}")
    print(f"   Téléphone : {nouveau_user['telephone']}")
    print(f"   Rôle : {nouveau_user['role']}")
    print(f"   Mot de passe : Ministre2026!")
    
    # Test de connexion
    print("\n🧪 Test de connexion...")
    user_test = await db.users.find_one(
        {"telephone": "+243 820 000 010"},
        {"_id": 0, "hashed_password": 0}
    )
    
    if user_test:
        print("✅ Compte accessible dans la base de données")
        print(f"   ID: {user_test['id']}")
        print(f"   Statut: {'Actif' if user_test['is_active'] else 'Inactif'}")
    
    client.close()
    print("\n🎉 Opération terminée avec succès !")

if __name__ == "__main__":
    asyncio.run(update_user())
