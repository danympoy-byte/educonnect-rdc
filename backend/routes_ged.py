"""
API Routes pour le Système de Gestion Électronique de Documents (GED)
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import uuid
import shutil
from pathlib import Path

from models import (
    Document, HistoriqueAction, Commentaire, NotificationDocument,
    StatutDocument, TypeAction, NiveauDiffusion, ModeLivraison, PrioriteDocument
)
from auth import get_current_user
from email_service import (
    email_nouveau_document,
    email_document_rejete,
    email_document_valide
)

router = APIRouter(prefix="/api/documents", tags=["GED"])

# Dossier pour stocker les fichiers uploadés
UPLOAD_DIR = Path("/app/uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


async def generer_numero_reference(db):
    """Génère un numéro de référence unique : MIN/EDU/2025/001"""
    annee = datetime.now(timezone.utc).year
    # Compter les documents de l'année en cours
    count = await db.documents.count_documents({
        "numero_reference": {"$regex": f"MIN/EDU/{annee}/"}
    })
    numero = count + 1
    return f"MIN/EDU/{annee}/{numero:04d}"



async def get_n_plus_1(user_id: str, db) -> Optional[dict]:
    """
    Trouve le N+1 (supérieur hiérarchique direct) d'un utilisateur
    Basé sur la hiérarchie des services MINEPST
    
    Returns: dict avec {id, nom, prenom, service_id, service_nom} ou None
    """
    # Récupérer l'utilisateur
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return None
    
    # Récupérer le service actif de l'utilisateur
    service_profiles = user.get("service_profiles", [])
    if not service_profiles:
        return None
    
    service_actif_id = user.get("service_actif_id")
    if service_actif_id:
        profile = next((p for p in service_profiles if p.get("service_id") == service_actif_id), None)
    else:
        profile = service_profiles[0]
    
    if not profile:
        return None
    
    service_id = profile.get("service_id")
    if not service_id:
        return None
    
    # Récupérer le service
    service = await db.services.find_one({"id": service_id}, {"_id": 0})
    if not service:
        return None
    
    # Récupérer le responsable du service (c'est le N+1)
    responsable_id = service.get("responsable_id")
    if not responsable_id:
        # Pas de responsable défini, chercher le parent
        parent_id = service.get("parent_id")
        if parent_id:
            parent_service = await db.services.find_one({"id": parent_id}, {"_id": 0})
            if parent_service:
                responsable_id = parent_service.get("responsable_id")
    
    if not responsable_id:
        return None
    
    # Récupérer les infos du N+1
    n_plus_1 = await db.users.find_one({"id": responsable_id}, {"_id": 0})
    if not n_plus_1:
        return None
    
    return {
        "id": n_plus_1.get("id"),
        "nom": n_plus_1.get("nom", ""),
        "prenom": n_plus_1.get("prenom", ""),
        "service_id": service_id,
        "service_nom": service.get("nom", "")
    }


async def check_validation_n_plus_1_requise(
    createur_id: str,
    niveau_diffusion: str,
    collaborateurs_ids: List[str],
    db
) -> tuple[bool, Optional[dict]]:
    """
    Vérifie si la validation du N+1 est requise
    
    Règles:
    - Si niveau_diffusion = "service" → Validation N+1 requise
    - Si collaborateurs de différents services → Validation N+1 requise
    
    Returns: (validation_requise: bool, n_plus_1: dict ou None)
    """
    # Vérifier si diffusion à tout le service
    if niveau_diffusion == "service":
        n_plus_1 = await get_n_plus_1(createur_id, db)
        return (True, n_plus_1)
    
    # Vérifier si collaborateurs de différents services
    if collaborateurs_ids and len(collaborateurs_ids) > 0:
        # Récupérer le service du créateur
        createur = await db.users.find_one({"id": createur_id}, {"_id": 0})
        if not createur:
            return (False, None)
        
        createur_service_profiles = createur.get("service_profiles", [])
        if not createur_service_profiles:
            return (False, None)
        
        createur_service_actif_id = createur.get("service_actif_id")
        if createur_service_actif_id:
            createur_profile = next((p for p in createur_service_profiles if p.get("service_id") == createur_service_actif_id), None)
        else:
            createur_profile = createur_service_profiles[0]
        
        if not createur_profile:
            return (False, None)
        
        createur_service_id = createur_profile.get("service_id")
        
        # Vérifier les services des collaborateurs
        for collab_id in collaborateurs_ids:
            collab = await db.users.find_one({"id": collab_id}, {"_id": 0})
            if collab:
                collab_service_profiles = collab.get("service_profiles", [])
                if collab_service_profiles:
                    collab_service_actif_id = collab.get("service_actif_id")
                    if collab_service_actif_id:
                        collab_profile = next((p for p in collab_service_profiles if p.get("service_id") == collab_service_actif_id), None)
                    else:
                        collab_profile = collab_service_profiles[0]
                    
                    if collab_profile:
                        collab_service_id = collab_profile.get("service_id")
                        # Si service différent du créateur
                        if collab_service_id != createur_service_id:
                            n_plus_1 = await get_n_plus_1(createur_id, db)
                            return (True, n_plus_1)
    
    return (False, None)


def creer_historique_action(db, document_id: str, user: dict, type_action: TypeAction, 
                            commentaire: str = None, raison_rejet: str = None,
                            ancien_proprietaire: str = None, nouveau_proprietaire: str = None,
                            type_tache: str = None):
    """Crée une entrée dans l'historique des actions"""
    user_id = get_user_id(user)
    action = HistoriqueAction(
        document_id=document_id,
        user_id=user_id,
        user_nom=f"{user.get('prenom', '')} {user.get('nom', '')}",
        user_role=user.get("role", ""),
        type_action=type_action,
        type_tache=type_tache,
        commentaire=commentaire,
        raison_rejet=raison_rejet,
        ancien_proprietaire=ancien_proprietaire,
        nouveau_proprietaire=nouveau_proprietaire
    )
    db.historique_actions.insert_one(action.dict())
    return action


