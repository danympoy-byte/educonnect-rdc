"""
Routes pour le chat/messagerie interne du GED
Permet aux utilisateurs de communiquer entre eux au sein de la plateforme
avec respect de la hiérarchie organisationnelle
"""
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import List, Optional
import os

from models import Conversation, ConversationCreate, MessageChat, MessageCreate
from auth import get_current_user
from dotenv import load_dotenv
from pathlib import Path

# Router
router = APIRouter(prefix="/api/chat", tags=["Chat / Messagerie"])

# MongoDB connection
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


# ============================================
# FONCTIONS UTILITAIRES - HIÉRARCHIE
# ============================================

async def get_user_niveau(user_id: str) -> int:
    """
    Récupère le niveau hiérarchique d'un utilisateur
    Compatible avec le nouveau système multi-services (service_profiles)
    """
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return 999  # Niveau très bas par défaut
    
    # Nouveau système : service_profiles
    service_profiles = user.get("service_profiles", [])
    if service_profiles and len(service_profiles) > 0:
        # Prendre le service actif ou le premier
        service_actif_id = user.get("service_actif_id")
        
        if service_actif_id:
            profile = next((p for p in service_profiles if p.get("service_id") == service_actif_id), None)
        else:
            profile = service_profiles[0]
        
        if profile:
            service_id = profile.get("service_id")
            if service_id:
                # Récupérer le service
                service = await db.services.find_one({"id": service_id}, {"_id": 0})
                if service:
                    niveau_str = service.get("niveau", "niveau_999")
                    # Convertir "niveau_3" -> 3
                    try:
                        return int(niveau_str.replace("niveau_", ""))
                    except:
                        return 999
    
    # Legacy : ancien système avec "services"
    services = user.get("services", [])
    if services:
        service_id = services[0].get("service_id")
        if service_id:
            service = await db.services.find_one({"id": service_id}, {"_id": 0})
            if service:
                niveau_str = service.get("niveau", "niveau_999")
                try:
                    return int(niveau_str.replace("niveau_", ""))
                except:
                    return 999
    
    # Par défaut : niveau très bas (utilisateur sans service)
    return 999


async def peut_initier_conversation(initiateur_id: str, destinataire_id: str) -> tuple[bool, str]:
    """
    Vérifie si un utilisateur peut initier une conversation avec un autre
    Règles:
    - Même niveau: OUI
    - Vers niveau inférieur (supérieur → subordonné): OUI
    - Vers niveau supérieur (subordonné → supérieur): NON
    
    Returns: (peut_initier, raison_si_non)
    """
    niveau_initiateur = await get_user_niveau(initiateur_id)
    niveau_destinataire = await get_user_niveau(destinataire_id)
    
    # Même niveau ou initiateur est supérieur: OK
    if niveau_initiateur <= niveau_destinataire:
        return True, ""
    
    # Initiateur est subordonné: NON
    return False, f"Vous ne pouvez pas initier une conversation avec un supérieur hiérarchique. Veuillez attendre qu'il vous contacte."


async def get_superieur_conversation(conversation_id: str) -> Optional[str]:
    """Retourne l'ID du participant ayant le niveau le plus élevé dans la conversation"""
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conversation:
        return None
    
    niveaux = []
    for participant_id in conversation["participants"]:
        niveau = await get_user_niveau(participant_id)
        niveaux.append((participant_id, niveau))
    
    # Trier par niveau (le plus bas = le plus haut hiérarchiquement)
    niveaux.sort(key=lambda x: x[1])
    
    return niveaux[0][0] if niveaux else None


# ============================================
# UTILISATEURS CONTACTABLES
# ============================================

@router.get(
    "/utilisateurs-contactables",
    summary="Liste des utilisateurs que je peux contacter"
)
async def get_utilisateurs_contactables(
    current_user: dict = Depends(get_current_user)
):
    """
    Retourne la liste des utilisateurs que l'utilisateur connecté peut contacter.
    Règles:
    - Pairs (même niveau): Oui
    - Subordonnés (niveaux inférieurs): Oui
    - Supérieurs (niveaux supérieurs): Oui aussi (pour permettre la communication)
    
    NOTE: La règle de hiérarchie stricte a été assouplie pour permettre 
    à tous les utilisateurs de contacter tous les autres utilisateurs.
    """
    # Récupérer tous les utilisateurs sauf l'utilisateur actuel
    tous_users = await db.users.find(
        {"id": {"$ne": current_user["sub"]}},
        {"_id": 0, "hashed_password": 0}
    ).to_list(500)
    
    # Retourner tous les utilisateurs (sans filtrage hiérarchique strict)
    utilisateurs_contactables = []
    for user in tous_users:
        # Déterminer le service
        service_nom = "N/A"
        service_profiles = user.get("service_profiles", [])
        
        if service_profiles:
            # Utiliser le service actif ou le premier
            service_actif_id = user.get("service_actif_id")
            if service_actif_id:
                profile = next((p for p in service_profiles if p.get("service_id") == service_actif_id), None)
                if profile:
                    service_nom = profile.get("service_nom", "N/A")
            else:
                service_nom = service_profiles[0].get("service_nom", "N/A")
        
        utilisateurs_contactables.append({
            "id": user["id"],
            "nom": user.get("nom", ""),
            "prenom": user.get("prenom", ""),
            "email": user.get("email", ""),
            "telephone": user.get("telephone", ""),
            "service": service_nom,
            "niveau": 0  # Pas de filtrage par niveau
        })
    
    return utilisateurs_contactables


