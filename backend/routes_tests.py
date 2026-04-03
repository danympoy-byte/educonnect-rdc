"""
Module 4 - Plateforme TEST & Certifications
Routes API pour recevoir les résultats de tests externes et afficher les statistiques
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime, timezone
from models import (
    Test, TestCreate, ResultatTest, ResultatTestCreate, 
    StatsTests, CategorieTest
)
from auth import get_current_user
from auth_externe import verify_api_client  # Réutiliser l'auth du Module 3

router = APIRouter(prefix="/api/tests", tags=["Tests & Certifications"])

# Sera injecté depuis server.py
db = None
tests_collection = None
resultats_tests_collection = None
etablissements_collection = None
viabilite_collection = None


def init_routes(database):
    """Initialiser les collections MongoDB"""
    global db, tests_collection, resultats_tests_collection, etablissements_collection, viabilite_collection
    db = database
    tests_collection = db.tests
    resultats_tests_collection = db.resultats_tests
    etablissements_collection = db.etablissements
    viabilite_collection = db.viabilite_etablissements


# ============================================
# ROUTES PUBLIQUES (POUR APPLICATION EXTERNE)
# ============================================

@router.post("/externes/resultats", status_code=status.HTTP_201_CREATED)
async def recevoir_resultats_test(
    resultat: ResultatTestCreate,
    api_client: dict = Depends(verify_api_client)
):
    """
    Recevoir les résultats d'un test depuis une application externe
    Authentification: Basic Auth (comme Module 3)
    """
    # Vérifier si le test existe déjà, sinon le créer
    test = await tests_collection.find_one({"nom": resultat.test_nom})
    
    if not test:
        # Créer automatiquement le test
        test_data = {
            "id": str(uuid.uuid4()),
            "nom": resultat.test_nom,
            "categorie": resultat.categorie,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await tests_collection.insert_one(test_data)
        test = test_data
    
    # Créer le résultat de test
    resultat_data = {
        "id": str(uuid.uuid4()),
        "test_id": test["id"],
        "test_nom": resultat.test_nom,
        "categorie": resultat.categorie,
        "nombre_participants": resultat.nombre_participants,
        "moyenne_globale": resultat.moyenne_globale,
        "participants_masculin": resultat.participants_masculin,
        "participants_feminin": resultat.participants_feminin,
        "moyenne_masculin": resultat.moyenne_masculin,
        "moyenne_feminin": resultat.moyenne_feminin,
        "resultats_par_province": resultat.resultats_par_province,
        "date_test": resultat.date_test.isoformat() if isinstance(resultat.date_test, datetime) else resultat.date_test,
        "api_client_id": api_client["username"],
        "received_at": datetime.now(timezone.utc).isoformat()
    }
    
    await resultats_tests_collection.insert_one(resultat_data)
    
    return {
        "message": "Résultats de test enregistrés avec succès",
        "resultat_id": resultat_data["id"]
    }


# ============================================
# ROUTES INTERNES (POUR RIE)
# ============================================

@router.get("/stats", response_model=StatsTests)
async def get_stats_tests(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques globales des tests"""
    
    # Compter les tests par catégorie
    tests_par_categorie = {}
    for categorie in CategorieTest:
        count = await resultats_tests_collection.count_documents({"categorie": categorie.value})
        tests_par_categorie[categorie.value] = count
    
    # Total des tests et participants
    total_tests = await resultats_tests_collection.count_documents({})
    
    # Calculer total participants et moyenne
    resultats = await resultats_tests_collection.find({}, {"_id": 0}).to_list(1000)
    total_participants = sum(r.get("nombre_participants", 0) for r in resultats)
    
    if resultats:
        moyenne_generale = sum(r.get("moyenne_globale", 0) for r in resultats) / len(resultats)
    else:
        moyenne_generale = 0.0
    
    # Calculer les établissements éligibles (score viabilité >= 80%)
    etablissements_eligibles = await calculer_etablissements_eligibles()
    
    return {
        "total_tests": total_tests,
        "total_participants": total_participants,
        "moyenne_generale": round(moyenne_generale, 2),
        "tests_par_categorie": tests_par_categorie,
        "etablissements_eligibles": etablissements_eligibles
    }


