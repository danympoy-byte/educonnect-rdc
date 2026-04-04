"""
Routes pour les APIs externes (Module 3 - Scolarité)
Permet aux systèmes externes d'envoyer des données vers RIE
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Optional
import os
import uuid

from models import (
    APIClient, APIClientCreate, Presence, PresenceCreate, 
    LogAPIExterne, StatistiquesPresence, NoteCreate, EleveCreate,
    UserRole, Sexe, NiveauScolaire
)
from auth_externe import verify_api_client, require_permission
from auth import get_current_user, require_role, get_password_hash
from parsers import DataParser, DataValidator
from utils import generate_ine, calculate_moyenne, get_appreciation

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'educonnect_rdc')]

router = APIRouter()


# ============================================
# GESTION DES CLIENTS API (Admin uniquement)
# ============================================

@router.post("/api/admin/api-clients")
async def creer_client_api(
    client_data: APIClientCreate,
    current_user: dict = Depends(require_role([UserRole.ADMIN_TECH]))
):
    """Créer un nouveau client API pour système externe"""
    
    # Vérifier si username existe déjà
    existing = await db.api_clients.find_one({"username": client_data.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Ce username existe déjà")
    
    # Créer le client API
    api_client = {
        "id": str(uuid.uuid4()),
        "username": client_data.username,
        "password_hash": get_password_hash(client_data.password),
        "etablissement_id": client_data.etablissement_id,
        "nom_systeme": client_data.nom_systeme,
        "permissions": client_data.permissions,
        "actif": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": None
    }
    
    await db.api_clients.insert_one(api_client)
    
    # Retourner les credentials (password en clair uniquement à la création)
    return {
        "success": True,
        "client_id": api_client['id'],
        "username": api_client['username'],
        "password": client_data.password,  # Montrer une seule fois
        "message": "Client API créé avec succès. Conservez ces credentials de manière sécurisée."
    }


@router.get("/api/admin/api-clients")
async def lister_clients_api(
    current_user: dict = Depends(require_role([UserRole.ADMIN_TECH]))
):
    """Lister tous les clients API"""
    clients = await db.api_clients.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
    return {"clients": clients}


@router.get("/api/admin/api-clients/logs")
async def lister_logs_api(
    limit: int = 100,
    current_user: dict = Depends(require_role([UserRole.ADMIN_TECH]))
):
    """Voir les logs des appels API externes"""
    logs = await db.logs_api_externe.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs}


# ============================================
# RÉCEPTION DES NOTES
# ============================================

@router.post("/api/externe/notes")
async def recevoir_notes(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("notes"))
):
    """
    Recevoir des notes depuis un système externe
    Supporte JSON, XML, CSV
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/notes",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Détecter le format
        if file:
            # CSV via upload
            data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            # JSON ou XML via body
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                data = DataParser.parse_json(content)
            elif format_type == 'xml':
                data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        # Valider et insérer les notes
        notes_inserees = []
        erreurs = []
        
        for idx, item in enumerate(data):
            try:
                # Valider les données
                validated = DataValidator.validate_note(item)
                
                # Créer la note
                note = {
                    "id": str(uuid.uuid4()),
                    "eleve_id": validated['eleve_id'],
                    "classe_id": validated['classe_id'],
                    "matiere": validated['matiere'],
                    "note": validated['note'],
                    "coefficient": validated['coefficient'],
                    "trimestre": validated['trimestre'],
                    "annee_scolaire": validated['annee_scolaire'],
                    "enseignant_id": validated['enseignant_id'],
                    "commentaire": validated.get('commentaire'),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "api_externe",
                    "api_client_id": api_client['id']
                }
                
                await db.notes.insert_one(note)
                notes_inserees.append(note['id'])
                
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(notes_inserees)
        log_entry['erreurs'] = erreurs
        
        if erreurs:
            log_entry['statut'] = 'partial' if notes_inserees else 'error'
        
        # Sauvegarder le log
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_notes_inserees": len(notes_inserees),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],  # Limiter à 10 erreurs dans la réponse
            "message": f"{len(notes_inserees)} notes insérées avec succès"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RÉCEPTION DES PRÉSENCES/ABSENCES
# ============================================