@router.post("/")
async def creer_document(
    titre: str = Form(...),
    description: str = Form(None),
    type_document: str = Form(...),
    categorie: str = Form(None),
    destinataire_final_id: str = Form(...),
    destinataire_final_nom: str = Form(...),
    circuit_validation: str = Form(""),  # Liste d'IDs séparés par virgules
    circuit_validation_roles: str = Form(""),  # NOUVEAU - Rôles séparés par virgules (contributeur, visa_correction, signature, expedition)
    niveau_diffusion: str = Form("prive"),
    mode_livraison: str = Form("interne"),
    niveau_confidentialite: str = Form("public"),
    necessite_signature: bool = Form(False),
    cc_user_ids: str = Form(""),  # Liste séparée par virgules
    collaborateurs_ids: str = Form(""),  # NOUVEAU - Liste des collaborateurs séparés par virgules
    mots_cles: str = Form(""),
    fichier: UploadFile = File(None),
    # Nouveaux paramètres pour les modèles
    save_as_template: bool = Form(False),
    template_name: str = Form(None),
    template_description: str = Form(None),
    load_from_template_id: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Créer un nouveau document (avec support des modèles et collaboration)
    
    Règles de validation N+1:
    - Si niveau_diffusion = "service" → Validation N+1 automatique
    - Si collaborateurs de différents services → Validation N+1 automatique
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Si on charge depuis un modèle, récupérer ses données
    if load_from_template_id:
        template = await db.documents.find_one({"id": load_from_template_id, "is_template": True}, {"_id": 0})
        if template:
            # Pré-remplir avec les données du modèle (si non fourni dans la requête)
            titre = titre or template.get("titre", "")
            description = description or template.get("description", "")
            type_document = type_document or template.get("type_document", "")
            categorie = categorie or template.get("categorie", "")
            circuit_validation = circuit_validation or ",".join(template.get("circuit_validation", []))
    
    # Vérifier la taille du fichier (max 50MB)
    file_size = 0
    if fichier:
        fichier.file.seek(0, 2)  # Aller à la fin
        file_size = fichier.file.tell()
        fichier.file.seek(0)  # Retour au début
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 50MB)")
    
    # Générer numéro de référence unique
    numero_ref = await generer_numero_reference(db)
    
    # Parser les listes
    circuit_ids = [id.strip() for id in circuit_validation.split(",") if id.strip()]
    circuit_roles = [role.strip() for role in circuit_validation_roles.split(",") if role.strip()]
    cc_ids = [id.strip() for id in cc_user_ids.split(",") if id.strip()]
    collab_ids = [id.strip() for id in collaborateurs_ids.split(",") if id.strip()]
    
    # S'assurer que chaque utilisateur du circuit a un rôle (défaut: contributeur)
    while len(circuit_roles) < len(circuit_ids):
        circuit_roles.append("contributeur")
    
    # NOUVEAU : Vérifier si validation N+1 requise
    validation_requise, n_plus_1 = await check_validation_n_plus_1_requise(
        user_id,
        niveau_diffusion,
        collab_ids,
        db
    )
    
    # Si validation N+1 requise, l'ajouter au début du circuit
    if validation_requise and n_plus_1:
        # Insérer le N+1 au début du circuit si pas déjà présent
        if n_plus_1["id"] not in circuit_ids:
            circuit_ids.insert(0, n_plus_1["id"])
            # Ajouter un rôle par défaut pour le N+1 (visa_correction)
            circuit_roles.insert(0, "visa_correction")
    
    # Récupérer les infos des collaborateurs
    collaborateurs_noms = []
    collaborateurs_services = []
    for collab_id in collab_ids:
        collab = await db.users.find_one({"id": collab_id}, {"_id": 0})
        if collab:
            collaborateurs_noms.append(f"{collab.get('prenom', '')} {collab.get('nom', '')}")
            # Récupérer le service du collaborateur
            collab_service_profiles = collab.get("service_profiles", [])
            if collab_service_profiles:
                collab_service_actif_id = collab.get("service_actif_id")
                if collab_service_actif_id:
                    collab_profile = next((p for p in collab_service_profiles if p.get("service_id") == collab_service_actif_id), None)
                else:
                    collab_profile = collab_service_profiles[0]
                
                if collab_profile:
                    service_id = collab_profile.get("service_id")
                    service = await db.services.find_one({"id": service_id}, {"_id": 0})
                    if service:
                        collaborateurs_services.append(service.get("nom", ""))
                    else:
                        collaborateurs_services.append("N/A")
                else:
                    collaborateurs_services.append("N/A")
            else:
                collaborateurs_services.append("N/A")
    
    # Créer le document
    document_data = {
        "numero_reference": numero_ref,
        "titre": titre,
        "description": description,
        "type_document": type_document,
        "categorie": categorie,
        "createur_id": user_id,
        "createur_nom": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        "createur_service_id": "",  # TODO: récupérer depuis user
        "createur_service_nom": "",
        "destinataire_final_id": destinataire_final_id,
        "destinataire_final_nom": destinataire_final_nom,
        "destinataire_service_id": "",  # TODO
        "destinataire_service_nom": "",
        "proprietaire_actuel_id": user_id,
        "proprietaire_actuel_nom": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        "circuit_validation": circuit_ids,
        "circuit_validation_noms": [],
        "circuit_validation_services": [],
        "circuit_validation_roles": circuit_roles,  # NOUVEAU - Rôles pour chaque validateur
        "etape_actuelle": 0,
        "niveau_diffusion": niveau_diffusion,
        "mode_livraison": mode_livraison,
        "niveau_confidentialite": niveau_confidentialite,
        "necessite_signature": necessite_signature,
        "cc_user_ids": cc_ids,
        "collaborateurs_ids": collab_ids,
        "collaborateurs_noms": collaborateurs_noms,
        "collaborateurs_services": collaborateurs_services,
        "validation_n_plus_1_requise": validation_requise,
        "validation_n_plus_1_user_id": n_plus_1["id"] if n_plus_1 else None,
        "validation_n_plus_1_nom": f"{n_plus_1['prenom']} {n_plus_1['nom']}" if n_plus_1 else None,
        "mots_cles": [kw.strip() for kw in mots_cles.split(",") if kw.strip()],
        "watermark_id": str(uuid.uuid4()),  # ID unique pour traçabilité
        # Gestion des modèles
        "is_template": save_as_template,
        "template_name": template_name if save_as_template else None,
        "template_description": template_description if save_as_template else None,
        # Champs du modèle Document
        "statut": "brouillon",
        "priorite": PrioriteDocument.NORMALE.value,
        "version": 1,
        "versions_precedentes": [],
        "date_creation": datetime.now(timezone.utc).isoformat(),
        "est_brouillon": True,
        "est_finalise": False,
        "est_signe": False
    }
    
    # Utiliser le modèle Document pour valider
    document = Document(**document_data)
    
    # Upload du fichier si présent
    if fichier:
        file_extension = os.path.splitext(fichier.filename)[1]
        file_path = UPLOAD_DIR / f"{document.id}{file_extension}"
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(fichier.file, buffer)
        
        document.fichier_url = str(file_path)
        document.fichier_nom = fichier.filename
        document.fichier_type = file_extension.replace(".", "")
        document.fichier_taille = file_size
    
    # Sauvegarder en base
    await db.documents.insert_one(document.model_dump())
    
    # Créer l'historique
    action_msg = f"Modèle créé : {template_name}" if save_as_template else f"Document créé : {titre}"
    if validation_requise and n_plus_1:
        action_msg += f" (Validation N+1 requise : {n_plus_1['prenom']} {n_plus_1['nom']})"
    
    creer_historique_action(
        db, document.id, current_user, TypeAction.CREATION,
        action_msg
    )
    
    return {
        "message": "Document créé avec succès",
        "document": document.model_dump(),
        "validation_n_plus_1_requise": validation_requise,
        "n_plus_1": n_plus_1 if validation_requise else None
    }


