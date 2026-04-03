#!/usr/bin/env python3
"""
Script de seed complet pour le RIE avec toutes les provinces de la RDC
Crée 10 éléments pour chaque profil utilisateur
"""

import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
import os
from datetime import datetime, timezone
import uuid
import random

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Configuration des provinces administratives et éducationnelles
PROVINCES_CONFIG = {
    "Bas-Uélé": [
        {"nom": "Bas-Uele", "ville": "BUTA"}
    ],
    "Équateur": [
        {"nom": "Équateur 1", "ville": "MBANDAKA"},
        {"nom": "Équateur 2", "ville": "BASANKUSU"}
    ],
    "Haut-Katanga": [
        {"nom": "Haut-Katanga 1", "ville": "LUBUMBASHI"},
        {"nom": "Haut-Katanga 2", "ville": "PWETO"}
    ],
    "Haut-Lomami": [
        {"nom": "Haut-Lomami 1", "ville": "KAMINA"},
        {"nom": "Haut-Lomami 2", "ville": "BUKAMA"}
    ],
    "Haut-Uélé": [
        {"nom": "Haut-Uele 1", "ville": "ISIRO"},
        {"nom": "Haut-Uele 2", "ville": "WATSHA"}
    ],
    "Ituri": [
        {"nom": "Ituri 1", "ville": "BUNIA"},
        {"nom": "Ituri 2", "ville": "ARU"},
        {"nom": "Ituri 3", "ville": "MAHAGI"}
    ],
    "Kasai": [
        {"nom": "Kasaï 1", "ville": "TSHIKAPA"},
        {"nom": "Kasaï 2", "ville": "MWEKA"}
    ],
    "Kasai-Central": [
        {"nom": "Kasaï Central 1", "ville": "KANANGA"},
        {"nom": "Kasaï Central 2", "ville": "LUIZA"}
    ],
    "Kasai-Oriental": [
        {"nom": "Kasaï-Oriental 1", "ville": "MBUJI-MAYI"},
        {"nom": "Kasaï-Oriental 2", "ville": "KABEYA KAMWANGA"}
    ],
    "Kinshasa": [
        {"nom": "Lukunga", "ville": "GOMBE"},
        {"nom": "Funa", "ville": "KASAVUBU"},
        {"nom": "Mont-Amba", "ville": "LIMETE"},
        {"nom": "Tshangu", "ville": "NDJILI"},
        {"nom": "Plateau", "ville": "N'SELE"}
    ],
    "Kongo-Central": [
        {"nom": "Kongo-Central 1", "ville": "MATADI"},
        {"nom": "Kongo-Central 2", "ville": "MBANZA-NGUNGU"},
        {"nom": "Kongo-Central 3", "ville": "INKISI"}
    ],
    "Kwango": [
        {"nom": "Kwango 1", "ville": "KENGE"},
        {"nom": "Kwango 2", "ville": "KASONGO LUNDA"}
    ],
    "Kwilu": [
        {"nom": "Kwilu 1", "ville": "BANDUNDU-VILLE"},
        {"nom": "Kwilu 2", "ville": "KIKWIT"},
        {"nom": "Kwilu 3", "ville": "IDIOFA-CENTRE"}
    ],
    "Lomami": [
        {"nom": "Lomami 1", "ville": "KABINDA"},
        {"nom": "Lomami 2", "ville": "NGANDAJIKA"}
    ],
    "Lualaba": [
        {"nom": "Lualaba 1", "ville": "KOLWEZI"},
        {"nom": "Lualaba 2", "ville": "KAPANGA/MUSUMBA"}
    ],
    "Mai-Ndombe": [
        {"nom": "Mai-Ndombe 1", "ville": "INONGO"},
        {"nom": "Mai-Ndombe 2", "ville": "BOLOBO"},
        {"nom": "Mai-Ndombe 3", "ville": "NIOKI"}
    ],
    "Maniema": [
        {"nom": "Maniema 1", "ville": "KINDU"},
        {"nom": "Maniema 2", "ville": "KABAMBARE"}
    ],
    "Mongala": [
        {"nom": "Mongala 1", "ville": "LISALA"},
        {"nom": "Mongala 2", "ville": "BUMBA"}
    ],
    "Nord-Kivu": [
        {"nom": "Nord-Kivu 1", "ville": "GOMA"},
        {"nom": "Nord-Kivu 2", "ville": "BUTEMBO"},
        {"nom": "Nord-Kivu 3", "ville": "WALIKALE"}
    ],
    "Nord-Ubangi": [
        {"nom": "Nord-Ubangi 1", "ville": "GBADOLITE"},
        {"nom": "Nord-Ubangi 2", "ville": "YAKOMA"}
    ],
    "Sankuru": [
        {"nom": "Sankuru 1", "ville": "LODJA"},
        {"nom": "Sankuru 2", "ville": "LUSAMBO"}
    ],
    "Sud-Kivu": [
        {"nom": "Sud-Kivu 1", "ville": "BUKAVU"},
        {"nom": "Sud-Kivu 2", "ville": "FIZI"},
        {"nom": "Sud-Kivu 3", "ville": "KAMITOGA"}
    ],
    "Sud-Ubangi": [
        {"nom": "Sud-Ubangi 1", "ville": "GEMENA"},
        {"nom": "Sud-Ubangi 2", "ville": "ZONGO"}
    ],
    "Tanganyika": [
        {"nom": "Tanganyika 1", "ville": "KALEMIE"},
        {"nom": "Tanganyika 2", "ville": "KONGOLO"}
    ],
    "Tshopo": [
        {"nom": "Tshopo 1", "ville": "KISANGANI"},
        {"nom": "Tshopo 2", "ville": "YANGAMBI"}
    ],
    "Tshuapa": [
        {"nom": "Tshuapa 1", "ville": "BOENDE"},
        {"nom": "Tshuapa 2", "ville": "BOKUNGU"}
    ]
}

