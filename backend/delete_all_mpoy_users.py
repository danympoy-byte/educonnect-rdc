#!/usr/bin/env python3
"""
Script pour supprimer TOUS les utilisateurs avec 'Mpoy' dans le nom (case-insensitive)
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def delete_all_mpoy_users():
    """Supprimer TOUS les utilisateurs avec 'Mpoy' dans le nom ou prénom"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🗑️  Recherche de TOUS les utilisateurs 'Mpoy'...")
    print("-" * 60)
    
    # Recherche avec regex case-insensitive
    mpoy_users = await db.users.find(
        {"$or": [
            {"nom": {"$regex": "mpoy", "$options": "i"}},
            {"prenom": {"$regex": "mpoy", "$options": "i"}}
        ]},
        {"_id": 0, "id": 1, "nom": 1, "prenom": 1, "telephone": 1, "email": 1}
    ).to_list(100)
    
    print(f"📋 {len(mpoy_users)} utilisateur(s) trouvé(s) :\n")
    
    if not mpoy_users:
        print("✅ Aucun utilisateur 'Mpoy' trouvé dans la base")
        client.close()
        return
    
    # Afficher tous les utilisateurs trouvés
    for i, user in enumerate(mpoy_users, 1):
        print(f"{i}. {user.get('prenom', '')} {user.get('nom', '')}")
        print(f"   ID: {user.get('id', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Téléphone: {user.get('telephone', 'N/A')}")
        print()
    
    # Suppression
    print("🔥 Suppression en cours...")
    result = await db.users.delete_many(
        {"$or": [
            {"nom": {"$regex": "mpoy", "$options": "i"}},
            {"prenom": {"$regex": "mpoy", "$options": "i"}}
        ]}
    )
    
    print(f"\n✅ {result.deleted_count} utilisateur(s) supprimé(s)")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    remaining = await db.users.find(
        {"$or": [
            {"nom": {"$regex": "mpoy", "$options": "i"}},
            {"prenom": {"$regex": "mpoy", "$options": "i"}}
        ]},
        {"_id": 0, "nom": 1, "prenom": 1}
    ).to_list(100)
    
    if remaining:
        print(f"⚠️  {len(remaining)} utilisateur(s) 'Mpoy' encore présent(s) !")
        for u in remaining:
            print(f"   - {u.get('prenom', '')} {u.get('nom', '')}")
    else:
        print("✅ Aucun utilisateur 'Mpoy' restant dans la base")
        print("✅ Ils n'apparaîtront plus dans les suggestions de destinataires")
    
    client.close()
    print("\n🎉 Opération terminée !")

if __name__ == "__main__":
    asyncio.run(delete_all_mpoy_users())