@router.get("/")
async def lister_documents(
    statut: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Lister les documents accessibles par l'utilisateur"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Construire le filtre selon le rôle et les permissions
    filtre = {}
    
    # Récupérer le rôle (peut être None avec le nouveau système multi-services)
    user_role = current_user.get("role")
    
    # Le ministre voit tout
    if user_role == "ministre":
        pass  # Pas de filtre
    # Les managers voient tout leur service
    elif user_role in ["secretaire_general", "directeur_provincial", "chef_sous_division"]:
        # TODO: Filtrer par service quand la notion de service sera implémentée
        pass
    else:
        # Utilisateur normal : voit ses documents créés, reçus, ou selon niveau diffusion
        filtre = {
            "$or": [
                {"createur_id": user_id},
                {"proprietaire_actuel_id": user_id},
                {"cc_user_ids": user_id},
                {"niveau_diffusion": "tous"}
            ]
        }
    
    if statut:
        filtre["statut"] = statut
    
    documents = await db.documents.find(filtre, {"_id": 0}).to_list(1000)
    return documents



@router.get("/templates/list")
async def lister_templates(current_user: dict = Depends(get_current_user)):
    """Lister tous les modèles (templates) disponibles"""
    from dependencies import get_db

    db = get_db()
    
    # Récupérer uniquement les documents qui sont des modèles
    templates = await db.documents.find(
        {"is_template": True}, 
        {"_id": 0}
    ).sort("date_creation", -1).to_list(100)
    
    return templates


@router.get("/{document_id}")
async def obtenir_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les détails d'un document"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les permissions
    user_role = current_user.get("role")
    peut_voir = (
        user_role == "ministre" or
        document["createur_id"] == user_id or
        document["proprietaire_actuel_id"] == user_id or
        user_id in document.get("cc_user_ids", []) or
        document["niveau_diffusion"] == "tous"
    )
    
    if not peut_voir:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Enregistrer la consultation dans l'historique
    creer_historique_action(
        db, document_id, current_user, TypeAction.CONSULTATION
    )
    
    # Récupérer l'historique des actions
    historique = await db.historique_actions.find(
        {"document_id": document_id}, {"_id": 0}
    ).sort("date_action", -1).to_list(100)
    
    # Récupérer les commentaires
    commentaires = await db.commentaires.find(
        {"document_id": document_id}, {"_id": 0}
    ).sort("date_creation", -1).to_list(100)
    
    return {
        "document": document,
        "historique": historique,
        "commentaires": commentaires
    }


@router.post("/{document_id}/prendre-en-charge")
async def prendre_en_charge(
    document_id: str,
    accepter: bool = True,
    raison_refus: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Prendre en charge un document (accepter ou refuser)"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire actuel
    if document["proprietaire_actuel_id"] != user_id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire actuel de ce document")
    
    if accepter:
        # Accepter le document
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "statut": StatutDocument.EN_COURS.value,
                    "date_prise_en_charge": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        creer_historique_action(
            db, document_id, current_user, TypeAction.PRISE_EN_CHARGE,
            "Document pris en charge"
        )
        
        return {"message": "Document pris en charge avec succès"}
    else:
        # Refuser le document (raison obligatoire)
        if not raison_refus:
            raise HTTPException(status_code=400, detail="La raison du refus est obligatoire")
        
        # Retourner au créateur
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "statut": StatutDocument.REJETE.value,
                    "proprietaire_actuel_id": document["createur_id"],
                    "proprietaire_actuel_nom": document["createur_nom"]
                }
            }
        )
        
        creer_historique_action(
            db, document_id, current_user, TypeAction.REJET,
            raison_rejet=raison_refus
        )
        
        # Envoyer notification email au créateur
        createur = await db.users.find_one({"id": document["createur_id"]}, {"_id": 0})
        if createur and createur.get("email"):
            url_frontend = os.getenv("FRONTEND_URL", "").replace("/api", "")
            if not url_frontend:
                raise ValueError("FRONTEND_URL must be configured for email notifications")
            url_document = f"{url_frontend}/#/documents/{document_id}"
            
            email_document_rejete(
                destinataire_email=createur["email"],
                destinataire_nom=document["createur_nom"],
                document_titre=document["titre"],
                document_ref=document["numero_reference"],
                rejeteur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
                raison_rejet=raison_refus,
                url_document=url_document
            )
        
        return {"message": "Document refusé", "raison": raison_refus}


