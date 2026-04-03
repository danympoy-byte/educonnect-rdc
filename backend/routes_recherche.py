"""
Service de recherche avancée avec indexation de texte intégral
Supporte l'extraction de texte depuis PDF, DOCX et images (OCR)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import os
from datetime import datetime, timezone

from auth import get_current_user

router = APIRouter(prefix="/api/recherche", tags=["Recherche Avancée"])


def get_user_id(user: dict) -> str:
    """Récupère l'ID de l'utilisateur du token JWT"""
    return user.get("sub", user.get("user_id", user.get("id", "")))


@router.post("/indexer-document/{document_id}")
async def indexer_document(
    document_id: str,
    force_reindex: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Indexer le contenu textuel d'un document pour la recherche
    Extrait le texte depuis PDF, DOCX, images (OCR)
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    
    document = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Vérifier les droits
    peut_indexer = (
        document["createur_id"] == user_id or
        current_user.get("role") in ["ministre", "secretaire_general"]
    )
    
    if not peut_indexer:
        raise HTTPException(status_code=403, detail="Droits insuffisants pour indexer")
    
    # Vérifier si déjà indexé
    if document.get("contenu_indexe") and not force_reindex:
        return {
            "message": "Document déjà indexé",
            "document_id": document_id,
            "taille_index": len(document.get("contenu_indexe", ""))
        }
    
    # Vérifier qu'il y a un fichier
    fichier_url = document.get("fichier_url")
    if not fichier_url:
        raise HTTPException(status_code=400, detail="Aucun fichier à indexer")
    
    fichier_type = document.get("fichier_type", "").lower()
    fichier_path = fichier_url.replace("file://", "") if fichier_url.startswith("file://") else fichier_url
    
    if not os.path.exists(fichier_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    
    # Extraire le texte selon le type
    try:
        texte_extrait = ""
        methode_extraction = ""
        
        # PDF
        if "pdf" in fichier_type:
            texte_extrait, methode_extraction = await extraire_texte_pdf(fichier_path)
        
        # DOCX
        elif "word" in fichier_type or fichier_type.endswith("docx"):
            texte_extrait, methode_extraction = await extraire_texte_docx(fichier_path)
        
        # Images (OCR)
        elif fichier_type.startswith("image/"):
            texte_extrait, methode_extraction = await extraire_texte_image_ocr(fichier_path)
        
        # Texte simple
        elif fichier_type.startswith("text/"):
            with open(fichier_path, "r", encoding="utf-8") as f:
                texte_extrait = f.read()
            methode_extraction = "lecture_directe"
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier non supporté pour l'indexation: {fichier_type}"
            )
        
        # Mettre à jour le document avec le contenu indexé
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "contenu_indexe": texte_extrait,
                    "date_indexation": datetime.now(timezone.utc).isoformat(),
                    "methode_extraction": methode_extraction,
                    "taille_contenu_indexe": len(texte_extrait)
                }
            }
        )
        
        return {
            "message": "Document indexé avec succès",
            "document_id": document_id,
            "taille_index": len(texte_extrait),
            "methode": methode_extraction,
            "apercu": texte_extrait[:200] + "..." if len(texte_extrait) > 200 else texte_extrait
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'indexation: {str(e)}"
        )


async def extraire_texte_pdf(fichier_path: str) -> tuple:
    """Extraire le texte d'un PDF"""
    try:
        import fitz
    except ImportError:
        raise HTTPException(status_code=500, detail="PyMuPDF non installé")
    
    doc = fitz.open(fichier_path)
    texte_complet = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        texte_complet.append(page.get_text())
    
    doc.close()
    
    return "\n\n".join(texte_complet), "pymupdf"


async def extraire_texte_docx(fichier_path: str) -> tuple:
    """Extraire le texte d'un DOCX"""
    try:
        from docx import Document
    except ImportError:
        raise HTTPException(status_code=500, detail="python-docx non installé")
    
    doc = Document(fichier_path)
    texte_complet = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    
    return texte_complet, "python-docx"


async def extraire_texte_image_ocr(fichier_path: str) -> tuple:
    """Extraire le texte d'une image via OCR"""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        # OCR optionnel - retourner un texte vide si non disponible
        return "", "ocr_non_disponible"
    
    try:
        image = Image.open(fichier_path)
        texte = pytesseract.image_to_string(image, lang='fra')  # Français
        return texte, "tesseract_ocr"
    except Exception as e:
        return f"[Erreur OCR: {str(e)}]", "ocr_erreur"


