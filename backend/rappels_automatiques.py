"""
Tâche background pour les rappels automatiques de documents en attente
"""
import asyncio
import os
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Import conditionnel pour gérer la fonction manquante
try:
    from email_service import email_rappel_document
except ImportError:
    # Fonction stub si email_rappel_document n'existe pas encore
    def email_rappel_document(destinataire_email, destinataire_nom, document_titre, document_ref, url_document):
        print(f"⚠️ email_rappel_document stub: {destinataire_email} - {document_titre}")
        return False

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")


async def verifier_documents_en_attente():
    """
    Vérifier les documents en attente et envoyer des rappels
    - Rappel après 48h d'inactivité
    - Puis toutes les 3h après le premier rappel
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"[{datetime.now()}] Vérification des documents en attente...")
    
    maintenant = datetime.now(timezone.utc)
    
    # Documents en attente depuis plus de 48h sans rappel récent
    date_limite_48h = (maintenant - timedelta(hours=48)).isoformat()
    
    # Documents déjà rappelés mais plus de 3h depuis dernier rappel
    date_limite_3h = (maintenant - timedelta(hours=3)).isoformat()
    
    # Récupérer tous les documents en attente
    documents = await db.documents.find({
        "statut": "en_attente",
        "date_creation": {"$lt": date_limite_48h}
    }, {"_id": 0}).to_list(1000)
    
    rappels_envoyes = 0
    
    for doc in documents:
        # Vérifier le dernier rappel
        dernier_rappel = await db.historique_actions.find_one(
            {
                "document_id": doc["id"],
                "type_action": "rappel"
            },
            {"_id": 0},
            sort=[("date_action", -1)]
        )
        
        # Déterminer si on doit envoyer un rappel
        doit_rappeler = False
        heures_attente = 0
        
        if not dernier_rappel:
            # Premier rappel (après 48h)
            doit_rappeler = True
            delta = maintenant - datetime.fromisoformat(doc["date_creation"].replace("Z", "+00:00"))
            heures_attente = int(delta.total_seconds() / 3600)
        else:
            # Rappel suivant (toutes les 3h)
            date_dernier_rappel = dernier_rappel["date_action"]
            if date_dernier_rappel < date_limite_3h:
                doit_rappeler = True
                delta = maintenant - datetime.fromisoformat(doc["date_creation"].replace("Z", "+00:00"))
                heures_attente = int(delta.total_seconds() / 3600)
        
        if doit_rappeler:
            # Récupérer le propriétaire actuel
            proprietaire = await db.users.find_one(
                {"id": doc["proprietaire_actuel_id"]},
                {"_id": 0}
            )
            
            if proprietaire and proprietaire.get("email"):
                # Envoyer le rappel
                url_frontend = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:3000").replace("/api", "")
                url_document = f"{url_frontend}/#/documents/{doc['id']}"
                
                success = email_rappel_document(
                    destinataire_email=proprietaire["email"],
                    destinataire_nom=doc["proprietaire_actuel_nom"],
                    document_titre=doc["titre"],
                    document_ref=doc["numero_reference"],
                    heures_attente=heures_attente,
                    url_document=url_document
                )
                
                if success:
                    # Enregistrer le rappel dans l'historique
                    historique = {
                        "id": str(asyncio.get_event_loop().time()),  # ID temporaire
                        "document_id": doc["id"],
                        "user_id": "system",
                        "user_nom": "Système automatique",
                        "user_role": "system",
                        "type_action": "rappel",
                        "commentaire": f"Rappel automatique envoyé après {heures_attente}h d'attente",
                        "date_action": maintenant.isoformat()
                    }
                    
                    await db.historique_actions.insert_one(historique)
                    rappels_envoyes += 1
                    print(f"  ✅ Rappel envoyé: {doc['numero_reference']} → {proprietaire['email']}")
    
    client.close()
    
    print(f"[{datetime.now()}] Vérification terminée. {rappels_envoyes} rappel(s) envoyé(s).")
    return rappels_envoyes


if __name__ == "__main__":
    # Test de la fonction
    asyncio.run(verifier_documents_en_attente())
