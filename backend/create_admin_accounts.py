#!/usr/bin/env python3
"""
Script pour créer les 3 comptes administrateurs Édu-Connect
Conformément aux spécifications dans /app/memory/admin_credentials.md
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

async def create_admin_accounts():
    """Créer les 3 comptes administrateurs"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔐 Création des comptes administrateurs Édu-Connect...")
    
    # Vérifier si les comptes existent déjà
    existing_admin = await db.users.find_one({"email": "admin@educonnect.cd"})
    if existing_admin:
        print("⚠️  Les comptes administrateurs existent déjà. Suppression des anciens comptes...")
        await db.users.delete_many({
            "email": {"$in": ["admin@educonnect.cd", "ged.admin@educonnect.cd", "sirh.admin@educonnect.cd"]}
        })
    
    # 1. Super Admin (Accès Complet)
    super_admin = {
        "id": str(uuid4()),
        "email": "admin@educonnect.cd",
        "telephone": "+243 900 000 001",
        "nom": "Super Admin",
        "prenom": "Système",
        "role": "administrateur_technique",
        "hashed_password": get_password_hash("Admin@EduConnect2026!"),
        "is_active": True,
        "service_id": "ADMIN",
        "niveau_hierarchique": 0,
        "permissions": [
            "all_access",
            "user_management",
            "system_settings",
            "ged_admin",
            "sirh_admin",
            "reports_access",
            "data_export"
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(super_admin)
    print("✅ Super Admin créé : admin@educonnect.cd")
    
    # 2. Admin GED
    admin_ged = {
        "id": str(uuid4()),
        "email": "ged.admin@educonnect.cd",
        "telephone": "+243 900 000 002",
        "nom": "Admin GED",
        "prenom": "Gestion",
        "role": "administrateur_technique",
        "hashed_password": get_password_hash("GED@Admin2026!"),
        "is_active": True,
        "service_id": "ADMIN_GED",
        "niveau_hierarchique": 1,
        "permissions": [
            "ged_admin",
            "document_management",
            "workflow_management",
            "external_entities",
            "distribution_lists"
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(admin_ged)
    print("✅ Admin GED créé : ged.admin@educonnect.cd")
    
    # 3. Admin SIRH
    admin_sirh = {
        "id": str(uuid4()),
        "email": "sirh.admin@educonnect.cd",
        "telephone": "+243 900 000 003",
        "nom": "Admin SIRH",
        "prenom": "Ressources Humaines",
        "role": "administrateur_technique",
        "hashed_password": get_password_hash("SIRH@Admin2026!"),
        "is_active": True,
        "service_id": "ADMIN_SIRH",
        "niveau_hierarchique": 1,
        "permissions": [
            "sirh_admin",
            "enseignant_management",
            "paie_management",
            "mutation_management",
            "dinacope_access"
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(admin_sirh)
    print("✅ Admin SIRH créé : sirh.admin@educonnect.cd")
    
    print("\n🎉 Tous les comptes administrateurs ont été créés avec succès !")
    print("\n📋 Résumé des comptes :")
    print("   1. Super Admin   : admin@educonnect.cd (+243 900 000 001)")
    print("   2. Admin GED     : ged.admin@educonnect.cd (+243 900 000 002)")
    print("   3. Admin SIRH    : sirh.admin@educonnect.cd (+243 900 000 003)")
    print("\n🔑 Voir /app/memory/admin_credentials.md pour les mots de passe")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_accounts())
