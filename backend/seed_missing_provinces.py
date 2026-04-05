"""
Script d'enrichissement des données pour les 16 provinces manquantes de la RDC.
Crée des établissements, classes, enseignants, élèves et notes pour chaque province.
IMPORTANT: Ne supprime PAS les données existantes.
"""
import asyncio
import os
import random
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'educonnect_rdc')

# Les 16 provinces sans données actuellement
PROVINCES_MANQUANTES = {
    "kwango": {
        "code": "KWG",
        "sous_divisions": ["Kenge", "Kasongo-Lunda", "Feshi", "Kahemba", "Popokabaka"]
    },
    "kwilu": {
        "code": "KWL",
        "sous_divisions": ["Kikwit", "Bandundu", "Bulungu", "Gungu", "Idiofa", "Mangai", "Bagata"]
    },
    "mai_ndombe": {
        "code": "MND",
        "sous_divisions": ["Inongo", "Nioki", "Kutu", "Kiri", "Oshwe", "Mushie"]
    },
    "mongala": {
        "code": "MGL",
        "sous_divisions": ["Lisala", "Bumba", "Bongandanga", "Pimu"]
    },
    "nord_ubangi": {
        "code": "NUB",
        "sous_divisions": ["Gbadolite", "Mobayi-Mbongo", "Yakoma", "Businga"]
    },
    "sud_ubangi": {
        "code": "SUB",
        "sous_divisions": ["Gemena", "Libenge", "Zongo", "Budjala", "Kungu"]
    },
    "tshuapa": {
        "code": "TSP",
        "sous_divisions": ["Boende", "Befale", "Djolu", "Ikela", "Monkoto"]
    },
    "bas_uele": {
        "code": "BUE",
        "sous_divisions": ["Buta", "Aketi", "Ango", "Bambesa", "Poko"]
    },
    "haut_uele": {
        "code": "HUE",
        "sous_divisions": ["Isiro", "Dungu", "Faradje", "Watsa", "Niangara", "Wamba"]
    },
    "maniema": {
        "code": "MAN",
        "sous_divisions": ["Kindu", "Kasongo", "Kabambare", "Pangi", "Punia", "Lubutu", "Kailo"]
    },
    "lualaba": {
        "code": "LUA",
        "sous_divisions": ["Kolwezi", "Dilolo", "Kapanga", "Lubudi", "Mutshatsha", "Sandoa"]
    },
    "tanganyika": {
        "code": "TAN",
        "sous_divisions": ["Kalemie", "Kongolo", "Moba", "Manono", "Nyunzu"]
    },
    "haut_lomami": {
        "code": "HLO",
        "sous_divisions": ["Kamina", "Kabongo", "Kaniama", "Malemba-Nkulu", "Bukama"]
    },
    "kasai": {
        "code": "KAS",
        "sous_divisions": ["Tshikapa", "Ilebo", "Luebo", "Mweka", "Dekese"]
    },
    "lomami": {
        "code": "LOM",
        "sous_divisions": ["Kabinda", "Mwene-Ditu", "Ngandajika", "Lubao", "Kamiji"]
    },
    "sankuru": {
        "code": "SAN",
        "sous_divisions": ["Lusambo", "Lodja", "Kole", "Lomela", "Katako-Kombe"]
    },
}

# Noms d'écoles réalistes RDC
NOMS_ECOLES_PRIMAIRES = [
    "EP Lumumba", "EP Kasa-Vubu", "EP Kimbangu", "EP Saint-Joseph", "EP Sainte-Marie",
    "EP Notre-Dame", "EP Saint-Pierre", "EP Elikya", "EP Boboto", "EP Bondeko",
    "EP La Colombe", "EP L'Avenir", "EP Le Progrès", "EP La Réussite", "EP Mapendo",
    "EP Tumaini", "EP Amani", "EP 30 Juin", "EP Mokili", "EP Bana ba Congo",
    "EP Bosembo", "EP Bolingo", "EP L'Excellence", "EP Libala", "EP Vijana"
]

NOMS_COLLEGES = [
    "CS Bosangani", "CS Bondeko", "CS Elikya", "Institut Lumumba", "Institut Kasa-Vubu",
    "Collège Saint-Joseph", "Collège Notre-Dame", "CS La Renaissance", "CS Le Flambeau",
    "CS L'Espérance", "Institut Technique Salama", "CS Bilingue", "CS Les Lauréats",
    "Athénée Royal", "Lycée Bosangani", "CS La Lumière", "Institut Mapendo"
]