@router.post("/{document_id}/transmettre")
async def transmettre_document(
    document_id: str,
    destinataire_id: str,
    destinataire_nom: str,
    commentaire: str = None,
    type_tache: str = "info",  # NOUVEAU - Type de tâche (info, class, asoc, cf)
    current_user: dict = Depends(get_current_user)
):
    """Transmettre un document à un autre utilisateur avec un type de tâche spécifique"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire actuel
    if document["proprietaire_actuel_id"] != user_id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire actuel")
    
    # Mettre à jour le propriétaire
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "proprietaire_actuel_id": destinataire_id,
                "proprietaire_actuel_nom": destinataire_nom,
                "statut": StatutDocument.EN_ATTENTE.value
            }
        }
    )
    
    # Libellés des types de tâches pour l'historique
    type_tache_labels = {
        "info": "Information (lecture seule)",
        "class": "Classement requis",
        "asoc": "Association à un dossier",
        "cf": "Copie pour information"
    }
    
    # Enregistrer dans l'historique avec le type de tâche
    commentaire_historique = commentaire or f"Transmis à {destinataire_nom}"
    commentaire_historique += f" - Tâche: {type_tache_labels.get(type_tache, type_tache.upper())}"
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.TRANSMISSION,
        commentaire=commentaire_historique,
        ancien_proprietaire=user_id,
        nouveau_proprietaire=destinataire_id,
        type_tache=type_tache
    )
    
    # Envoyer notification email au destinataire
    destinataire = await db.users.find_one({"id": destinataire_id}, {"_id": 0})
    if destinataire and destinataire.get("email"):
        url_frontend = os.getenv("FRONTEND_URL", "").replace("/api", "")
        if not url_frontend:
            raise ValueError("FRONTEND_URL must be configured for email notifications")
        url_document = f"{url_frontend}/#/documents/{document_id}"
        
        email_nouveau_document(
            destinataire_email=destinataire["email"],
            destinataire_nom=destinataire_nom,
            document_titre=document["titre"],
            document_ref=document["numero_reference"],
            expediteur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
            url_document=url_document
        )
    
    return {"message": f"Document transmis à {destinataire_nom}"}




@router.post("/{document_id}/deleguer")
async def deleguer_tache(
    document_id: str,
    delegataire_id: str,
    delegataire_nom: str,
    commentaire: str = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Déléguer une tâche à un autre utilisateur
    Différence avec transmission : la délégation signifie "je ne peux pas traiter, quelqu'un d'autre le fait pour moi"
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire actuel
    if document["proprietaire_actuel_id"] != user_id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire actuel de ce document")
    
    # Vérifier que l'utilisateur ne se délègue pas à lui-même
    if delegataire_id == user_id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous déléguer une tâche à vous-même")
    
    # Mettre à jour le propriétaire
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "proprietaire_actuel_id": delegataire_id,
                "proprietaire_actuel_nom": delegataire_nom,
                "statut": StatutDocument.EN_ATTENTE.value
            }
        }
    )
    
    # Enregistrer dans l'historique
    commentaire_historique = commentaire or f"Tâche déléguée à {delegataire_nom}"
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.DELEGATION,
        commentaire=commentaire_historique,
        ancien_proprietaire=user_id,
        nouveau_proprietaire=delegataire_id
    )
    
    # Envoyer notification email au délégataire
    delegataire = await db.users.find_one({"id": delegataire_id}, {"_id": 0})
    if delegataire and delegataire.get("email"):
        url_frontend = os.getenv("FRONTEND_URL", "").replace("/api", "")
        if not url_frontend:
            raise ValueError("FRONTEND_URL must be configured for email notifications")
        url_document = f"{url_frontend}/#/documents/{document_id}"
        
        email_nouveau_document(
            destinataire_email=delegataire["email"],
            destinataire_nom=delegataire_nom,
            document_titre=document["titre"],
            document_ref=document["numero_reference"],
            expediteur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
            url_document=url_document
        )
    
    return {
        "message": f"Tâche déléguée à {delegataire_nom}",
        "delegataire_id": delegataire_id,
        "delegataire_nom": delegataire_nom
    }


@router.post("/{document_id}/valider")
async def valider_document(
    document_id: str,
    commentaire: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Valider un document (validation finale)"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est le destinataire final
    if document["destinataire_final_id"] != user_id:
        raise HTTPException(status_code=403, detail="Seul le destinataire final peut valider")
    
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "statut": StatutDocument.VALIDE.value,
                "date_validation": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.VALIDATION,
        commentaire=commentaire or "Document validé"
    )
    
    return {"message": "Document validé avec succès"}


@router.post("/{document_id}/commentaires")
async def ajouter_commentaire(
    document_id: str,
    contenu: str,
    est_interne: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Ajouter un commentaire sur un document"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    commentaire = Commentaire(
        document_id=document_id,
        user_id=user_id,
        user_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        contenu=contenu,
        est_interne=est_interne
    )
    
    db.commentaires.insert_one(commentaire.dict())
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.COMMENTAIRE,
        commentaire=contenu
    )
    
    return {"message": "Commentaire ajouté", "commentaire": commentaire.dict()}


@router.get("/{document_id}/telecharger")
async def telecharger_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Télécharger le fichier d'un document"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    if not document.get("fichier_url"):
        raise HTTPException(status_code=404, detail="Aucun fichier attaché")
    
    # Vérifier les permissions
    user_role = current_user.get("role")
    peut_voir = (
        user_role == "ministre" or
        document["createur_id"] == user_id or
        document["proprietaire_actuel_id"] == user_id or
        user_id in document.get("cc_user_ids", [])
    )
    
    if not peut_voir:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Enregistrer le téléchargement dans l'historique
    creer_historique_action(
        db, document_id, current_user, TypeAction.CONSULTATION,
        "Fichier téléchargé"
    )



@router.post("/{document_id}/avancer-circuit")
async def avancer_dans_circuit(
    document_id: str,
    commentaire: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Avancer un document dans son circuit de validation"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur est le propriétaire actuel
    if document["proprietaire_actuel_id"] != user_id:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas le propriétaire actuel")
    
    # Si pas de circuit ou circuit terminé, valider directement
    if not document.get("circuit_validation") or len(document["circuit_validation"]) == 0:
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "statut": StatutDocument.VALIDE.value,
                    "date_validation": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        creer_historique_action(
            db, document_id, current_user, TypeAction.VALIDATION,
            commentaire=commentaire or "Document validé (pas de circuit)"
        )
        
        return {"message": "Document validé", "termine": True}
    
    # Avancer dans le circuit
    etape_actuelle = document.get("etape_actuelle", 0)
    circuit = document["circuit_validation"]
    
    # Si on est à la dernière étape, valider
    if etape_actuelle >= len(circuit) - 1:
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "statut": StatutDocument.VALIDE.value,
                    "date_validation": datetime.now(timezone.utc).isoformat(),
                    "etape_actuelle": etape_actuelle + 1
                }
            }
        )
        
        creer_historique_action(
            db, document_id, current_user, TypeAction.VALIDATION,
            commentaire=commentaire or "Validation finale"
        )
        
        return {"message": "Document validé (circuit terminé)", "termine": True}
    
    # Passer à l'étape suivante
    prochain_user_id = circuit[etape_actuelle + 1]
    
    # Récupérer le nom du prochain validateur
    prochain_user = await db.users.find_one({"id": prochain_user_id}, {"_id": 0})
    if not prochain_user:
        raise HTTPException(status_code=404, detail="Prochain validateur non trouvé")
    
    prochain_nom = f"{prochain_user.get('prenom', '')} {prochain_user.get('nom', '')}"
    
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "proprietaire_actuel_id": prochain_user_id,
                "proprietaire_actuel_nom": prochain_nom,
                "etape_actuelle": etape_actuelle + 1,
                "statut": StatutDocument.EN_ATTENTE.value
            }
        }
    )
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.TRANSMISSION,
        commentaire=commentaire or f"Transmis à {prochain_nom} (étape {etape_actuelle + 2}/{len(circuit)})",
        ancien_proprietaire=user_id,
        nouveau_proprietaire=prochain_user_id
    )
    
    # TODO: Envoyer notification email au prochain validateur
    
    return {
        "message": f"Document transmis à {prochain_nom}",
        "etape": etape_actuelle + 2,
        "total_etapes": len(circuit),
        "termine": False
    }


@router.post("/{document_id}/bypass-etape")
async def bypass_etape_validation(
    document_id: str,
    justification: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Contourner l'étape actuelle du circuit de validation (dérogation)
    Requiert une justification et un rôle hiérarchique suffisant
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier que l'utilisateur a le droit de faire un bypass
    # Seuls les rôles hiérarchiques peuvent faire un bypass
    user_role = current_user.get("role")
    roles_autorises = ["ministre", "secretaire_general", "directeur_provincial"]
    
    if user_role not in roles_autorises:
        raise HTTPException(
            status_code=403, 
            detail="Seuls les responsables hiérarchiques peuvent effectuer une dérogation"
        )
    
    # Justification obligatoire
    if not justification or len(justification.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Une justification détaillée (minimum 10 caractères) est obligatoire pour une dérogation"
        )
    
    # Récupérer le circuit de validation
    circuit = document.get("circuit_validation", [])
    etape_actuelle = document.get("etape_actuelle", 0)
    
    if not circuit or etape_actuelle >= len(circuit):
        raise HTTPException(
            status_code=400,
            detail="Aucune étape à contourner (circuit terminé ou vide)"
        )
    
    # Passer à l'étape suivante (bypass)
    nouvelle_etape = etape_actuelle + 1
    
    # Si c'était la dernière étape, valider le document
    if nouvelle_etape >= len(circuit):
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "statut": StatutDocument.VALIDE.value,
                    "date_validation": datetime.now(timezone.utc).isoformat(),
                    "etape_actuelle": nouvelle_etape
                }
            }
        )
        
        creer_historique_action(
            db, document_id, current_user, TypeAction.BYPASS,
            commentaire=f"Dérogation (étape finale) - Justification: {justification}"
        )
        
        return {
            "message": "Dérogation effectuée - Document validé",
            "termine": True,
            "justification": justification
        }
    
    # Sinon, passer à l'étape suivante
    prochain_user_id = circuit[nouvelle_etape]
    prochain_user = await db.users.find_one({"id": prochain_user_id}, {"_id": 0})
    
    if not prochain_user:
        raise HTTPException(status_code=404, detail="Prochain validateur non trouvé")
    
    prochain_nom = f"{prochain_user.get('prenom', '')} {prochain_user.get('nom', '')}"
    
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "proprietaire_actuel_id": prochain_user_id,
                "proprietaire_actuel_nom": prochain_nom,
                "etape_actuelle": nouvelle_etape,
                "statut": StatutDocument.EN_ATTENTE.value
            }
        }
    )
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.BYPASS,
        commentaire=f"Dérogation d'étape - Passé à {prochain_nom} - Justification: {justification}",
        ancien_proprietaire=document["proprietaire_actuel_id"],
        nouveau_proprietaire=prochain_user_id
    )
    
    return {
        "message": f"Dérogation effectuée - Document transmis à {prochain_nom}",
        "etape": nouvelle_etape + 1,
        "total_etapes": len(circuit),
        "termine": False,
        "justification": justification
    }


@router.get("/stats/dashboard")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les statistiques pour le dashboard"""


