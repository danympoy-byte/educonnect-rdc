"""
Génération automatique des rapports statistiques trimestriels GED
Refactorisé en fonctions modulaires pour meilleure maintenabilité.
"""
import asyncio
import os
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List, Tuple

from models import RapportTrimestriel, StatutDocument
from email_service import email_rapport_trimestriel

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")


def calculer_trimestre_actuel():
    """Calcule le trimestre actuel et les dates"""
    maintenant = datetime.now(timezone.utc)
    mois = maintenant.month
    annee = maintenant.year
    
    if 1 <= mois <= 3:
        trimestre = 1
    elif 4 <= mois <= 6:
        trimestre = 2
    elif 7 <= mois <= 9:
        trimestre = 3
    else:
        trimestre = 4
    
    debut, fin = get_dates_trimestre(trimestre, annee)
    return trimestre, annee, debut, fin


def calculer_trimestre_precedent(trimestre: int, annee: int):
    """Calcule le trimestre précédent"""
    if trimestre == 1:
        return 4, annee - 1
    else:
        return trimestre - 1, annee


def get_dates_trimestre(trimestre: int, annee: int) -> Tuple[datetime, datetime]:
    """Retourne les dates de début et fin pour un trimestre donné."""
    mois_debut = {1: 1, 2: 4, 3: 7, 4: 10}
    mois_fin = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}

    debut = datetime(annee, mois_debut[trimestre], 1, tzinfo=timezone.utc)
    m, j = mois_fin[trimestre]
    fin = datetime(annee, m, j, 23, 59, 59, tzinfo=timezone.utc)
    return debut, fin


async def stats_globales(db, filtre_periode: dict) -> dict:
    """Calcule les statistiques globales de documents pour la période."""
    total = await db.documents.count_documents(filtre_periode)
    valides = await db.documents.count_documents({**filtre_periode, "statut": StatutDocument.VALIDE.value})
    rejetes = await db.documents.count_documents({**filtre_periode, "statut": StatutDocument.REJETE.value})
    en_cours = await db.documents.count_documents({
        **filtre_periode,
        "statut": {"$in": [StatutDocument.EN_ATTENTE.value, StatutDocument.EN_COURS.value]}
    })
    archives = await db.documents.count_documents({**filtre_periode, "statut": StatutDocument.ARCHIVE.value})
    return {
        "total": total, "valides": valides, "rejetes": rejetes,
        "en_cours": en_cours, "archives": archives
    }


async def stats_par_type_document(db, filtre_periode: dict) -> dict:
    """Calcule les statistiques par type de document."""
    stats = {}
    for type_doc in ["administratif", "rh", "financier", "pedagogique"]:
        count = await db.documents.count_documents({**filtre_periode, "type_document": type_doc})
        valides = await db.documents.count_documents({
            **filtre_periode, "type_document": type_doc, "statut": StatutDocument.VALIDE.value
        })
        rejetes = await db.documents.count_documents({
            **filtre_periode, "type_document": type_doc, "statut": StatutDocument.REJETE.value
        })
        stats[type_doc] = {
            "total": count, "valides": valides, "rejetes": rejetes,
            "taux_validation": round((valides / count * 100) if count > 0 else 0, 2)
        }
    return stats


