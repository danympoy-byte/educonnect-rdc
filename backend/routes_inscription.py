"""
Routes d'inscription en 3 étapes pour Édu-Connect
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import Optional
from models import (
    UserCreateStep1, UserCreateStep2, UserCreateStep3,
    User, Diplome, ExperienceProfessionnelle, UserServiceProfile
)
from auth import get_password_hash
from datetime import datetime, timezone
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/inscription", tags=["Inscription"])

UPLOAD_DIR = Path("/app/backend/uploads/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/etape1")
async def inscription_etape1(data: UserCreateStep1):
    """
    Étape 1: Informations personnelles et professionnelles
    Retourne l'ID de l'utilisateur créé pour continuer l'inscription
    
    Cette étape est idempotente : si l'utilisateur revient en arrière depuis l'étape 2,
    ses informations seront mises à jour au lieu de créer un doublon.
    """
    from dependencies import get_db

    db = get_db()
    
    # Vérifier si le téléphone existe déjà
    existing_user = await db.users.find_one({"telephone": data.telephone}, {"_id": 0})
    
    # Convertir les diplômes et expériences
    diplomes = [Diplome(**d) for d in data.diplomes]
    experiences = [ExperienceProfessionnelle(**e) for e in data.experiences]
    
    if existing_user:
        # Si l'utilisateur existe déjà
        if existing_user.get("profil_complete", False):
            # Profil déjà complet = vrai doublon
            raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà utilisé")
        
        # Profil incomplet : mise à jour des informations (l'utilisateur revient en arrière)
        user_id = existing_user["id"]
        
        update_data = {
            "nom": data.nom,
            "postnom": data.postnom,
            "prenom": data.prenom,
            "sexe": data.sexe,
            "etat_civil": data.etat_civil,
            "date_naissance": data.date_naissance,
            "lieu_naissance": data.lieu_naissance,
            "adresse": data.adresse,
            "diplomes": [d.model_dump() for d in diplomes],
            "experiences": [e.model_dump() for e in experiences],
            "hashed_password": get_password_hash(data.password),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Informations mises à jour avec succès",
            "user_id": user_id,
            "prenom": data.prenom,
            "nom": data.nom,
            "etape_suivante": "etape2"
        }
    
    # Créer un nouvel utilisateur
    new_user = User(
        nom=data.nom,
        postnom=data.postnom,
        prenom=data.prenom,
        sexe=data.sexe,
        etat_civil=data.etat_civil,
        date_naissance=data.date_naissance,
        lieu_naissance=data.lieu_naissance,
        telephone=data.telephone,
        adresse=data.adresse,
        diplomes=[d.model_dump() for d in diplomes],
        experiences=[e.model_dump() for e in experiences],
        hashed_password=get_password_hash(data.password),
        service_profiles=[],  # Sera rempli à l'étape 2
        profil_complete=False,  # Sera mis à True à l'étape 3
        is_active=True
    )
    
    await db.users.insert_one(new_user.model_dump())
    
    return {
        "message": "Étape 1 terminée avec succès",
        "user_id": new_user.id,
        "prenom": new_user.prenom,
        "nom": new_user.nom,
        "etape_suivante": "etape2"
    }


@router.post("/etape2")
async def inscription_etape2(data: UserCreateStep2):
    """
    Étape 2: Sélection du service / poste
    L'utilisateur peut maintenant se connecter après cette étape.
    Supporte les postes provinciaux, d'établissement, et centraux.
    """
    from dependencies import get_db

    db = get_db()
    
    # Vérifier que l'utilisateur existe
    user = await db.users.find_one({"id": data.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Déterminer le rôle à partir du poste
    poste_str = data.poste or ""
    role_part = poste_str.split(" - ")[0].strip() if " - " in poste_str else poste_str.strip()
    
    # Mapping des rôles connus
    ROLES_MAPPING = {
        "proved": "proved",
        "ipp": "ipp",
        "diprocope": "diprocope",
        "ministre_provincial": "ministre_provincial",
        "chef_etablissement": "chef_etablissement",
        "directeur_ecole": "directeur_ecole",
        "conseiller_principal_education": "conseiller_principal_education",
        "enseignant": "enseignant",
        "personnel_administratif": "personnel_administratif",
        "inspecteur_pedagogique": "inspecteur_pedagogique",
        "agent_dinacope": "agent_dinacope",
    }
    
    role = ROLES_MAPPING.get(role_part, "personnel_administratif")
    
    # Si un service est fourni (administration centrale), le traiter
    service_nom = "Non affecté"
    service_code = "NA"
    
    if data.service_id:
        service = await db.services.find_one({"id": data.service_id}, {"_id": 0})
        if service:
            service_nom = service["nom"]
            service_code = service["code"]
    else:
        # Pour les postes provinciaux/établissement, pas de service organigramme requis
        if role in ["proved", "ipp", "diprocope", "ministre_provincial"]:
            service_nom = f"Province - {poste_str}"
            service_code = f"PROV-{role.upper()}"
        elif role in ["chef_etablissement", "directeur_ecole", "conseiller_principal_education", "enseignant"]:
            service_nom = f"Établissement - {role}"
            service_code = f"ETAB-{role.upper()}"
    
    # Créer le profil de service
    service_profile = UserServiceProfile(
        user_id=data.user_id,
        service_id=data.service_id or f"auto-{role}",
        service_nom=service_nom,
        service_code=service_code,
        poste=data.poste,
        est_responsable=role in ["proved", "ipp", "diprocope", "ministre_provincial", "chef_etablissement", "directeur_ecole"],
        date_affectation=datetime.now(timezone.utc)
    )
    
    # Mettre à jour l'utilisateur avec le rôle
    await db.users.update_one(
        {"id": data.user_id},
        {
            "$push": {"service_profiles": service_profile.model_dump()},
            "$set": {
                "service_actif_id": data.service_id or f"auto-{role}",
                "role": role
            }
        }
    )
    
    # Générer un email par défaut basé sur le nom
    email_default = f"{user['prenom'].lower()}.{user['nom'].lower()}@educonnect.gouv.cd"
    
    return {
        "message": "Inscription terminée ! Vous pouvez maintenant vous connecter.",
        "user_id": data.user_id,
        "service_affecte": service_nom,
        "poste": data.poste,
        "role": role,
        "connexion": {
            "telephone": user["telephone"],
            "mot_de_passe": "Utilisez le mot de passe que vous avez choisi"
        },
        "notification": {
            "titre": "Complétez votre profil",
            "message": "N'oubliez pas d'ajouter votre photo, email et compte bancaire pour finaliser votre profil.",
            "profil_complet": False
        },
        "email_suggere": email_default
    }


@router.post("/etape3")
async def inscription_etape3(
    user_id: str,
    email: Optional[str] = None,
    numero_compte_bancaire: Optional[str] = None,
    banque: Optional[str] = None
):
    """
    Étape 3: Complétion du profil (optionnel)
    L'utilisateur peut faire cela à n'importe quel moment après l'étape 2
    """
    from dependencies import get_db

    db = get_db()
    
    # Vérifier que l'utilisateur existe
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Préparer les champs à mettre à jour
    update_fields = {}
    if email:
        # Vérifier que l'email n'est pas déjà utilisé
        existing_email = await db.users.find_one(
            {"email": email, "id": {"$ne": user_id}},
            {"_id": 0}
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        update_fields["email"] = email
    
    if numero_compte_bancaire:
        update_fields["numero_compte_bancaire"] = numero_compte_bancaire
    
    if banque:
        update_fields["banque"] = banque
    
    # Vérifier si le profil est maintenant complet
    profil_complet = bool(
        (user.get("email") or email) and
        (user.get("numero_compte_bancaire") or numero_compte_bancaire) and
        user.get("photo_url")  # La photo doit être uploadée séparément
    )
    
    update_fields["profil_complete"] = profil_complet
    update_fields["updated_at"] = datetime.now(timezone.utc)
    
    # Mettre à jour
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_fields}
    )
    
    message = "Profil mis à jour avec succès"
    if profil_complet:
        message = "✅ Profil 100% complet ! Félicitations."
    else:
        manquants = []
        if not (user.get("email") or email):
            manquants.append("email")
        if not (user.get("numero_compte_bancaire") or numero_compte_bancaire):
            manquants.append("compte bancaire")
        if not user.get("photo_url"):
            manquants.append("photo")
        
        message += f" Il vous manque: {', '.join(manquants)}"
    
    return {
        "message": message,
        "profil_complete": profil_complet,
        "user_id": user_id
    }


@router.post("/upload-photo/{user_id}")
async def upload_photo(user_id: str, photo: UploadFile = File(...)):
    """
    Upload de la photo de profil
    """
    from dependencies import get_db

    db = get_db()
    
    # Vérifier que l'utilisateur existe
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier le type de fichier
    if not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")
    
    # Sauvegarder la photo
    file_extension = photo.filename.split(".")[-1]
    file_path = UPLOAD_DIR / f"{user_id}.{file_extension}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)
    
    photo_url = str(file_path)
    
    # Mettre à jour l'utilisateur
    profil_complet = bool(
        user.get("email") and
        user.get("numero_compte_bancaire") and
        photo_url
    )
    
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "photo_url": photo_url,
                "profil_complete": profil_complet,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {
        "message": "Photo uploadée avec succès",
        "photo_url": photo_url,
        "profil_complete": profil_complet
    }


@router.get("/notification-profil/{user_id}")
async def get_notification_profil(user_id: str):
    """
    Récupère les éléments manquants du profil pour afficher une notification
    """
    from dependencies import get_db

    db = get_db()
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    if user.get("profil_complete"):
        return {
            "afficher_notification": False,
            "message": "Profil complet"
        }
    
    manquants = []
    if not user.get("email"):
        manquants.append("email")
    if not user.get("numero_compte_bancaire"):
        manquants.append("compte bancaire")
    if not user.get("photo_url"):
        manquants.append("photo de profil")
    
    return {
        "afficher_notification": True,
        "message": f"Complétez votre profil en ajoutant: {', '.join(manquants)}",
        "elements_manquants": manquants,
        "profil_complete": False
    }
