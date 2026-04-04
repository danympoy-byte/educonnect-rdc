"""
Seed script pour générer des notes réalistes pour les élèves existants.
Matières basées sur le programme scolaire RDC.
"""
import asyncio
import os
import random
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "educonnect")

# Matières par cycle
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

def generate_note(base_level="moyen"):
    """Générer une note réaliste selon le profil de l'élève"""
    if base_level == "excellent":
        return round(random.gauss(16, 1.5), 1)
    elif base_level == "bon":
        return round(random.gauss(14, 2), 1)
    elif base_level == "moyen":
        return round(random.gauss(11, 2.5), 1)
    elif base_level == "faible":
        return round(random.gauss(7, 2), 1)
    else:
        return round(random.gauss(10, 3), 1)

def clamp_note(n):
    return max(0, min(20, round(n, 1)))

async def seed_notes():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Vérifier si des notes existent déjà
    existing_count = await db.notes.count_documents({})
    if existing_count > 0:
        print(f"Il y a deja {existing_count} notes en base. Nettoyage...")
        await db.notes.delete_many({})
        await db.bulletins.delete_many({})
        print("Notes et bulletins supprimés.")
    
    # Récupérer élèves avec leurs classes
    eleves = await db.eleves.find({}, {"_id": 0}).to_list(20000)
    print(f"Trouvé {len(eleves)} élèves")
    
    # Récupérer enseignants
    enseignants = await db.enseignants.find({}, {"_id": 0, "id": 1, "etablissement_id": 1}).to_list(1000)
    enseignants_par_etab = {}
    for ens in enseignants:
        etab_id = ens.get("etablissement_id", "")
        if etab_id not in enseignants_par_etab:
            enseignants_par_etab[etab_id] = []
        enseignants_par_etab[etab_id].append(ens["id"])
    
    notes_to_insert = []
    bulletins_to_insert = []
    annee_scolaire = "2025-2026"
    trimestres = ["trimestre_1", "trimestre_2", "trimestre_3"]
    
    # Limiter à 2000 élèves pour performance
    sample_size = min(2000, len(eleves))
    sampled_eleves = random.sample(eleves, sample_size)
    
    profils = ["excellent", "bon", "moyen", "moyen", "moyen", "faible"]
    
    for idx, eleve in enumerate(sampled_eleves):
        if idx % 200 == 0:
            print(f"Traitement élève {idx}/{sample_size}...")
        
        is_primaire = "primaire" in eleve.get("niveau", "")
        matieres = MATIERES_PRIMAIRE if is_primaire else MATIERES_SECONDAIRE
        coefficients = COEFFICIENTS_PRIMAIRE if is_primaire else COEFFICIENTS_SECONDAIRE
        
        profil = random.choice(profils)
        etab_id = eleve.get("etablissement_id", "")
        ens_list = enseignants_par_etab.get(etab_id, [])
        
        for trimestre in trimestres:
            notes_trimestre = []
            
            for matiere in matieres:
                note_val = clamp_note(generate_note(profil))
                coef = coefficients.get(matiere, 1)
                ens_id = random.choice(ens_list) if ens_list else "unknown"
                
                note = {
                    "id": str(uuid.uuid4()),
                    "eleve_id": eleve["id"],
                    "classe_id": eleve.get("classe_id", ""),
                    "matiere": matiere,
                    "note": note_val,
                    "coefficient": float(coef),
                    "trimestre": trimestre,
                    "annee_scolaire": annee_scolaire,
                    "enseignant_id": ens_id,
                    "commentaire": None,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                notes_to_insert.append(note)
                notes_trimestre.append({"note": note_val, "coefficient": coef, "matiere": matiere})
            
            # Calculer bulletin
            total_pondere = sum(n["note"] * n["coefficient"] for n in notes_trimestre)
            total_coef = sum(n["coefficient"] for n in notes_trimestre)
            moyenne = round(total_pondere / total_coef, 2) if total_coef > 0 else 0
            
            appreciation = "Excellent" if moyenne >= 16 else \
                          "Tres Bien" if moyenne >= 14 else \
                          "Bien" if moyenne >= 12 else \
                          "Assez Bien" if moyenne >= 10 else \
                          "Passable" if moyenne >= 8 else "Insuffisant"
            
            bulletin = {
                "id": str(uuid.uuid4()),
                "eleve_id": eleve["id"],
                "classe_id": eleve.get("classe_id", ""),
                "trimestre": trimestre,
                "annee_scolaire": annee_scolaire,
                "moyenne_generale": moyenne,
                "notes_detail": [
                    {"matiere": n["matiere"], "note": n["note"], "coefficient": n["coefficient"]}
                    for n in notes_trimestre
                ],
                "rang": None,
                "effectif_classe": None,
                "appreciation_generale": appreciation,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            bulletins_to_insert.append(bulletin)
    
    # Insertion par batch
    print(f"Insertion de {len(notes_to_insert)} notes...")
    batch_size = 5000
    for i in range(0, len(notes_to_insert), batch_size):
        batch = notes_to_insert[i:i + batch_size]
        await db.notes.insert_many(batch)
        print(f"  Batch {i // batch_size + 1}: {len(batch)} notes insérées")
    
    print(f"Insertion de {len(bulletins_to_insert)} bulletins...")
    for i in range(0, len(bulletins_to_insert), batch_size):
        batch = bulletins_to_insert[i:i + batch_size]
        await db.bulletins.insert_many(batch)
        print(f"  Batch {i // batch_size + 1}: {len(batch)} bulletins insérés")
    
    # Créer index
    await db.notes.create_index("eleve_id")
    await db.notes.create_index("classe_id")
    await db.notes.create_index("trimestre")
    await db.bulletins.create_index("eleve_id")
    await db.bulletins.create_index("classe_id")
    
    print(f"\nSeed terminé!")
    print(f"  Notes: {len(notes_to_insert)}")
    print(f"  Bulletins: {len(bulletins_to_insert)}")
    print(f"  Élèves évalués: {sample_size}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_notes())
