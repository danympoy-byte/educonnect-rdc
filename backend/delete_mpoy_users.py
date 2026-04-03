#!/usr/bin/env python3
"""
Script pour supprimer les utilisateurs Dany Mpoy Mukeba, Dany Mpoy et Betty Mpoy
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

async def delete_users():
    """Supprimer les utilisateurs spécifiés"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🗑️  Recherche et suppression des utilisateurs...")
    print("-" * 60)
    
    # Liste des noms à supprimer
    users_to_delete = [
        {"nom": "Mpoy Mukeba", "prenom": "Dany"},
        {"nom": "Mpoy", "prenom": "Dany"},
        {"nom": "Mpoy", "prenom": "Betty"}
    ]
    
    total_deleted = 0
    
    for user_info in users_to_delete:
        nom = user_info["nom"]
        prenom = user_info["prenom"]
        
        # Chercher l'utilisateur
        user = await db.users.find_one(
            {"nom": nom, "prenom": prenom},
            {"_id": 0, "id": 1, "nom": 1, "prenom": 1, "telephone": 1, "email": 1}
        )
        
        if user:
            print(f"\n📋 Utilisateur trouvé :")
            print(f"   Nom : {user.get('prenom', '')} {user.get('nom', '')}")
            print(f"   ID : {user.get('id', 'N/A')}")
            print(f"   Email : {user.get('email', 'N/A')}")
            print(f"   Téléphone : {user.get('telephone', 'N/A')}")
            
            # Supprimer l'utilisateur
            result = await db.users.delete_one(
                {"nom": nom, "prenom": prenom}
            )
            
            if result.deleted_count > 0:
                print(f"   ✅ SUPPRIMÉ avec succès")
                total_deleted += 1
            else:
                print(f"   ❌ Échec de suppression")
        else:
            print(f"\n⚠️  Utilisateur non trouvé : {prenom} {nom}")
    
    print("\n" + "=" * 60)
    print(f"📊 Résumé : {total_deleted} utilisateur(s) supprimé(s)")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    all_users = await db.users.find(
        {"$or": [
            {"nom": "Mpoy Mukeba"},
            {"nom": "Mpoy"}
        ]},
        {"_id": 0, "nom": 1, "prenom": 1}
    ).to_list(100)
    
    if all_users:
        print(f"⚠️  {len(all_users)} utilisateur(s) 'Mpoy' restant(s) dans la base :")
        for u in all_users:
            print(f"   - {u.get('prenom', '')} {u.get('nom', '')}")
    else:
        print("✅ Aucun utilisateur 'Mpoy' restant dans la base")
    
    client.close()
    print("\n🎉 Opération terminée !")

if __name__ == "__main__":
    asyncio.run(delete_users())
