"""
Script de création d'établissements scolaires de la RDC
Données basées sur la structure SECOPE/DINACOPE
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from models import Etablissement, TypeEtablissement, CategorieEtablissement
import os
from dotenv import load_dotenv
import random

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Données des provinces RDC avec leurs sous-divisions
PROVINCES_DATA = {
    "kinshasa": {
        "nom": "Kinshasa",
        "code": "KIN",
        "sous_divisions": ["Gombe", "Lingwala", "Barumbu", "Kinshasa", "Kintambo", "Ngaliema", "Mont-Ngafula", "Selembao", "Bumbu", "Makala", "Ngiri-Ngiri", "Kalamu", "Lemba", "Limete", "Matete", "Ndjili", "Kimbanseke", "Masina", "Nsele", "Maluku"]
    },
    "kongo_central": {
        "nom": "Kongo Central",
        "code": "KGC",
        "sous_divisions": ["Matadi", "Boma", "Muanda", "Lukula", "Tshela", "Seke-Banza", "Luozi", "Songololo", "Mbanza-Ngungu", "Madimba", "Kasangulu", "Kimvula"]
    },
    "nord_kivu": {
        "nom": "Nord-Kivu",
        "code": "NKV",
        "sous_divisions": ["Goma", "Beni", "Butembo", "Masisi", "Rutshuru", "Nyiragongo", "Lubero", "Walikale"]
    },
    "sud_kivu": {
        "nom": "Sud-Kivu",
        "code": "SKV",
        "sous_divisions": ["Bukavu", "Uvira", "Kabare", "Walungu", "Kalehe", "Idjwi", "Shabunda", "Mwenga", "Fizi"]
    },
    "haut_katanga": {
        "nom": "Haut-Katanga",
        "code": "HKT",
        "sous_divisions": ["Lubumbashi", "Likasi", "Kipushi", "Kambove", "Sakania", "Pweto", "Mitwaba"]
    },
    "kasai_central": {
        "nom": "Kasaï-Central",
        "code": "KAC",
        "sous_divisions": ["Kananga", "Demba", "Dibaya", "Dimbelenge", "Kazumba", "Luiza"]
    },
    "kasai_oriental": {
        "nom": "Kasaï-Oriental",
        "code": "KAO",
        "sous_divisions": ["Mbuji-Mayi", "Tshilenge", "Miabi", "Kabeya-Kamwanga", "Katanda", "Lupatapata"]
    },
    "equateur": {
        "nom": "Équateur",
        "code": "EQU",
        "sous_divisions": ["Mbandaka", "Bikoro", "Ingende", "Bolomba", "Basankusu", "Bomongo"]
    },
    "tshopo": {
        "nom": "Tshopo",
        "code": "TSH",
        "sous_divisions": ["Kisangani", "Isangi", "Yahuma", "Basoko", "Banalia", "Bafwasende", "Ubundu"]
    },
    "ituri": {
        "nom": "Ituri",
        "code": "ITU",
        "sous_divisions": ["Bunia", "Aru", "Mahagi", "Djugu", "Irumu", "Mambasa"]
    }
}

# Noms d'écoles réalistes RDC
NOMS_ECOLES_PRIMAIRES = [
    "EP Lumumba", "EP Mobutu", "EP Kasa-Vubu", "EP Mulele", "EP Kimbangu",
    "EP Saint-Joseph", "EP Sainte-Marie", "EP Notre-Dame", "EP Saint-Pierre", "EP Saint-Paul",
    "EP Elikya", "EP Boboto", "EP Bondeko", "EP Bolingo", "EP Bosembo",
    "EP La Colombe", "EP L'Avenir", "EP Le Progrès", "EP La Réussite", "EP L'Excellence",
    "EP Mapendo", "EP Tumaini", "EP Amani", "EP Upendo", "EP Furaha",
    "EP 1er Mai", "EP 30 Juin", "EP 24 Novembre", "EP 17 Mai", "EP 4 Janvier",
    "EP Mokili", "EP Mboka", "EP Ndako", "EP Libala", "EP Masanga",
    "EP Bana ba Congo", "EP Wana wa Afrika", "EP Vijana", "EP Watoto", "EP Mwana"
]

NOMS_COLLEGES = [
    "CS Bosangani", "CS Bondeko", "CS Elikya", "CS Boboto", "CS Bolingo",
    "Institut Lumumba", "Institut Mobutu", "Institut Kasa-Vubu", "Institut Kimbangu", "Institut Mulele",
    "Collège Saint-Joseph", "Collège Sainte-Marie", "Collège Notre-Dame", "Collège Saint-Pierre", "Collège Boboto",
    "CS La Renaissance", "CS Le Flambeau", "CS L'Espérance", "CS La Lumière", "CS Le Savoir",
    "Institut Technique Salama", "Institut Technique Mapendo", "Institut Technique Amani",
    "CS Bilingue Kinshasa", "CS Excellence Plus", "CS Les Lauréats", "CS L'Étoile",
    "Athénée de Kinshasa", "Lycée Bosangani", "Lycée Elikya"
]

NOMS_LYCEES = [
    "Lycée Lumumba", "Lycée Mobutu", "Lycée Kasa-Vubu", "Lycée National",
    "Lycée Technique de Kinshasa", "Lycée Technique de Lubumbashi", "Lycée Technique de Goma",
    "Lycée Bosangani", "Lycée Elikya", "Lycée Bondeko", "Lycée Boboto",
    "Lycée Saint-Joseph", "Lycée Sainte-Marie", "Lycée Notre-Dame du Congo",
    "Lycée de l'Excellence", "Lycée La Réussite", "Lycée Le Savoir",
    "Institut Supérieur Technique", "Institut de Formation Professionnelle",
    "Lycée Scientifique National", "Lycée des Sciences et Technologies"
]

# Codes SECOPE simulés
def generate_esecope_code(province_code, type_etab, num):
    type_code = {"ecole_primaire": "EP", "college": "CS", "lycee": "LY"}
    return f"{province_code}-{type_code.get(type_etab, 'ET')}-{num:04d}"


async def create_etablissements():
    """Créer des établissements scolaires réalistes"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Vérifier si des établissements existent déjà
    count = await db.etablissements.count_documents({})
    if count > 0:
        print(f"⚠️  {count} établissements existent déjà. Ajout de nouveaux établissements...")
    
    etablissements = []
    esecope_counter = {}
    
    for province_id, province_data in PROVINCES_DATA.items():
        province_code = province_data["code"]
        esecope_counter[province_code] = esecope_counter.get(province_code, 0)
        
        # Créer des établissements pour chaque sous-division
        for sous_div in province_data["sous_divisions"]:
            # 3-5 écoles primaires par sous-division
            num_primaires = random.randint(3, 5)
            for i in range(num_primaires):
                esecope_counter[province_code] += 1
                nom_base = random.choice(NOMS_ECOLES_PRIMAIRES)
                nom = f"{nom_base} {sous_div}" if random.random() > 0.5 else f"{nom_base} {i+1}"
                
                etab = Etablissement(
                    nom=nom,
                    type=TypeEtablissement.ECOLE_PRIMAIRE,
                    categorie=random.choice([CategorieEtablissement.PUBLIQUE, CategorieEtablissement.PUBLIQUE, CategorieEtablissement.PRIVEE]),  # 66% publique
                    code_etablissement=generate_esecope_code(province_code, "ecole_primaire", esecope_counter[province_code]),
                    adresse=f"Avenue {random.choice(['Lumumba', 'Mobutu', 'Kasa-Vubu', 'Principale', 'de la Paix', 'du Commerce', 'des Écoles'])} n°{random.randint(1, 200)}, {sous_div}",
                    province_id=province_id,
                    sous_division_id=sous_div.lower().replace(" ", "_").replace("-", "_")
                )
                etablissements.append(etab.model_dump())
            
            # 1-3 collèges par sous-division
            num_colleges = random.randint(1, 3)
            for i in range(num_colleges):
                esecope_counter[province_code] += 1
                nom_base = random.choice(NOMS_COLLEGES)
                nom = f"{nom_base} {sous_div}" if random.random() > 0.5 else nom_base
                
                etab = Etablissement(
                    nom=nom,
                    type=TypeEtablissement.COLLEGE,
                    categorie=random.choice([CategorieEtablissement.PUBLIQUE, CategorieEtablissement.PRIVEE]),
                    code_etablissement=generate_esecope_code(province_code, "college", esecope_counter[province_code]),
                    adresse=f"Boulevard {random.choice(['du 30 Juin', 'Lumumba', 'Triomphal', 'de la Révolution', 'des Nations'])} n°{random.randint(1, 100)}, {sous_div}",
                    province_id=province_id,
                    sous_division_id=sous_div.lower().replace(" ", "_").replace("-", "_")
                )
                etablissements.append(etab.model_dump())
            
            # 0-1 lycée par sous-division (seulement dans les grandes villes)
            if sous_div in ["Gombe", "Lubumbashi", "Goma", "Bukavu", "Mbuji-Mayi", "Kananga", "Kisangani", "Matadi", "Mbandaka", "Bunia"] or random.random() > 0.7:
                esecope_counter[province_code] += 1
                nom_base = random.choice(NOMS_LYCEES)
                nom = f"{nom_base} de {sous_div}" if random.random() > 0.5 else nom_base
                
                avenues_lycee = ["de l'Université", "du Savoir", "de l'Excellence", "des Étudiants"]
                etab = Etablissement(
                    nom=nom,
                    type=TypeEtablissement.LYCEE,
                    categorie=random.choice([CategorieEtablissement.PUBLIQUE, CategorieEtablissement.PUBLIQUE, CategorieEtablissement.PRIVEE]),
                    code_etablissement=generate_esecope_code(province_code, "lycee", esecope_counter[province_code]),
                    adresse=f"Avenue {random.choice(avenues_lycee)} n°{random.randint(1, 50)}, {sous_div}",
                    province_id=province_id,
                    sous_division_id=sous_div.lower().replace(" ", "_").replace("-", "_")
                )
                etablissements.append(etab.model_dump())
    
    # Insérer tous les établissements
    if etablissements:
        result = await db.etablissements.insert_many(etablissements)
        print(f"✅ {len(result.inserted_ids)} établissements créés avec succès!")
        
        # Statistiques
        primaires = len([e for e in etablissements if e["type"] == "ecole_primaire"])
        colleges = len([e for e in etablissements if e["type"] == "college"])
        lycees = len([e for e in etablissements if e["type"] == "lycee"])
        publiques = len([e for e in etablissements if e["categorie"] == "publique"])
        privees = len([e for e in etablissements if e["categorie"] == "privee"])
        
        print(f"\n📊 Répartition:")
        print(f"   - Écoles primaires: {primaires}")
        print(f"   - Collèges: {colleges}")
        print(f"   - Lycées: {lycees}")
        print(f"   - Établissements publics: {publiques}")
        print(f"   - Établissements privés: {privees}")
        print(f"   - Provinces couvertes: {len(PROVINCES_DATA)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_etablissements())
