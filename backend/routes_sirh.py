"""
API Routes pour le Module SIRH (Gestion RH)
Fiche agent détaillée, Contrôle DINACOPE, Mutations multi-niveaux
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from uuid import uuid4

from models import (
    GradeEnseignant, TypeMutation, StatutMutation,
    HistoriqueAffectation, HistoriquePromotion, HistoriqueMutationDiscipline,
    VerificationDINACOPE, DonneesDINACOPE, DemandeMutation, DetectionFraude
)
from auth import get_current_user

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
_client = AsyncIOMotorClient(mongo_url)
_db = _client[os.environ.get('DB_NAME', 'educonnect_rdc')]

def get_db():
    return _db

router = APIRouter(prefix="/api/sirh", tags=["SIRH"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("user_id", user.get("id", ""))


async def generer_numero_mutation(db):
    """Génère un numéro de référence unique : MIN/MUTATION/2025/001"""
    annee = datetime.now(timezone.utc).year
    count = await db.demandes_mutations.count_documents({
        "numero_reference": {"$regex": f"MIN/MUTATION/{annee}/"}
    })
    numero = count + 1
    return f"MIN/MUTATION/{annee}/{numero:04d}"


# ============================================
# FICHE AGENT DÉTAILLÉE
# ============================================

@router.get("/enseignants/{enseignant_id}/fiche-detaillee")
async def obtenir_fiche_agent_detaillee(
    enseignant_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir la fiche complète d'un enseignant avec tout son historique
    Accessible par: enseignant lui-même, directeur, DPE, ministre
    """
    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Récupérer l'enseignant
    enseignant = await db.enseignants.find_one({"id": enseignant_id}, {"_id": 0})
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    
    # Récupérer les infos utilisateur
    user = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier les permissions
    peut_consulter = False
    
    # L'enseignant lui-même
    if user_id == enseignant["user_id"]:
        peut_consulter = True
    
    # Directeur de son établissement
    elif current_user["role"] in ["directeur_ecole", "chef_etablissement"]:
        if current_user.get("etablissement_id") == enseignant["etablissement_id"]:
            peut_consulter = True
    
    # DPE de sa province
    elif current_user["role"] == "directeur_provincial":
        etablissement = await db.etablissements.find_one(
            {"id": enseignant["etablissement_id"]},
            {"_id": 0, "province_id": 1}
        )
        if etablissement and current_user.get("province_id") == etablissement.get("province_id"):
            peut_consulter = True
    
    # Ministre, Secrétaire Général, Admin
    elif current_user["role"] in ["ministre", "secretaire_general", "administrateur_technique"]:
        peut_consulter = True
    
    if not peut_consulter:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette fiche")
    
    # Récupérer l'établissement actuel
    etablissement = await db.etablissements.find_one(
        {"id": enseignant["etablissement_id"]},
        {"_id": 0}
    )
    
    # Récupérer la province
    province = None
    if etablissement:
        province = await db.provinces.find_one(
            {"id": etablissement.get("province_id")},
            {"_id": 0}
        )
    
    # Récupérer l'historique des affectations
    historique_affectations = await db.historique_affectations.find(
        {"enseignant_id": enseignant_id},
        {"_id": 0}
    ).sort("date_debut", -1).to_list(100)
    
    # Récupérer l'historique des promotions
    historique_promotions = await db.historique_promotions.find(
        {"enseignant_id": enseignant_id},
        {"_id": 0}
    ).sort("date_promotion", -1).to_list(100)
    
    # Récupérer l'historique des mutations de discipline
    historique_disciplines = await db.historique_mutations_discipline.find(
        {"enseignant_id": enseignant_id},
        {"_id": 0}
    ).sort("date_mutation", -1).to_list(100)
    
    # Récupérer les mutations en cours ou validées
    mutations = await db.demandes_mutations.find(
        {"enseignant_id": enseignant_id},
        {"_id": 0}
    ).sort("date_demande", -1).to_list(50)
    
    # Récupérer la dernière vérification DINACOPE
    derniere_verification = await db.verifications_dinacope.find_one(
        {"enseignant_id": enseignant_id, "statut": "verifie"},
        {"_id": 0},
        sort=[("date_verification", -1)]
    )
    
    return {
        "enseignant": enseignant,
        "utilisateur": {
            "nom": user.get("nom"),
            "prenom": user.get("prenom"),
            "email": user.get("email"),
            "sexe": user.get("sexe")
        },
        "etablissement_actuel": etablissement,
        "province_actuelle": province,
        "historique_affectations": historique_affectations,
        "historique_promotions": historique_promotions,
        "historique_mutations_discipline": historique_disciplines,
        "mutations": mutations,
        "derniere_verification_dinacope": derniere_verification
    }