# Noms congolais pour les utilisateurs
NOMS_CONGOLAIS = [
    "Kabila", "Tshisekedi", "Lumumba", "Mobutu", "Kasa-Vubu", "Mulele", "Kimbangu",
    "Ngalula", "Kamanda", "Bofossa", "Mwamba", "Kalala", "Mutombo", "Mukendi",
    "Ndala", "Tshimanga", "Kapend", "Mulumba", "Ilunga", "Kabeya"
]

PRENOMS_CONGOLAIS = [
    "Jean", "Marie", "Joseph", "Emmanuel", "Grace", "Pauline", "Daniel",
    "Christine", "Patrick", "Sylvie", "François", "Henriette", "Marcel",
    "Thérèse", "Antoine", "Béatrice", "Pierre", "Alphonsine", "André", "Lucie"
]

NOMS_ECOLES = [
    "Lumumba", "Indépendance", "Mobutu", "Kasa-Vubu", "Mulele", "Kimbangu",
    "Liberté", "Unité", "Progrès", "Excellence", "Espoir", "Avenir", "Succès",
    "Victoire", "Paix", "Amani", "Renaissance", "Horizon", "Clarté", "Aurore"
]

def generate_code_province(nom_province):
    """Génère un code de province basé sur le nom"""
    # Prendre les 3 premières lettres en majuscules
    code = nom_province[:3].upper().replace(" ", "").replace("-", "")
    return code

def generate_identifiant_etablissement():
    """Génère un identifiant à 6 chiffres pour un établissement"""
    return f"{random.randint(100000, 999999)}"

def generate_matricule_enseignant(existing_codes):
    """Génère un matricule unique pour un enseignant"""
    while True:
        matricule = f"ENS-{random.randint(100000, 999999)}"
        if matricule not in existing_codes:
            existing_codes.add(matricule)
            return matricule

def generate_ine(existing_codes):
    """Génère un INE unique pour un élève"""
    while True:
        ine = f"INE-{random.randint(10000000, 99999999)}"
        if ine not in existing_codes:
            existing_codes.add(ine)
            return ine

