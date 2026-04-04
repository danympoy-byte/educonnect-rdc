from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import des modèles et utilitaires
from models import (
    User, UserCreate, UserLogin, Token, UserRole, UserResponse,
    Province, ProvinceCreate,
    SousDivision, SousDivisionCreate,
    Etablissement, EtablissementCreate, TypeEtablissement,
    Enseignant, EnseignantCreate,
    Eleve, EleveCreate, NiveauScolaire,
    Classe, ClasseCreate,
    Note, NoteCreate, Trimestre,
    Bulletin, BulletinCreate,
    AuditLog, AuditLogCreate,
    Stats,
    # GED Models
    Document, HistoriqueAction, Commentaire, NotificationDocument,
    StatutDocument, TypeAction, NiveauDiffusion, ModeLivraison, RapportTrimestriel,
    # SIRH Models
    GradeEnseignant, TypeMutation, StatutMutation,
    HistoriqueAffectation, HistoriquePromotion, HistoriqueMutationDiscipline,
    VerificationDINACOPE, DonneesDINACOPE, DemandeMutation, DetectionFraude,
    # DINACOPE Avancé
    GrileSalariale, FichePaie, ControlePhysiqueMensuel, ViabiliteEtablissement, ExportDINACOPE,
    # Module 3 - Scolarité (APIs Externes)
    APIClient, APIClientCreate, Presence, PresenceCreate, LogAPIExterne, StatistiquesPresence
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_role
)
from utils import (
    generate_matricule_enseignant, generate_ine, generate_code_etablissement,
    calculate_moyenne, get_appreciation, serialize_datetime
)
from mapping_provinces import get_province_administrative, PROVINCES_ADMINISTRATIVES

# Configuration
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
users_collection = db.users
provinces_collection = db.provinces
sous_divisions_collection = db.sous_divisions
etablissements_collection = db.etablissements
enseignants_collection = db.enseignants
eleves_collection = db.eleves
classes_collection = db.classes
notes_collection = db.notes
bulletins_collection = db.bulletins
audit_logs_collection = db.audit_logs

