"""
Script de création d'enseignants, élèves et classes pour Édu-Connect
Données basées sur la structure SECOPE/DINACOPE de la RDC
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from models import (
    Enseignant, Eleve, Classe, User, NiveauScolaire, Sexe,
    TypeEtablissement
)
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timezone
import uuid

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Prénoms congolais courants
PRENOMS_HOMMES = [
    "Jean", "Pierre", "Paul", "Joseph", "François", "Patrick", "Christian", "Didier",
    "Emmanuel", "David", "Samuel", "Daniel", "Michel", "Jacques", "André", "Léon",
    "Albert", "Robert", "Richard", "Serge", "Alain", "Bernard", "Claude", "Gaston",
    "Moïse", "Élie", "Noé", "Isaac", "Jacob", "Josué", "Caleb", "Gédéon",
    "Kabongo", "Mulongo", "Tshisekedi", "Katumbi", "Mukendi", "Kalombo", "Mbaya", "Ngoyi",
    "Mbuyi", "Tshilombo", "Kasongo", "Ilunga", "Mutombo", "Dikembe", "Lokombe", "Lisanga"
]

PRENOMS_FEMMES = [
    "Marie", "Jeanne", "Anne", "Claire", "Sophie", "Céline", "Nathalie", "Sylvie",
    "Chantal", "Monique", "Béatrice", "Véronique", "Christine", "Catherine", "Patricia", "Brigitte",
    "Henriette", "Jacqueline", "Georgette", "Angélique", "Espérance", "Grâce", "Divine", "Gloire",
    "Mireille", "Solange", "Odette", "Pauline", "Bernadette", "Clémentine", "Joséphine", "Marguerite",
    "Mwamba", "Kabila", "Tshala", "Mbombo", "Nsimba", "Nzuzi", "Mujinga", "Kisimba"
]

NOMS_FAMILLE = [
    "Lumumba", "Mobutu", "Kabila", "Tshisekedi", "Kasa-Vubu", "Mulele", "Kimbangu", "Kasavubu",
    "Mbuji", "Nkunda", "Bemba", "Katumbi", "Mukendi", "Kalombo", "Mbaya", "Ngoyi",
    "Mutombo", "Dikembe", "Ilunga", "Kasongo", "Mwamba", "Kabongo", "Mulongo", "Tshilombo",
    "Lokombe", "Lisanga", "Nsimba", "Nzuzi", "Mujinga", "Kisimba", "Mbombo", "Tshala",
    "Luboya", "Ngoy", "Mwenze", "Kayembe", "Tshikala", "Mukamba", "Tshibangu", "Mbuyu",
    "Kalonji", "Mpiana", "Kazadi", "Mukalay", "Mwilambwe", "Ngandu", "Kabeya", "Mutamba",
    "Bukasa", "Nkongolo", "Kabemba", "Mwana", "Banza", "Kimpanga", "Masamba", "Lukusa"
]

# Matières enseignées
MATIERES_PRIMAIRE = [
    "Français", "Mathématiques", "Éveil scientifique", "Éducation civique",
    "Éducation physique", "Dessin", "Musique", "Lingala", "Swahili"
]

MATIERES_SECONDAIRE = [
    "Français", "Mathématiques", "Physique", "Chimie", "Biologie", "Géographie",
    "Histoire", "Éducation civique", "Anglais", "Philosophie", "Informatique",
    "Économie", "Éducation physique", "Latin", "Lingala", "Swahili"
]

# Grades enseignants SECOPE
GRADES_ENSEIGNANTS = [
    "D6", "D4", "G3", "L2", "A1", "A0"
]

# Banques RDC
BANQUES_RDC = [
    "Rawbank", "Equity BCDC", "TMB", "FBN Bank", "Ecobank", "Standard Bank",
    "Access Bank", "UBA", "Sofibanque", "BCDC"
]

# Lieux de naissance
LIEUX_NAISSANCE = [
    "Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kananga", "Kisangani", "Goma", "Bukavu",
    "Matadi", "Kikwit", "Kolwezi", "Likasi", "Tshikapa", "Bunia", "Mbandaka",
    "Uvira", "Boma", "Kalemie", "Beni", "Butembo", "Isiro"
]


def generate_matricule_secope(province_code, num):
    """Génère un matricule SECOPE réaliste"""
    return f"SEC-{province_code}-{num:06d}"


def generate_ine(province_code, annee, num):
    """Génère un INE (Identifiant National Élève)"""
    return f"INE-{province_code}-{annee}-{num:06d}"


def generate_phone():
    """Génère un numéro de téléphone congolais"""
    prefixes = ["081", "082", "083", "084", "085", "089", "097", "099"]
    return f"+243 {random.choice(prefixes)} {random.randint(100, 999)} {random.randint(100, 999)}"


def generate_compte_bancaire():
    """Génère un numéro de compte bancaire"""
    return f"{random.randint(1000, 9999)}-{random.randint(10000, 99999)}-{random.randint(100, 999)}"


def random_date_naissance(min_age, max_age):
    """Génère une date de naissance aléatoire"""
    annee = 2026 - random.randint(min_age, max_age)
    mois = random.randint(1, 12)
    jour = random.randint(1, 28)
    return f"{annee}-{mois:02d}-{jour:02d}"


async def create_enseignants_eleves_classes():
    """Créer des enseignants, élèves et classes"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Récupérer les établissements
    etablissements = await db.etablissements.find({}, {"_id": 0}).to_list(1000)
    
    if not etablissements:
        print("❌ Aucun établissement trouvé. Exécutez d'abord seed_etablissements.py")
        return
    
    print(f"📚 {len(etablissements)} établissements trouvés")
    
    # Compteurs
    total_enseignants = 0
    total_eleves = 0
    total_classes = 0
    matricule_counter = {}
    ine_counter = {}
    
    classes_list = []
    enseignants_list = []
    eleves_list = []
    users_list = []
    
    for etab in etablissements:
        province_code = etab["code_etablissement"].split("-")[0]
        matricule_counter[province_code] = matricule_counter.get(province_code, 0)
        ine_counter[province_code] = ine_counter.get(province_code, 0)
        
        # Déterminer le nombre de classes selon le type
        if etab["type"] == "ecole_primaire":
            niveaux = [
                NiveauScolaire.PRIMAIRE_1, NiveauScolaire.PRIMAIRE_2,
                NiveauScolaire.PRIMAIRE_3, NiveauScolaire.PRIMAIRE_4,
                NiveauScolaire.PRIMAIRE_5, NiveauScolaire.PRIMAIRE_6
            ]
            classes_par_niveau = random.randint(1, 2)
            eleves_par_classe = random.randint(35, 55)
            matieres = MATIERES_PRIMAIRE
        elif etab["type"] == "college":
            niveaux = [
                NiveauScolaire.SECONDAIRE_1, NiveauScolaire.SECONDAIRE_2,
                NiveauScolaire.SECONDAIRE_3, NiveauScolaire.SECONDAIRE_4
            ]
            classes_par_niveau = random.randint(1, 3)
            eleves_par_classe = random.randint(40, 60)
            matieres = MATIERES_SECONDAIRE
        else:  # lycee
            niveaux = [
                NiveauScolaire.SECONDAIRE_5, NiveauScolaire.SECONDAIRE_6
            ]
            classes_par_niveau = random.randint(2, 4)
            eleves_par_classe = random.randint(35, 50)
            matieres = MATIERES_SECONDAIRE
        
        # Créer les classes
        classes_etab = []
        for niveau in niveaux:
            for i in range(classes_par_niveau):
                lettre = chr(65 + i)  # A, B, C...
                niveau_nom = niveau.value.replace("_", " ").title()
                
                classe = Classe(
                    nom=f"{niveau_nom} {lettre}",
                    niveau=niveau,
                    etablissement_id=etab["id"],
                    annee_scolaire="2025-2026"
                )
                classes_list.append(classe.model_dump())
                classes_etab.append(classe)
                total_classes += 1
        
        # Créer les enseignants (1-2 par classe + quelques suppléants)
        num_enseignants = len(classes_etab) + random.randint(2, 5)
        
        for i in range(num_enseignants):
            matricule_counter[province_code] += 1
            
            # Créer un user pour l'enseignant
            sexe = random.choice([Sexe.MASCULIN, Sexe.FEMININ])
            prenom = random.choice(PRENOMS_HOMMES if sexe == Sexe.MASCULIN else PRENOMS_FEMMES)
            nom = random.choice(NOMS_FAMILLE)
            
            user_id = str(uuid.uuid4())
            user = {
                "id": user_id,
                "nom": nom,
                "prenom": prenom,
                "postnom": random.choice(NOMS_FAMILLE),
                "sexe": sexe.value,
                "etat_civil": random.choice(["celibataire", "marie", "divorce", "veuf"]),
                "date_naissance": random_date_naissance(25, 60),
                "lieu_naissance": random.choice(LIEUX_NAISSANCE),
                "telephone": generate_phone(),
                "email": f"{prenom.lower()}.{nom.lower()}@educonnect.cd",
                "role": "enseignant",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            users_list.append(user)
            
            # Assigner comme prof principal si possible
            est_prof_principal = i < len(classes_etab)
            classe_principale = classes_etab[i] if est_prof_principal else None
            
            enseignant = Enseignant(
                user_id=user_id,
                matricule=generate_matricule_secope(province_code, matricule_counter[province_code]),
                etablissement_id=etab["id"],
                matieres=random.sample(matieres, min(3, len(matieres))),
                est_professeur_principal=est_prof_principal,
                classe_principale_id=classe_principale.id if classe_principale else None,
                grade=random.choice(GRADES_ENSEIGNANTS),
                adresse_personnelle=f"Avenue {random.choice(['Lumumba', 'Kasa-Vubu', 'Mobutu', 'de la Paix'])} n°{random.randint(1, 200)}",
                telephone_personnel=generate_phone(),
                email_personnel=f"{prenom.lower()}.{nom.lower()}@gmail.com",
                etat_civil=user["etat_civil"],
                nombre_enfants=random.randint(0, 6),
                banque=random.choice(BANQUES_RDC),
                numero_compte=generate_compte_bancaire()
            )
            enseignants_list.append(enseignant.model_dump())
            
            # Mettre à jour la classe avec le prof principal
            if classe_principale:
                for c in classes_list:
                    if c["id"] == classe_principale.id:
                        c["professeur_principal_id"] = enseignant.id
            
            total_enseignants += 1
        
        # Créer les élèves pour chaque classe
        for classe in classes_etab:
            # Nombre d'élèves par classe
            num_eleves = eleves_par_classe
            
            for j in range(num_eleves):
                ine_counter[province_code] += 1
                
                sexe = random.choice([Sexe.MASCULIN, Sexe.FEMININ])
                prenom = random.choice(PRENOMS_HOMMES if sexe == Sexe.MASCULIN else PRENOMS_FEMMES)
                nom = random.choice(NOMS_FAMILLE)
                
                # Âge selon le niveau
                if "primaire" in classe.niveau.value:
                    age_min, age_max = 6, 14
                else:
                    age_min, age_max = 12, 22
                
                user_id = str(uuid.uuid4())
                user = {
                    "id": user_id,
                    "nom": nom,
                    "prenom": prenom,
                    "postnom": random.choice(NOMS_FAMILLE),
                    "sexe": sexe.value,
                    "date_naissance": random_date_naissance(age_min, age_max),
                    "lieu_naissance": random.choice(LIEUX_NAISSANCE),
                    "telephone": generate_phone() if random.random() > 0.7 else "",
                    "email": f"{prenom.lower()}.{nom.lower()}.eleve@educonnect.cd" if random.random() > 0.5 else "",
                    "role": "eleve",
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                users_list.append(user)
                
                eleve = Eleve(
                    user_id=user_id,
                    ine=generate_ine(province_code, "2025", ine_counter[province_code]),
                    etablissement_id=etab["id"],
                    classe_id=classe.id,
                    niveau=classe.niveau,
                    sexe=sexe,
                    date_naissance=user["date_naissance"],
                    lieu_naissance=user["lieu_naissance"]
                )
                eleves_list.append(eleve.model_dump())
                total_eleves += 1
        
        # Limiter pour éviter trop de données (prendre 1 établissement sur 5)
        if total_eleves > 15000:
            print(f"⚠️  Limite atteinte, arrêt de la génération")
            break
    
    # Insérer les données en batch
    print(f"\n📝 Insertion des données...")
    
    if classes_list:
        await db.classes.insert_many(classes_list)
        print(f"   ✅ {len(classes_list)} classes créées")
    
    if enseignants_list:
        await db.enseignants.insert_many(enseignants_list)
        print(f"   ✅ {len(enseignants_list)} enseignants créés")
    
    if eleves_list:
        # Insérer par lots de 5000
        batch_size = 5000
        for i in range(0, len(eleves_list), batch_size):
            batch = eleves_list[i:i+batch_size]
            await db.eleves.insert_many(batch)
            print(f"   ✅ {len(batch)} élèves insérés (batch {i//batch_size + 1})")
    
    # Statistiques finales
    print(f"\n📊 Résumé:")
    print(f"   - Classes: {total_classes}")
    print(f"   - Enseignants: {total_enseignants}")
    print(f"   - Élèves: {total_eleves}")
    
    # Répartition par sexe des élèves
    masculins = len([e for e in eleves_list if e["sexe"] == "masculin"])
    feminins = len([e for e in eleves_list if e["sexe"] == "feminin"])
    print(f"   - Garçons: {masculins} ({masculins*100//total_eleves if total_eleves else 0}%)")
    print(f"   - Filles: {feminins} ({feminins*100//total_eleves if total_eleves else 0}%)")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_enseignants_eleves_classes())