async def seed_data():
    print("🌱 Démarrage du seed complet des données RIE...")
    
    # Clear existing data
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
    
    # 1. Créer les provinces administratives et éducationnelles
    print("\n🗺️  Création des provinces...")
    provinces = []
    sous_divisions = []
    province_code_counter = 1
    
    for prov_admin, prov_educ_list in PROVINCES_CONFIG.items():
        # Créer la province administrative
        code_prov = f"P{province_code_counter:02d}"
        province_id = str(uuid.uuid4())
        
        province = {
            "id": province_id,
            "nom": prov_admin,
            "code": code_prov,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        provinces.append(province)
        
        # Créer les provinces éducationnelles (sous-divisions)
        for prov_educ in prov_educ_list:
            sous_div = {
                "id": str(uuid.uuid4()),
                "nom": prov_educ["nom"],
                "code": f"{code_prov}-{prov_educ['ville'][:3]}",
                "province_id": province_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            sous_divisions.append(sous_div)
        
        province_code_counter += 1
    
    await db.provinces.insert_many(provinces)
    await db.sous_divisions.insert_many(sous_divisions)
    print(f"   ✅ {len(provinces)} provinces administratives créées")
    print(f"   ✅ {len(sous_divisions)} provinces éducationnelles créées")
    
    # 2. Créer 10 utilisateurs de chaque profil (16 profils)
    print("\n👥 Création des utilisateurs (10 par profil)...")
    
    roles_config = [
        ("ministre", "Ministre de l'Éducation", None, None),
        ("secretaire_general", "Secrétaire Général", None, None),
        ("directeur_provincial", "DPE", "province", None),
        ("chef_sous_division", "Chef Sous-division", "province", "sous_division"),
        ("chef_etablissement", "Chef Établissement", "province", "etablissement"),
        ("directeur_ecole", "Directeur École", "province", "etablissement"),
        ("conseiller_principal_education", "CPE", "province", "etablissement"),
        ("enseignant", "Enseignant", "province", "etablissement"),
        ("eleve_primaire", "Élève Primaire", "province", "etablissement"),
        ("eleve_secondaire", "Élève Secondaire", "province", "etablissement"),
        ("parent", "Parent", None, None),
        ("inspecteur_pedagogique", "Inspecteur", "province", None),
        ("agent_dinacope", "Agent DINACOPE", "province", None),
        ("personnel_administratif", "Personnel Admin", "province", "etablissement"),
        ("infirmier_scolaire", "Infirmier", "province", "etablissement"),
        ("administrateur_technique", "Admin Technique", None, None)
    ]
    
    all_users = []
    user_counter = {"total": 0}
    
    for role, role_label, need_province, need_etablissement in roles_config:
        for i in range(10):
            user_id = str(uuid.uuid4())
            nom = random.choice(NOMS_CONGOLAIS)
            prenom = random.choice(PRENOMS_CONGOLAIS)
            
            # Assigner un sexe pour enseignants, directeurs, élèves
            sexe = None
            if role in ["enseignant", "directeur_ecole", "chef_etablissement", "eleve_primaire", "eleve_secondaire"]:
                sexe = random.choice(["masculin", "feminin"])
            
            # Sélectionner aléatoirement une province si nécessaire
            province_id = None
            sous_division_id = None
            etablissement_id = None
            
            if need_province:
                province = random.choice(provinces)
                province_id = province["id"]
                
                # Sélectionner une sous-division de cette province
                sous_divs_prov = [sd for sd in sous_divisions if sd["province_id"] == province_id]
                if sous_divs_prov and need_etablissement:
                    sous_division_id = random.choice(sous_divs_prov)["id"]
            
            email = f"{role}.{nom.lower()}{i+1}@rie.cd"
            
            user = {
                "id": user_id,
                "email": email,
                "nom": nom,
                "prenom": prenom,
                "role": role,
                "sexe": sexe,
                "hashed_password": get_password_hash("password123"),
                "is_active": True,
                "province_id": province_id,
                "sous_division_id": sous_division_id,
                "etablissement_id": etablissement_id,  # Sera mis à jour après création établissements
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            all_users.append(user)
            user_counter["total"] += 1
    
    await db.users.insert_many(all_users)
    print(f"   ✅ {user_counter['total']} utilisateurs créés (10 par profil × 16 profils)")
    
    # 3. Créer des établissements répartis dans toutes les provinces éducationnelles
    print("\n🏫 Création des établissements...")
    etablissements = []
    etablissement_codes = set()
    
    # Créer 5 établissements par province éducationnelle (300 établissements au total)
    for sous_div in sous_divisions:
        province = next(p for p in provinces if p["id"] == sous_div["province_id"])
        
        for i in range(5):
            code_etab = generate_identifiant_etablissement()
            while code_etab in etablissement_codes:
                code_etab = generate_identifiant_etablissement()
            etablissement_codes.add(code_etab)
            
            type_etab = random.choice(["ecole_primaire", "college", "lycee"])
            
            # Déterminer la catégorie (60% publique, 40% privée)
            categorie = random.choices(
                ["publique", "privee"],
                weights=[60, 40]
            )[0]
            
            # Nom selon la catégorie
            if categorie == "publique":
                statut_label = random.choice(["EP", "École Publique", "Institut Public"])
            else:
                statut_label = random.choice(["École Privée", "Institut Privé", "Collège Privé"])
            
            nom_ecole = random.choice(NOMS_ECOLES)
            
            ville = sous_div["nom"].split("(")[-1].strip(")")
            
            etab = {
                "id": str(uuid.uuid4()),
                "nom": f"{statut_label} {nom_ecole} {i+1}",
                "type": type_etab,
                "categorie": categorie,
                "code_etablissement": code_etab,
                "adresse": f"Avenue {nom_ecole}, {ville}",
                "province_id": province["id"],
                "sous_division_id": sous_div["id"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            etablissements.append(etab)
    
    await db.etablissements.insert_many(etablissements)
    
    # Compter par catégorie
    nb_publics = len([e for e in etablissements if e["categorie"] == "publique"])
    nb_prives = len([e for e in etablissements if e["categorie"] == "privee"])
    print(f"   ✅ {len(etablissements)} établissements créés")
    print(f"      • Publics: {nb_publics}")
    print(f"      • Privés: {nb_prives}")
    
    # 4. Mettre à jour les utilisateurs avec des établissements
    print("\n🔄 Affectation des utilisateurs aux établissements...")
    users_to_update = [u for u in all_users if u["role"] in [
        "chef_etablissement", "directeur_ecole", "conseiller_principal_education",
        "enseignant", "eleve_primaire", "eleve_secondaire", "personnel_administratif",
        "infirmier_scolaire"
    ]]
    
    for user in users_to_update:
        # Trouver un établissement dans la province de l'utilisateur
        etabs_province = [e for e in etablissements if e["province_id"] == user["province_id"]]
        if etabs_province:
            etab = random.choice(etabs_province)
            await db.users.update_one(
                {"id": user["id"]},
                {"$set": {"etablissement_id": etab["id"]}}
            )
            # Mettre à jour dans la liste locale aussi
            user["etablissement_id"] = etab["id"]
    
    print(f"   ✅ Utilisateurs affectés aux établissements")
    
    # 5. Créer des profils enseignants
    print("\n👨‍🏫 Création des profils enseignants...")
    enseignants_users = [u for u in all_users if u["role"] == "enseignant"]
    enseignants_profiles = []
    matricules_used = set()
    
    matieres_list = [
        ["Mathématiques", "Physique"],
        ["Français", "Littérature"],
        ["Sciences", "Biologie"],
        ["Histoire", "Géographie"],
        ["Anglais", "Communication"],
        ["Chimie", "Sciences Naturelles"],
        ["Éducation Civique", "Philosophie"],
        ["Arts Plastiques", "Musique"]
    ]
    
    for ens_user in enseignants_users:
        if ens_user.get("etablissement_id"):
            matricule = generate_matricule_enseignant(matricules_used)
            
            ens_profile = {
                "id": str(uuid.uuid4()),
                "user_id": ens_user["id"],
                "matricule": matricule,
                "etablissement_id": ens_user["etablissement_id"],
                "matieres": random.choice(matieres_list),
                "est_professeur_principal": random.choice([True, False]),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            enseignants_profiles.append(ens_profile)
    
    if enseignants_profiles:
        await db.enseignants.insert_many(enseignants_profiles)
    print(f"   ✅ {len(enseignants_profiles)} profils enseignants créés")
    
    # 6. Créer des classes
    print("\n📚 Création des classes...")
    classes = []
    niveaux_primaire = [
        "1ere_annee_primaire", "2eme_annee_primaire", "3eme_annee_primaire",
        "4eme_annee_primaire", "5eme_annee_primaire", "6eme_annee_primaire"
    ]
    niveaux_secondaire = [
        "1ere_annee_secondaire", "2eme_annee_secondaire", "3eme_annee_secondaire",
        "4eme_annee_secondaire", "5eme_annee_secondaire", "6eme_annee_secondaire"
    ]
    
    niveau_labels = {
        "1ere_annee_primaire": "1ère Primaire",
        "2eme_annee_primaire": "2ème Primaire",
        "3eme_annee_primaire": "3ème Primaire",
        "4eme_annee_primaire": "4ème Primaire",
        "5eme_annee_primaire": "5ème Primaire",
        "6eme_annee_primaire": "6ème Primaire",
        "1ere_annee_secondaire": "1ère Secondaire",
        "2eme_annee_secondaire": "2ème Secondaire",
        "3eme_annee_secondaire": "3ème Secondaire",
        "4eme_annee_secondaire": "4ème Secondaire",
        "5eme_annee_secondaire": "5ème Secondaire",
        "6eme_annee_secondaire": "6ème Secondaire"
    }
    
    for etab in etablissements[:100]:  # Créer des classes pour 100 établissements
        if etab["type"] == "ecole_primaire":
            niveaux = niveaux_primaire
        else:
            niveaux = niveaux_secondaire
        
        for niveau in niveaux:
            classe = {
                "id": str(uuid.uuid4()),
                "nom": f"{niveau_labels[niveau]} A",
                "niveau": niveau,
                "etablissement_id": etab["id"],
                "professeur_principal_id": None,
                "annee_scolaire": "2024-2025",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            classes.append(classe)
    
    if classes:
        await db.classes.insert_many(classes)
    print(f"   ✅ {len(classes)} classes créées")
    
    # 7. Créer des profils élèves
    print("\n👨‍🎓 Création des profils élèves...")
    eleves_primaire = [u for u in all_users if u["role"] == "eleve_primaire"]
    eleves_secondaire = [u for u in all_users if u["role"] == "eleve_secondaire"]
    eleves_profiles = []
    ines_used = set()
    
    niveaux_primaire = [
        "1ere_annee_primaire", "2eme_annee_primaire", "3eme_annee_primaire",
        "4eme_annee_primaire", "5eme_annee_primaire", "6eme_annee_primaire"
    ]
    niveaux_secondaire = [
        "1ere_annee_secondaire", "2eme_annee_secondaire", "3eme_annee_secondaire",
        "4eme_annee_secondaire", "5eme_annee_secondaire", "6eme_annee_secondaire"
    ]
    
    # Élèves primaires
    for eleve_user in eleves_primaire:
        if eleve_user.get("etablissement_id"):
            ine = generate_ine(ines_used)
            niveau = random.choice(niveaux_primaire)
            sexe = random.choice(["masculin", "feminin"])
            
            # Trouver une classe correspondante
            classes_etab = [c for c in classes if c["etablissement_id"] == eleve_user["etablissement_id"] and c["niveau"] == niveau]
            classe_id = classes_etab[0]["id"] if classes_etab else None
            
            eleve_profile = {
                "id": str(uuid.uuid4()),
                "user_id": eleve_user["id"],
                "ine": ine,
                "etablissement_id": eleve_user["etablissement_id"],
                "classe_id": classe_id,
                "niveau": niveau,
                "sexe": sexe,
                "date_naissance": f"{random.randint(2014, 2018)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "lieu_naissance": random.choice(["Kinshasa", "Lubumbashi", "Goma", "Kisangani", "Bukavu", "Kananga", "Mbuji-Mayi"]),
                "parents_ids": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            eleves_profiles.append(eleve_profile)
    
    # Élèves secondaires
    for eleve_user in eleves_secondaire:
        if eleve_user.get("etablissement_id"):
            ine = generate_ine(ines_used)
            niveau = random.choice(niveaux_secondaire)
            sexe = random.choice(["masculin", "feminin"])
            
            # Trouver une classe correspondante
            classes_etab = [c for c in classes if c["etablissement_id"] == eleve_user["etablissement_id"] and c["niveau"] == niveau]
            classe_id = classes_etab[0]["id"] if classes_etab else None
            
            eleve_profile = {
                "id": str(uuid.uuid4()),
                "user_id": eleve_user["id"],
                "ine": ine,
                "etablissement_id": eleve_user["etablissement_id"],
                "classe_id": classe_id,
                "niveau": niveau,
                "sexe": sexe,
                "date_naissance": f"{random.randint(2006, 2012)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "lieu_naissance": random.choice(["Kinshasa", "Lubumbashi", "Goma", "Kisangani", "Bukavu", "Kananga", "Mbuji-Mayi"]),
                "parents_ids": [],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            eleves_profiles.append(eleve_profile)
    
    if eleves_profiles:
        await db.eleves.insert_many(eleves_profiles)
    
    # Compter par sexe
    nb_masculin = len([e for e in eleves_profiles if e["sexe"] == "masculin"])
    nb_feminin = len([e for e in eleves_profiles if e["sexe"] == "feminin"])
    print(f"   ✅ {len(eleves_profiles)} profils élèves créés")
    print(f"      • Masculin: {nb_masculin}")
    print(f"      • Féminin: {nb_feminin}")
    
    print("\n✨ Seed terminé avec succès!")
    print(f"\n📊 Résumé des données créées:")
    print(f"   • {len(provinces)} provinces administratives")
    print(f"   • {len(sous_divisions)} provinces éducationnelles")
    print(f"   • {len(all_users)} utilisateurs (10 par profil)")
    print(f"   • {len(etablissements)} établissements")
    print(f"   • {len(enseignants_profiles)} enseignants")
    print(f"   • {len(eleves_profiles)} élèves")
    print(f"   • {len(classes)} classes")
    
    # Stats par sexe
    enseignants_m = len([u for u in all_users if u["role"] == "enseignant" and u.get("sexe") == "masculin"])
    enseignants_f = len([u for u in all_users if u["role"] == "enseignant" and u.get("sexe") == "feminin"])
    directeurs_m = len([u for u in all_users if u["role"] in ["directeur_ecole", "chef_etablissement"] and u.get("sexe") == "masculin"])
    directeurs_f = len([u for u in all_users if u["role"] in ["directeur_ecole", "chef_etablissement"] and u.get("sexe") == "feminin"])
    
    print(f"\n👥 Répartition par sexe:")
    print(f"   Enseignants: {enseignants_m} hommes, {enseignants_f} femmes")
    print(f"   Directeurs: {directeurs_m} hommes, {directeurs_f} femmes")
    print(f"   Élèves: {nb_masculin} garçons, {nb_feminin} filles")
    
    print("\n📝 Exemples de comptes créés:")
    print("   • Admin: administrateur_technique.kabila1@rie.cd / password123")
    print("   • Ministre: ministre.tshisekedi1@rie.cd / password123")
    print("   • DPE: directeur_provincial.lumumba1@rie.cd / password123")
    print("   • Directeur: directeur_ecole.mobutu1@rie.cd / password123")
    print("   • Enseignant: enseignant.ngalula1@rie.cd / password123")
    print("   • Élève: eleve_primaire.kamanda1@rie.cd / password123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