# Create the main app with enhanced OpenAPI documentation
app = FastAPI(
    title="Édu-Connect API",
    description="""
    ## Plateforme Éducative Nationale - République Démocratique du Congo
    
    API complète pour la gestion du **Système Intégré de Gestion de l'Éducation (SIGE)** de la RDC.
    
    ### 🎯 Modules disponibles
    
    - **📄 GED** : Gestion Électronique des Documents avec circuits de validation hiérarchiques
    - **👨‍🏫 SIRH** : Système d'Information des Ressources Humaines (enseignants, mutations, promotions)
    - **👨‍🎓 Scolarité** : Gestion des élèves, classes, notes, bulletins
    - **🏫 Établissements** : Gestion des écoles (primaire, collèges, lycées)
    - **🔍 DINACOPE** : Contrôles, viabilité, détection de fraudes
    - **📊 Statistiques** : Tableaux de bord et analyses
    - **🗺️ Provinces** : Organisation territoriale administrative
    - **📋 Rapports** : Génération de rapports trimestriels
    - **🔌 APIs Externes** : Intégration avec systèmes tiers
    - **🔐 API Keys** : Gestion des clés d'authentification pour développeurs externes
    
    ### 🔐 Authentification
    
    Deux méthodes d'authentification disponibles :
    
    1. **JWT Token (utilisateurs internes)** :
       - Connectez-vous via `/api/auth/login`
       - Utilisez le token dans le header : `Authorization: Bearer <token>`
    
    2. **API Key (développeurs externes)** :
       - Générez une clé via le Dashboard Admin
       - Utilisez la clé dans le header : `X-API-Key: educon_...`
    
    ### 📚 Documentation
    
    - **Swagger UI** : Interface interactive (cette page)
    - **ReDoc** : Documentation détaillée → `/api/redoc`
    - **Schéma OpenAPI** : Format JSON → `/api/openapi.json`
    
    ### 🌐 Environnement
    
    - **Version** : 2.0.0
    - **Ministère** : Éducation Nationale et Nouvelle Citoyenneté (MINEPST)
    - **Organisation** : 51 services sur 5 niveaux hiérarchiques
    
    ---
    
    **Contact** : support@educonnect.gouv.cd
    """,
    version="2.0.0",
    contact={
        "name": "Support Technique Édu-Connect",
        "email": "support@educonnect.gouv.cd"
    },
    license_info={
        "name": "Gouvernement de la RDC",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# HELPER FUNCTIONS
# ============================================

async def log_action(user_id: str, action: str, entity_type: str, entity_id: str = None, details: dict = None):
    """Enregistre une action dans le journal d'audit"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await audit_logs_collection.insert_one(doc)


# ============================================
# AUTH ROUTES
# ============================================

@api_router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Inscription d'un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Créer l'utilisateur
    user = User(
        email=user_data.email,
        nom=user_data.nom,
        prenom=user_data.prenom,
        role=user_data.role,
        hashed_password=get_password_hash(user_data.password),
        province_id=user_data.province_id,
        sous_division_id=user_data.sous_division_id,
        etablissement_id=user_data.etablissement_id
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await users_collection.insert_one(doc)
    
    # Log
    await log_action(user.id, "CREATE", "User", user.id)
    
    return user


@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    """Connexion d'un utilisateur (email ou téléphone)"""
    # Trouver l'utilisateur par email OU par téléphone
    user_doc = await users_collection.find_one({
        "$or": [
            {"email": credentials.email},
            {"telephone": credentials.email}  # Le champ "email" du formulaire peut contenir le téléphone
        ]
    })
    
    if not user_doc or not verify_password(credentials.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/téléphone ou mot de passe incorrect"
        )
    
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Gestion des comptes éphémères (démonstration)
    if user_doc.get("is_ephemeral"):
        maintenant = datetime.now(timezone.utc)
        
        if user_doc.get("expires_at"):
            # Vérifier si le compte a expiré
            expires = user_doc["expires_at"]
            if isinstance(expires, str):
                expires = datetime.fromisoformat(expires)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if maintenant > expires:
                # Désactiver le compte expiré
                await users_collection.update_one(
                    {"id": user_doc["id"]},
                    {"$set": {"is_active": False}}
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Ce compte de démonstration a expiré (validité 24h après première connexion)"
                )
        elif user_doc.get("first_login_at") is None:
            # Première connexion : activer le compte pour 24h
            expires_at = maintenant + timedelta(hours=24)
            await users_collection.update_one(
                {"id": user_doc["id"]},
                {"$set": {
                    "first_login_at": maintenant.isoformat(),
                    "expires_at": expires_at.isoformat()
                }}
            )
    
    # Créer le token avec les nouvelles données
    token_data = {
        "sub": user_doc["id"],
        "nom": user_doc["nom"],
        "prenom": user_doc["prenom"],
        "telephone": user_doc.get("telephone"),
    }
    
    # Ajouter email et role s'ils existent (legacy)
    if user_doc.get("email"):
        token_data["email"] = user_doc["email"]
    if user_doc.get("role"):
        token_data["role"] = user_doc["role"]
    
    access_token = create_access_token(data=token_data)
    
    # Configurer le cookie httpOnly sécurisé
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Pas accessible via JavaScript
        secure=True,    # HTTPS uniquement
        samesite="lax", # Protection CSRF
        max_age=60 * 60 * 24 * 30  # 30 jours
    )
    
    # Préparer les données utilisateur (sans le mot de passe)
    user_data = {k: v for k, v in user_doc.items() if k != "hashed_password" and k != "_id"}
    
    # Log
    await log_action(user_doc["id"], "LOGIN", "User", user_doc["id"])
    
    # Retourner aussi le token pour compatibilité (sera supprimé plus tard du frontend)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@api_router.post("/auth/logout")
async def logout(response: Response):
    """Déconnexion - supprime le cookie httpOnly"""
    response.delete_cookie(key="access_token")
    return {"message": "Déconnexion réussie"}



@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    user_doc = await users_collection.find_one({"id": current_user["sub"]}, {"_id": 0, "hashed_password": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user_doc


# ============================================
# PROVINCES ROUTES
# ============================================

@api_router.post("/provinces", response_model=Province, status_code=status.HTTP_201_CREATED)
async def create_province(province_data: ProvinceCreate, current_user: dict = Depends(get_current_user)):
    """Créer une nouvelle province (Admin seulement)"""
    # Vérifier le code unique
    existing = await provinces_collection.find_one({"code": province_data.code})
    if existing:
        raise HTTPException(status_code=400, detail="Ce code province existe déjà")
    
    province = Province(**province_data.model_dump())
    doc = province.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await provinces_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Province", province.id)
    
    return province


@api_router.get("/provinces", response_model=List[Province])
async def get_provinces(current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les provinces"""
    provinces = await provinces_collection.find({}, {"_id": 0}).to_list(1000)
    return provinces


@api_router.get("/provinces/{province_id}", response_model=Province)
async def get_province(province_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer une province par ID"""
    province = await provinces_collection.find_one({"id": province_id}, {"_id": 0})
    if not province:
        raise HTTPException(status_code=404, detail="Province non trouvée")
    return province


# ============================================
# SOUS-DIVISIONS ROUTES
# ============================================

@api_router.post("/sous-divisions", response_model=SousDivision, status_code=status.HTTP_201_CREATED)
async def create_sous_division(data: SousDivisionCreate, current_user: dict = Depends(get_current_user)):
    """Créer une nouvelle sous-division"""
    sous_div = SousDivision(**data.model_dump())
    doc = sous_div.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await sous_divisions_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "SousDivision", sous_div.id)
    
    return sous_div


@api_router.get("/sous-divisions", response_model=List[SousDivision])
async def get_sous_divisions(province_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les sous-divisions (optionnellement filtrées par province)"""
    query = {}
    if province_id:
        query["province_id"] = province_id
    
    sous_divs = await sous_divisions_collection.find(query, {"_id": 0}).to_list(1000)
    return sous_divs


# ============================================
# ÉTABLISSEMENTS ROUTES
# ============================================

@api_router.post("/etablissements", response_model=Etablissement, status_code=status.HTTP_201_CREATED)
async def create_etablissement(data: EtablissementCreate, current_user: dict = Depends(get_current_user)):
    """Créer un nouvel établissement"""
    # Récupérer le code de la province
    province = await provinces_collection.find_one({"id": data.province_id})
    if not province:
        raise HTTPException(status_code=404, detail="Province non trouvée")
    
    # Générer le code établissement
    code_etab = generate_code_etablissement(etablissements_collection, province["code"])
    
    etablissement = Etablissement(
        **data.model_dump(),
        code_etablissement=code_etab
    )
    
    doc = etablissement.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    # Conversion synchrone pour insert_one
    result = await etablissements_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Etablissement", etablissement.id)
    
    return etablissement


@api_router.get("/etablissements", response_model=List[Etablissement])
async def get_etablissements(
    province_id: Optional[str] = None,
    sous_division_id: Optional[str] = None,
    type: Optional[TypeEtablissement] = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les établissements (avec filtres optionnels)"""
    query = {}
    if province_id:
        query["province_id"] = province_id
    if sous_division_id:
        query["sous_division_id"] = sous_division_id
    if type:
        query["type"] = type
    
    etablissements = await etablissements_collection.find(query, {"_id": 0}).to_list(1000)
    return etablissements


@api_router.get("/etablissements/{etablissement_id}", response_model=Etablissement)
async def get_etablissement(etablissement_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un établissement par ID"""
    etablissement = await etablissements_collection.find_one({"id": etablissement_id}, {"_id": 0})
    if not etablissement:
        raise HTTPException(status_code=404, detail="Établissement non trouvé")
    return etablissement


# ============================================
# ENSEIGNANTS ROUTES
# ============================================

@api_router.post("/enseignants", response_model=Enseignant, status_code=status.HTTP_201_CREATED)
async def create_enseignant(data: EnseignantCreate, current_user: dict = Depends(get_current_user)):
    """Créer un profil enseignant"""
    # Vérifier que l'utilisateur existe
    user = await users_collection.find_one({"id": data.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Générer le matricule
    matricule = generate_matricule_enseignant(enseignants_collection)
    
    enseignant = Enseignant(
        **data.model_dump(),
        matricule=matricule
    )
    
    doc = enseignant.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await enseignants_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Enseignant", enseignant.id)
    
    return enseignant


@api_router.get("/enseignants", response_model=List[Enseignant])
async def get_enseignants(
    etablissement_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer tous les enseignants"""
    query = {}
    if etablissement_id:
        query["etablissement_id"] = etablissement_id
    
    enseignants = await enseignants_collection.find(query, {"_id": 0}).to_list(1000)
    return enseignants


@api_router.get("/enseignants/{enseignant_id}", response_model=Enseignant)
async def get_enseignant(enseignant_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un enseignant par ID"""
    enseignant = await enseignants_collection.find_one({"id": enseignant_id}, {"_id": 0})
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant non trouvé")
    return enseignant


@api_router.get("/enseignants/by-user/{user_id}", response_model=Enseignant)
async def get_enseignant_by_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un enseignant par user_id"""
    enseignant = await enseignants_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not enseignant:
        raise HTTPException(status_code=404, detail="Profil enseignant non trouvé")
    return enseignant


# ============================================
# ÉLÈVES ROUTES
# ============================================

@api_router.post("/eleves", response_model=Eleve, status_code=status.HTTP_201_CREATED)
async def create_eleve(data: EleveCreate, current_user: dict = Depends(get_current_user)):
    """Créer un profil élève"""
    # Vérifier que l'utilisateur existe
    user = await users_collection.find_one({"id": data.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Générer l'INE
    ine = generate_ine(eleves_collection)
    
    eleve = Eleve(
        **data.model_dump(),
        ine=ine
    )
    
    doc = eleve.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await eleves_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Eleve", eleve.id)
    
    return eleve


@api_router.get("/eleves")
async def get_eleves(
    etablissement_id: Optional[str] = None,
    classe_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer tous les élèves avec pagination et informations utilisateur
    
    Args:
        etablissement_id: Filtrer par établissement
        classe_id: Filtrer par classe
        page: Numéro de page (commence à 1)
        page_size: Nombre d'élèves par page (max 500)
    """
    query = {}
    if etablissement_id:
        query["etablissement_id"] = etablissement_id
    if classe_id:
        query["classe_id"] = classe_id
    
    # Limiter page_size à 500 maximum
    page_size = min(page_size, 500)
    skip = (page - 1) * page_size
    
    eleves = await eleves_collection.find(query, {"_id": 0}).skip(skip).limit(page_size).to_list(page_size)
    
    # Si les élèves n'ont pas de nom_complet, essayer de récupérer depuis users
    for eleve in eleves:
        if not eleve.get("nom_complet"):
            user = await users_collection.find_one({"id": eleve.get("user_id")}, {"_id": 0, "hashed_password": 0})
            if user:
                eleve["nom"] = user.get("nom", "")
                eleve["prenom"] = user.get("prenom", "")
                eleve["postnom"] = user.get("postnom", "")
                eleve["nom_complet"] = f"{user.get('prenom', '')} {user.get('nom', '')} {user.get('postnom', '')}".strip()
    
    return eleves


@api_router.get("/eleves/{eleve_id}", response_model=Eleve)
async def get_eleve(eleve_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un élève par ID"""
    eleve = await eleves_collection.find_one({"id": eleve_id}, {"_id": 0})
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève non trouvé")
    return eleve


@api_router.get("/eleves/by-user/{user_id}", response_model=Eleve)
async def get_eleve_by_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un élève par user_id"""
    eleve = await eleves_collection.find_one({"user_id": user_id}, {"_id": 0})
    if not eleve:
        raise HTTPException(status_code=404, detail="Profil élève non trouvé")
    return eleve


# ============================================
# CLASSES ROUTES
# ============================================

@api_router.post("/classes", response_model=Classe, status_code=status.HTTP_201_CREATED)
async def create_classe(data: ClasseCreate, current_user: dict = Depends(get_current_user)):
    """Créer une nouvelle classe"""
    classe = Classe(**data.model_dump())
    doc = classe.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await classes_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Classe", classe.id)
    
    return classe


@api_router.get("/classes", response_model=List[Classe])
async def get_classes(
    etablissement_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer toutes les classes"""
    query = {}
    if etablissement_id:
        query["etablissement_id"] = etablissement_id
    
    classes = await classes_collection.find(query, {"_id": 0}).to_list(1000)
    return classes


@api_router.get("/classes/{classe_id}", response_model=Classe)
async def get_classe(classe_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer une classe par ID"""
    classe = await classes_collection.find_one({"id": classe_id}, {"_id": 0})
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    return classe


# ============================================
# NOTES ROUTES
# ============================================

@api_router.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(data: NoteCreate, current_user: dict = Depends(get_current_user)):
    """Créer une note"""
    note = Note(**data.model_dump())
    doc = note.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await notes_collection.insert_one(doc)
    await log_action(current_user["sub"], "CREATE", "Note", note.id)
    
    return note


@api_router.get("/notes", response_model=List[Note])
async def get_notes(
    eleve_id: Optional[str] = None,
    classe_id: Optional[str] = None,
    trimestre: Optional[Trimestre] = None,
    annee_scolaire: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les notes avec pagination
    
    Args:
        eleve_id: Filtrer par élève
        classe_id: Filtrer par classe
        trimestre: Filtrer par trimestre
        annee_scolaire: Filtrer par année scolaire
        page: Numéro de page (commence à 1)
        page_size: Nombre de notes par page (max 500)
    """
    query = {}
    if eleve_id:
        query["eleve_id"] = eleve_id
    if classe_id:
        query["classe_id"] = classe_id
    if trimestre:
        query["trimestre"] = trimestre
    if annee_scolaire:
        query["annee_scolaire"] = annee_scolaire
    
    # Limiter page_size à 500 maximum
    page_size = min(page_size, 500)
    skip = (page - 1) * page_size
    
    notes = await notes_collection.find(query, {"_id": 0}).skip(skip).limit(page_size).to_list(page_size)
    return notes


@api_router.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, note_value: float, current_user: dict = Depends(get_current_user)):
    """Modifier une note"""
    result = await notes_collection.update_one(
        {"id": note_id},
        {"$set": {"note": note_value}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    
    await log_action(current_user["sub"], "UPDATE", "Note", note_id)
    
    note = await notes_collection.find_one({"id": note_id}, {"_id": 0})
    return note


# ============================================
# BULLETINS ROUTES
# ============================================

@api_router.post("/bulletins/generate", response_model=Bulletin, status_code=status.HTTP_201_CREATED)
async def generate_bulletin(data: BulletinCreate, current_user: dict = Depends(get_current_user)):
    """Générer un bulletin pour un élève"""
    # Récupérer toutes les notes de l'élève pour ce trimestre
    notes = await notes_collection.find({
        "eleve_id": data.eleve_id,
        "classe_id": data.classe_id,
        "trimestre": data.trimestre,
        "annee_scolaire": data.annee_scolaire
    }, {"_id": 0}).to_list(1000)
    
    if not notes:
        raise HTTPException(status_code=404, detail="Aucune note trouvée pour ce trimestre")
    
    # Calculer la moyenne générale
    notes_avec_coef = [{"note": n["note"], "coefficient": n["coefficient"]} for n in notes]
    moyenne_generale = calculate_moyenne(notes_avec_coef)
    
    # Préparer les détails des notes
    notes_detail = []
    for n in notes:
        notes_detail.append({
            "matiere": n["matiere"],
            "note": n["note"],
            "coefficient": n["coefficient"]
        })
    
    # Calculer le rang (optionnel pour le MVP)
    # Compter l'effectif de la classe
    effectif = await eleves_collection.count_documents({"classe_id": data.classe_id})
    
    # Créer le bulletin
    bulletin = Bulletin(
        eleve_id=data.eleve_id,
        classe_id=data.classe_id,
        trimestre=data.trimestre,
        annee_scolaire=data.annee_scolaire,
        moyenne_generale=moyenne_generale,
        notes_detail=notes_detail,
        effectif_classe=effectif,
        appreciation_generale=get_appreciation(moyenne_generale)
    )
    
    doc = bulletin.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    # Vérifier si un bulletin existe déjà
    existing = await bulletins_collection.find_one({
        "eleve_id": data.eleve_id,
        "trimestre": data.trimestre,
        "annee_scolaire": data.annee_scolaire
    })
    
    if existing:
        # Mettre à jour
        await bulletins_collection.update_one(
            {"id": existing["id"]},
            {"$set": doc}
        )
        bulletin.id = existing["id"]
    else:
        # Créer nouveau
        await bulletins_collection.insert_one(doc)
    
    await log_action(current_user["sub"], "GENERATE", "Bulletin", bulletin.id)
    
    return bulletin


@api_router.get("/bulletins", response_model=List[Bulletin])
async def get_bulletins(
    eleve_id: Optional[str] = None,
    classe_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Récupérer les bulletins"""
    query = {}
    if eleve_id:
        query["eleve_id"] = eleve_id
    if classe_id:
        query["classe_id"] = classe_id
    
    bulletins = await bulletins_collection.find(query, {"_id": 0}).to_list(1000)
    return bulletins


@api_router.get("/bulletins/{bulletin_id}", response_model=Bulletin)
async def get_bulletin(bulletin_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un bulletin par ID"""
    bulletin = await bulletins_collection.find_one({"id": bulletin_id}, {"_id": 0})
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin non trouvé")
    return bulletin


# ============================================
# STATISTIQUES ROUTES
# ============================================

@api_router.get("/stats/global", response_model=Stats)
async def get_global_stats(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques globales"""
    total_etablissements = await etablissements_collection.count_documents({})
    total_enseignants = await enseignants_collection.count_documents({})
    total_eleves = await eleves_collection.count_documents({})
    total_classes = await classes_collection.count_documents({})
    
    # Élèves primaire vs secondaire
    total_eleves_primaire = await eleves_collection.count_documents({
        "niveau": {"$in": ["1ere_annee_primaire", "2eme_annee_primaire", "3eme_annee_primaire", 
                           "4eme_annee_primaire", "5eme_annee_primaire", "6eme_annee_primaire"]}
    })
    total_eleves_secondaire = total_eleves - total_eleves_primaire
    
    # Répartition par province
    pipeline_provinces = [
        {
            "$group": {
                "_id": "$province_id",
                "count": {"$sum": 1}
            }
        }
    ]
    
    repartition_provinces_raw = await etablissements_collection.aggregate(pipeline_provinces).to_list(100)
    repartition_par_province = {}
    
    for item in repartition_provinces_raw:
        province_id = item["_id"]
        province = await provinces_collection.find_one({"id": province_id})
        if province:
            repartition_par_province[province["nom"]] = item["count"]
    
    # Répartition par niveau
    pipeline_niveaux = [
        {
            "$group": {
                "_id": "$niveau",
                "count": {"$sum": 1}
            }
        }
    ]
    
    repartition_niveaux_raw = await eleves_collection.aggregate(pipeline_niveaux).to_list(100)
    repartition_par_niveau = {item["_id"]: item["count"] for item in repartition_niveaux_raw}
    
    return Stats(
        total_etablissements=total_etablissements,
        total_enseignants=total_enseignants,
        total_eleves=total_eleves,
        total_eleves_primaire=total_eleves_primaire,
        total_eleves_secondaire=total_eleves_secondaire,
        total_classes=total_classes,
        repartition_par_province=repartition_par_province,
        repartition_par_niveau=repartition_par_niveau
    )


@api_router.get("/stats/sexe")
async def get_stats_sexe(current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques par sexe"""
    # Répartition globale par sexe - ÉLÈVES
    total_masculin = await eleves_collection.count_documents({"sexe": "masculin"})
    total_feminin = await eleves_collection.count_documents({"sexe": "feminin"})
    
    # Répartition par sexe et par niveau - ÉLÈVES
    pipeline_sexe_niveau = [
        {
            "$group": {
                "_id": {"niveau": "$niveau", "sexe": "$sexe"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    sexe_niveau_raw = await eleves_collection.aggregate(pipeline_sexe_niveau).to_list(100)
    repartition_sexe_niveau = {}
    
    for item in sexe_niveau_raw:
        niveau = item["_id"]["niveau"]
        sexe = item["_id"]["sexe"]
        if niveau not in repartition_sexe_niveau:
            repartition_sexe_niveau[niveau] = {"masculin": 0, "feminin": 0}
        repartition_sexe_niveau[niveau][sexe] = item["count"]
    
    # Répartition par sexe et par province - ÉLÈVES
    pipeline_sexe_province = [
        {
            "$group": {
                "_id": {"etablissement_id": "$etablissement_id", "sexe": "$sexe"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    sexe_province_raw = await eleves_collection.aggregate(pipeline_sexe_province).to_list(1000)
    
    # Regrouper par province ADMINISTRATIVE
    province_sexe = {}
    for item in sexe_province_raw:
        etab_id = item["_id"]["etablissement_id"]
        sexe = item["_id"]["sexe"]
        count = item["count"]
        
        # Trouver la province de l'établissement
        etab = await etablissements_collection.find_one({"id": etab_id})
        if etab:
            province = await provinces_collection.find_one({"id": etab["province_id"]})
            if province:
                province_educationnelle = province["nom"]
                # Convertir en province administrative
                province_admin = get_province_administrative(province_educationnelle)
                if province_admin not in province_sexe:
                    province_sexe[province_admin] = {"masculin": 0, "feminin": 0}
                province_sexe[province_admin][sexe] += count
    
    # ENSEIGNANTS - Statistiques par sexe
    total_enseignants_masculin = await users_collection.count_documents({
        "role": "enseignant",
        "sexe": "masculin"
    })
    total_enseignants_feminin = await users_collection.count_documents({
        "role": "enseignant",
        "sexe": "feminin"
    })
    
    # Enseignants par province ADMINISTRATIVE
    enseignants_par_province = {}
    enseignants_list = await users_collection.find(
        {"role": "enseignant"},
        {"_id": 0, "etablissement_id": 1, "sexe": 1}
    ).to_list(1000)
    
    for ens in enseignants_list:
        if ens.get("etablissement_id") and ens.get("sexe"):
            etab = await etablissements_collection.find_one({"id": ens["etablissement_id"]})
            if etab:
                province = await provinces_collection.find_one({"id": etab["province_id"]})
                if province:
                    province_educationnelle = province["nom"]
                    # Convertir en province administrative
                    province_admin = get_province_administrative(province_educationnelle)
                    if province_admin not in enseignants_par_province:
                        enseignants_par_province[province_admin] = {"masculin": 0, "feminin": 0}
                    enseignants_par_province[province_admin][ens["sexe"]] += 1
    
    # DIRECTEURS - Statistiques globales par sexe
    total_directeurs_masculin = await users_collection.count_documents({
        "role": {"$in": ["directeur_ecole", "chef_etablissement"]},
        "sexe": "masculin"
    })
    total_directeurs_feminin = await users_collection.count_documents({
        "role": {"$in": ["directeur_ecole", "chef_etablissement"]},
        "sexe": "feminin"
    })
    
    return {
        "eleves": {
            "global": {
                "masculin": total_masculin,
                "feminin": total_feminin,
                "total": total_masculin + total_feminin
            },
            "par_niveau": repartition_sexe_niveau,
            "par_province": province_sexe
        },
        "enseignants": {
            "global": {
                "masculin": total_enseignants_masculin,
                "feminin": total_enseignants_feminin,
                "total": total_enseignants_masculin + total_enseignants_feminin
            },
            "par_province": enseignants_par_province
        },
        "directeurs": {
            "global": {
                "masculin": total_directeurs_masculin,
                "feminin": total_directeurs_feminin,
                "total": total_directeurs_masculin + total_directeurs_feminin
            }
        }
    }


@api_router.get("/stats/province/{province_id}")
async def get_province_stats(province_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les statistiques d'une province"""
    total_etablissements = await etablissements_collection.count_documents({"province_id": province_id})
    
    # Récupérer les IDs des établissements de la province
    etablissements = await etablissements_collection.find({"province_id": province_id}, {"id": 1, "_id": 0}).to_list(1000)
    etablissement_ids = [e["id"] for e in etablissements]
    
    total_enseignants = await enseignants_collection.count_documents({"etablissement_id": {"$in": etablissement_ids}})
    total_eleves = await eleves_collection.count_documents({"etablissement_id": {"$in": etablissement_ids}})
    
    return {
        "province_id": province_id,
        "total_etablissements": total_etablissements,
        "total_enseignants": total_enseignants,
        "total_eleves": total_eleves
    }


# ============================================
# USERS MANAGEMENT ROUTES
# ============================================

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(
    role: Optional[UserRole] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer tous les utilisateurs
    Accessible à tous les utilisateurs connectés (pour recherche dans documents/conversations)
    """
    query = {}
    if role:
        query["role"] = role
    
    users = await users_collection.find(query, {"_id": 0, "hashed_password": 0}).to_list(1000)
    return users


@api_router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer un utilisateur par ID"""
    user = await users_collection.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


# ============================================
# ROOT & HEALTH CHECK
# ============================================

@api_router.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API du Réseau Intégré de l'Éducation (RIE)",
        "version": "1.0.0",
        "status": "active"
    }


@api_router.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        # Tester la connexion MongoDB
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service indisponible")


# ============================================
# USER PROFILE UPDATE ROUTES
# ============================================

@api_router.put("/users/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Mettre à jour le profil utilisateur
    L'utilisateur ne peut modifier que son propre profil
    """
    # Vérifier que l'utilisateur modifie bien son propre profil
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez modifier que votre propre profil"
        )
    
    # Champs autorisés pour la mise à jour
    allowed_fields = ["nom", "prenom", "email", "telephone", "service_id", "poste"]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields and v}
    
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Aucune donnée valide à mettre à jour"
        )
    
    # Vérifier si l'email existe déjà (si modifié)
    if "email" in update_data:
        existing_user = await users_collection.find_one(
            {"email": update_data["email"], "id": {"$ne": user_id}},
            {"_id": 0}
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Cet email est déjà utilisé par un autre utilisateur"
            )
    
    # Vérifier si le téléphone existe déjà (si modifié)
    if "telephone" in update_data:
        existing_user = await users_collection.find_one(
            {"telephone": update_data["telephone"], "id": {"$ne": user_id}},
            {"_id": 0}
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Ce numéro de téléphone est déjà utilisé par un autre utilisateur"
            )
    
    # Ajouter la date de mise à jour
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Mettre à jour l'utilisateur
    result = await users_collection.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Enregistrer l'action dans les logs
    await log_action(user_id, "UPDATE", "User Profile", user_id)
    
    # Récupérer et retourner l'utilisateur mis à jour
    updated_user = await users_collection.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    return updated_user


@api_router.put("/users/{user_id}/password")
async def change_user_password(
    user_id: str,
    password_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Changer le mot de passe utilisateur
    L'utilisateur ne peut changer que son propre mot de passe
    """
    # Vérifier que l'utilisateur modifie bien son propre mot de passe
    if current_user["sub"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez modifier que votre propre mot de passe"
        )
    
    # Valider les données
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Mot de passe actuel et nouveau mot de passe requis"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Le nouveau mot de passe doit contenir au moins 8 caractères"
        )
    
    # Récupérer l'utilisateur
    user = await users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier le mot de passe actuel
    if not verify_password(current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=400,
            detail="Mot de passe actuel incorrect"
        )
    
    # Hasher le nouveau mot de passe
    new_hashed_password = get_password_hash(new_password)
    
    # Mettre à jour le mot de passe
    result = await users_collection.update_one(
        {"id": user_id},
        {
            "$set": {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Enregistrer l'action dans les logs
    await log_action(user_id, "UPDATE", "User Password", user_id)
    
    return {"message": "Mot de passe modifié avec succès"}


# Include the router in the main app
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure le router GED
from routes_ged import router as ged_router
app.include_router(ged_router)

# Inclure le router Listes
from routes_listes import router as listes_router

# Inclure le router Plan de Classement
from routes_plan_classement import router as plan_classement_router
app.include_router(plan_classement_router)

# Inclure le router Entités Externes
from routes_entites_externes import router as entites_externes_router
app.include_router(entites_externes_router)

# Inclure le router Preview
from routes_preview import router as preview_router
app.include_router(preview_router)

# Inclure le router Recherche Avancée
from routes_recherche import router as recherche_router
app.include_router(recherche_router)

# Inclure le router Contexte (Double Zone)
from routes_contexte import router as contexte_router
app.include_router(contexte_router)





app.include_router(listes_router)


# Inclure le router Rapports
from routes_rapports import router as rapports_router
app.include_router(rapports_router)

# Inclure le router SIRH
from routes_sirh import router as sirh_router
app.include_router(sirh_router)

# Inclure le router DINACOPE Avancé
from routes_dinacope import router as dinacope_router
app.include_router(dinacope_router)

# Inclure le router APIs Externes (Module 3)
from routes_externe import router as externe_router
app.include_router(externe_router)

# Inclure le router Tests
from routes_tests import router as tests_router, init_routes as init_tests_routes
init_tests_routes(db)
app.include_router(tests_router)

# Inclure le router Services (Organigramme)
from routes_services import router as services_router
app.include_router(services_router)

# Inclure le router Inscription
from routes_inscription import router as inscription_router
app.include_router(inscription_router)

# Inclure le router API Keys (Gestion des clés pour développeurs externes)
from routes_api_keys import router as api_keys_router
app.include_router(api_keys_router)

# Inclure le router Exports (PDF/Excel)
from routes_exports import router as exports_router
app.include_router(exports_router)

# Inclure le router Chat/Messagerie
from routes_chat import router as chat_router
app.include_router(chat_router)

# Inclure le router Demo (utilisateurs éphémères)
from routes_demo import router as demo_router
app.include_router(demo_router)


# Configurer le scheduler pour les rappels automatiques
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_scheduler():
    """Démarrer le scheduler pour les tâches périodiques"""
    try:
        from rappels_automatiques import verifier_documents_en_attente
        from generer_rapport_trimestriel import generer_rapport_trimestriel
        
        # Vérifier les documents en attente toutes les 3 heures
        scheduler.add_job(
            verifier_documents_en_attente,
            'interval',
            hours=3,
            id='rappels_documents',
            replace_existing=True
        )
        
        # Générer le rapport trimestriel tous les 3 mois (le 1er de chaque trimestre à 00h00)
        # Trimestres: 1er janvier, 1er avril, 1er juillet, 1er octobre
        scheduler.add_job(
            generer_rapport_trimestriel,
            'cron',
            month='1,4,7,10',  # Janvier, Avril, Juillet, Octobre
            day=1,
            hour=0,
            minute=0,
            id='rapport_trimestriel',
            replace_existing=True
        )
        
        scheduler.start()
        print("✅ Scheduler démarré:")
        print("   - Rappels automatiques: toutes les 3h")
        print("   - Rapports trimestriels: 1er de chaque trimestre à 00h00")
    except Exception as e:
        print(f"⚠️ Erreur démarrage scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        if scheduler.running:
            scheduler.shutdown()
    except:
        pass
    client.close()