@router.get("/resultats", response_model=List[ResultatTest])
async def get_resultats_tests(
    categorie: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les résultats de tests, optionnellement filtrés par catégorie"""
    
    query = {}
    if categorie:
        query["categorie"] = categorie
    
    resultats = await resultats_tests_collection.find(query, {"_id": 0}).to_list(1000)
    return resultats


@router.get("/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les catégories de tests avec statistiques"""
    
    categories_stats = []
    
    for categorie in CategorieTest:
        resultats = await resultats_tests_collection.find(
            {"categorie": categorie.value},
            {"_id": 0}
        ).to_list(1000)
        
        if resultats:
            total_participants = sum(r.get("nombre_participants", 0) for r in resultats)
            moyenne = sum(r.get("moyenne_globale", 0) for r in resultats) / len(resultats)
        else:
            total_participants = 0
            moyenne = 0.0
        
        categories_stats.append({
            "categorie": categorie.value,
            "label": categorie.value.capitalize(),
            "nombre_tests": len(resultats),
            "total_participants": total_participants,
            "moyenne": round(moyenne, 2)
        })
    
    return categories_stats


@router.get("/etablissements-eligibles")
async def get_etablissements_eligibles(current_user: dict = Depends(get_current_user)):
    """
    Récupérer la liste des établissements éligibles pour accueillir des tests
    Critères: Score viabilité >= 80% (Excellent ou Bon)
    """
    
    # Récupérer tous les établissements avec leur score de viabilité
    etablissements_eligibles = []
    
    etablissements = await etablissements_collection.find({}, {"_id": 0}).to_list(1000)
    
    for etab in etablissements:
        viabilite = await viabilite_collection.find_one(
            {"etablissement_id": etab["id"]},
            {"_id": 0},
            sort=[("date_evaluation", -1)]
        )
        
        if viabilite and viabilite.get("score_total", 0) >= 80:
            etablissements_eligibles.append({
                "id": etab["id"],
                "nom": etab["nom"],
                "province_id": etab.get("province_id"),
                "score_viabilite": viabilite["score_total"],
                "niveau": viabilite.get("niveau", "Bon"),
                "salle_informatique": viabilite.get("infrastructures", {}).get("salle_informatique", False),
                "connexion_internet": viabilite.get("infrastructures", {}).get("connexion_internet", False),
                "electricite": viabilite.get("infrastructures", {}).get("electricite_stable", False)
            })
    
    return etablissements_eligibles


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

async def calculer_etablissements_eligibles():
    """Calculer les statistiques des établissements éligibles"""
    
    total_etablissements = await etablissements_collection.count_documents({})
    
    # Compter établissements avec score >= 90 (Excellent)
    excellent_count = 0
    # Compter établissements avec score 80-89 (Bon)
    bon_count = 0
    
    etablissements = await etablissements_collection.find({}, {"_id": 0, "id": 1}).to_list(1000)
    
    for etab in etablissements:
        viabilite = await viabilite_collection.find_one(
            {"etablissement_id": etab["id"]},
            {"_id": 0, "score_total": 1},
            sort=[("date_evaluation", -1)]
        )
        
        if viabilite:
            score = viabilite.get("score_total", 0)
            if score >= 90:
                excellent_count += 1
            elif score >= 80:
                bon_count += 1
    
    total_eligibles = excellent_count + bon_count
    pourcentage_eligibles = (total_eligibles / total_etablissements * 100) if total_etablissements > 0 else 0
    
    return {
        "excellent": excellent_count,
        "bon": bon_count,
        "total_eligibles": total_eligibles,
        "total_etablissements": total_etablissements,
        "pourcentage": round(pourcentage_eligibles, 2)
    }


import uuid