# ============================================
# CONTRÔLE DINACOPE
# ============================================

@router.get("/dinacope/verifications")
async def lister_verifications_dinacope(
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    current_user: dict = Depends(get_current_user)
):
    """Lister toutes les vérifications DINACOPE (pour agents DINACOPE uniquement)"""
    db = get_db()
    
    if current_user["role"] not in ["agent_dinacope", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents DINACOPE")
    
    filtre = {}
    if statut:
        filtre["statut"] = statut
    
    verifications = await db.verifications_dinacope.find(filtre, {"_id": 0}).sort("date_envoi", -1).to_list(500)
    
    # Enrichir avec les noms des enseignants
    for verif in verifications:
        enseignant = await db.enseignants.find_one({"id": verif["enseignant_id"]}, {"_id": 0})
        if enseignant:
            user = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
            verif["enseignant_nom"] = f"{user.get('prenom', '')} {user.get('nom', '')}"
            verif["enseignant_matricule"] = enseignant.get("matricule")
    
    return {
        "total": len(verifications),
        "verifications": verifications
    }


@router.post("/dinacope/envoyer-lien")
async def envoyer_lien_verification(
    enseignant_id: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Envoyer un lien de vérification à un enseignant"""
    db = get_db()
    
    if current_user["role"] not in ["agent_dinacope", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents DINACOPE")
    
    user_id = get_user_id(current_user)
    
    # Vérifier que l'enseignant existe
    enseignant = await db.enseignants.find_one({"id": enseignant_id}, {"_id": 0})
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    
    user = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Créer une vérification
    token = str(uuid4())
    frontend_url = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:3000").replace("/api", "")
    lien = f"{frontend_url}/#/verification-dinacope/{token}"
    
    date_expiration = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    
    verification = VerificationDINACOPE(
        enseignant_id=enseignant_id,
        agent_dinacope_id=user_id,
        agent_dinacope_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        token_verification=token,
        lien_verification=lien,
        date_expiration=date_expiration,
        donnees_avant={
            "adresse_personnelle": enseignant.get("adresse_personnelle", ""),
            "telephone_personnel": enseignant.get("telephone_personnel", ""),
            "email_personnel": enseignant.get("email_personnel", ""),
            "etat_civil": enseignant.get("etat_civil", "celibataire"),
            "nombre_enfants": enseignant.get("nombre_enfants", 0),
            "conjoint_nom": enseignant.get("conjoint_nom", ""),
            "banque": enseignant.get("banque", ""),
            "numero_compte": enseignant.get("numero_compte", ""),
            "grade": enseignant.get("grade", "mécanisé")
        }
    )
    
    await db.verifications_dinacope.insert_one(verification.model_dump())
    
    # Envoyer l'email
    email_sent = email_verification_dinacope(
        destinataire_email=user.get("email"),
        destinataire_nom=f"{user.get('prenom')} {user.get('nom')}",
        lien_verification=lien,
        date_expiration=date_expiration
    )
    
    return {
        "message": "Lien de vérification envoyé avec succès",
        "verification_id": verification.id,
        "lien": lien,
        "email_envoye": email_sent
    }


@router.get("/dinacope/verifier/{token}")
async def obtenir_formulaire_verification(token: str):
    """Obtenir le formulaire de vérification (accessible sans auth via token)"""
    db = get_db()
    
    verification = await db.verifications_dinacope.find_one(
        {"token_verification": token},
        {"_id": 0}
    )
    
    if not verification:
        raise HTTPException(status_code=404, detail="Lien de vérification invalide")
    
    # Vérifier expiration
    if datetime.fromisoformat(verification["date_expiration"].replace("Z", "+00:00")) < datetime.now(timezone.utc):
        await db.verifications_dinacope.update_one(
            {"token_verification": token},
            {"$set": {"statut": "expiree"}}
        )
        raise HTTPException(status_code=410, detail="Lien de vérification expiré")
    
    if verification["statut"] == "verifie":
        raise HTTPException(status_code=400, detail="Vérification déjà effectuée")
    
    # Récupérer les infos enseignant
    enseignant = await db.enseignants.find_one(
        {"id": verification["enseignant_id"]},
        {"_id": 0}
    )
    user = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    
    return {
        "verification": verification,
        "enseignant": {
            "nom": user.get("nom"),
            "prenom": user.get("prenom"),
            "matricule": enseignant.get("matricule"),
            "grade": enseignant.get("grade"),
            "adresse_personnelle": enseignant.get("adresse_personnelle", ""),
            "telephone_personnel": enseignant.get("telephone_personnel", ""),
            "email_personnel": enseignant.get("email_personnel", ""),
            "etat_civil": enseignant.get("etat_civil", "celibataire"),
            "nombre_enfants": enseignant.get("nombre_enfants", 0),
            "conjoint_nom": enseignant.get("conjoint_nom", ""),
            "banque": enseignant.get("banque", ""),
            "numero_compte": enseignant.get("numero_compte", "")
        }
    }


@router.post("/dinacope/verifier/{token}")
async def soumettre_verification(
    token: str,
    donnees: dict = Body(...)
):
    """Soumettre les données vérifiées/mises à jour"""
    db = get_db()
    
    verification = await db.verifications_dinacope.find_one(
        {"token_verification": token},
        {"_id": 0}
    )
    
    if not verification:
        raise HTTPException(status_code=404, detail="Lien de vérification invalide")
    
    if verification["statut"] == "verifie":
        raise HTTPException(status_code=400, detail="Vérification déjà effectuée")
    
    # Vérifier expiration
    if datetime.fromisoformat(verification["date_expiration"].replace("Z", "+00:00")) < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Lien de vérification expiré")
    
    # Mettre à jour les données de l'enseignant
    enseignant_id = verification["enseignant_id"]
    
    # Identifier les champs modifiés
    champs_modifies = []
    donnees_avant = verification.get("donnees_avant", {})
    for key, value in donnees.items():
        if key in donnees_avant and donnees_avant[key] != value:
            champs_modifies.append(key)
    
    # Mettre à jour l'enseignant
    await db.enseignants.update_one(
        {"id": enseignant_id},
        {
            "$set": {
                "adresse_personnelle": donnees.get("adresse_personnelle", ""),
                "telephone_personnel": donnees.get("telephone_personnel", ""),
                "email_personnel": donnees.get("email_personnel", ""),
                "etat_civil": donnees.get("etat_civil", "celibataire"),
                "nombre_enfants": donnees.get("nombre_enfants", 0),
                "conjoint_nom": donnees.get("conjoint_nom", ""),
                "banque": donnees.get("banque", ""),
                "numero_compte": donnees.get("numero_compte", ""),
                "grade": donnees.get("grade", "mécanisé"),
                "photo_url": donnees.get("photo_url"),
                "derniere_verification_dinacope": datetime.now(timezone.utc).isoformat(),
                "derniere_verification_dinacope_id": verification["id"]
            }
        }
    )
    
    # Marquer la vérification comme effectuée
    await db.verifications_dinacope.update_one(
        {"id": verification["id"]},
        {
            "$set": {
                "statut": "verifie",
                "date_verification": datetime.now(timezone.utc).isoformat(),
                "donnees_apres": donnees,
                "champs_modifies": champs_modifies
            }
        }
    )
    
    # Lancer la détection de fraudes en arrière-plan
    await detecter_fraudes(db, enseignant_id)
    
    return {
        "message": "Vérification effectuée avec succès",
        "champs_modifies": champs_modifies
    }


@router.get("/dinacope/fraudes")
async def lister_fraudes_detectees(
    statut: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lister les fraudes détectées"""
    db = get_db()
    
    if current_user["role"] not in ["agent_dinacope", "administrateur_technique"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents DINACOPE")
    
    filtre = {}
    if statut:
        filtre["statut"] = statut
    
    fraudes = await db.detections_fraudes.find(filtre, {"_id": 0}).sort("date_detection", -1).to_list(200)
    
    return {
        "total": len(fraudes),
        "fraudes": fraudes
    }


async def detecter_fraudes(db, enseignant_id: str):
    """Détecter les fraudes pour un enseignant"""
    enseignant = await db.enseignants.find_one({"id": enseignant_id}, {"_id": 0})
    if not enseignant:
        return
    
    user = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    
    # 1. Vérifier matricule doublon
    matricules_doublons = await db.enseignants.find(
        {"matricule": enseignant["matricule"]},
        {"_id": 0}
    ).to_list(10)
    
    if len(matricules_doublons) > 1:
        enseignants_concernes = []
        for ens in matricules_doublons:
            u = await db.users.find_one({"id": ens["user_id"]}, {"_id": 0})
            etab = await db.etablissements.find_one({"id": ens["etablissement_id"]}, {"_id": 0})
            enseignants_concernes.append({
                "id": ens["id"],
                "nom": f"{u.get('prenom')} {u.get('nom')}",
                "matricule": ens["matricule"],
                "etablissement": etab.get("nom") if etab else "Inconnu"
            })
        
        fraude = DetectionFraude(
            type_fraude="matricule_doublon",
            niveau_gravite="critique",
            enseignants_concernes=enseignants_concernes,
            champ_problematique="matricule",
            valeur_problematique=enseignant["matricule"]
        )
        await db.detections_fraudes.insert_one(fraude.model_dump())
    
    # 2. Vérifier identité (nom + prénom + date de naissance)
    # On compare avec les users ayant le même nom et prénom
    identites_similaires = await db.users.find(
        {
            "nom": user["nom"],
            "prenom": user["prenom"]
        },
        {"_id": 0}
    ).to_list(10)
    
    if len(identites_similaires) > 1:
        # Vérifier s'ils ont la même date de naissance (si disponible)
        # Pour l'instant on signale juste les noms similaires
        pass
    
    # 3. Vérifier téléphone doublon
    if enseignant.get("telephone_personnel"):
        telephones_doublons = await db.enseignants.find(
            {"telephone_personnel": enseignant["telephone_personnel"]},
            {"_id": 0}
        ).to_list(10)
        
        if len(telephones_doublons) > 1:
            enseignants_concernes = []
            for ens in telephones_doublons:
                u = await db.users.find_one({"id": ens["user_id"]}, {"_id": 0})
                enseignants_concernes.append({
                    "id": ens["id"],
                    "nom": f"{u.get('prenom')} {u.get('nom')}",
                    "matricule": ens["matricule"]
                })
            
            fraude = DetectionFraude(
                type_fraude="contact_doublon",
                niveau_gravite="moyen",
                enseignants_concernes=enseignants_concernes,
                champ_problematique="telephone",
                valeur_problematique=enseignant["telephone_personnel"]
            )
            await db.detections_fraudes.insert_one(fraude.model_dump())


# ============================================
# MUTATIONS MULTI-NIVEAUX
# ============================================

@router.post("/mutations")
async def creer_demande_mutation(
    type_mutation: TypeMutation = Body(...),
    motif: str = Body(...),
    justification: str = Body(""),
    enseignant_id: str = Body(...),
    # Pour mutation géographique
    etablissement_destination_id: Optional[str] = Body(None),
    # Pour mutation promotion
    grade_demande: Optional[str] = Body(None),
    # Pour mutation discipline
    nouvelles_matieres: Optional[List[str]] = Body(None),
    # Date souhaitée
    date_souhaitee: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """Créer une demande de mutation"""
    db = get_db()
    
    user_id = get_user_id(current_user)
    
    # Vérifier que l'enseignant existe
    enseignant = await db.enseignants.find_one({"id": enseignant_id}, {"_id": 0})
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    
    user_enseignant = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    
    # Vérifier les permissions
    peut_demander = False
    
    # L'enseignant lui-même
    if user_id == enseignant["user_id"]:
        peut_demander = True
    
    # Son directeur
    elif current_user["role"] in ["directeur_ecole", "chef_etablissement"]:
        if current_user.get("etablissement_id") == enseignant["etablissement_id"]:
            peut_demander = True
    
    # DPE de sa province
    elif current_user["role"] == "directeur_provincial":
        etablissement = await db.etablissements.find_one(
            {"id": enseignant["etablissement_id"]},
            {"_id": 0}
        )
        if etablissement and current_user.get("province_id") == etablissement.get("province_id"):
            peut_demander = True
    
    if not peut_demander:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas créer une demande pour cet enseignant")
    
    # Récupérer les infos actuelles
    etablissement_actuel = await db.etablissements.find_one(
        {"id": enseignant["etablissement_id"]},
        {"_id": 0}
    )
    province_actuelle = await db.provinces.find_one(
        {"id": etablissement_actuel["province_id"]},
        {"_id": 0}
    )
    
    # Préparer les infos de destination (si mutation géographique)
    etablissement_destination = None
    province_destination = None
    
    if type_mutation == TypeMutation.GEOGRAPHIQUE and etablissement_destination_id:
        etablissement_destination = await db.etablissements.find_one(
            {"id": etablissement_destination_id},
            {"_id": 0}
        )
        if not etablissement_destination:
            raise HTTPException(status_code=404, detail="Établissement de destination non trouvé")
        
        province_destination = await db.provinces.find_one(
            {"id": etablissement_destination["province_id"]},
            {"_id": 0}
        )
    
    # Générer numéro de référence
    numero_ref = await generer_numero_mutation(db)
    
    # Créer le circuit de validation
    # Circuit: Directeur actuel → DPE province actuelle → DPE province destination → Secrétaire général
    circuit = []
    
    # 1. Directeur actuel
    directeur = await db.users.find_one(
        {
            "etablissement_id": enseignant["etablissement_id"],
            "role": {"$in": ["directeur_ecole", "chef_etablissement"]}
        },
        {"_id": 0}
    )
    if directeur:
        circuit.append({
            "role": "directeur",
            "user_id": directeur["id"],
            "user_nom": f"{directeur.get('prenom')} {directeur.get('nom')}",
            "statut": "en_attente",
            "date": None,
            "commentaire": ""
        })
    
    # 2. DPE province actuelle
    dpe_actuel = await db.users.find_one(
        {
            "province_id": province_actuelle["id"],
            "role": "directeur_provincial"
        },
        {"_id": 0}
    )
    if dpe_actuel:
        circuit.append({
            "role": "dpe_origine",
            "user_id": dpe_actuel["id"],
            "user_nom": f"{dpe_actuel.get('prenom')} {dpe_actuel.get('nom')}",
            "statut": "en_attente",
            "date": None,
            "commentaire": ""
        })
    
    # 3. DPE province destination (si mutation géographique)
    if type_mutation == TypeMutation.GEOGRAPHIQUE and province_destination:
        if province_destination["id"] != province_actuelle["id"]:
            dpe_destination = await db.users.find_one(
                {
                    "province_id": province_destination["id"],
                    "role": "directeur_provincial"
                },
                {"_id": 0}
            )
            if dpe_destination:
                circuit.append({
                    "role": "dpe_destination",
                    "user_id": dpe_destination["id"],
                    "user_nom": f"{dpe_destination.get('prenom')} {dpe_destination.get('nom')}",
                    "statut": "en_attente",
                    "date": None,
                    "commentaire": ""
                })
    
    # 4. Secrétaire général
    sg = await db.users.find_one({"role": "secretaire_general"}, {"_id": 0})
    if sg:
        circuit.append({
            "role": "secretaire_general",
            "user_id": sg["id"],
            "user_nom": f"{sg.get('prenom')} {sg.get('nom')}",
            "statut": "en_attente",
            "date": None,
            "commentaire": ""
        })
    
    # Créer la demande
    demande = DemandeMutation(
        numero_reference=numero_ref,
        enseignant_id=enseignant_id,
        enseignant_nom=f"{user_enseignant.get('prenom')} {user_enseignant.get('nom')}",
        enseignant_matricule=enseignant["matricule"],
        type_mutation=type_mutation,
        initiateur_id=user_id,
        initiateur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        initiateur_role=current_user["role"],
        etablissement_actuel_id=enseignant["etablissement_id"],
        etablissement_actuel_nom=etablissement_actuel["nom"],
        province_actuelle_id=province_actuelle["id"],
        province_actuelle_nom=province_actuelle["nom"],
        etablissement_destination_id=etablissement_destination_id,
        etablissement_destination_nom=etablissement_destination["nom"] if etablissement_destination else None,
        province_destination_id=province_destination["id"] if province_destination else None,
        province_destination_nom=province_destination["nom"] if province_destination else None,
        grade_actuel=enseignant.get("grade"),
        grade_demande=grade_demande,
        matieres_actuelles=enseignant.get("matieres", []),
        matieres_demandees=nouvelles_matieres or [],
        circuit_validation=circuit,
        motif=motif,
        justification=justification,
        date_souhaitee=date_souhaitee
    )
    
    await db.demandes_mutations.insert_one(demande.model_dump())
    
    # Notifier le premier validateur (directeur)
    # if circuit and len(circuit) > 0:
    #     premier_validateur = circuit[0]
    #     TODO: Envoyer email au premier validateur
    
    return {
        "message": "Demande de mutation créée avec succès",
        "demande": demande.model_dump()
    }


@router.get("/mutations")
async def lister_mutations(
    statut: Optional[StatutMutation] = Query(None),
    enseignant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lister les demandes de mutation"""
    db = get_db()
    
    # user_id = get_user_id(current_user)
    
    filtre = {}
    
    # Filtrer par enseignant si demandé
    if enseignant_id:
        filtre["enseignant_id"] = enseignant_id
    
    # Filtrer par statut
    if statut:
        filtre["statut"] = statut.value
    
    # Permissions: voir seulement les mutations pertinentes
    if current_user["role"] == "enseignant":
        # L'enseignant voit ses propres mutations
        filtre["enseignant_id"] = current_user["id"]
    elif current_user["role"] in ["directeur_ecole", "chef_etablissement"]:
        # Le directeur voit les mutations de son établissement
        filtre["$or"] = [
            {"etablissement_actuel_id": current_user.get("etablissement_id")},
            {"etablissement_destination_id": current_user.get("etablissement_id")}
        ]
    elif current_user["role"] == "directeur_provincial":
        # Le DPE voit les mutations de sa province
        filtre["$or"] = [
            {"province_actuelle_id": current_user.get("province_id")},
            {"province_destination_id": current_user.get("province_id")}
        ]
    # Ministre, SG, Admin voient tout
    
    mutations = await db.demandes_mutations.find(filtre, {"_id": 0}).sort("date_demande", -1).to_list(200)
    
    return {
        "total": len(mutations),
        "mutations": mutations
    }


@router.post("/mutations/{mutation_id}/valider")
async def valider_mutation(
    mutation_id: str,
    commentaire: str = Body(""),
    current_user: dict = Depends(get_current_user)
):
    """Valider une demande de mutation"""
    db = get_db()
    
    user_id = get_user_id(current_user)
    
    mutation = await db.demandes_mutations.find_one({"id": mutation_id}, {"_id": 0})
    if not mutation:
        raise HTTPException(status_code=404, detail="Demande de mutation non trouvée")
    
    # Vérifier que l'utilisateur est dans le circuit de validation
    circuit = mutation["circuit_validation"]
    mon_etape = None
    mon_index = -1
    
    for i, etape in enumerate(circuit):
        if etape["user_id"] == user_id and etape["statut"] == "en_attente":
            mon_etape = etape
            mon_index = i
            break
    
    if not mon_etape:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à valider cette demande à cette étape")
    
    # Marquer l'étape comme validée
    circuit[mon_index]["statut"] = "valide"
    circuit[mon_index]["date"] = datetime.now(timezone.utc).isoformat()
    circuit[mon_index]["commentaire"] = commentaire
    
    # Déterminer le nouveau statut de la mutation
    nouveau_statut = mutation["statut"]
    
    if mon_etape["role"] == "directeur":
        nouveau_statut = StatutMutation.VALIDEE_DIRECTEUR.value
    elif mon_etape["role"] == "dpe_origine":
        nouveau_statut = StatutMutation.VALIDEE_DPE_ORIGINE.value
    elif mon_etape["role"] == "dpe_destination":
        nouveau_statut = StatutMutation.VALIDEE_DPE_DESTINATION.value
    elif mon_etape["role"] == "secretaire_general":
        nouveau_statut = StatutMutation.VALIDEE_SG.value
        
        # Si c'est la dernière étape, appliquer la mutation
        if mon_index == len(circuit) - 1:
            nouveau_statut = StatutMutation.APPROUVEE.value
            await appliquer_mutation(db, mutation)
    
    # Mettre à jour la mutation
    await db.demandes_mutations.update_one(
        {"id": mutation_id},
        {
            "$set": {
                "statut": nouveau_statut,
                "circuit_validation": circuit
            }
        }
    )
    
    # Notifier le prochain validateur ou l'enseignant si approuvée
    if nouveau_statut == StatutMutation.APPROUVEE.value:
        # Notifier l'enseignant
        enseignant = await db.enseignants.find_one({"id": mutation["enseignant_id"]}, {"_id": 0})
        user_enseignant = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
        
        email_notification_mutation(
            destinataire_email=user_enseignant.get("email"),
            destinataire_nom=f"{user_enseignant.get('prenom')} {user_enseignant.get('nom')}",
            numero_reference=mutation["numero_reference"],
            type_mutation=mutation["type_mutation"],
            statut="approuvee"
        )
        
        await db.demandes_mutations.update_one(
            {"id": mutation_id},
            {
                "$set": {
                    "enseignant_notifie": True,
                    "date_notification_enseignant": datetime.now(timezone.utc).isoformat()
                }
            }
        )
    # elif mon_index + 1 < len(circuit):
    #     Notifier le prochain validateur
    #     prochain = circuit[mon_index + 1]
    #     TODO: Envoyer email au prochain validateur
    
    return {
        "message": "Mutation validée avec succès",
        "nouveau_statut": nouveau_statut
    }


@router.post("/mutations/{mutation_id}/rejeter")
async def rejeter_mutation(
    mutation_id: str,
    raison: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Rejeter une demande de mutation"""
    db = get_db()
    
    user_id = get_user_id(current_user)
    
    mutation = await db.demandes_mutations.find_one({"id": mutation_id}, {"_id": 0})
    if not mutation:
        raise HTTPException(status_code=404, detail="Demande de mutation non trouvée")
    
    # Vérifier que l'utilisateur est dans le circuit
    circuit = mutation["circuit_validation"]
    peut_rejeter = False
    
    for etape in circuit:
        if etape["user_id"] == user_id:
            peut_rejeter = True
            break
    
    if not peut_rejeter:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à rejeter cette demande")
    
    # Marquer comme rejetée
    await db.demandes_mutations.update_one(
        {"id": mutation_id},
        {
            "$set": {
                "statut": StatutMutation.REJETEE.value,
                "date_cloture": datetime.now(timezone.utc).isoformat()
            },
            "$push": {
                "circuit_validation": {
                    "role": current_user["role"],
                    "user_id": user_id,
                    "user_nom": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
                    "statut": "rejete",
                    "date": datetime.now(timezone.utc).isoformat(),
                    "commentaire": raison
                }
            }
        }
    )
    
    # Notifier l'enseignant
    enseignant = await db.enseignants.find_one({"id": mutation["enseignant_id"]}, {"_id": 0})
    user_enseignant = await db.users.find_one({"id": enseignant["user_id"]}, {"_id": 0})
    
    email_notification_mutation(
        destinataire_email=user_enseignant.get("email"),
        destinataire_nom=f"{user_enseignant.get('prenom')} {user_enseignant.get('nom')}",
        numero_reference=mutation["numero_reference"],
        type_mutation=mutation["type_mutation"],
        statut="rejetee",
        raison_rejet=raison
    )
    
    return {"message": "Mutation rejetée"}


async def appliquer_mutation(db, mutation: dict):
    """Appliquer une mutation approuvée"""
    enseignant_id = mutation["enseignant_id"]
    type_mutation = mutation["type_mutation"]
    
    date_effective = datetime.now(timezone.utc).isoformat()
    
    if type_mutation == "geographique":
        # Clôturer l'affectation actuelle
        await db.historique_affectations.update_many(
            {"enseignant_id": enseignant_id, "date_fin": None},
            {"$set": {"date_fin": date_effective}}
        )
        
        # Créer nouvelle affectation
        nouvelle_affectation = HistoriqueAffectation(
            enseignant_id=enseignant_id,
            etablissement_id=mutation["etablissement_destination_id"],
            etablissement_nom=mutation["etablissement_destination_nom"],
            province_id=mutation["province_destination_id"],
            province_nom=mutation["province_destination_nom"],
            date_debut=date_effective,
            motif="Mutation géographique",
            mutation_id=mutation["id"]
        )
        await db.historique_affectations.insert_one(nouvelle_affectation.model_dump())
        
        # Mettre à jour l'enseignant
        await db.enseignants.update_one(
            {"id": enseignant_id},
            {"$set": {"etablissement_id": mutation["etablissement_destination_id"]}}
        )
    
    elif type_mutation == "promotion":
        # Enregistrer promotion
        promotion = HistoriquePromotion(
            enseignant_id=enseignant_id,
            ancien_grade=mutation["grade_actuel"],
            nouveau_grade=mutation["grade_demande"],
            date_promotion=date_effective,
            motif=mutation["motif"],
            decision_reference=mutation["numero_reference"],
            mutation_id=mutation["id"]
        )
        await db.historique_promotions.insert_one(promotion.model_dump())
        
        # Mettre à jour l'enseignant
        await db.enseignants.update_one(
            {"id": enseignant_id},
            {"$set": {"grade": mutation["grade_demande"]}}
        )
    
    elif type_mutation == "discipline":
        # Enregistrer mutation de discipline
        mutation_disc = HistoriqueMutationDiscipline(
            enseignant_id=enseignant_id,
            anciennes_matieres=mutation["matieres_actuelles"],
            nouvelles_matieres=mutation["matieres_demandees"],
            date_mutation=date_effective,
            motif=mutation["motif"],
            mutation_id=mutation["id"]
        )
        await db.historique_mutations_discipline.insert_one(mutation_disc.model_dump())
        
        # Mettre à jour l'enseignant
        await db.enseignants.update_one(
            {"id": enseignant_id},
            {"$set": {"matieres": mutation["matieres_demandees"]}}
        )
    
    # Marquer la date effective
    await db.demandes_mutations.update_one(
        {"id": mutation["id"]},
        {"$set": {"date_effective": date_effective, "date_cloture": date_effective}}
    )
