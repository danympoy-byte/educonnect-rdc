"""
Script d'enrichissement léger pour les provinces manquantes restantes.
Traite par établissement pour limiter l'usage mémoire.
"""
import asyncio, os, random, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'educonnect_rdc')

PROVINCES_RESTANTES = {
    "maniema": {"code": "MAN", "sous_divisions": ["Kindu", "Kasongo", "Kabambare", "Pangi", "Punia", "Lubutu", "Kailo"]},
    "lualaba": {"code": "LUA", "sous_divisions": ["Kolwezi", "Dilolo", "Kapanga", "Lubudi", "Mutshatsha", "Sandoa"]},
    "tanganyika": {"code": "TAN", "sous_divisions": ["Kalemie", "Kongolo", "Moba", "Manono", "Nyunzu"]},
    "haut_lomami": {"code": "HLO", "sous_divisions": ["Kamina", "Kabongo", "Kaniama", "Malemba-Nkulu", "Bukama"]},
    "kasai": {"code": "KAS", "sous_divisions": ["Tshikapa", "Ilebo", "Luebo", "Mweka", "Dekese"]},
    "lomami": {"code": "LOM", "sous_divisions": ["Kabinda", "Mwene-Ditu", "Ngandajika", "Lubao", "Kamiji"]},
    "sankuru": {"code": "SAN", "sous_divisions": ["Lusambo", "Lodja", "Kole", "Lomela", "Katako-Kombe"]},
}

NOMS_EP = ["EP Lumumba","EP Kasa-Vubu","EP Kimbangu","EP Saint-Joseph","EP Elikya","EP Boboto","EP Bondeko","EP La Colombe","EP L'Avenir","EP Mapendo","EP Tumaini","EP Amani","EP Bosembo","EP Bolingo","EP Vijana"]
NOMS_CS = ["CS Bosangani","CS Bondeko","CS Elikya","Institut Lumumba","Collège Saint-Joseph","CS La Renaissance","CS Le Flambeau","CS L'Espérance","Institut Technique Salama","CS Les Lauréats"]
NOMS_LY = ["Lycée National","Lycée Technique","Lycée Bosangani","Lycée Saint-Joseph","Lycée de l'Excellence","Lycée Scientifique","Lycée Elikya"]
PH = ["Jean","Pierre","Paul","Joseph","Emmanuel","David","Samuel","Kabongo","Mulongo","Mukendi","Kalombo","Mbuyi","Kasongo","Ilunga"]
PF = ["Marie","Jeanne","Anne","Claire","Sophie","Espérance","Grâce","Divine","Mwamba","Tshala","Nsimba","Nzuzi","Mujinga","Solange"]
NF = ["Lumumba","Tshisekedi","Kabila","Katumbi","Mukendi","Kalombo","Ngoyi","Mutombo","Ilunga","Kasongo","Mwamba","Kabongo","Mulongo","Nsimba","Luboya","Ngoy","Kayembe","Tshikala","Kalonji","Mpiana","Kazadi","Ngandu","Kabeya"]
MAT_P = ["Francais","Mathematiques","Sciences Naturelles","Histoire","Geographie","Education Civique","Education Physique","Dessin","Musique"]
MAT_S = ["Francais","Mathematiques","Physique","Chimie","Biologie","Histoire","Geographie","Education Civique","Anglais","Philosophie","Education Physique","Informatique"]
COEF_P = {"Francais":3,"Mathematiques":3,"Sciences Naturelles":2,"Histoire":1,"Geographie":1,"Education Civique":1,"Education Physique":1,"Dessin":1,"Musique":1}
COEF_S = {"Francais":3,"Mathematiques":4,"Physique":3,"Chimie":2,"Biologie":2,"Histoire":2,"Geographie":2,"Education Civique":1,"Anglais":2,"Philosophie":2,"Education Physique":1,"Informatique":2}
GRADES = ["D6","D4","G3","L2","A1","A0"]
BANQUES = ["Rawbank","Equity BCDC","TMB","Ecobank","UBA"]
NIV_P = ["1ere_annee_primaire","2eme_annee_primaire","3eme_annee_primaire","4eme_annee_primaire","5eme_annee_primaire","6eme_annee_primaire"]
NIV_C = ["1ere_annee_secondaire","2eme_annee_secondaire","3eme_annee_secondaire","4eme_annee_secondaire"]
NIV_L = ["5eme_annee_secondaire","6eme_annee_secondaire"]
TRIM = ["trimestre_1","trimestre_2","trimestre_3"]