@router.post("/{document_id}/verrouiller")
async def verrouiller_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Verrouiller un document pour éviter les modifications simultanées
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier si déjà verrouillé
    if document.get("est_verrouille", False):
        verrouille_par = document.get("verrouille_par_user_nom", "Un autre utilisateur")
        date_verrou = document.get("date_verrouillage", "")
        
        # Vérifier si le verrouillage a expiré (30 minutes)
        if date_verrou:
            date_verrou_dt = datetime.fromisoformat(date_verrou.replace('Z', '+00:00'))
            maintenant = datetime.now(timezone.utc)
            delta = (maintenant - date_verrou_dt).total_seconds() / 60
            
            if delta > 30:
                # Auto-déverrouillage après 30 minutes
                pass
            elif document.get("verrouille_par_user_id") == user_id:
                # L'utilisateur a déjà verrouillé ce document
                return {
                    "message": "Document déjà verrouillé par vous",
                    "est_verrouille": True,
                    "date_verrouillage": date_verrou
                }
            else:
                raise HTTPException(
                    status_code=423,  # Locked
                    detail=f"Document verrouillé par {verrouille_par} depuis {date_verrou}"
                )
    
    # Verrouiller le document
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "est_verrouille": True,
                "verrouille_par_user_id": user_id,
                "verrouille_par_user_nom": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
                "date_verrouillage": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.MODIFICATION,
        commentaire="Document verrouillé pour modification"
    )
    
    return {
        "message": "Document verrouillé avec succès",
        "est_verrouille": True,
        "verrouille_par_user_id": user_id,
        "verrouille_par_user_nom": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        "date_verrouillage": datetime.now(timezone.utc).isoformat()
    }