async def calculer_delais_validation(db, filtre_periode: dict) -> Tuple[float, float]:
    """Calcule le délai moyen et médian de validation en heures."""
    pipeline = [
        {"$match": {**filtre_periode, "statut": StatutDocument.VALIDE.value, "date_validation": {"$exists": True}}},
        {"$addFields": {"delai": {"$divide": [
            {"$subtract": [
                {"$dateFromString": {"dateString": "$date_validation"}},
                {"$dateFromString": {"dateString": "$date_creation"}}
            ]}, 3600000
        ]}}},
        {"$group": {"_id": None, "delai_moyen": {"$avg": "$delai"}, "delais": {"$push": "$delai"}}}
    ]
    result = await db.documents.aggregate(pipeline).to_list(1)
    delai_moyen = result[0]["delai_moyen"] if result and result[0].get("delai_moyen") else 0

    delai_median = 0
    if result and result[0].get("delais"):
        delais_sorted = sorted(result[0]["delais"])
        n = len(delais_sorted)
        if n > 0:
            delai_median = (delais_sorted[n // 2 - 1] + delais_sorted[n // 2]) / 2 if n % 2 == 0 else delais_sorted[n // 2]

    return delai_moyen, delai_median


async def get_documents_en_retard(db) -> List[dict]:
    """Récupère les documents en attente depuis plus de 48h."""
    date_limite = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    return await db.documents.find(
        {"statut": {"$in": [StatutDocument.EN_ATTENTE.value, StatutDocument.EN_COURS.value]}, "date_creation": {"$lt": date_limite}},
        {"_id": 0, "id": 1, "numero_reference": 1, "titre": 1, "proprietaire_actuel_nom": 1, "date_creation": 1}
    ).to_list(100)


async def get_top_createurs(db, filtre_periode: dict) -> List[dict]:
    """Récupère le top 10 des créateurs de documents."""
    pipeline = [
        {"$match": filtre_periode},
        {"$group": {"_id": "$createur_id", "nom": {"$first": "$createur_nom"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 10}
    ]
    result = await db.documents.aggregate(pipeline).to_list(10)
    return [{"user_id": r["_id"], "nom": r["nom"], "documents_crees": r["count"]} for r in result]


async def get_top_validateurs(db, debut: datetime, fin: datetime) -> List[dict]:
    """Récupère le top 10 des validateurs."""
    pipeline = [
        {"$match": {"type_action": "validation", "date_action": {"$gte": debut.isoformat(), "$lte": fin.isoformat()}}},
        {"$group": {"_id": "$user_id", "nom": {"$first": "$user_nom"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}, {"$limit": 10}
    ]
    result = await db.historique_actions.aggregate(pipeline).to_list(10)
    return [{"user_id": r["_id"], "nom": r["nom"], "validations_effectuees": r["count"]} for r in result]


async def get_utilisateurs_lents(db, filtre_periode: dict, delai_moyen: float) -> List[dict]:
    """Identifie les utilisateurs les plus lents à traiter les documents."""
    if delai_moyen <= 0:
        return []
    pipeline = [
        {"$match": {**filtre_periode, "statut": StatutDocument.VALIDE.value, "date_validation": {"$exists": True}}},
        {"$addFields": {"delai": {"$divide": [
            {"$subtract": [
                {"$dateFromString": {"dateString": "$date_validation"}},
                {"$dateFromString": {"dateString": "$date_creation"}}
            ]}, 3600000
        ]}}},
        {"$group": {
            "_id": "$proprietaire_actuel_id", "nom": {"$first": "$proprietaire_actuel_nom"},
            "delai_moyen_user": {"$avg": "$delai"}, "count": {"$sum": 1}
        }},
        {"$match": {"delai_moyen_user": {"$gt": delai_moyen}, "count": {"$gte": 3}}},
        {"$sort": {"delai_moyen_user": -1}}, {"$limit": 10}
    ]
    result = await db.documents.aggregate(pipeline).to_list(10)
    return [
        {"user_id": r["_id"], "nom": r["nom"], "delai_moyen_heures": round(r["delai_moyen_user"], 2), "documents_traites": r["count"]}
        for r in result
    ]


def calculer_comparaison(total_documents, taux_validation, delai_moyen, rapport_precedent) -> dict:
    """Compare les statistiques avec le trimestre précédent."""
    if not rapport_precedent:
        return {}

    def evolution(actuel, precedent):
        return round(((actuel - precedent) / precedent) * 100, 2) if precedent > 0 else 0

    return {
        "documents_crees": {
            "actuel": total_documents,
            "precedent": rapport_precedent.get("total_documents_crees", 0),
            "evolution_pct": evolution(total_documents, rapport_precedent.get("total_documents_crees", 0))
        },
        "taux_validation": {
            "actuel": taux_validation,
            "precedent": rapport_precedent.get("taux_validation", 0),
            "evolution_pct": round(taux_validation - rapport_precedent.get("taux_validation", 0), 2)
        },
        "delai_moyen": {
            "actuel": round(delai_moyen, 2),
            "precedent": round(rapport_precedent.get("delai_moyen_validation_heures", 0), 2),
            "evolution_pct": evolution(delai_moyen, rapport_precedent.get("delai_moyen_validation_heures", 0))
        }
    }


async def envoyer_emails_rapport(db, trimestre, annee, total_documents, total_valides, taux_validation, delai_moyen) -> List[str]:
    """Envoie le rapport par email aux décideurs."""
    destinataires = await db.users.find(
        {"role": {"$in": ["ministre", "secretaire_general", "directeur_provincial"]}},
        {"_id": 0, "email": 1, "prenom": 1, "nom": 1}
    ).to_list(100)

    emails_envoyes = []
    for dest in destinataires:
        if dest.get("email"):
            success = email_rapport_trimestriel(
                destinataire_email=dest["email"],
                destinataire_nom=f"{dest.get('prenom', '')} {dest.get('nom', '')}",
                trimestre=trimestre, annee=annee,
                total_documents=total_documents, total_valides=total_valides,
                taux_validation=taux_validation, delai_moyen=round(delai_moyen, 2)
            )
            if success:
                emails_envoyes.append(dest["email"])
    return emails_envoyes


async def generer_rapport_trimestriel(trimestre: int = None, annee: int = None, genere_par: str = "system"):
    """Génère un rapport statistique pour un trimestre donné."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        if trimestre is None or annee is None:
            trimestre_actuel, annee_actuelle, _, _ = calculer_trimestre_actuel()
            trimestre, annee = calculer_trimestre_precedent(trimestre_actuel, annee_actuelle)

        debut, fin = get_dates_trimestre(trimestre, annee)
        print(f"[{datetime.now()}] Génération du rapport T{trimestre} {annee} ({debut.date()} -> {fin.date()})")

        # Vérifier existence
        rapport_existant = await db.rapports_trimestriels.find_one({"trimestre": trimestre, "annee": annee}, {"_id": 0})
        if rapport_existant:
            print(f"Rapport T{trimestre} {annee} déjà généré le {rapport_existant['date_generation']}")
            return rapport_existant

        filtre_periode = {"date_creation": {"$gte": debut.isoformat(), "$lte": fin.isoformat()}}

        # Collecte des données
        globales = await stats_globales(db, filtre_periode)
        par_type = await stats_par_type_document(db, filtre_periode)
        delai_moyen, delai_median = await calculer_delais_validation(db, filtre_periode)
        docs_en_retard = await get_documents_en_retard(db)
        top_createurs = await get_top_createurs(db, filtre_periode)
        top_validateurs = await get_top_validateurs(db, debut, fin)
        utilisateurs_lents = await get_utilisateurs_lents(db, filtre_periode, delai_moyen)

        taux_validation = round((globales["valides"] / globales["total"] * 100) if globales["total"] > 0 else 0, 2)
        taux_rejet = round((globales["rejetes"] / globales["total"] * 100) if globales["total"] > 0 else 0, 2)

        # Comparaison trimestre précédent
        t_prec, a_prec = calculer_trimestre_precedent(trimestre, annee)
        rapport_prec = await db.rapports_trimestriels.find_one({"trimestre": t_prec, "annee": a_prec}, {"_id": 0})
        comparaison = calculer_comparaison(globales["total"], taux_validation, delai_moyen, rapport_prec)

        # Construire et sauvegarder le rapport
        rapport = RapportTrimestriel(
            periode_debut=debut.isoformat(), periode_fin=fin.isoformat(),
            trimestre=trimestre, annee=annee,
            total_documents_crees=globales["total"], total_documents_valides=globales["valides"],
            total_documents_rejetes=globales["rejetes"], total_documents_en_cours=globales["en_cours"],
            total_documents_archives=globales["archives"],
            stats_par_type=par_type,
            delai_moyen_validation_heures=round(delai_moyen, 2),
            delai_median_validation_heures=round(delai_median, 2),
            taux_validation=taux_validation, taux_rejet=taux_rejet,
            documents_en_retard=len(docs_en_retard),
            documents_en_retard_details=docs_en_retard[:20],
            top_createurs=top_createurs, top_validateurs=top_validateurs,
            utilisateurs_les_plus_lents=utilisateurs_lents,
            stats_par_province={},
            comparaison_trimestre_precedent=comparaison,
            genere_par=genere_par
        )

        await db.rapports_trimestriels.insert_one(rapport.model_dump())
        print(f"Rapport T{trimestre} {annee} généré: {globales['total']} docs | {globales['valides']} validés | Taux: {taux_validation}%")

        # Envoi des emails
        emails = await envoyer_emails_rapport(db, trimestre, annee, globales["total"], globales["valides"], taux_validation, delai_moyen)
        await db.rapports_trimestriels.update_one(
            {"id": rapport.id},
            {"$set": {"envoi_email_effectue": len(emails) > 0, "destinataires_email": emails}}
        )
        print(f"Emails envoyés à {len(emails)} décideurs")

        return rapport.model_dump()
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        asyncio.run(generer_rapport_trimestriel(int(sys.argv[1]), int(sys.argv[2])))
    else:
        print("Génération du rapport pour le trimestre précédent...")
        asyncio.run(generer_rapport_trimestriel())