@router.get("/recherche-contenu")
async def rechercher_dans_contenu(
    q: str = Query(..., min_length=3, description="Texte à rechercher"),
    type_document: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    createur_id: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Rechercher dans le contenu indexé des documents
    Recherche textuelle intégrale avec filtres
    """
    from dependencies import get_db

    db = get_db()
    
    user_id = get_user_id(current_user)
    user_role = current_user.get("role")
    
    # Construire le filtre de base
    filtre = {
        "contenu_indexe": {"$regex": q, "$options": "i"}  # Recherche insensible à la casse
    }
    
    # Filtres additionnels
    if type_document:
        filtre["type_document"] = type_document
    
    if date_debut:
        filtre["date_creation"] = {"$gte": date_debut}
    
    if date_fin:
        if "date_creation" in filtre:
            filtre["date_creation"]["$lte"] = date_fin
        else:
            filtre["date_creation"] = {"$lte": date_fin}
    
    if createur_id:
        filtre["createur_id"] = createur_id
    
    # Appliquer les restrictions d'accès
    if user_role != "ministre":
        filtre["$or"] = [
            {"createur_id": user_id},
            {"proprietaire_actuel_id": user_id},
            {"circuit_validation": user_id},
            {"collaborateurs_ids": user_id},
            {"niveau_diffusion": "public"}
        ]
    
    # Rechercher
    documents = await db.documents.find(
        filtre,
        {
            "_id": 0,
            "id": 1,
            "numero_reference": 1,
            "titre": 1,
            "type_document": 1,
            "date_creation": 1,
            "createur_nom": 1,
            "contenu_indexe": 1,
            "fichier_nom": 1,
            "statut": 1
        }
    ).sort("date_creation", -1).to_list(limit)
    
    # Générer des extraits de contexte
    resultats_avec_extraits = []
    for doc in documents:
        contenu = doc.get("contenu_indexe", "")
        
        # Trouver la position du terme recherché
        position = contenu.lower().find(q.lower())
        
        if position != -1:
            # Extraire un contexte de 150 caractères autour
            debut = max(0, position - 75)
            fin = min(len(contenu), position + len(q) + 75)
            extrait = "..." + contenu[debut:fin] + "..."
            
            # Mettre en évidence le terme recherché
            extrait_highlight = extrait.replace(
                q,
                f"**{q}**"  # Markdown bold
            )
        else:
            extrait_highlight = contenu[:150] + "..."
        
        doc_resultat = {
            **doc,
            "extrait_contexte": extrait_highlight,
            "taille_contenu": len(contenu)
        }
        
        # Supprimer le contenu complet pour alléger la réponse
        doc_resultat.pop("contenu_indexe", None)
        
        resultats_avec_extraits.append(doc_resultat)
    
    return {
        "requete": q,
        "total_resultats": len(resultats_avec_extraits),
        "resultats": resultats_avec_extraits
    }


@router.post("/indexer-tous")
async def indexer_tous_documents(
    force_reindex: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Indexer tous les documents qui ont un fichier mais pas d'index
    Réservé aux administrateurs
    """
    from dependencies import get_db

    db = get_db()
    
    user_role = current_user.get("role")
    
    if user_role not in ["ministre", "secretaire_general"]:
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs")
    
    # Trouver les documents à indexer
    filtre = {"fichier_url": {"$exists": True, "$ne": None}}
    
    if not force_reindex:
        filtre["contenu_indexe"] = {"$exists": False}
    
    documents_a_indexer = await db.documents.find(
        filtre,
        {"_id": 0, "id": 1, "titre": 1}
    ).to_list(1000)
    
    if not documents_a_indexer:
        return {
            "message": "Tous les documents sont déjà indexés",
            "total": 0
        }
    
    # Indexer en arrière-plan (simulation - dans une vraie app, utiliser Celery/RQ)
    resultats = {
        "total_a_indexer": len(documents_a_indexer),
        "succes": 0,
        "echecs": 0,
        "documents": []
    }
    
    for doc in documents_a_indexer[:20]:  # Limiter à 20 pour éviter timeout
        try:
            result = await indexer_document(doc["id"], force_reindex, current_user)
            resultats["succes"] += 1
            resultats["documents"].append({
                "id": doc["id"],
                "titre": doc["titre"],
                "statut": "indexé"
            })
        except Exception as e:
            resultats["echecs"] += 1
            resultats["documents"].append({
                "id": doc["id"],
                "titre": doc["titre"],
                "statut": "erreur",
                "erreur": str(e)
            })
    
    return resultats


@router.get("/stats-indexation")
async def statistiques_indexation(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiques sur l'indexation des documents
    """
    from dependencies import get_db

    db = get_db()
    
    total_documents = await db.documents.count_documents({"fichier_url": {"$exists": True, "$ne": None}})
    documents_indexes = await db.documents.count_documents({"contenu_indexe": {"$exists": True, "$ne": ""}})
    documents_non_indexes = total_documents - documents_indexes
    
    # Taille totale indexée
    pipeline = [
        {"$match": {"contenu_indexe": {"$exists": True}}},
        {"$group": {
            "_id": None,
            "taille_totale": {"$sum": "$taille_contenu_indexe"}
        }}
    ]
    
    resultat = await db.documents.aggregate(pipeline).to_list(1)
    taille_totale = resultat[0]["taille_totale"] if resultat else 0
    
    return {
        "total_documents_avec_fichier": total_documents,
        "documents_indexes": documents_indexes,
        "documents_non_indexes": documents_non_indexes,
        "pourcentage_indexe": round((documents_indexes / total_documents * 100) if total_documents > 0 else 0, 2),
        "taille_totale_index_bytes": taille_totale,
        "taille_totale_index_mb": round(taille_totale / 1024 / 1024, 2)
    }