NOMS_LYCEES = [
    "Lycée National", "Lycée Technique", "Lycée Bosangani", "Lycée Saint-Joseph",
    "Lycée de l'Excellence", "Lycée Le Savoir", "Lycée Scientifique",
    "Institut Supérieur Technique", "Lycée Elikya", "Lycée Bondeko"
]

PRENOMS_HOMMES = [
    "Jean", "Pierre", "Paul", "Joseph", "François", "Patrick", "Christian", "Didier",
    "Emmanuel", "David", "Samuel", "Daniel", "Michel", "André", "Moïse", "Élie",
    "Kabongo", "Mulongo", "Mukendi", "Kalombo", "Mbuyi", "Kasongo", "Ilunga", "Mutombo"
]

PRENOMS_FEMMES = [
    "Marie", "Jeanne", "Anne", "Claire", "Sophie", "Céline", "Nathalie", "Sylvie",
    "Chantal", "Monique", "Béatrice", "Espérance", "Grâce", "Divine", "Gloire",
    "Mwamba", "Tshala", "Nsimba", "Nzuzi", "Mujinga", "Kisimba", "Solange", "Pauline"
]

NOMS_FAMILLE = [
    "Lumumba", "Tshisekedi", "Kabila", "Katumbi", "Mukendi", "Kalombo", "Ngoyi",
    "Mutombo", "Ilunga", "Kasongo", "Mwamba", "Kabongo", "Mulongo", "Nsimba",
    "Luboya", "Ngoy", "Mwenze", "Kayembe", "Tshikala", "Mukamba", "Tshibangu",
    "Kalonji", "Mpiana", "Kazadi", "Ngandu", "Kabeya", "Mutamba", "Bukasa",
    "Nkongolo", "Banza", "Masamba", "Lukusa", "Mbuyu", "Mukalay", "Kabemba"
]

MATIERES_PRIMAIRE = [
    "Francais", "Mathematiques", "Sciences Naturelles",
    "Histoire", "Geographie", "Education Civique",
    "Education Physique", "Dessin", "Musique"
]

MATIERES_SECONDAIRE = [
    "Francais", "Mathematiques", "Physique", "Chimie",
    "Biologie", "Histoire", "Geographie",
    "Education Civique", "Anglais", "Philosophie",
    "Education Physique", "Informatique"
]

COEFFICIENTS_PRIMAIRE = {
    "Francais": 3, "Mathematiques": 3, "Sciences Naturelles": 2,
    "Histoire": 1, "Geographie": 1, "Education Civique": 1,
    "Education Physique": 1, "Dessin": 1, "Musique": 1
}

COEFFICIENTS_SECONDAIRE = {
    "Francais": 3, "Mathematiques": 4, "Physique": 3, "Chimie": 2,
    "Biologie": 2, "Histoire": 2, "Geographie": 2,
    "Education Civique": 1, "Anglais": 2, "Philosophie": 2,
    "Education Physique": 1, "Informatique": 2
}

GRADES_ENSEIGNANTS = ["D6", "D4", "G3", "L2", "A1", "A0"]
BANQUES_RDC = ["Rawbank", "Equity BCDC", "TMB", "FBN Bank", "Ecobank", "Standard Bank", "UBA"]
CATEGORIES = ["publique", "publique", "privee"]  # 66% publique
NIVEAUX_PRIMAIRE = [
    "1ere_annee_primaire", "2eme_annee_primaire", "3eme_annee_primaire",
    "4eme_annee_primaire", "5eme_annee_primaire", "6eme_annee_primaire"
]
NIVEAUX_COLLEGE = [
    "1ere_annee_secondaire", "2eme_annee_secondaire",
    "3eme_annee_secondaire", "4eme_annee_secondaire"
]
NIVEAUX_LYCEE = ["5eme_annee_secondaire", "6eme_annee_secondaire"]
TRIMESTRES = ["trimestre_1", "trimestre_2", "trimestre_3"]


def generate_note(profil="moyen"):
    if profil == "excellent":
        return round(max(0, min(20, random.gauss(16, 1.5))), 1)
    elif profil == "bon":
        return round(max(0, min(20, random.gauss(14, 2))), 1)
    elif profil == "moyen":
        return round(max(0, min(20, random.gauss(11, 2.5))), 1)
    elif profil == "faible":
        return round(max(0, min(20, random.gauss(7, 2))), 1)
    return round(max(0, min(20, random.gauss(10, 3))), 1)


