"""
Logique d'auto-génération du circuit de validation pour les documents
Circuit: Créateur → N+1 → Directeur → DG → SG → Ministre
"""
from typing import List, Tuple, Optional


async def generer_circuit_validation(
    db,
    createur_id: str,
    createur_service_id: str,
    destinataire_final_id: str
) -> Tuple[List[str], List[str], List[str]]:
    """
    Génère automatiquement le circuit de validation basé sur la hiérarchie
    
    Args:
        db: Instance de la base de données
        createur_id: ID de l'utilisateur créateur
        createur_service_id: ID du service du créateur
        destinataire_final_id: ID du destinataire final
    
    Returns:
        Tuple de 3 listes:
        - circuit_validation: List[user_ids]
        - circuit_validation_noms: List[str]
        - circuit_validation_services: List[str]
    """
    
    # 1. Récupérer les informations du créateur
    createur = await db.users.find_one({"id": createur_id}, {"_id": 0})
    if not createur:
        raise ValueError("Créateur non trouvé")
    
    # 2. Récupérer le service du créateur
    service_createur = await db.services.find_one({"id": createur_service_id}, {"_id": 0})
    if not service_createur:
        raise ValueError("Service du créateur non trouvé")
    
    # 3. Remonter la hiérarchie des services
    circuit_services = []
    current_service_id = createur_service_id
    
    while current_service_id:
        service = await db.services.find_one({"id": current_service_id}, {"_id": 0})
        if not service:
            break
        circuit_services.append(service)
        current_service_id = service.get("parent_id")
    
    # 4. Pour chaque service dans la hiérarchie, trouver le responsable
    circuit_user_ids = []
    circuit_noms = []
    circuit_services_noms = []
    
    for service in circuit_services:
        # Trouver le responsable de ce service
        responsable_id = service.get("responsable_id")
        
        if responsable_id:
            # Le service a un responsable désigné
            responsable = await db.users.find_one({"id": responsable_id}, {"_id": 0})
            if responsable and responsable["id"] not in circuit_user_ids:
                circuit_user_ids.append(responsable["id"])
                nom_complet = f"{responsable.get('prenom', '')} {responsable.get('nom', '')}"
                circuit_noms.append(nom_complet)
                circuit_services_noms.append(service["nom"])
        else:
            # Pas de responsable désigné: chercher un utilisateur dont c'est le service actif
            # et qui est marqué comme responsable dans son profile de service
            user_profile = await db.users.find_one(
                {
                    "service_profiles.service_id": service["id"],
                    "service_profiles.est_responsable": True
                },
                {"_id": 0}
            )
            
            if user_profile and user_profile["id"] not in circuit_user_ids:
                circuit_user_ids.append(user_profile["id"])
                nom_complet = f"{user_profile.get('prenom', '')} {user_profile.get('nom', '')}"
                circuit_noms.append(nom_complet)
                circuit_services_noms.append(service["nom"])
    
    # 5. Ajouter le destinataire final à la fin s'il n'est pas déjà dans le circuit
    if destinataire_final_id and destinataire_final_id not in circuit_user_ids:
        destinataire = await db.users.find_one({"id": destinataire_final_id}, {"_id": 0})
        if destinataire:
            circuit_user_ids.append(destinataire_final_id)
            nom_complet = f"{destinataire.get('prenom', '')} {destinataire.get('nom', '')}"
            circuit_noms.append(nom_complet)
            
            # Trouver le service du destinataire
            if destinataire.get("service_profiles"):
                service_dest_id = destinataire["service_profiles"][0]["service_id"]
                service_dest = await db.services.find_one({"id": service_dest_id}, {"_id": 0})
                if service_dest:
                    circuit_services_noms.append(service_dest["nom"])
                else:
                    circuit_services_noms.append("Service inconnu")
            else:
                circuit_services_noms.append("Service inconnu")
    
    # 6. S'assurer qu'il y a au moins 1 validateur
    if not circuit_user_ids:
        # Circuit minimum: le créateur lui-même (auto-validation)
        circuit_user_ids = [createur_id]
        nom_complet = f"{createur.get('prenom', '')} {createur.get('nom', '')}"
        circuit_noms = [nom_complet]
        circuit_services_noms = [service_createur["nom"]]
    
    return circuit_user_ids, circuit_noms, circuit_services_noms


async def verifier_peut_valider_directement(db, user_id: str) -> bool:
    """
    Vérifie si l'utilisateur peut valider directement (Ministre ou SG)
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur
    
    Returns:
        bool: True si l'utilisateur peut valider directement
    """
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return False
    
    # Vérifier si l'utilisateur est dans un service Ministre ou SG
    if user.get("service_profiles"):
        for profile in user["service_profiles"]:
            service = await db.services.find_one({"id": profile["service_id"]}, {"_id": 0})
            if service:
                # Ministre (niveau 1) ou SG (niveau 2, code "SG")
                if service["niveau"] == "niveau_1" or service["code"] == "SG":
                    return True
    
    return False


async def get_services_affectables(db, user_id: str) -> List[dict]:
    """
    Récupère la liste des services auxquels le Ministre ou SG peut affecter un document
    
    Args:
        db: Instance de la base de données
        user_id: ID de l'utilisateur (Ministre ou SG)
    
    Returns:
        List[dict]: Liste des services (Niveau 3 et en dessous)
    """
    # Vérifier que l'utilisateur peut affecter
    peut_affecter = await verifier_peut_valider_directement(db, user_id)
    if not peut_affecter:
        return []
    
    # Récupérer tous les services de niveau 3, 4 et 5
    services = await db.services.find(
        {
            "niveau": {"$in": ["niveau_3", "niveau_4", "niveau_5"]}
        },
        {"_id": 0}
    ).sort("nom", 1).to_list(1000)
    
    return services
