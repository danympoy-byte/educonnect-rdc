"""
Script de migration : Suppression des anciennes données et création de nouveaux utilisateurs de test
conformes au nouveau système de services.
Refactorisé en fonctions modulaires.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from auth import get_password_hash

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


async def nettoyer_collections(db) -> dict:
    """Supprime les anciennes données des collections principales."""
    print("\n  ETAPE 1: Suppression des anciennes données")
    print("-" * 60)
    stats = {}
    for collection in ['users', 'documents', 'mutations', 'presences']:
        count = await db[collection].count_documents({})
        await db[collection].delete_many({})
        stats[collection] = count
        print(f"  - {collection}: {count} documents supprimés")
    return stats


async def recuperer_services(db) -> dict:
    """Récupère et indexe les services clés par code."""
    print("\n  ETAPE 2: Récupération des services")
    print("-" * 60)
    services = await db.services.find({}, {"_id": 0}).to_list(1000)
    print(f"  - {len(services)} services disponibles")

    codes = ['MIN', 'SG', 'DGA', 'DGA_FIN', 'DGTIC', 'DGTIC_SI']
    index = {}
    for code in codes:
        index[code] = next((s for s in services if s['code'] == code), None)
    return index


def creer_utilisateur(user_id, nom, postnom, prenom, sexe, etat_civil, date_naissance,
                      lieu_naissance, telephone, adresse, email, diplomes, experiences,
                      service, poste, est_responsable, password, profil_complete=True,
                      numero_compte=None, banque=None):
    """Construit un dictionnaire utilisateur standardisé."""
    return {
        "id": user_id,
        "nom": nom, "postnom": postnom, "prenom": prenom,
        "sexe": sexe, "etat_civil": etat_civil,
        "date_naissance": date_naissance, "lieu_naissance": lieu_naissance,
        "telephone": telephone, "adresse": adresse, "email": email,
        "diplomes": diplomes, "experiences": experiences,
        "service_profiles": [{
            "id": f"prof_{user_id}",
            "user_id": user_id,
            "service_id": service['id'],
            "service_nom": service['nom'],
            "service_code": service['code'],
            "poste": poste,
            "est_responsable": est_responsable,
            "date_affectation": datetime.now(timezone.utc).isoformat()
        }],
        "service_actif_id": service['id'],
        "numero_compte_bancaire": numero_compte,
        "banque": banque,
        "photo_url": None,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "profil_complete": profil_complete,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


def generer_utilisateurs_test(services: dict) -> list:
    """Génère la liste complète des utilisateurs de test."""
    print("\n  ETAPE 3: Création des nouveaux utilisateurs")
    print("-" * 60)
    users = []

    if services.get('MIN'):
        u = creer_utilisateur(
            "ministre_001", "TSHISEKEDI", "TSHILOMBO", "Félix", "masculin", "marie",
            "1963-06-13", "Kinshasa", "+243 820 000 001", "Gombe, Kinshasa",
            "ministre@educonnect.gouv.cd",
            [{"intitule": "Doctorat en Sciences Politiques", "etablissement": "Université de Kinshasa", "annee_obtention": 1995, "pays": "RDC"}],
            [{"poste": "Ministre de l'Éducation", "employeur": "Gouvernement de la RDC", "date_debut": "2024-01", "date_fin": None, "description": "Ministre de l'Enseignement Primaire, Secondaire et Technique"}],
            services['MIN'], "Ministre", True, "Ministre2026!",
            numero_compte="001234567890", banque="Banque Centrale du Congo"
        )
        users.append(u)
        print(f"  - Ministre créé: {u['prenom']} {u['nom']}")

    if services.get('SG'):
        u = creer_utilisateur(
            "sg_001", "KABONGO", "MWAMBA", "Jean-Pierre", "masculin", "marie",
            "1970-03-15", "Lubumbashi", "+243 820 000 002", "Gombe, Kinshasa",
            "sg@educonnect.gouv.cd",
            [{"intitule": "Master en Administration Publique", "etablissement": "École Nationale d'Administration", "annee_obtention": 2000, "pays": "RDC"}],
            [{"poste": "Secrétaire Général", "employeur": "MINEPST", "date_debut": "2023-06", "date_fin": None, "description": "Coordination générale des services du Ministère"}],
            services['SG'], "Secrétaire Général", True, "SG2026!",
            numero_compte="001234567891", banque="Rawbank"
        )
        users.append(u)
        print(f"  - Secrétaire Général créé: {u['prenom']} {u['nom']}")

    if services.get('DGA'):
        u = creer_utilisateur(
            "dg_admin_001", "MULUMBA", "NKULU", "Grace", "feminin", "marie",
            "1975-08-22", "Kinshasa", "+243 820 000 003", "Ngaliema, Kinshasa",
            "dg.admin@educonnect.gouv.cd",
            [{"intitule": "Master en Gestion des Ressources Humaines", "etablissement": "Université Protestante du Congo", "annee_obtention": 2005, "pays": "RDC"}],
            [{"poste": "Directrice Générale de l'Administration", "employeur": "MINEPST", "date_debut": "2022-01", "date_fin": None, "description": "Gestion administrative, RH et financière"}],
            services['DGA'], "Directrice Générale", True, "DGAdmin2026!",
            numero_compte="001234567892", banque="Equity Bank"
        )
        users.append(u)
        print(f"  - DG Administration créé: {u['prenom']} {u['nom']}")

    if services.get('DGA_FIN') and services.get('DGA'):
        u = creer_utilisateur(
            "chef_fin_001", "KAMANDA", "TSHITENGE", "Patrick", "masculin", "celibataire",
            "1985-11-10", "Mbuji-Mayi", "+243 820 000 004", "Lemba, Kinshasa",
            "patrick.kamanda@educonnect.gouv.cd",
            [{"intitule": "Licence en Comptabilité", "etablissement": "Institut Supérieur de Commerce", "annee_obtention": 2010, "pays": "RDC"}],
            [{"poste": "Chef de Service Finances", "employeur": "MINEPST - DGA", "date_debut": "2020-03", "date_fin": None, "description": "Gestion budgétaire et comptabilité"}],
            services['DGA_FIN'], "Chef de Service", True, "ChefFin2026!",
            profil_complete=False
        )
        users.append(u)
        print(f"  - Chef Finances créé: {u['prenom']} {u['nom']} (profil incomplet)")

    if services.get('DGTIC_SI'):
        u = creer_utilisateur(
            "agent_dgtic_001", "NGALULA", "MUKENDI", "David", "masculin", "marie",
            "1990-05-18", "Kinshasa", "+243 820 000 005", "Limete, Kinshasa",
            None,
            [{"intitule": "Licence en Informatique", "etablissement": "Université de Kinshasa", "annee_obtention": 2015, "pays": "RDC"}],
            [{"poste": "Développeur Systèmes d'Information", "employeur": "MINEPST - DGTIC", "date_debut": "2018-09", "date_fin": None, "description": "Développement et maintenance d'Édu-Connect"}],
            services['DGTIC_SI'], "Développeur", False, "AgentDGTIC2026!",
            profil_complete=False
        )
        users.append(u)
        print(f"  - Agent DGTIC créé: {u['prenom']} {u['nom']} (profil incomplet)")

    return users


async def assigner_responsables(db, services: dict):
    """Assigne les responsables aux services."""
    print("\n  ETAPE 4: Assignation des responsables aux services")
    print("-" * 60)
    assignments = [
        ('MIN', 'ministre_001', 'Ministre'),
        ('SG', 'sg_001', 'SG'),
        ('DGA', 'dg_admin_001', 'DG Admin'),
        ('DGA_FIN', 'chef_fin_001', 'Chef Finances'),
    ]
    for code, user_id, label in assignments:
        service = services.get(code)
        if service:
            await db.services.update_one({"id": service['id']}, {"$set": {"responsable_id": user_id}})
            print(f"  - {label} assigné au service {code}")


def afficher_resume(users: list, services_count: int):
    """Affiche le résumé de la migration."""
    print("\n" + "=" * 60)
    print("MIGRATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    print(f"\n  Statistiques:")
    print(f"  - Utilisateurs créés: {len(users)}")
    print(f"  - Services disponibles: {services_count}")
    print(f"  - Profils complets: {sum(1 for u in users if u['profil_complete'])}")
    print(f"  - Profils incomplets: {sum(1 for u in users if not u['profil_complete'])}")

    print("\n  Identifiants de connexion:")
    print("-" * 60)
    for user in users:
        print(f"  Tel: {user['telephone']}")
        print(f"     -> {user['prenom']} {user['nom']} ({user['service_profiles'][0]['poste']})")
        print(f"     -> Service: {user['service_profiles'][0]['service_nom']}")
        if not user['profil_complete']:
            print(f"     Profil incomplet (notification affichée)")
        print()


async def migrate():
    """Migration complète des données."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("=" * 60)
    print("MIGRATION DES DONNÉES - ÉDU-CONNECT")
    print("=" * 60)

    try:
        await nettoyer_collections(db)
        services = await recuperer_services(db)
        all_services = await db.services.find({}, {"_id": 0}).to_list(1000)
        users = generer_utilisateurs_test(services)

        if users:
            await db.users.insert_many(users)
            print(f"\n  {len(users)} utilisateurs créés avec succès!")

        await assigner_responsables(db, services)
        afficher_resume(users, len(all_services))
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