async def seed_province(db, province_id, province_data):
    """Seed une province complète: établissements, classes, enseignants, élèves, notes"""
    code = province_data["code"]
    sous_divs = province_data["sous_divisions"]
    now = datetime.now(timezone.utc).isoformat()

    etab_list = []
    classes_list = []
    enseignants_list = []
    eleves_list = []
    notes_list = []
    bulletins_list = []

    etab_counter = 0
    mat_counter = 0
    ine_counter = 0

    for sous_div in sous_divs:
        sd_key = sous_div.lower().replace(" ", "_").replace("-", "_")

        # 2-4 ecoles primaires
        for _ in range(random.randint(2, 4)):
            etab_counter += 1
            etab_id = str(uuid.uuid4())
            nom = f"{random.choice(NOMS_ECOLES_PRIMAIRES)} {sous_div}"
            etab_list.append({
                "id": etab_id,
                "nom": nom,
                "type": "ecole_primaire",
                "categorie": random.choice(CATEGORIES),
                "code_etablissement": f"{code}-EP-{etab_counter:04d}",
                "adresse": f"Avenue {random.choice(['Lumumba','de la Paix','Principale','du Commerce'])} n{random.randint(1,200)}, {sous_div}",
                "province_id": province_id,
                "sous_division_id": sd_key,
                "directeur_id": None,
                "created_at": now,
                "derniere_maj_effectifs": None,
                "effectif_classes": 0,
                "effectif_eleves": 0,
                "effectif_enseignants": 0
            })

        # 1-2 colleges
        for _ in range(random.randint(1, 2)):
            etab_counter += 1
            etab_id = str(uuid.uuid4())
            nom = f"{random.choice(NOMS_COLLEGES)} {sous_div}"
            etab_list.append({
                "id": etab_id,
                "nom": nom,
                "type": "college",
                "categorie": random.choice(CATEGORIES),
                "code_etablissement": f"{code}-CS-{etab_counter:04d}",
                "adresse": f"Boulevard {random.choice(['du 30 Juin','Lumumba','Triomphal'])} n{random.randint(1,100)}, {sous_div}",
                "province_id": province_id,
                "sous_division_id": sd_key,
                "directeur_id": None,
                "created_at": now,
                "derniere_maj_effectifs": None,
                "effectif_classes": 0,
                "effectif_eleves": 0,
                "effectif_enseignants": 0
            })

        # 0-1 lycee (chef-lieu only or random)
        if sous_div == sous_divs[0] or random.random() > 0.6:
            etab_counter += 1
            etab_id = str(uuid.uuid4())
            nom = f"{random.choice(NOMS_LYCEES)} de {sous_div}"
            etab_list.append({
                "id": etab_id,
                "nom": nom,
                "type": "lycee",
                "categorie": random.choice(CATEGORIES),
                "code_etablissement": f"{code}-LY-{etab_counter:04d}",
                "adresse": f"Avenue {random.choice(['du Savoir','de l Excellence'])} n{random.randint(1,50)}, {sous_div}",
                "province_id": province_id,
                "sous_division_id": sd_key,
                "directeur_id": None,
                "created_at": now,
                "derniere_maj_effectifs": None,
                "effectif_classes": 0,
                "effectif_eleves": 0,
                "effectif_enseignants": 0
            })

    # Insert establishments
    if etab_list:
        await db.etablissements.insert_many(etab_list)

    # Now create classes, teachers, students, notes for each establishment
    for etab in etab_list:
        etab_type = etab["type"]
        etab_id = etab["id"]

        if etab_type == "ecole_primaire":
            niveaux = NIVEAUX_PRIMAIRE
            classes_par_niv = random.randint(1, 2)
            eleves_par_classe = random.randint(30, 50)
            matieres = MATIERES_PRIMAIRE
            coefficients = COEFFICIENTS_PRIMAIRE
        elif etab_type == "college":
            niveaux = NIVEAUX_COLLEGE
            classes_par_niv = random.randint(1, 2)
            eleves_par_classe = random.randint(35, 55)
            matieres = MATIERES_SECONDAIRE
            coefficients = COEFFICIENTS_SECONDAIRE
        else:
            niveaux = NIVEAUX_LYCEE
            classes_par_niv = random.randint(1, 3)
            eleves_par_classe = random.randint(30, 45)
            matieres = MATIERES_SECONDAIRE
            coefficients = COEFFICIENTS_SECONDAIRE

        etab_classes = []
        for niveau in niveaux:
            for i in range(classes_par_niv):
                lettre = chr(65 + i)
                classe_id = str(uuid.uuid4())
                classe = {
                    "id": classe_id,
                    "nom": f"{niveau.replace('_',' ').title()} {lettre}",
                    "niveau": niveau,
                    "etablissement_id": etab_id,
                    "annee_scolaire": "2025-2026",
                    "professeur_principal_id": None,
                    "created_at": now
                }
                classes_list.append(classe)
                etab_classes.append(classe)

        # Enseignants: 1 per class + 2 extras
        num_ens = len(etab_classes) + random.randint(1, 3)
        ens_ids = []
        for i in range(num_ens):
            mat_counter += 1
            sexe = random.choice(["masculin", "feminin"])
            prenom = random.choice(PRENOMS_HOMMES if sexe == "masculin" else PRENOMS_FEMMES)
            nom = random.choice(NOMS_FAMILLE)
            ens_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            ens_ids.append(ens_id)

            enseignants_list.append({
                "id": ens_id,
                "user_id": user_id,
                "matricule": f"SEC-{code}-{mat_counter:06d}",
                "etablissement_id": etab_id,
                "matieres": random.sample(matieres, min(3, len(matieres))),
                "est_professeur_principal": i < len(etab_classes),
                "classe_principale_id": etab_classes[i]["id"] if i < len(etab_classes) else None,
                "grade": random.choice(GRADES_ENSEIGNANTS),
                "adresse_personnelle": f"Avenue {random.choice(['Lumumba','de la Paix'])} n{random.randint(1,200)}",
                "telephone_personnel": f"+243 {random.choice(['081','082','083','097'])} {random.randint(100,999)} {random.randint(100,999)}",
                "email_personnel": f"{prenom.lower()}.{nom.lower()}{random.randint(1,99)}@gmail.com",
                "etat_civil": random.choice(["celibataire", "marie"]),
                "nombre_enfants": random.randint(0, 5),
                "conjoint_nom": "",
                "banque": random.choice(BANQUES_RDC),
                "numero_compte": f"{random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(100,999)}",
                "photo_url": None,
                "derniere_verification_dinacope": None,
                "derniere_verification_dinacope_id": None,
                "created_at": now,
                "nom": nom,
                "nom_complet": f"{prenom} {nom}",
                "postnom": random.choice(NOMS_FAMILLE),
                "prenom": prenom,
                "sexe": sexe
            })

            # Set prof principal on class
            if i < len(etab_classes):
                etab_classes[i]["professeur_principal_id"] = ens_id

        # Eleves for each class
        for classe in etab_classes:
            profils = ["excellent", "bon", "moyen", "moyen", "moyen", "faible"]
            for _ in range(eleves_par_classe):
                ine_counter += 1
                sexe = random.choice(["masculin", "feminin"])
                prenom = random.choice(PRENOMS_HOMMES if sexe == "masculin" else PRENOMS_FEMMES)
                nom = random.choice(NOMS_FAMILLE)
                eleve_id = str(uuid.uuid4())
                user_id = str(uuid.uuid4())

                is_primaire = "primaire" in classe["niveau"]
                age_min, age_max = (6, 14) if is_primaire else (12, 22)
                annee_naissance = 2026 - random.randint(age_min, age_max)
                date_naissance = f"{annee_naissance}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

                eleves_list.append({
                    "id": eleve_id,
                    "user_id": user_id,
                    "ine": f"INE-{code}-2025-{ine_counter:06d}",
                    "etablissement_id": etab_id,
                    "classe_id": classe["id"],
                    "niveau": classe["niveau"],
                    "sexe": sexe,
                    "date_naissance": date_naissance,
                    "lieu_naissance": random.choice(province_data["sous_divisions"]),
                    "created_at": now
                })

                # Notes pour cet élève (toutes matières, 3 trimestres)
                profil = random.choice(profils)
                ens_for_notes = random.choice(ens_ids) if ens_ids else None
                current_matieres = MATIERES_PRIMAIRE if is_primaire else MATIERES_SECONDAIRE
                current_coefficients = COEFFICIENTS_PRIMAIRE if is_primaire else COEFFICIENTS_SECONDAIRE

                notes_eleve_par_trimestre = {}
                for trimestre in TRIMESTRES:
                    notes_trimestre = []
                    for matiere in current_matieres:
                        note_val = generate_note(profil)
                        coeff = current_coefficients.get(matiere, 1)
                        note_id = str(uuid.uuid4())
                        notes_list.append({
                            "id": note_id,
                            "eleve_id": eleve_id,
                            "classe_id": classe["id"],
                            "matiere": matiere,
                            "note": note_val,
                            "coefficient": float(coeff),
                            "trimestre": trimestre,
                            "annee_scolaire": "2025-2026",
                            "enseignant_id": ens_for_notes,
                            "commentaire": None,
                            "created_at": now
                        })
                        notes_trimestre.append({"matiere": matiere, "note": note_val, "coeff": coeff})
                    notes_eleve_par_trimestre[trimestre] = notes_trimestre

                # Bulletin pour chaque trimestre
                for trimestre in TRIMESTRES:
                    notes_t = notes_eleve_par_trimestre[trimestre]
                    total_pts = sum(n["note"] * n["coeff"] for n in notes_t)
                    total_coeff = sum(n["coeff"] for n in notes_t)
                    moyenne = round(total_pts / total_coeff, 2) if total_coeff > 0 else 0

                    if moyenne >= 16:
                        appreciation = "Excellent"
                    elif moyenne >= 14:
                        appreciation = "Très Bien"
                    elif moyenne >= 12:
                        appreciation = "Bien"
                    elif moyenne >= 10:
                        appreciation = "Assez Bien"
                    elif moyenne >= 8:
                        appreciation = "Passable"
                    else:
                        appreciation = "Insuffisant"

                    bulletins_list.append({
                        "id": str(uuid.uuid4()),
                        "eleve_id": eleve_id,
                        "classe_id": classe["id"],
                        "trimestre": trimestre,
                        "annee_scolaire": "2025-2026",
                        "moyenne_generale": moyenne,
                        "appreciation": appreciation,
                        "rang": None,
                        "notes_detail": [{"matiere": n["matiere"], "note": n["note"], "coefficient": n["coeff"]} for n in notes_t],
                        "created_at": now
                    })

    # Batch insert all data
    if classes_list:
        await db.classes.insert_many(classes_list)
    if enseignants_list:
        await db.enseignants.insert_many(enseignants_list)

    # Insert eleves in batches of 3000
    for i in range(0, len(eleves_list), 3000):
        batch = eleves_list[i:i+3000]
        await db.eleves.insert_many(batch)

    # Insert notes in batches of 5000
    for i in range(0, len(notes_list), 5000):
        batch = notes_list[i:i+5000]
        await db.notes.insert_many(batch)

    # Insert bulletins in batches of 3000
    for i in range(0, len(bulletins_list), 3000):
        batch = bulletins_list[i:i+3000]
        await db.bulletins.insert_many(batch)

    return {
        "etablissements": len(etab_list),
        "classes": len(classes_list),
        "enseignants": len(enseignants_list),
        "eleves": len(eleves_list),
        "notes": len(notes_list),
        "bulletins": len(bulletins_list)
    }


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Verify which provinces already have data
    existing = set()
    async for doc in db.etablissements.aggregate([{"$group": {"_id": "$province_id"}}]):
        existing.add(doc["_id"])

    print(f"Provinces avec données existantes: {len(existing)}")
    print(f"Provinces à peupler: {len(PROVINCES_MANQUANTES)}")

    totaux = {"etablissements": 0, "classes": 0, "enseignants": 0, "eleves": 0, "notes": 0, "bulletins": 0}

    for prov_id, prov_data in PROVINCES_MANQUANTES.items():
        if prov_id in existing:
            print(f"  {prov_id}: données déjà présentes, ignoré")
            continue

        print(f"  Seeding {prov_id} ({prov_data['code']})...")
        result = await seed_province(db, prov_id, prov_data)
        for k, v in result.items():
            totaux[k] += v
        print(f"    -> {result['etablissements']} etabs, {result['classes']} classes, "
              f"{result['enseignants']} ens, {result['eleves']} elv, {result['notes']} notes")

    print(f"\nTotaux ajoutés:")
    for k, v in totaux.items():
        print(f"  {k}: {v}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