@router.post("/{document_id}/deverrouiller")
async def deverrouiller_document(
    document_id: str,
    force: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Déverrouiller un document
    Le paramètre 'force' permet à un admin de déverrouiller un document verrouillé par un autre utilisateur
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    user_role = current_user.get("role")
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier si le document est verrouillé
    if not document.get("est_verrouille", False):
        return {
            "message": "Document non verrouillé",
            "est_verrouille": False
        }
    
    # Vérifier les permissions
    verrouille_par = document.get("verrouille_par_user_id")
    
    if verrouille_par != user_id:
        # Seul celui qui a verrouillé ou un admin peut déverrouiller
        if not force or user_role not in ["ministre", "secretaire_general"]:
            raise HTTPException(
                status_code=403,
                detail="Seul l'utilisateur qui a verrouillé ou un administrateur peut déverrouiller ce document"
            )
    
    # Déverrouiller
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "est_verrouille": False,
                "verrouille_par_user_id": None,
                "verrouille_par_user_nom": None,
                "date_verrouillage": None
            }
        }
    )
    
    commentaire_force = " (déverrouillage forcé)" if force and verrouille_par != user_id else ""
    creer_historique_action(
        db, document_id, current_user, TypeAction.MODIFICATION,
        commentaire=f"Document déverrouillé{commentaire_force}"
    )
    
    return {
        "message": "Document déverrouillé avec succès",
        "est_verrouille": False
    }

    from dependencies import get_db


    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Documents en attente de mon action
    en_attente = await db.documents.count_documents({
        "proprietaire_actuel_id": user_id,
        "statut": {"$in": [StatutDocument.EN_ATTENTE.value, StatutDocument.EN_COURS.value]}
    })
    
    # Documents que j'ai créés
    mes_documents = await db.documents.count_documents({
        "createur_id": user_id
    })
    
    # Documents traités (validés) par moi
    traites = await db.historique_actions.count_documents({
        "user_id": user_id,
        "type_action": TypeAction.VALIDATION.value
    })
    
    # Documents en retard (plus de 48h sans action)
    date_limite = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    en_retard = await db.documents.count_documents({
        "proprietaire_actuel_id": user_id,
        "statut": StatutDocument.EN_ATTENTE.value,
        "date_creation": {"$lt": date_limite}
    })
    
    # Délai moyen de traitement (pour mes documents validés)
    pipeline = [
        {
            "$match": {
                "createur_id": user_id,
                "statut": StatutDocument.VALIDE.value,
                "date_validation": {"$exists": True}
            }
        },
        {
            "$addFields": {
                "delai": {
                    "$divide": [
                        {
                            "$subtract": [
                                {"$dateFromString": {"dateString": "$date_validation"}},
                                {"$dateFromString": {"dateString": "$date_creation"}}
                            ]
                        },
                        3600000  # Convertir en heures
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "delai_moyen_heures": {"$avg": "$delai"}
            }
        }
    ]
    
    delai_result = await db.documents.aggregate(pipeline).to_list(1)
    delai_moyen = delai_result[0]["delai_moyen_heures"] if delai_result else 0
    
    return {
        "en_attente": en_attente,
        "mes_documents": mes_documents,
        "traites": traites,
        "en_retard": en_retard,
        "delai_moyen_heures": round(delai_moyen, 2) if delai_moyen else 0
    }



@router.post("/{document_id}/lier")
async def lier_documents(
    document_id: str,
    document_lie_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Lier deux documents ensemble (relation bidirectionnelle)
    Cas d'usage : invitation + agenda, courrier + réponse, etc.
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Vérifier que les deux documents existent
    document1 = await db.documents.find_one({"id": document_id}, {"_id": 0})
    document2 = await db.documents.find_one({"id": document_lie_id}, {"_id": 0})
    
    if not document1:
        raise HTTPException(status_code=404, detail="Document principal non trouvé")
    if not document2:
        raise HTTPException(status_code=404, detail="Document à lier non trouvé")
    
    # Vérifier que l'utilisateur a accès au document principal
    user_role = current_user.get("role")
    peut_lier = (
        user_role == "ministre" or
        document1["createur_id"] == user_id or
        document1["proprietaire_actuel_id"] == user_id
    )
    
    if not peut_lier:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits pour lier ce document")
    
    # Vérifier si déjà liés
    if document_lie_id in document1.get("documents_lies", []):
        return {
            "message": "Documents déjà liés",
            "document_id": document_id,
            "document_lie_id": document_lie_id
        }
    
    # Créer la liaison bidirectionnelle
    await db.documents.update_one(
        {"id": document_id},
        {"$addToSet": {"documents_lies": document_lie_id}}
    )
    
    await db.documents.update_one(
        {"id": document_lie_id},
        {"$addToSet": {"documents_lies": document_id}}
    )
    
    # Enregistrer dans l'historique des deux documents
    creer_historique_action(
        db, document_id, current_user, TypeAction.MODIFICATION,
        commentaire=f"Document lié à : {document2.get('titre', '')} ({document2.get('numero_reference', '')})"
    )
    
    creer_historique_action(
        db, document_lie_id, current_user, TypeAction.MODIFICATION,
        commentaire=f"Document lié à : {document1.get('titre', '')} ({document1.get('numero_reference', '')})"
    )
    
    return {
        "message": "Documents liés avec succès",
        "document_id": document_id,
        "document_lie_id": document_lie_id,
        "liaison_bidirectionnelle": True
    }


@router.delete("/{document_id}/lier/{document_lie_id}")
async def delier_documents(
    document_id: str,
    document_lie_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer le lien entre deux documents
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document1 = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document1:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les droits
    user_role = current_user.get("role")
    peut_delier = (
        user_role == "ministre" or
        document1["createur_id"] == user_id or
        document1["proprietaire_actuel_id"] == user_id
    )
    
    if not peut_delier:
        raise HTTPException(status_code=403, detail="Vous n'avez pas les droits pour délier ce document")
    
    # Supprimer la liaison bidirectionnelle
    await db.documents.update_one(
        {"id": document_id},
        {"$pull": {"documents_lies": document_lie_id}}
    )
    
    await db.documents.update_one(
        {"id": document_lie_id},
        {"$pull": {"documents_lies": document_id}}
    )
    
    creer_historique_action(
        db, document_id, current_user, TypeAction.MODIFICATION,
        commentaire=f"Liaison supprimée avec document {document_lie_id}"
    )
    
    return {
        "message": "Liaison supprimée avec succès",
        "document_id": document_id,
        "document_lie_id": document_lie_id
    }


@router.post("/{document_id}/transmettre-externe")
async def transmettre_externe(
    document_id: str,
    email_destinataire: str,
    message_perso: str = None,
    duree_jours: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """
    Transmettre un document à une personne externe par email
    Génère un lien temporaire sécurisé avec expiration
    """
    from dependencies import get_db

    db = get_db()
    import secrets
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les droits (créateur ou propriétaire actuel)
    peut_transmettre = (
        document["createur_id"] == user_id or
        document["proprietaire_actuel_id"] == user_id or
        current_user.get("role") == "ministre"
    )
    
    if not peut_transmettre:
        raise HTTPException(
            status_code=403,
            detail="Seul le créateur ou le propriétaire actuel peut transmettre à l'externe"
        )
    
    # Vérifier que le document a un fichier
    if not document.get("fichier_url"):
        raise HTTPException(
            status_code=400,
            detail="Ce document n'a pas de fichier joint. Impossible de le transmettre à l'externe."
        )
    
    # Valider l'email
    if not email_destinataire or "@" not in email_destinataire:
        raise HTTPException(status_code=400, detail="Email destinataire invalide")
    
    # Générer un token sécurisé
    token_externe = secrets.token_urlsafe(32)
    
    # Calculer la date d'expiration
    date_expiration = (datetime.now(timezone.utc) + timedelta(days=duree_jours)).isoformat()
    
    # Mettre à jour le document
    await db.documents.update_one(
        {"id": document_id},
        {
            "$set": {
                "lien_externe_token": token_externe,
                "lien_externe_expire_le": date_expiration
            },
            "$addToSet": {
                "transmis_externe_a": email_destinataire
            }
        }
    )
    
    # Générer le lien public
    url_frontend = os.getenv("FRONTEND_URL", "").replace("/api", "")
    if not url_frontend:
        raise HTTPException(
            status_code=500,
            detail="FRONTEND_URL must be configured for external document sharing"
        )
    lien_telechargement = f"{url_frontend}/#/documents/externe/{document_id}?token={token_externe}"
    
    # Enregistrer dans l'historique
    creer_historique_action(
        db, document_id, current_user, TypeAction.TRANSMISSION,
        commentaire=f"Document transmis à l'externe : {email_destinataire} (expiration: {duree_jours} jours)"
    )
    
    # Envoyer l'email (mock pour l'instant, à remplacer par vrai service)
    print(f"""
    ========== EMAIL EXTERNE ==========
    À: {email_destinataire}
    Sujet: Document officiel : {document.get('titre')}
    
    Bonjour,
    
    {current_user.get('prenom', '')} {current_user.get('nom', '')} vous a transmis un document officiel :
    
    Titre: {document.get('titre')}
    Référence: {document.get('numero_reference')}
    
    {message_perso or ''}
    
    Vous pouvez télécharger ce document via le lien suivant (valide {duree_jours} jours) :
    {lien_telechargement}
    
    ⚠️ Ce lien expire le {date_expiration[:10]}
    
    Cordialement,
    Système Édu-Connect - MINEPST RDC
    ===================================
    """)
    
    return {
        "message": f"Document transmis à {email_destinataire}",
        "email_destinataire": email_destinataire,
        "lien_telechargement": lien_telechargement,
        "expire_le": date_expiration,
        "duree_jours": duree_jours
    }


@router.get("/externe/{document_id}")
async def telecharger_document_externe(
    document_id: str,
    token: str
):
    """
    Télécharger un document via lien externe temporaire
    Accessible sans authentification JWT
    """
    from dependencies import get_db

    db = get_db()
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier le token
    if document.get("lien_externe_token") != token:
        raise HTTPException(status_code=403, detail="Token invalide ou expiré")
    
    # Vérifier l'expiration
    date_expiration = document.get("lien_externe_expire_le")
    if not date_expiration:
        raise HTTPException(status_code=403, detail="Aucun accès externe configuré")
    
    date_exp_dt = datetime.fromisoformat(date_expiration.replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > date_exp_dt:
        raise HTTPException(status_code=403, detail="Le lien a expiré")
    
    # Vérifier qu'il y a un fichier
    fichier_url = document.get("fichier_url")
    if not fichier_url:
        raise HTTPException(status_code=404, detail="Aucun fichier attaché")
    
    # Retourner les métadonnées du document (sans informations sensibles)
    return {
        "id": document_id,
        "titre": document.get("titre"),
        "numero_reference": document.get("numero_reference"),
        "type_document": document.get("type_document"),
        "date_creation": document.get("date_creation"),
        "fichier_nom": document.get("fichier_nom"),
        "fichier_type": document.get("fichier_type"),
        "fichier_taille": document.get("fichier_taille"),
        "expire_le": date_expiration,
        "message": "Accès autorisé - Document disponible"
    }


@router.get("/search")
async def rechercher_documents(
    q: str = Query(None, description="Recherche par mots-clés"),
    type_document: str = Query(None),
    statut: str = Query(None),
    date_debut: str = Query(None),
    date_fin: str = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Rechercher des documents avec filtres avancés"""
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Construire le filtre de base (permissions)
    filtre = {}
    
    user_role = current_user.get("role")
    if user_role != "ministre":
        filtre = {
            "$or": [
                {"createur_id": user_id},
                {"proprietaire_actuel_id": user_id},
                {"cc_user_ids": user_id},
                {"niveau_diffusion": "tous"}
            ]
        }
    
    # Ajouter les filtres de recherche
    conditions = []
    
    if q:
        conditions.append({
            "$or": [
                {"titre": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"numero_reference": {"$regex": q, "$options": "i"}},
                {"mots_cles": {"$regex": q, "$options": "i"}}
            ]
        })
    
    if type_document:
        conditions.append({"type_document": type_document})
    
    if statut:
        conditions.append({"statut": statut})
    
    if date_debut:
        conditions.append({"date_creation": {"$gte": date_debut}})
    
    if date_fin:
        conditions.append({"date_creation": {"$lte": date_fin}})
    
    # Combiner les filtres
    if conditions:
        if "$or" in filtre or "$and" in filtre:
            filtre = {"$and": [filtre, {"$and": conditions}]}
        else:
            if filtre:
                filtre.update({"$and": conditions})
            else:
                filtre = {"$and": conditions}
    
    # Exécuter la recherche
    documents = await db.documents.find(filtre, {"_id": 0}).to_list(1000)
    
    return {
        "total": len(documents),
        "documents": documents
    }