# ============================================
# CONVERSATIONS
# ============================================

@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle conversation"
)
async def create_conversation(
    data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crée une nouvelle conversation avec un ou plusieurs participants
    
    Règles hiérarchiques:
    - Même niveau: conversation autorisée
    - Supérieur → Subordonné: conversation autorisée
    - Subordonné → Supérieur: conversation REFUSÉE
    """
    # Vérifier la hiérarchie pour chaque participant
    for participant_id in data.participants_ids:
        peut_initier, raison = await peut_initier_conversation(current_user["sub"], participant_id)
        if not peut_initier:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=raison
            )
    
    # Récupérer les infos des participants (avec niveau hiérarchique)
    participants_ids = list(set([current_user["sub"]] + data.participants_ids))  # Inclure le créateur
    
    participants_info = []
    for participant_id in participants_ids:
        user = await db.users.find_one({"id": participant_id}, {"_id": 0, "password": 0})
        if user:
            niveau = await get_user_niveau(participant_id)
            service_nom = user.get("services", [{}])[0].get("service_nom", "N/A") if user.get("services") else "N/A"
            
            participants_info.append({
                "id": user["id"],
                "nom": user.get("nom", ""),
                "prenom": user.get("prenom", ""),
                "service": service_nom,
                "niveau": niveau
            })
    
    # Créer la conversation
    conversation = Conversation(
        titre=data.titre,
        participants=participants_ids,
        participants_info=participants_info,
        createur_id=current_user["sub"],
        createur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        tags=data.tags or [],
        document_lie_id=data.document_lie_id,
        statut="active"
    )
    
    conv_dict = conversation.model_dump()
    conv_dict["date_creation"] = conv_dict["date_creation"].isoformat()
    conv_dict["derniere_activite"] = conv_dict["derniere_activite"].isoformat()
    
    await db.conversations.insert_one(conv_dict)
    
    # Créer le premier message
    premier_message = MessageChat(
        conversation_id=conversation.id,
        expediteur_id=current_user["sub"],
        expediteur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        expediteur_service=current_user.get("services", [{}])[0].get("service_nom", "N/A") if current_user.get("services") else "N/A",
        contenu=data.premier_message,
        lu_par=[current_user["sub"]]
    )
    
    msg_dict = premier_message.model_dump()
    msg_dict["date_envoi"] = msg_dict["date_envoi"].isoformat()
    
    await db.messages_chat.insert_one(msg_dict)
    
    return {
        "message": "Conversation créée avec succès",
        "conversation_id": conversation.id
    }


@router.get(
    "/conversations",
    summary="Lister mes conversations"
)
async def list_conversations(
    archive: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Liste toutes les conversations de l'utilisateur connecté
    """
    query = {"participants": current_user["sub"]}
    if archive is not None:
        query["archive"] = archive
    
    conversations = await db.conversations.find(
        query,
        {"_id": 0}
    ).sort("derniere_activite", -1).to_list(100)
    
    # Pour chaque conversation, récupérer le dernier message
    for conv in conversations:
        dernier_msg = await db.messages_chat.find_one(
            {"conversation_id": conv["id"]},
            {"_id": 0}
        ).sort("date_envoi", -1)
        
        conv["dernier_message"] = dernier_msg.get("contenu", "") if dernier_msg else ""
        conv["dernier_message_date"] = dernier_msg.get("date_envoi", "") if dernier_msg else ""
        
        # Compter les messages non lus
        messages_non_lus = await db.messages_chat.count_documents({
            "conversation_id": conv["id"],
            "lu_par": {"$ne": current_user["sub"]}
        })
        conv["messages_non_lus"] = messages_non_lus
    
    return conversations


@router.get(
    "/conversations/{conversation_id}",
    summary="Détails d'une conversation"
)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les détails d'une conversation
    """
    conversation = await db.conversations.find_one(
        {"id": conversation_id, "participants": current_user["sub"]},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable ou vous n'y avez pas accès"
        )
    
    return conversation


@router.put(
    "/conversations/{conversation_id}/archive",
    summary="Archiver/Désarchiver une conversation"
)
async def archive_conversation(
    conversation_id: str,
    archive: bool,
    current_user: dict = Depends(get_current_user)
):
    """
    Archive ou désarchive une conversation (ne la supprime pas)
    """
    result = await db.conversations.update_one(
        {"id": conversation_id, "participants": current_user["sub"]},
        {"$set": {"archive": archive}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable"
        )
    
    return {"message": "Conversation archivée" if archive else "Conversation désarchivée"}


@router.put(
    "/conversations/{conversation_id}/terminer",
    summary="Terminer une conversation (supérieur uniquement)"
)
async def terminer_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Termine une conversation. Seul le participant de niveau hiérarchique le plus élevé peut terminer.
    Une fois terminée, plus aucun message ne peut être envoyé.
    """
    # Vérifier que l'utilisateur est le supérieur de la conversation
    superieur_id = await get_superieur_conversation(conversation_id)
    
    if superieur_id != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le supérieur hiérarchique peut terminer cette conversation"
        )
    
    # Terminer la conversation
    result = await db.conversations.update_one(
        {"id": conversation_id},
        {
            "$set": {
                "statut": "terminee",
                "terminee_par": current_user["sub"],
                "date_terminaison": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation introuvable"
        )
    
    return {"message": "Conversation terminée avec succès"}


# ============================================
# MESSAGES
# ============================================

@router.post(
    "/conversations/{conversation_id}/messages",
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message"
)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Envoie un message dans une conversation
    Bloqué si la conversation est terminée
    """
    # Vérifier que l'utilisateur est participant
    conversation = await db.conversations.find_one(
        {"id": conversation_id, "participants": current_user["sub"]},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas participant à cette conversation"
        )
    
    # Vérifier que la conversation n'est pas terminée
    if conversation.get("statut") == "terminee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette conversation a été terminée par le supérieur. Aucun message ne peut être envoyé."
        )
    
    # Créer le message
    message = MessageChat(
        conversation_id=conversation_id,
        expediteur_id=current_user["sub"],
        expediteur_nom=f"{current_user.get('prenom', '')} {current_user.get('nom', '')}",
        expediteur_service=current_user.get("services", [{}])[0].get("service_nom", "N/A") if current_user.get("services") else "N/A",
        contenu=data.contenu,
        lu_par=[current_user["sub"]]
    )
    
    msg_dict = message.model_dump()
    msg_dict["date_envoi"] = msg_dict["date_envoi"].isoformat()
    
    await db.messages_chat.insert_one(msg_dict)
    
    # Mettre à jour la dernière activité de la conversation
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"derniere_activite": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Message envoyé", "message_id": message.id}


@router.get(
    "/conversations/{conversation_id}/messages",
    summary="Récupérer les messages d'une conversation"
)
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère tous les messages d'une conversation
    """
    # Vérifier l'accès
    conversation = await db.conversations.find_one(
        {"id": conversation_id, "participants": current_user["sub"]},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé à cette conversation"
        )
    
    # Récupérer les messages
    messages = await db.messages_chat.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("date_envoi", 1).to_list(1000)
    
    # Marquer les messages comme lus
    await db.messages_chat.update_many(
        {"conversation_id": conversation_id, "lu_par": {"$ne": current_user["sub"]}},
        {"$push": {"lu_par": current_user["sub"]}}
    )
    
    return messages


# ============================================
# RECHERCHE
# ============================================

@router.get(
    "/search",
    summary="Rechercher dans les conversations et messages"
)
async def search_messages(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Recherche dans les titres de conversations et le contenu des messages
    """
    if len(q) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La recherche doit contenir au moins 3 caractères"
        )
    
    # Recherche dans les conversations
    conversations = await db.conversations.find(
        {
            "participants": current_user["sub"],
            "$or": [
                {"titre": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}}
            ]
        },
        {"_id": 0}
    ).to_list(50)
    
    # Recherche dans les messages
    messages = await db.messages_chat.find(
        {"contenu": {"$regex": q, "$options": "i"}},
        {"_id": 0}
    ).to_list(100)
    
    # Filtrer les messages pour ne garder que ceux des conversations accessibles
    conv_ids = [conv["id"] for conv in conversations]
    messages_filtrés = []
    
    for msg in messages:
        if msg["conversation_id"] not in conv_ids:
            # Vérifier si l'utilisateur a accès à cette conversation
            conv = await db.conversations.find_one(
                {"id": msg["conversation_id"], "participants": current_user["sub"]},
                {"_id": 0}
            )
            if conv:
                messages_filtrés.append(msg)
        else:
            messages_filtrés.append(msg)
    
    return {
        "conversations": conversations,
        "messages": messages_filtrés,
        "total_resultats": len(conversations) + len(messages_filtrés)
    }


# ============================================
# EXPORT / IMPRESSION
# ============================================

@router.get(
    "/conversations/{conversation_id}/export",
    summary="Exporter une conversation (pour impression)"
)
async def export_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Génère un export de la conversation pour impression (format structuré)
    """
    # Vérifier l'accès
    conversation = await db.conversations.find_one(
        {"id": conversation_id, "participants": current_user["sub"]},
        {"_id": 0}
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé"
        )
    
    # Récupérer tous les messages
    messages = await db.messages_chat.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("date_envoi", 1).to_list(1000)
    
    return {
        "conversation": conversation,
        "messages": messages,
        "date_export": datetime.now(timezone.utc).isoformat(),
        "exporte_par": f"{current_user.get('prenom', '')} {current_user.get('nom', '')}"
    }