@router.post("/api/externe/presences")
async def recevoir_presences(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("presences"))
):
    """
    Recevoir des présences/absences depuis un système externe
    Supporte JSON, XML, CSV
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/presences",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Détecter le format
        if file:
            data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                data = DataParser.parse_json(content)
            elif format_type == 'xml':
                data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        # Valider et insérer les présences
        presences_inserees = []
        erreurs = []
        
        for idx, item in enumerate(data):
            try:
                # Valider les données
                validated = DataValidator.validate_presence(item)
                
                # Vérifier si existe déjà pour cette date
                existing = await db.presences.find_one({
                    "eleve_id": validated['eleve_id'],
                    "date": validated['date']
                }, {"_id": 0})
                
                if existing:
                    # Mettre à jour
                    await db.presences.update_one(
                        {"id": existing['id']},
                        {"$set": {
                            "present": validated['present'],
                            "justifie": validated.get('justifie', False),
                            "motif": validated.get('motif'),
                            "api_client_id": api_client['id']
                        }}
                    )
                    presences_inserees.append(existing['id'])
                else:
                    # Créer nouvelle présence
                    presence = {
                        "id": str(uuid.uuid4()),
                        "eleve_id": validated['eleve_id'],
                        "classe_id": validated['classe_id'],
                        "etablissement_id": validated['etablissement_id'],
                        "date": validated['date'],
                        "present": validated['present'],
                        "justifie": validated.get('justifie', False),
                        "motif": validated.get('motif'),
                        "api_client_id": api_client['id'],
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    await db.presences.insert_one(presence)
                    presences_inserees.append(presence['id'])
                
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(presences_inserees)
        log_entry['erreurs'] = erreurs
        
        if erreurs:
            log_entry['statut'] = 'partial' if presences_inserees else 'error'
        
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_presences_inserees": len(presences_inserees),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],
            "message": f"{len(presences_inserees)} présences traitées avec succès"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RÉCEPTION DES INSCRIPTIONS D'ÉLÈVES
# ============================================

@router.post("/api/externe/inscriptions")
async def recevoir_inscriptions(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("inscriptions"))
):
    """
    Recevoir des inscriptions d'élèves depuis un système externe
    Supporte JSON, XML, CSV
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/inscriptions",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Détecter le format
        if file:
            data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                data = DataParser.parse_json(content)
            elif format_type == 'xml':
                data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        # Valider et insérer les inscriptions
        inscriptions_inserees = []
        erreurs = []
        
        for idx, item in enumerate(data):
            try:
                # Valider les données
                validated = DataValidator.validate_inscription(item)
                
                # Vérifier si l'élève existe déjà par email
                existing_user = await db.users.find_one(
                    {"email": validated['email']},
                    {"_id": 0}
                )
                
                if existing_user:
                    erreurs.append(f"Ligne {idx + 1}: Élève existe déjà (email: {validated['email']})")
                    continue
                
                # Créer l'utilisateur
                user = {
                    "id": str(uuid.uuid4()),
                    "nom": validated['nom'],
                    "prenom": validated['prenom'],
                    "email": validated['email'],
                    "password_hash": get_password_hash(validated.get('password', 'password123')),
                    "role": "eleve_primaire" if "primaire" in validated['niveau'] else "eleve_secondaire",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.users.insert_one(user)
                
                # Générer INE
                ine = generate_ine()
                
                # Créer le profil élève
                eleve = {
                    "id": str(uuid.uuid4()),
                    "user_id": user['id'],
                    "ine": ine,
                    "etablissement_id": validated['etablissement_id'],
                    "classe_id": validated.get('classe_id'),
                    "niveau": validated['niveau'],
                    "sexe": validated['sexe'],
                    "date_naissance": validated['date_naissance'],
                    "lieu_naissance": validated.get('lieu_naissance', ''),
                    "parents_ids": [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "api_externe",
                    "api_client_id": api_client['id']
                }
                
                await db.eleves.insert_one(eleve)
                inscriptions_inserees.append(eleve['id'])
                
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(inscriptions_inserees)
        log_entry['erreurs'] = erreurs
        
        if erreurs:
            log_entry['statut'] = 'partial' if inscriptions_inserees else 'error'
        
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_inscriptions_inserees": len(inscriptions_inserees),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],
            "message": f"{len(inscriptions_inserees)} inscriptions traitées avec succès"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RÉCEPTION DES AFFECTATIONS D'ENSEIGNANTS
# ============================================

@router.post("/api/externe/affectations")
async def recevoir_affectations(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("affectations"))
):
    """
    Recevoir des affectations d'enseignants depuis un système externe
    Supporte JSON, XML, CSV
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/affectations",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Détecter le format
        if file:
            data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                data = DataParser.parse_json(content)
            elif format_type == 'xml':
                data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        # Valider et insérer les affectations
        affectations_inserees = []
        erreurs = []
        
        for idx, item in enumerate(data):
            try:
                # Valider les données
                validated = DataValidator.validate_affectation(item)
                
                # Vérifier que l'enseignant existe
                enseignant = await db.enseignants.find_one(
                    {"id": validated['enseignant_id']},
                    {"_id": 0}
                )
                
                if not enseignant:
                    erreurs.append(f"Ligne {idx + 1}: Enseignant introuvable (ID: {validated['enseignant_id']})")
                    continue
                
                # Vérifier que l'établissement existe
                etablissement = await db.etablissements.find_one(
                    {"id": validated['etablissement_id']},
                    {"_id": 0}
                )
                
                if not etablissement:
                    erreurs.append(f"Ligne {idx + 1}: Établissement introuvable (ID: {validated['etablissement_id']})")
                    continue
                
                # Créer l'historique d'affectation
                affectation = {
                    "id": str(uuid.uuid4()),
                    "enseignant_id": validated['enseignant_id'],
                    "etablissement_id": validated['etablissement_id'],
                    "date_debut": validated['date_debut'],
                    "date_fin": validated.get('date_fin'),
                    "poste": validated.get('poste', 'Enseignant'),
                    "charge_horaire": validated.get('charge_horaire'),
                    "matieres": validated.get('matieres', []),
                    "commentaire": validated.get('commentaire'),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "api_externe",
                    "api_client_id": api_client['id']
                }
                
                await db.historique_affectations.insert_one(affectation)
                
                # Mettre à jour l'établissement_id de l'enseignant
                await db.enseignants.update_one(
                    {"id": validated['enseignant_id']},
                    {"$set": {"etablissement_id": validated['etablissement_id']}}
                )
                
                affectations_inserees.append(affectation['id'])
                
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(affectations_inserees)
        log_entry['erreurs'] = erreurs
        
        if erreurs:
            log_entry['statut'] = 'partial' if affectations_inserees else 'error'
        
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_affectations_inserees": len(affectations_inserees),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],
            "message": f"{len(affectations_inserees)} affectations traitées avec succès"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RÉCEPTION DES ÉVALUATIONS (depuis outils de tests en ligne)
# ============================================

@router.post("/api/externe/evaluations")
async def recevoir_evaluations(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("notes"))
):
    """
    Recevoir des résultats d'évaluations depuis des outils de tests en ligne.
    Accepte JSON, XML, CSV.
    
    Format JSON attendu:
    {
        "etablissement_id": "string",
        "classe_id": "string",
        "matiere": "string",
        "trimestre": "trimestre_1",
        "annee_scolaire": "2025-2026",
        "enseignant_id": "string",
        "notes": [
            {"eleve_id": "string", "note": 15.5, "commentaire": "optional"}
        ]
    }
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/evaluations",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        if file:
            raw_data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                raw_data = DataParser.parse_json(content)
            elif format_type == 'xml':
                raw_data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        notes_inserees = []
        erreurs = []
        
        for idx, item in enumerate(raw_data):
            try:
                # Si le format est groupé (un objet avec un tableau "notes")
                if 'notes' in item and isinstance(item['notes'], list):
                    etab_id = item.get('etablissement_id', '')
                    classe_id = item.get('classe_id', '')
                    matiere = item.get('matiere', '')
                    trimestre = item.get('trimestre', 'trimestre_1')
                    annee = item.get('annee_scolaire', '2025-2026')
                    ens_id = item.get('enseignant_id', '')
                    
                    if not matiere:
                        erreurs.append(f"Bloc {idx + 1}: Matière manquante")
                        continue
                    
                    for n_idx, note_item in enumerate(item['notes']):
                        try:
                            eleve_id = note_item.get('eleve_id', '')
                            note_val = float(note_item.get('note', 0))
                            
                            if not eleve_id:
                                erreurs.append(f"Bloc {idx + 1}, note {n_idx + 1}: eleve_id manquant")
                                continue
                            if note_val < 0 or note_val > 20:
                                erreurs.append(f"Bloc {idx + 1}, note {n_idx + 1}: note invalide ({note_val})")
                                continue
                            
                            note = {
                                "id": str(uuid.uuid4()),
                                "eleve_id": eleve_id,
                                "classe_id": classe_id,
                                "matiere": matiere,
                                "note": note_val,
                                "coefficient": float(note_item.get('coefficient', 1.0)),
                                "trimestre": trimestre,
                                "annee_scolaire": annee,
                                "enseignant_id": ens_id,
                                "commentaire": note_item.get('commentaire'),
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "source": "api_externe",
                                "api_client_id": api_client['id']
                            }
                            await db.notes.insert_one(note)
                            notes_inserees.append(note['id'])
                        except Exception as e:
                            erreurs.append(f"Bloc {idx + 1}, note {n_idx + 1}: {str(e)}")
                else:
                    # Format plat (une note par ligne)
                    validated = DataValidator.validate_note(item)
                    note = {
                        "id": str(uuid.uuid4()),
                        "eleve_id": validated['eleve_id'],
                        "classe_id": validated['classe_id'],
                        "matiere": validated['matiere'],
                        "note": validated['note'],
                        "coefficient": validated['coefficient'],
                        "trimestre": validated['trimestre'],
                        "annee_scolaire": validated['annee_scolaire'],
                        "enseignant_id": validated['enseignant_id'],
                        "commentaire": validated.get('commentaire'),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "source": "api_externe",
                        "api_client_id": api_client['id']
                    }
                    await db.notes.insert_one(note)
                    notes_inserees.append(note['id'])
                    
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(notes_inserees)
        log_entry['erreurs'] = erreurs
        if erreurs:
            log_entry['statut'] = 'partial' if notes_inserees else 'error'
        
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_notes_inserees": len(notes_inserees),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],
            "message": f"{len(notes_inserees)} notes d'évaluation insérées avec succès"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RÉCEPTION DES EFFECTIFS (mise à jour depuis systèmes de gestion)
# ============================================

@router.post("/api/externe/effectifs")
async def recevoir_effectifs(
    request: Request,
    file: Optional[UploadFile] = File(None),
    api_client: dict = Depends(require_permission("inscriptions"))
):
    """
    Recevoir les mises à jour d'effectifs depuis les systèmes de gestion scolaire.
    Accepte JSON, XML, CSV.
    
    Format JSON attendu:
    [
        {
            "etablissement_id": "string",
            "total_eleves": 450,
            "total_enseignants": 28,
            "total_classes": 12,
            "date_maj": "2026-04-04",
            "details_par_niveau": {
                "1ere_annee_primaire": 45,
                "2eme_annee_primaire": 50
            }
        }
    ]
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "api_client_id": api_client['id'],
        "endpoint": "/api/externe/effectifs",
        "methode": "POST",
        "format_donnees": "",
        "statut": "success",
        "nb_enregistrements": 0,
        "erreurs": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        if file:
            raw_data = await DataParser.parse_csv(file)
            log_entry['format_donnees'] = 'csv'
        else:
            content_type = request.headers.get('content-type', 'application/json')
            format_type = DataParser.detect_format(content_type)
            log_entry['format_donnees'] = format_type
            
            body = await request.body()
            content = body.decode('utf-8')
            
            if format_type == 'json':
                raw_data = DataParser.parse_json(content)
            elif format_type == 'xml':
                raw_data = DataParser.parse_xml(content)
            else:
                raise HTTPException(status_code=400, detail="Format non supporté")
        
        effectifs_traites = []
        erreurs = []
        
        for idx, item in enumerate(raw_data):
            try:
                etab_id = item.get('etablissement_id', '')
                if not etab_id:
                    erreurs.append(f"Ligne {idx + 1}: etablissement_id manquant")
                    continue
                
                # Vérifier que l'établissement existe
                etab = await db.etablissements.find_one({"id": etab_id}, {"_id": 0, "id": 1, "nom": 1})
                if not etab:
                    erreurs.append(f"Ligne {idx + 1}: Établissement introuvable ({etab_id})")
                    continue
                
                # Stocker le snapshot des effectifs
                snapshot = {
                    "id": str(uuid.uuid4()),
                    "etablissement_id": etab_id,
                    "total_eleves": int(item.get('total_eleves', 0)),
                    "total_enseignants": int(item.get('total_enseignants', 0)),
                    "total_classes": int(item.get('total_classes', 0)),
                    "date_maj": item.get('date_maj', datetime.now(timezone.utc).strftime('%Y-%m-%d')),
                    "details_par_niveau": item.get('details_par_niveau', {}),
                    "source": "api_externe",
                    "api_client_id": api_client['id'],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                await db.effectifs_snapshots.insert_one(snapshot)
                
                # Mettre à jour les compteurs de l'établissement
                update_fields = {}
                if item.get('total_eleves'):
                    update_fields['effectif_eleves'] = int(item['total_eleves'])
                if item.get('total_enseignants'):
                    update_fields['effectif_enseignants'] = int(item['total_enseignants'])
                if item.get('total_classes'):
                    update_fields['effectif_classes'] = int(item['total_classes'])
                update_fields['derniere_maj_effectifs'] = datetime.now(timezone.utc).isoformat()
                
                if update_fields:
                    await db.etablissements.update_one(
                        {"id": etab_id},
                        {"$set": update_fields}
                    )
                
                effectifs_traites.append(etab_id)
                
            except Exception as e:
                erreurs.append(f"Ligne {idx + 1}: {str(e)}")
        
        log_entry['nb_enregistrements'] = len(effectifs_traites)
        log_entry['erreurs'] = erreurs
        if erreurs:
            log_entry['statut'] = 'partial' if effectifs_traites else 'error'
        
        await db.logs_api_externe.insert_one(log_entry)
        
        return {
            "success": True,
            "nb_etablissements_traites": len(effectifs_traites),
            "nb_erreurs": len(erreurs),
            "erreurs": erreurs[:10],
            "message": f"Effectifs mis à jour pour {len(effectifs_traites)} établissement(s)"
        }
        
    except Exception as e:
        log_entry['statut'] = 'error'
        log_entry['erreurs'] = [str(e)]
        await db.logs_api_externe.insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# STATISTIQUES DE PRÉSENCE
# ============================================

@router.get("/api/presences/statistiques")
async def obtenir_statistiques_presence(
    classe_id: Optional[str] = None,
    etablissement_id: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les statistiques de présence/absence"""
    
    # Construire le filtre
    query = {}
    if classe_id:
        query['classe_id'] = classe_id
    if etablissement_id:
        query['etablissement_id'] = etablissement_id
    if date_debut:
        query['date'] = {"$gte": date_debut}
    if date_fin:
        if 'date' in query:
            query['date']['$lte'] = date_fin
        else:
            query['date'] = {"$lte": date_fin}
    
    # Récupérer toutes les présences
    presences = await db.presences.find(query, {"_id": 0}).to_list(10000)
    
    if not presences:
        return {
            "taux_presence": 0,
            "nb_presences": 0,
            "nb_absences": 0,
            "nb_absences_justifiees": 0,
            "nb_absences_injustifiees": 0,
            "eleves_absenteisme_eleve": []
        }
    
    # Calculer les statistiques
    nb_presences = sum(1 for p in presences if p['present'])
    nb_absences = sum(1 for p in presences if not p['present'])
    nb_absences_justifiees = sum(1 for p in presences if not p['present'] and p.get('justifie', False))
    nb_absences_injustifiees = nb_absences - nb_absences_justifiees
    
    total = len(presences)
    taux_presence = (nb_presences / total * 100) if total > 0 else 0
    
    # Calculer l'absentéisme par élève
    from collections import defaultdict
    absences_par_eleve = defaultdict(lambda: {'total': 0, 'absences': 0})
    
    for p in presences:
        eleve_id = p['eleve_id']
        absences_par_eleve[eleve_id]['total'] += 1
        if not p['present']:
            absences_par_eleve[eleve_id]['absences'] += 1
    
    # Identifier les élèves avec fort absentéisme (> 20%)
    eleves_problematiques = []
    for eleve_id, stats in absences_par_eleve.items():
        taux_absence = (stats['absences'] / stats['total'] * 100) if stats['total'] > 0 else 0
        if taux_absence > 20:
            # Récupérer info élève
            eleve_info = await db.eleves.find_one({"id": eleve_id}, {"_id": 0})
            if eleve_info:
                user_info = await db.users.find_one({"id": eleve_info['user_id']}, {"_id": 0})
                eleves_problematiques.append({
                    "eleve_id": eleve_id,
                    "nom": f"{user_info.get('nom', '')} {user_info.get('prenom', '')}",
                    "taux_absence": round(taux_absence, 2),
                    "nb_absences": stats['absences'],
                    "nb_total_jours": stats['total']
                })
    
    # Trier par taux d'absence décroissant
    eleves_problematiques.sort(key=lambda x: x['taux_absence'], reverse=True)
    
    return {
        "periode_debut": date_debut or "Non spécifié",
        "periode_fin": date_fin or "Non spécifié",
        "taux_presence": round(taux_presence, 2),
        "nb_presences": nb_presences,
        "nb_absences": nb_absences,
        "nb_absences_justifiees": nb_absences_justifiees,
        "nb_absences_injustifiees": nb_absences_injustifiees,
        "eleves_absenteisme_eleve": eleves_problematiques[:20]  # Top 20
    }


# ============================================
# GÉNÉRATION AUTOMATIQUE DE BULLETINS (DÉSACTIVÉ)
# ============================================

# Fonctionnalité désactivée à la demande de l'utilisateur


# ============================================
# STATUT DES SOURCES DE DONNÉES
# ============================================

@router.get("/api/externe/sources/status")
async def get_sources_status(
    current_user: dict = Depends(get_current_user)
):
    """Obtenir le statut des sources de données externes"""
    
    # Compter les clients API actifs
    nb_clients = await db.api_clients.count_documents({"actif": True})
    
    # Derniers logs par endpoint
    endpoints = [
        "/api/externe/notes", "/api/externe/evaluations",
        "/api/externe/presences", "/api/externe/effectifs",
        "/api/externe/inscriptions", "/api/externe/affectations"
    ]
    
    sources = []
    for ep in endpoints:
        last_log = await db.logs_api_externe.find_one(
            {"endpoint": ep}, {"_id": 0}
        )
        total_logs = await db.logs_api_externe.count_documents({"endpoint": ep})
        total_success = await db.logs_api_externe.count_documents({"endpoint": ep, "statut": "success"})
        total_records = 0
        
        pipeline = [
            {"$match": {"endpoint": ep}},
            {"$group": {"_id": None, "total": {"$sum": "$nb_enregistrements"}}}
        ]
        agg = await db.logs_api_externe.aggregate(pipeline).to_list(1)
        if agg:
            total_records = agg[0].get("total", 0)
        
        sources.append({
            "endpoint": ep,
            "nom": ep.split("/")[-1].replace("-", " ").title(),
            "nb_appels": total_logs,
            "nb_succes": total_success,
            "nb_enregistrements_total": total_records,
            "dernier_appel": last_log.get("timestamp") if last_log else None,
            "dernier_statut": last_log.get("statut") if last_log else "jamais_utilise"
        })
    
    # Stats globales
    total_logs = await db.logs_api_externe.count_documents({})
    total_presences = await db.presences.count_documents({})
    total_effectifs_snapshots = await db.effectifs_snapshots.count_documents({})
    
    return {
        "nb_clients_api_actifs": nb_clients,
        "sources": sources,
        "stats_globales": {
            "total_appels_api": total_logs,
            "total_presences_enregistrees": total_presences,
            "total_snapshots_effectifs": total_effectifs_snapshots
        }
    }


@router.get("/api/externe/logs")
async def get_logs_externes(
    limit: int = 50,
    endpoint: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les logs des appels API externes"""
    query = {}
    if endpoint:
        query["endpoint"] = endpoint
    
    logs = await db.logs_api_externe.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}


