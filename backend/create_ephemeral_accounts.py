"""
Création de comptes éphémères Test01-Test10 avec accès Ministre.
Validité : 24h après la première connexion.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from datetime import datetime, timezone
import uuid

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

ACCOUNTS = []
for i in range(1, 11):
    num = f"{i:02d}"
    ACCOUNTS.append({
        "id": str(uuid.uuid4()),
        "email": f"test{num}@educonnect.cd",
        "telephone": f"+243 900 100 {num}0",
        "nom": f"Test{num}",
        "prenom": "Compte Démo",
        "role": "ministre",
        "is_active": True,
        "is_ephemeral": True,
        "first_login_at": None,
        "expires_at": None,
        "service_id": "MIN-EPSP",
        "niveau_hierarchique": 1,
        "permissions": [
            "all_access",
            "user_management",
            "ged_admin",
            "sirh_admin",
            "reports_access",
            "data_export"
        ],
        "hashed_password": get_password_hash(f"Test{num}@2026"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "contexte_travail": "equipe"
    })


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["educonnect_rdc"]

    created = 0
    updated = 0
    for account in ACCOUNTS:
        existing = await db.users.find_one({"email": account["email"]}, {"_id": 0})
        if existing:
            # Reset: reactivate and clear expiry
            await db.users.update_one(
                {"email": account["email"]},
                {"$set": {
                    "is_active": True,
                    "is_ephemeral": True,
                    "first_login_at": None,
                    "expires_at": None,
                    "hashed_password": account["hashed_password"],
                    "role": "ministre",
                    "permissions": account["permissions"],
                    "niveau_hierarchique": 1,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            updated += 1
            print(f"  Reset: {account['email']}")
        else:
            await db.users.insert_one(account)
            created += 1
            print(f"  Cree: {account['email']}")

    print(f"\nResultat: {created} crees, {updated} reinitialises")
    print("\n--- Comptes ephemeres ---")
    print(f"{'Email':<30} {'Mot de passe':<20} {'Role'}")
    print("-" * 70)
    for i in range(1, 11):
        num = f"{i:02d}"
        print(f"test{num}@educonnect.cd          Test{num}@2026          ministre")
    print("\nValidite: 24h apres la premiere connexion")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
