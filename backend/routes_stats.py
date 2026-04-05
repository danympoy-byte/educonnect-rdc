"""
Routes pour les statistiques (Dashboard)
Extraites de server.py pour la modularité
"""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
import os

from models import Stats
from auth import get_current_user
from mapping_provinces import get_province_administrative

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'educonnect_rdc')]

# Collections
provinces_collection = db.provinces
etablissements_collection = db.etablissements
enseignants_collection = db.enseignants
eleves_collection = db.eleves
classes_collection = db.classes
notes_collection = db.notes
users_collection = db.users

router = APIRouter()


@router.get("/api/stats/global", response_model=Stats)
async def get_global_stats(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques globales"""
    total_etablissements = await etablissements_collection.count_documents({})
    total_enseignants = await enseignants_collection.count_documents({})
    total_eleves = await eleves_collection.count_documents({})
    total_classes = await classes_collection.count_documents({})

    # Élèves primaire vs secondaire
    total_eleves_primaire = await eleves_collection.count_documents({
        "niveau": {"$in": ["1ere_annee_primaire", "2eme_annee_primaire", "3eme_annee_primaire",
                           "4eme_annee_primaire", "5eme_annee_primaire", "6eme_annee_primaire"]}
    })
    total_eleves_secondaire = total_eleves - total_eleves_primaire

    # Répartition par province
    pipeline_provinces = [
        {
            "$group": {
                "_id": "$province_id",
                "count": {"$sum": 1}
            }
        }
    ]

    repartition_provinces_raw = await etablissements_collection.aggregate(pipeline_provinces).to_list(100)
    repartition_par_province = {}

    for item in repartition_provinces_raw:
        province_id = item["_id"]
        province = await provinces_collection.find_one({"id": province_id})
        if province:
            repartition_par_province[province["nom"]] = item["count"]

    # Répartition par niveau
    pipeline_niveaux = [
        {
            "$group": {
                "_id": "$niveau",
                "count": {"$sum": 1}
            }
        }
    ]

    repartition_niveaux_raw = await eleves_collection.aggregate(pipeline_niveaux).to_list(100)
    repartition_par_niveau = {item["_id"]: item["count"] for item in repartition_niveaux_raw}

    return Stats(
        total_etablissements=total_etablissements,
        total_enseignants=total_enseignants,
        total_eleves=total_eleves,
        total_eleves_primaire=total_eleves_primaire,
        total_eleves_secondaire=total_eleves_secondaire,
        total_classes=total_classes,
        repartition_par_province=repartition_par_province,
        repartition_par_niveau=repartition_par_niveau
    )


@router.get("/api/stats/sexe")
async def get_stats_sexe(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques par sexe"""
    # Répartition globale par sexe - ÉLÈVES
    total_masculin = await eleves_collection.count_documents({"sexe": "masculin"})
    total_feminin = await eleves_collection.count_documents({"sexe": "feminin"})

    # Répartition par sexe et par niveau - ÉLÈVES
    pipeline_sexe_niveau = [
        {
            "$group": {
                "_id": {"niveau": "$niveau", "sexe": "$sexe"},
                "count": {"$sum": 1}
            }
        }
    ]

    sexe_niveau_raw = await eleves_collection.aggregate(pipeline_sexe_niveau).to_list(100)
    repartition_sexe_niveau = {}

    for item in sexe_niveau_raw:
        niveau = item["_id"]["niveau"]
        sexe = item["_id"]["sexe"]
        if niveau not in repartition_sexe_niveau:
            repartition_sexe_niveau[niveau] = {"masculin": 0, "feminin": 0}
        repartition_sexe_niveau[niveau][sexe] = item["count"]

    # Répartition par sexe et par province - ÉLÈVES
    pipeline_sexe_province = [
        {
            "$group": {
                "_id": {"etablissement_id": "$etablissement_id", "sexe": "$sexe"},
                "count": {"$sum": 1}
            }
        }
    ]

    sexe_province_raw = await eleves_collection.aggregate(pipeline_sexe_province).to_list(1000)

    # Regrouper par province ADMINISTRATIVE
    province_sexe = {}
    for item in sexe_province_raw:
        etab_id = item["_id"]["etablissement_id"]
        sexe = item["_id"]["sexe"]
        count = item["count"]

        # Trouver la province de l'établissement
        etab = await etablissements_collection.find_one({"id": etab_id})
        if etab:
            province = await provinces_collection.find_one({"id": etab["province_id"]})
            if province:
                province_educationnelle = province["nom"]
                # Convertir en province administrative
                province_admin = get_province_administrative(province_educationnelle)
                if province_admin not in province_sexe:
                    province_sexe[province_admin] = {"masculin": 0, "feminin": 0}
                province_sexe[province_admin][sexe] += count

    # ENSEIGNANTS - Statistiques par sexe depuis la collection enseignants
    total_enseignants_masculin = await enseignants_collection.count_documents({"sexe": "masculin"})
    total_enseignants_feminin = await enseignants_collection.count_documents({"sexe": "feminin"})

    # Enseignants par province ADMINISTRATIVE
    enseignants_par_province = {}
    enseignants_list = await enseignants_collection.find(
        {},
        {"_id": 0, "etablissement_id": 1, "sexe": 1}
    ).to_list(1000)

    for ens in enseignants_list:
        if ens.get("etablissement_id") and ens.get("sexe"):
            etab = await etablissements_collection.find_one({"id": ens["etablissement_id"]})
            if etab:
                province = await provinces_collection.find_one({"id": etab["province_id"]})
                if province:
                    province_educationnelle = province["nom"]
                    # Convertir en province administrative
                    province_admin = get_province_administrative(province_educationnelle)
                    if province_admin not in enseignants_par_province:
                        enseignants_par_province[province_admin] = {"masculin": 0, "feminin": 0}
                    enseignants_par_province[province_admin][ens["sexe"]] += 1

    # DIRECTEURS - Statistiques globales par sexe
    total_directeurs_masculin = await users_collection.count_documents({
        "role": {"$in": ["directeur_ecole", "chef_etablissement"]},
        "sexe": "masculin"
    })
    total_directeurs_feminin = await users_collection.count_documents({
        "role": {"$in": ["directeur_ecole", "chef_etablissement"]},
        "sexe": "feminin"
    })

    return {
        "eleves": {
            "global": {
                "masculin": total_masculin,
                "feminin": total_feminin,
                "total": total_masculin + total_feminin
            },
            "par_niveau": repartition_sexe_niveau,
            "par_province": province_sexe
        },
        "enseignants": {
            "global": {
                "masculin": total_enseignants_masculin,
                "feminin": total_enseignants_feminin,
                "total": total_enseignants_masculin + total_enseignants_feminin
            },
            "par_province": enseignants_par_province
        },
        "directeurs": {
            "global": {
                "masculin": total_directeurs_masculin,
                "feminin": total_directeurs_feminin,
                "total": total_directeurs_masculin + total_directeurs_feminin
            }
        }
    }


@router.get("/api/stats/evolution")
async def get_stats_evolution(current_user: dict = Depends(get_current_user)):
    """Statistiques d'évolution temporelle sur 12 mois"""
    now = datetime.now(timezone.utc)
    mois_labels = []
    data_eleves = []
    data_enseignants = []
    data_etablissements = []

    for i in range(11, -1, -1):
        # Premier jour du mois i mois en arrière
        target = now - timedelta(days=i * 30)
        mois_labels.append(target.strftime("%b %Y"))

        # Calculer la date limite (fin du mois)
        date_limite = (now - timedelta(days=(i - 1) * 30)).isoformat() if i > 0 else now.isoformat()

        # Compter les entités créées jusqu'à cette date
        count_eleves = await eleves_collection.count_documents(
            {"created_at": {"$lte": date_limite}}
        )
        count_enseignants = await enseignants_collection.count_documents(
            {"created_at": {"$lte": date_limite}}
        )
        count_etab = await etablissements_collection.count_documents(
            {"created_at": {"$lte": date_limite}}
        )

        data_eleves.append(count_eleves)
        data_enseignants.append(count_enseignants)
        data_etablissements.append(count_etab)

    # Aussi calculer les nouvelles inscriptions par mois
    inscriptions_par_mois = []
    for i in range(11, -1, -1):
        debut_mois = (now - timedelta(days=(i + 1) * 30)).isoformat()
        fin_mois = (now - timedelta(days=i * 30)).isoformat()

        nouveaux_eleves = await eleves_collection.count_documents(
            {"created_at": {"$gte": debut_mois, "$lte": fin_mois}}
        )
        nouveaux_enseignants = await enseignants_collection.count_documents(
            {"created_at": {"$gte": debut_mois, "$lte": fin_mois}}
        )

        inscriptions_par_mois.append({
            "mois": mois_labels[11 - i],
            "eleves": nouveaux_eleves,
            "enseignants": nouveaux_enseignants
        })

    return {
        "mois": mois_labels,
        "cumul": {
            "eleves": data_eleves,
            "enseignants": data_enseignants,
            "etablissements": data_etablissements
        },
        "inscriptions_mensuelles": inscriptions_par_mois
    }


@router.get("/api/stats/notes")
async def get_stats_notes(current_user: dict = Depends(get_current_user)):
    """Statistiques des notes et moyennes par matière"""
    # Moyenne par matière
    pipeline_matieres = [
        {
            "$group": {
                "_id": "$matiere",
                "moyenne": {"$avg": "$note"},
                "count": {"$sum": 1},
                "min": {"$min": "$note"},
                "max": {"$max": "$note"}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    matieres_stats = await notes_collection.aggregate(pipeline_matieres).to_list(50)

    # Distribution des notes
    pipeline_distribution = [
        {
            "$bucket": {
                "groupBy": "$note",
                "boundaries": [0, 5, 8, 10, 12, 14, 16, 20.1],
                "default": "autre",
                "output": {"count": {"$sum": 1}}
            }
        }
    ]

    try:
        distribution = await notes_collection.aggregate(pipeline_distribution).to_list(20)
    except Exception:
        distribution = []

    # Moyenne par trimestre
    pipeline_trimestre = [
        {
            "$group": {
                "_id": "$trimestre",
                "moyenne": {"$avg": "$note"},
                "count": {"$sum": 1}
            }
        }
    ]

    trimestres_stats = await notes_collection.aggregate(pipeline_trimestre).to_list(5)

    return {
        "par_matiere": [
            {
                "matiere": str(s["_id"]),
                "moyenne": round(s["moyenne"], 2),
                "count": s["count"],
                "min": s["min"],
                "max": s["max"]
            }
            for s in matieres_stats
        ],
        "distribution": [
            {"tranche": str(d["_id"]), "count": d["count"]}
            for d in distribution if d["_id"] != "autre"
        ],
        "par_trimestre": [
            {
                "trimestre": str(t["_id"]).replace("trimestre_", "T"),
                "moyenne": round(t["moyenne"], 2),
                "count": t["count"]
            }
            for t in trimestres_stats
        ]
    }


@router.get("/api/stats/province/{province_id}")
async def get_province_stats(province_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques d'une province"""
    total_etablissements = await etablissements_collection.count_documents({"province_id": province_id})

    # Récupérer les IDs des établissements de la province
    etablissements = await etablissements_collection.find({"province_id": province_id}, {"id": 1, "_id": 0}).to_list(1000)
    etablissement_ids = [e["id"] for e in etablissements]

    total_enseignants = await enseignants_collection.count_documents({"etablissement_id": {"$in": etablissement_ids}})
    total_eleves = await eleves_collection.count_documents({"etablissement_id": {"$in": etablissement_ids}})

    return {
        "province_id": province_id,
        "total_etablissements": total_etablissements,
        "total_enseignants": total_enseignants,
        "total_eleves": total_eleves
    }