def gen_note(p="moyen"):
    if p=="excellent": return round(max(0,min(20,random.gauss(16,1.5))),1)
    elif p=="bon": return round(max(0,min(20,random.gauss(14,2))),1)
    elif p=="moyen": return round(max(0,min(20,random.gauss(11,2.5))),1)
    elif p=="faible": return round(max(0,min(20,random.gauss(7,2))),1)
    return round(max(0,min(20,random.gauss(10,3))),1)

async def seed_etab(db, etab, code):
    """Seed one establishment: classes, teachers, students, notes - insert immediately"""
    now = datetime.now(timezone.utc).isoformat()
    et = etab["type"]
    eid = etab["id"]
    is_p = et == "ecole_primaire"
    nivs = NIV_P if is_p else (NIV_C if et=="college" else NIV_L)
    cpn = random.randint(1,2)
    epn = random.randint(25,40)
    mats = MAT_P if is_p else MAT_S
    coefs = COEF_P if is_p else COEF_S

    classes = []
    for niv in nivs:
        for i in range(cpn):
            cid = str(uuid.uuid4())
            classes.append({"id":cid,"nom":f"{niv.replace('_',' ').title()} {chr(65+i)}","niveau":niv,"etablissement_id":eid,"annee_scolaire":"2025-2026","professeur_principal_id":None,"created_at":now})

    if classes:
        await db.classes.insert_many(classes)

    # Teachers
    ne = len(classes) + random.randint(1,2)
    ens_list = []
    ens_ids = []
    for i in range(ne):
        sx = random.choice(["masculin","feminin"])
        pr = random.choice(PH if sx=="masculin" else PF)
        nm = random.choice(NF)
        eid2 = str(uuid.uuid4())
        ens_ids.append(eid2)
        ens_list.append({"id":eid2,"user_id":str(uuid.uuid4()),"matricule":f"SEC-{code}-{random.randint(100000,999999)}","etablissement_id":eid,"matieres":random.sample(mats,min(3,len(mats))),"est_professeur_principal":i<len(classes),"classe_principale_id":classes[i]["id"] if i<len(classes) else None,"grade":random.choice(GRADES),"adresse_personnelle":f"Ave Lumumba n{random.randint(1,200)}","telephone_personnel":f"+243 {random.choice(['081','082','097'])} {random.randint(100,999)} {random.randint(100,999)}","email_personnel":f"{pr.lower()}.{nm.lower()}{random.randint(1,99)}@gmail.com","etat_civil":random.choice(["celibataire","marie"]),"nombre_enfants":random.randint(0,5),"conjoint_nom":"","banque":random.choice(BANQUES),"numero_compte":f"{random.randint(1000,9999)}-{random.randint(10000,99999)}-{random.randint(100,999)}","photo_url":None,"derniere_verification_dinacope":None,"derniere_verification_dinacope_id":None,"created_at":now,"nom":nm,"nom_complet":f"{pr} {nm}","postnom":random.choice(NF),"prenom":pr,"sexe":sx})
    if ens_list:
        await db.enseignants.insert_many(ens_list)

    # Students + notes + bulletins per class (insert immediately per class)
    profils = ["excellent","bon","moyen","moyen","moyen","faible"]
    for cls in classes:
        eleves = []
        notes = []
        bulletins = []
        for _ in range(epn):
            sx = random.choice(["masculin","feminin"])
            pr = random.choice(PH if sx=="masculin" else PF)
            nm = random.choice(NF)
            elid = str(uuid.uuid4())
            an = 2026 - random.randint(6 if is_p else 12, 14 if is_p else 22)
            eleves.append({"id":elid,"user_id":str(uuid.uuid4()),"ine":f"INE-{code}-2025-{random.randint(100000,999999)}","etablissement_id":eid,"classe_id":cls["id"],"niveau":cls["niveau"],"sexe":sx,"date_naissance":f"{an}-{random.randint(1,12):02d}-{random.randint(1,28):02d}","lieu_naissance":random.choice(etab.get("_sous_divs",["Ville"])),"created_at":now})

            pf = random.choice(profils)
            ens_id = random.choice(ens_ids) if ens_ids else None
            for tri in TRIM:
                nts = []
                for mat in mats:
                    nv = gen_note(pf)
                    cf = coefs.get(mat,1)
                    notes.append({"id":str(uuid.uuid4()),"eleve_id":elid,"classe_id":cls["id"],"matiere":mat,"note":nv,"coefficient":float(cf),"trimestre":tri,"annee_scolaire":"2025-2026","enseignant_id":ens_id,"commentaire":None,"created_at":now})
                    nts.append({"matiere":mat,"note":nv,"coeff":cf})
                tp = sum(n["note"]*n["coeff"] for n in nts)
                tc = sum(n["coeff"] for n in nts)
                moy = round(tp/tc,2) if tc>0 else 0
                app = "Excellent" if moy>=16 else "Très Bien" if moy>=14 else "Bien" if moy>=12 else "Assez Bien" if moy>=10 else "Passable" if moy>=8 else "Insuffisant"
                bulletins.append({"id":str(uuid.uuid4()),"eleve_id":elid,"classe_id":cls["id"],"trimestre":tri,"annee_scolaire":"2025-2026","moyenne_generale":moy,"appreciation":app,"rang":None,"notes_detail":[{"matiere":n["matiere"],"note":n["note"],"coefficient":n["coeff"]} for n in nts],"created_at":now})

        if eleves:
            await db.eleves.insert_many(eleves)
        if notes:
            for i in range(0, len(notes), 5000):
                await db.notes.insert_many(notes[i:i+5000])
        if bulletins:
            await db.bulletins.insert_many(bulletins)
        # Free memory
        del eleves, notes, bulletins

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    existing = set()
    async for doc in db.etablissements.aggregate([{"$group": {"_id": "$province_id"}}]):
        existing.add(doc["_id"])

    for pid, pd in PROVINCES_RESTANTES.items():
        if pid in existing:
            print(f"  {pid}: skip (already has data)")
            continue
        print(f"  Seeding {pid}...")
        code = pd["code"]
        sds = pd["sous_divisions"]
        now = datetime.now(timezone.utc).isoformat()
        etabs = []
        ec = 0
        for sd in sds:
            sdk = sd.lower().replace(" ","_").replace("-","_")
            for _ in range(random.randint(2,3)):
                ec += 1
                etabs.append({"id":str(uuid.uuid4()),"nom":f"{random.choice(NOMS_EP)} {sd}","type":"ecole_primaire","categorie":random.choice(["publique","publique","privee"]),"code_etablissement":f"{code}-EP-{ec:04d}","adresse":f"Ave Principale n{random.randint(1,200)}, {sd}","province_id":pid,"sous_division_id":sdk,"directeur_id":None,"created_at":now,"derniere_maj_effectifs":None,"effectif_classes":0,"effectif_eleves":0,"effectif_enseignants":0,"_sous_divs":sds})
            for _ in range(random.randint(1,2)):
                ec += 1
                etabs.append({"id":str(uuid.uuid4()),"nom":f"{random.choice(NOMS_CS)} {sd}","type":"college","categorie":random.choice(["publique","privee"]),"code_etablissement":f"{code}-CS-{ec:04d}","adresse":f"Blvd du 30 Juin n{random.randint(1,100)}, {sd}","province_id":pid,"sous_division_id":sdk,"directeur_id":None,"created_at":now,"derniere_maj_effectifs":None,"effectif_classes":0,"effectif_eleves":0,"effectif_enseignants":0,"_sous_divs":sds})
            if sd == sds[0] or random.random() > 0.6:
                ec += 1
                etabs.append({"id":str(uuid.uuid4()),"nom":f"{random.choice(NOMS_LY)} de {sd}","type":"lycee","categorie":random.choice(["publique","publique","privee"]),"code_etablissement":f"{code}-LY-{ec:04d}","adresse":f"Ave du Savoir n{random.randint(1,50)}, {sd}","province_id":pid,"sous_division_id":sdk,"directeur_id":None,"created_at":now,"derniere_maj_effectifs":None,"effectif_classes":0,"effectif_eleves":0,"effectif_enseignants":0,"_sous_divs":sds})

        # Remove temp field before insert
        etabs_clean = [{k:v for k,v in e.items() if k!="_sous_divs"} for e in etabs]
        await db.etablissements.insert_many(etabs_clean)
        print(f"    {len(etabs)} etabs inserted")

        for idx, etab in enumerate(etabs):
            await seed_etab(db, etab, code)
            if (idx+1) % 10 == 0:
                print(f"    {idx+1}/{len(etabs)} etabs seeded")
        print(f"    {pid} done!")

    client.close()
    print("All done!")

if __name__ == "__main__":
    asyncio.run(main())
