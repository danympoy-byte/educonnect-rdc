#!/usr/bin/env python3
"""
Script de seed pour créer des données de démonstration pour le RIE
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from models import UserRole
from auth import get_password_hash
from utils import generate_matricule_enseignant, generate_ine, generate_code_etablissement
import os
from datetime import datetime, timezone
import uuid

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

async def seed_data():
    print("🌱 Démarrage du seed des données...")
    
    # Clear existing data (optional for demo)
    print("🗑️  Nettoyage des données existantes...")
    await db.users.delete_many({})
    await db.provinces.delete_many({})
    await db.sous_divisions.delete_many({})
    await db.etablissements.delete_many({})
    await db.enseignants.delete_many({})
    await db.eleves.delete_many({})
    await db.classes.delete_many({})
    await db.notes.delete_many({})
    await db.bulletins.delete_many({})
    await db.audit_logs.delete_many({})
    
    # 1. Créer les provinces
    print("🗺️  Création des provinces...")
    provinces = [
        {"id": str(uuid.uuid4()), "nom": "Kinshasa", "code": "KIN", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "nom": "Kongo Central", "code": "KCT", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "nom": "Katanga", "code": "KAT", "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.provinces.insert_many(provinces)
    print(f"   ✅ {len(provinces)} provinces créées")
    
    # 2. Créer les sous-divisions
    print("📍 Création des sous-divisions...")
    sous_divisions = [
        {"id": str(uuid.uuid4()), "nom": "Kinshasa Centre", "code": "KIN-C", "province_id": provinces[0]["id"], "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "nom": "Kinshasa Est", "code": "KIN-E", "province_id": provinces[0]["id"], "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "nom": "Matadi", "code": "KCT-M", "province_id": provinces[1]["id"], "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.sous_divisions.insert_many(sous_divisions)
    print(f"   ✅ {len(sous_divisions)} sous-divisions créées")
    
    # 3. Créer des utilisateurs
    print("👥 Création des utilisateurs...")
    
    # Admin technique
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": "admin@rie.cd",
        "nom": "Admin",
        "prenom": "Système",
        "role": "administrateur_technique",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(admin_user)
    
    # Ministre
    ministre_user = {
        "id": str(uuid.uuid4()),
        "email": "ministre@education.cd",
        "nom": "Kabila",
        "prenom": "Jean",
        "role": "ministre",
        "hashed_password": get_password_hash("ministre123"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(ministre_user)
    
    # DPE
    dpe_user = {
        "id": str(uuid.uuid4()),
        "email": "dpe.kinshasa@education.cd",
        "nom": "Tshisekedi",
        "prenom": "Marie",
        "role": "directeur_provincial",
        "hashed_password": get_password_hash("dpe123"),
        "province_id": provinces[0]["id"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(dpe_user)
    
    print(f"   ✅ 3 utilisateurs admin créés")
    
    # 4. Créer des établissements
    print("🏫 Création des établissements...")
    
    etablissements = []
    for i in range(5):
        code_etab = generate_code_etablissement(db.etablissements, provinces[0]["code"])
        etab = {
            "id": str(uuid.uuid4()),
            "nom": f"École Primaire {i+1}",
            "type": "ecole_primaire",
            "code_etablissement": code_etab,
            "adresse": f"Avenue Lumumba {i+1}, Kinshasa",
            "province_id": provinces[0]["id"],
            "sous_division_id": sous_divisions[0]["id"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        etablissements.append(etab)
    
    await db.etablissements.insert_many(etablissements)
    print(f"   ✅ {len(etablissements)} établissements créés")
    
    # 5. Créer des directeurs d'école
    print("👨‍💼 Création des directeurs...")
    
    directeurs = []
    for i, etab in enumerate(etablissements):
        dir_user = {
            "id": str(uuid.uuid4()),
            "email": f"directeur{i+1}@rie.cd",
            "nom": f"Directeur{i+1}",
            "prenom": f"Pierre",
            "role": "directeur_ecole",
            "hashed_password": get_password_hash("directeur123"),
            "etablissement_id": etab["id"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        directeurs.append(dir_user)
    
    await db.users.insert_many(directeurs)
    print(f"   ✅ {len(directeurs)} directeurs créés")
    
    # 6. Créer des enseignants
    print("👨‍🏫 Création des enseignants...")
    
    enseignants_users = []
    enseignants_profiles = []
    
    for i in range(10):
        ens_user = {
            "id": str(uuid.uuid4()),
            "email": f"enseignant{i+1}@rie.cd",
            "nom": f"Enseignant{i+1}",
            "prenom": f"Paul",
            "role": "enseignant",
            "hashed_password": get_password_hash("enseignant123"),
            "etablissement_id": etablissements[i % len(etablissements)]["id"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        enseignants_users.append(ens_user)
        
        matricule = generate_matricule_enseignant(db.enseignants)
        ens_profile = {
            "id": str(uuid.uuid4()),
            "user_id": ens_user["id"],
            "matricule": matricule,
            "etablissement_id": etablissements[i % len(etablissements)]["id"],
            "matieres": ["Mathématiques", "Français"] if i % 2 == 0 else ["Sciences", "Histoire"],
            "est_professeur_principal": i < 3,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        enseignants_profiles.append(ens_profile)
    
    await db.users.insert_many(enseignants_users)
    await db.enseignants.insert_many(enseignants_profiles)
    print(f"   ✅ {len(enseignants_users)} enseignants créés")
    
    # 7. Créer des classes
    print("📚 Création des classes...")
    
    classes = []
    niveaux = ["CP1", "CP2", "CE1", "CE2", "CM1", "CM2"]
    
    for etab in etablissements:
        for i, niveau in enumerate(niveaux):
            classe = {
                "id": str(uuid.uuid4()),
                "nom": f"{niveau} A",
                "niveau": niveau,
                "etablissement_id": etab["id"],
                "professeur_principal_id": enseignants_profiles[i % len(enseignants_profiles)]["id"] if i < len(enseignants_profiles) else None,
                "annee_scolaire": "2024-2025",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            classes.append(classe)
    
    await db.classes.insert_many(classes)
    print(f"   ✅ {len(classes)} classes créées")
    
    # 8. Créer des élèves
    print("👨‍🎓 Création des élèves...")
    
    eleves_users = []
    eleves_profiles = []
    
    for i in range(50):
        eleve_user = {
            "id": str(uuid.uuid4()),
            "email": f"eleve{i+1}@rie.cd",
            "nom": f"Eleve{i+1}",
            "prenom": f"Jean",
            "role": "eleve_primaire",
            "hashed_password": get_password_hash("eleve123"),
            "etablissement_id": etablissements[i % len(etablissements)]["id"],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        eleves_users.append(eleve_user)
        
        ine = generate_ine(db.eleves)
        niveau_idx = i % len(niveaux)
        eleve_profile = {
            "id": str(uuid.uuid4()),
            "user_id": eleve_user["id"],
            "ine": ine,
            "etablissement_id": etablissements[i % len(etablissements)]["id"],
            "classe_id": classes[niveau_idx]["id"],
            "niveau": niveaux[niveau_idx],
            "date_naissance": "2010-05-15",
            "lieu_naissance": "Kinshasa",
            "parents_ids": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        eleves_profiles.append(eleve_profile)
    
    await db.users.insert_many(eleves_users)
    await db.eleves.insert_many(eleves_profiles)
    print(f"   ✅ {len(eleves_users)} élèves créés")
    
    # 9. Créer quelques parents
    print("👨‍👩‍👧 Création des parents...")
    
    parents = []
    for i in range(10):
        parent = {
            "id": str(uuid.uuid4()),
            "email": f"parent{i+1}@rie.cd",
            "nom": f"Parent{i+1}",
            "prenom": f"Marie",
            "role": "parent",
            "hashed_password": get_password_hash("parent123"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        parents.append(parent)
    
    await db.users.insert_many(parents)
    print(f"   ✅ {len(parents)} parents créés")
    
    print("\n✨ Seed terminé avec succès!")
    print("\n📝 Comptes de test créés:")
    print("   Admin: admin@rie.cd / admin123")
    print("   Ministre: ministre@education.cd / ministre123")
    print("   DPE: dpe.kinshasa@education.cd / dpe123")
    print("   Directeur: directeur1@rie.cd / directeur123")
    print("   Enseignant: enseignant1@rie.cd / enseignant123")
    print("   Élève: eleve1@rie.cd / eleve123")
    print("   Parent: parent1@rie.cd / parent123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
