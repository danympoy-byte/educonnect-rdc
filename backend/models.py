from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
import uuid


# ============================================
# ENUMS - Rôles et Types
# ============================================

class UserRole(str, Enum):
    MINISTRE = "ministre"
    SECRETAIRE_GENERAL = "secretaire_general"
    DPE = "directeur_provincial"
    CHEF_SOUS_DIVISION = "chef_sous_division"
    CHEF_ETABLISSEMENT = "chef_etablissement"
    DIRECTEUR_ECOLE = "directeur_ecole"
    CPE = "conseiller_principal_education"
    ENSEIGNANT = "enseignant"
    ELEVE_PRIMAIRE = "eleve_primaire"
    ELEVE_SECONDAIRE = "eleve_secondaire"
    PARENT = "parent"
    INSPECTEUR = "inspecteur_pedagogique"
    AGENT_DINACOPE = "agent_dinacope"
    PERSONNEL_ADMIN = "personnel_administratif"
    INFIRMIER = "infirmier_scolaire"
    ADMIN_TECH = "administrateur_technique"


class TypeEtablissement(str, Enum):
    ECOLE_PRIMAIRE = "ecole_primaire"
    COLLEGE = "college"
    LYCEE = "lycee"


class NiveauScolaire(str, Enum):
    # Primaire (6 ans)
    PRIMAIRE_1 = "1ere_annee_primaire"
    PRIMAIRE_2 = "2eme_annee_primaire"
    PRIMAIRE_3 = "3eme_annee_primaire"
    PRIMAIRE_4 = "4eme_annee_primaire"
    PRIMAIRE_5 = "5eme_annee_primaire"
    PRIMAIRE_6 = "6eme_annee_primaire"
    # Secondaire (6 ans)
    SECONDAIRE_1 = "1ere_annee_secondaire"
    SECONDAIRE_2 = "2eme_annee_secondaire"
    SECONDAIRE_3 = "3eme_annee_secondaire"
    SECONDAIRE_4 = "4eme_annee_secondaire"
    SECONDAIRE_5 = "5eme_annee_secondaire"
    SECONDAIRE_6 = "6eme_annee_secondaire"


class Sexe(str, Enum):
    MASCULIN = "masculin"
    FEMININ = "feminin"


class Trimestre(str, Enum):
    T1 = "trimestre_1"
    T2 = "trimestre_2"
    T3 = "trimestre_3"


class EtatCivil(str, Enum):
    CELIBATAIRE = "celibataire"
    MARIE = "marie"
    DIVORCE = "divorce"
    VEUF = "veuf"


class NiveauService(str, Enum):
    """Niveau hiérarchique dans l'organigramme"""
    NIVEAU_1 = "niveau_1"  # Ministre
    NIVEAU_2 = "niveau_2"  # Cabinet, Inspections, Secrétariat Général
    NIVEAU_3 = "niveau_3"  # Directions Générales
    NIVEAU_4 = "niveau_4"  # Directions/Sous-directions
    NIVEAU_5 = "niveau_5"  # Services


class PrioriteDocument(str, Enum):
    """Niveau de priorité pour le traitement des documents"""
    CRITIQUE = "priorite_1"  # Urgent - Immédiat
    ELEVEE = "priorite_2"    # Important - Échéance proche
    NORMALE = "priorite_3"   # Nécessaire - Non immédiat
    FAIBLE = "priorite_4"    # Peu important


# ============================================
# MODELS - Base
# ============================================

class Province(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    code: str  # Code unique de la province
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProvinceCreate(BaseModel):
    nom: str
    code: str


class SousDivision(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    code: str
    province_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SousDivisionCreate(BaseModel):
    nom: str
    code: str
    province_id: str



# ============================================
# MODELS - Services et Organigramme
# ============================================

class Service(BaseModel):
    """
    Représente un service dans l'organigramme du ministère.
    Hiérarchie: Niveau 1 (Ministre) → Niveau 2 (Cabinet, SG) → Niveau 3 (DG) → Niveau 4 (Directions) → Niveau 5 (Services)
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str  # Ex: "Direction Générale de l'Administration"
    code: str  # Ex: "DGA", "DGA_FIN", "CAB_MIN"
    niveau: NiveauService  # Niveau hiérarchique (1 à 5)
    parent_id: Optional[str] = None  # ID du service parent (None pour le Ministre)
    responsable_id: Optional[str] = None  # ID de l'utilisateur responsable du service
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceCreate(BaseModel):
    nom: str
    code: str
    niveau: NiveauService
    parent_id: Optional[str] = None
    description: Optional[str] = None


class UserServiceProfile(BaseModel):
    """
    Représente l'appartenance d'un utilisateur à un service.
    Un utilisateur peut avoir plusieurs profils (un par service).
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    service_id: str
    service_nom: str  # Dénormalisé pour performance
    service_code: str
    poste: str  # Intitulé du poste dans ce service
    est_responsable: bool = False  # True si c'est le responsable du service
    date_affectation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Diplome(BaseModel):
    """Diplôme d'un utilisateur"""
    model_config = ConfigDict(extra="ignore")
    
    intitule: str  # Ex: "Licence en Sciences de l'Éducation"
    etablissement: str
    annee_obtention: Optional[int] = None
    pays: str = "RDC"


class ExperienceProfessionnelle(BaseModel):
    """Expérience professionnelle d'un utilisateur"""
    model_config = ConfigDict(extra="ignore")
    
    poste: str
    employeur: str
    date_debut: str  # Format: YYYY-MM
    date_fin: Optional[str] = None  # None si poste actuel
    description: Optional[str] = None


class CategorieEtablissement(str, Enum):
    PUBLIQUE = "publique"
    PRIVEE = "privee"


class Etablissement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    type: TypeEtablissement
    categorie: CategorieEtablissement  # Catégorie: publique ou privée
    code_etablissement: str  # Code unique auto-généré
    adresse: str
    province_id: str
    sous_division_id: str
    directeur_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EtablissementCreate(BaseModel):
    nom: str
    type: TypeEtablissement
    categorie: CategorieEtablissement
    adresse: str
    province_id: str
    sous_division_id: str


class User(BaseModel):
    """
    Utilisateur du système Édu-Connect.
    Système multi-profils: un utilisateur peut appartenir à plusieurs services.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Informations personnelles (Étape 1 inscription)
    nom: str
    postnom: Optional[str] = None  # Nom de famille complet
    prenom: str
    sexe: Sexe
    etat_civil: EtatCivil
    date_naissance: str  # Format: YYYY-MM-DD
    lieu_naissance: str
    
    # Contact et administratif
    telephone: str
    adresse: str
    email: Optional[str] = None  # Peut être ajouté plus tard (Étape 3)
    
    # Professionnel
    diplomes: List[Diplome] = []
    experiences: List[ExperienceProfessionnelle] = []
    
    # Services (multi-appartenance)
    service_profiles: List[UserServiceProfile] = []  # Liste des services dont il fait partie
    service_actif_id: Optional[str] = None  # Service sélectionné lors de la session en cours
    
    # Financier (peut être ajouté plus tard)
    numero_compte_bancaire: Optional[str] = None
    banque: Optional[str] = None
    
    # Profil
    photo_url: Optional[str] = None  # Peut être ajoutée plus tard (Étape 3)
    
    # Sécurité
    hashed_password: str
    is_active: bool = True
    profil_complete: bool = False  # True quand photo, email et compte bancaire sont renseignés
    
    # Legacy fields (pour compatibilité temporaire - à supprimer après migration)
    role: Optional[UserRole] = None
    province_id: Optional[str] = None
    sous_division_id: Optional[str] = None
    etablissement_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class UserCreateStep1(BaseModel):
    """Étape 1: Informations personnelles et professionnelles"""
    nom: str
    postnom: Optional[str] = None
    prenom: str
    sexe: Sexe
    etat_civil: EtatCivil
    date_naissance: str
    lieu_naissance: str
    telephone: str
    adresse: str
    password: str
    # Diplômes et expériences sous forme de JSON
    diplomes: List[dict] = []  # [{intitule, etablissement, annee_obtention, pays}]
    experiences: List[dict] = []  # [{poste, employeur, date_debut, date_fin, description}]


class UserCreateStep2(BaseModel):
    """Étape 2: Sélection du service"""
    user_id: str
    service_id: str
    poste: str  # Intitulé du poste dans le service


class UserCreateStep3(BaseModel):
    """Étape 3: Complétion du profil (optionnel initialement)"""
    user_id: str
    email: Optional[str] = None
    numero_compte_bancaire: Optional[str] = None
    banque: Optional[str] = None
    photo_url: Optional[str] = None



# Legacy UserCreate pour compatibilité avec l'ancien système (à supprimer après migration complète)
class UserCreate(BaseModel):
    """Ancien modèle UserCreate - DEPRECATED - Utiliser UserCreateStep1/2/3"""
    email: str
    nom: str
    prenom: str
    role: UserRole
    password: str
    sexe: Optional[Sexe] = None
    province_id: Optional[str] = None
    sous_division_id: Optional[str] = None
    etablissement_id: Optional[str] = None



class UserResponse(BaseModel):
    """
    Model pour les réponses API sans le mot de passe.
    Compatible avec le système multi-services d'Édu-Connect.
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str
    nom: str
    prenom: str
    postnom: Optional[str] = None
    sexe: Optional[Sexe] = None  # Optionnel pour les comptes admin
    etat_civil: Optional[EtatCivil] = None
    date_naissance: Optional[str] = None
    lieu_naissance: Optional[str] = None
    
    # Contact
    telephone: str
    adresse: Optional[str] = None
    email: Optional[str] = None  # Peut être None pour profils incomplets
    
    # Services (nouveau système)
    service_profiles: Optional[List[dict]] = []
    service_actif_id: Optional[str] = None
    
    # Financier
    numero_compte_bancaire: Optional[str] = None
    banque: Optional[str] = None
    
    # Professionnel
    diplomes: Optional[List[dict]] = []
    experiences: Optional[List[dict]] = []
    
    # Profil
    photo_url: Optional[str] = None
    is_active: bool = True
    profil_complete: bool = False
    
    # Legacy fields (compatibilité)
    role: Optional[UserRole] = None
    province_id: Optional[str] = None
    sous_division_id: Optional[str] = None
    etablissement_id: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class Enseignant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    matricule: str  # Matricule unique auto-généré (format: ENS-XXXXXX)
    etablissement_id: str
    matieres: List[str] = []  # Liste des matières enseignées
    est_professeur_principal: bool = False
    classe_principale_id: Optional[str] = None  # Si professeur principal
    
    # Grade professionnel
    grade: str = "mécanisé"  # stagiaire, mécanisé, qualifié, diplômé, licencié, etc.
    
    # Données DINACOPE (optionnelles)
    adresse_personnelle: str = ""
    telephone_personnel: str = ""
    email_personnel: str = ""
    etat_civil: str = "celibataire"
    nombre_enfants: int = 0
    conjoint_nom: str = ""
    banque: str = ""
    numero_compte: str = ""
    photo_url: Optional[str] = None
    
    # Dernière vérification DINACOPE
    derniere_verification_dinacope: Optional[str] = None
    derniere_verification_dinacope_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EnseignantCreate(BaseModel):
    user_id: str
    etablissement_id: str
    matieres: List[str] = []
    est_professeur_principal: bool = False
    classe_principale_id: Optional[str] = None


class Eleve(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    ine: str  # Identifiant National Élève (format: INE-XXXXXXXX)
    etablissement_id: str
    classe_id: Optional[str] = None
    niveau: NiveauScolaire
    sexe: Sexe  # Masculin ou Féminin
    date_naissance: str
    lieu_naissance: str
    parents_ids: List[str] = []  # Liste des IDs des parents/tuteurs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EleveCreate(BaseModel):
    user_id: str
    etablissement_id: str
    classe_id: Optional[str] = None
    niveau: NiveauScolaire
    sexe: Sexe
    date_naissance: str
    lieu_naissance: str
    parents_ids: List[str] = []


class Classe(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str  # Ex: "6ème A", "CM2 B"
    niveau: NiveauScolaire
    etablissement_id: str
    professeur_principal_id: Optional[str] = None
    annee_scolaire: str  # Ex: "2024-2025"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClasseCreate(BaseModel):
    nom: str
    niveau: NiveauScolaire
    etablissement_id: str
    professeur_principal_id: Optional[str] = None
    annee_scolaire: str


class Note(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eleve_id: str
    classe_id: str
    matiere: str
    note: float  # Note sur 20
    coefficient: float = 1.0
    trimestre: Trimestre
    annee_scolaire: str
    enseignant_id: str
    commentaire: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NoteCreate(BaseModel):
    eleve_id: str
    classe_id: str
    matiere: str
    note: float
    coefficient: float = 1.0
    trimestre: Trimestre
    annee_scolaire: str
    enseignant_id: str
    commentaire: Optional[str] = None


class Bulletin(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eleve_id: str
    classe_id: str
    trimestre: Trimestre
    annee_scolaire: str
    moyenne_generale: float
    notes_detail: List[dict] = []  # [{matiere, note, coefficient, moyenne_classe}]
    rang: Optional[int] = None
    effectif_classe: Optional[int] = None
    appreciation_generale: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BulletinCreate(BaseModel):
    eleve_id: str
    classe_id: str
    trimestre: Trimestre
    annee_scolaire: str


# ============================================
# MODELS - Logs et Audit
# ============================================

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type: str  # User, Eleve, Note, etc.
    entity_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogCreate(BaseModel):
    user_id: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None


# ============================================
# MODELS - Statistiques
# ============================================

class Stats(BaseModel):
    total_etablissements: int = 0
    total_enseignants: int = 0
    total_eleves: int = 0
    total_eleves_primaire: int = 0
    total_eleves_secondaire: int = 0
    total_classes: int = 0
    repartition_par_province: dict = {}
    repartition_par_niveau: dict = {}



# ============================================
# SYSTÈME GED - GESTION DOCUMENTAIRE
# ============================================

class StatutDocument(str, Enum):
    BROUILLON = "brouillon"
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    REJETE = "rejete"
    ARCHIVE = "archive"


class NiveauDiffusion(str, Enum):
    PRIVE = "prive"  # Entre créateur et destinataire uniquement
    SERVICE = "service"  # Tout le service peut voir
    TOUS = "tous"  # Tous les services


class ModeLivraison(str, Enum):
    EMAIL = "email"
    PHYSIQUE = "physique"
    CITOYEN = "citoyen"
    INTERNE = "interne"


class TypeAction(str, Enum):
    CREATION = "creation"
    CONSULTATION = "consultation"
    PRISE_EN_CHARGE = "prise_en_charge"
    ACCEPTATION = "acceptation"
    REJET = "rejet"
    TRANSMISSION = "transmission"
    DELEGATION = "delegation"  # Délégation de tâche à un autre utilisateur
    COMMENTAIRE = "commentaire"
    VALIDATION = "validation"
    SIGNATURE = "signature"
    MODIFICATION = "modification"
    SUPPRESSION = "suppression"
    BYPASS = "bypass"  # Dérogation d'une étape du circuit


class TypeTache(str, Enum):
    """Type de tâche attribuée à un utilisateur (conformité GED DRC)"""
    INFO = "info"  # Information - Lecture seule, pour information
    CLASS = "class"  # Classement - Classer le document dans le plan de classement
    ASOC = "asoc"  # Association - Associer le document à un dossier
    CF = "cf"  # Copie pour information - Copie sans action requise



class RoleCircuitValidation(str, Enum):
    """Rôle d'une personne dans le circuit de validation d'un document"""
    contributeur = "contributeur"  # Contribue au contenu du document
    visa_correction = "visa_correction"  # Visa de correction/relecture
    signature = "signature"  # Signature du document
    expedition = "expedition"  # Expédition après signature finale


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_reference: str  # Auto-généré : MIN/EDU/2025/001
    titre: str
    description: Optional[str] = None
    type_document: str  # administratif, rh, financier, pedagogique
    categorie: Optional[str] = None
    
    # Fichier
    fichier_url: Optional[str] = None
    fichier_nom: Optional[str] = None
    fichier_type: Optional[str] = None  # pdf, docx, xlsx, jpg, png
    fichier_taille: Optional[int] = None  # en bytes
    
    # Workflow
    createur_id: str
    createur_nom: str
    createur_service_id: str  # Service du créateur
    createur_service_nom: str
    
    destinataire_final_id: str  # Qui doit valider/signer en dernier
    destinataire_final_nom: str
    destinataire_service_id: str  # Service du destinataire
    destinataire_service_nom: str
    
    proprietaire_actuel_id: str  # Qui a le doc actuellement
    proprietaire_actuel_nom: str
    
    # Circuit de validation (OBLIGATOIRE)
    # Auto-généré selon la hiérarchie: Créateur → N+1 → Directeur → SG → Ministre
    circuit_validation: List[str]  # Liste des user_ids dans l'ordre (OBLIGATOIRE - pas de défaut [])
    circuit_validation_noms: List[str] = []  # Noms correspondants pour affichage
    circuit_validation_services: List[str] = []  # Services correspondants
    circuit_validation_roles: List[str] = []  # NOUVEAU - Rôles (contributeur, visa_correction, signature, expedition)
    etape_actuelle: int = 0  # Position dans le circuit
    
    # Priorité (NOUVEAU - OBLIGATOIRE)
    priorite: PrioriteDocument = PrioriteDocument.NORMALE
    
    # Verrouillage (NOUVEAU - Conformité GED)
    est_verrouille: bool = False
    verrouille_par_user_id: Optional[str] = None
    verrouille_par_user_nom: Optional[str] = None
    date_verrouillage: Optional[str] = None
    
    # Affectation à un service (pour Ministre/SG)
    affecte_a_service_id: Optional[str] = None
    affecte_a_service_nom: Optional[str] = None
    commentaire_affectation: Optional[str] = None
    
    # Statut et métadonnées
    statut: StatutDocument = StatutDocument.BROUILLON
    niveau_diffusion: NiveauDiffusion = NiveauDiffusion.PRIVE
    mode_livraison: ModeLivraison = ModeLivraison.INTERNE
    niveau_confidentialite: str = "public"  # public, confidentiel, secret
    
    # Gestion des versions
    version: int = 1
    versions_precedentes: List[str] = []  # IDs des versions précédentes
    
    # Dates et délais
    date_creation: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    date_echeance: Optional[str] = None
    date_prise_en_charge: Optional[str] = None
    date_validation: Optional[str] = None
    delai_traitement_heures: Optional[int] = None
    
    # Flags
    est_brouillon: bool = True
    est_finalise: bool = False
    necessite_signature: bool = False
    est_signe: bool = False
    watermark_id: Optional[str] = None  # ID unique invisible pour traçabilité
    
    # Copie pour information (CC)
    cc_user_ids: List[str] = []
    
    # Collaborateurs (NOUVEAU - personnes travaillant ensemble sur le document)
    collaborateurs_ids: List[str] = []  # IDs des collaborateurs
    collaborateurs_noms: List[str] = []  # Noms pour affichage
    collaborateurs_services: List[str] = []  # Services des collaborateurs
    validation_n_plus_1_requise: bool = False  # True si validation N+1 nécessaire
    validation_n_plus_1_user_id: Optional[str] = None  # ID du N+1
    validation_n_plus_1_nom: Optional[str] = None  # Nom du N+1
    
    # Mots-clés et recherche
    mots_cles: List[str] = []
    
    # Liaison de dossiers (NOUVEAU - P1 Conformité)
    documents_lies: List[str] = []  # IDs des documents liés (bidirectionnel)
    
    # Plan de classement (NOUVEAU - P1 Conformité)
    plan_classement_id: Optional[str] = None  # ID du plan de classement
    plan_classement_code: Optional[str] = None  # Code pour affichage rapide
    plan_classement_chemin: Optional[str] = None  # Chemin complet hiérarchique
    
    # Transmission externe (NOUVEAU - P1 Conformité)
    lien_externe_token: Optional[str] = None  # Token pour accès externe temporaire
    lien_externe_expire_le: Optional[str] = None  # Date d'expiration du lien
    transmis_externe_a: List[str] = []  # Liste des emails externes
    
    # Indexation de contenu (NOUVEAU - P2 Conformité)
    contenu_indexe: Optional[str] = None  # Contenu textuel extrait pour recherche
    date_indexation: Optional[str] = None
    methode_extraction: Optional[str] = None  # pymupdf, python-docx, tesseract_ocr
    taille_contenu_indexe: Optional[int] = None
    
    # Gestion des modèles (templates)
    is_template: bool = False  # Si True, ce document est un modèle réutilisable
    template_name: Optional[str] = None  # Nom du modèle
    template_description: Optional[str] = None  # Description du modèle
    
    model_config = ConfigDict(use_enum_values=True)


class HistoriqueAction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    user_id: str
    user_nom: str
    user_role: str
    type_action: TypeAction
    type_tache: Optional[str] = None  # NOUVEAU - Type de tâche (INFO, CLASS, ASOC, CF)
    commentaire: Optional[str] = None
    raison_rejet: Optional[str] = None
    date_action: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Métadonnées supplémentaires
    ancien_proprietaire: Optional[str] = None
    nouveau_proprietaire: Optional[str] = None
    ancienne_valeur: Optional[dict] = None  # Pour les modifications
    nouvelle_valeur: Optional[dict] = None
    
    model_config = ConfigDict(use_enum_values=True)


class Commentaire(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    user_id: str
    user_nom: str
    contenu: str
    est_interne: bool = True  # Commentaire interne au service ou visible par tous
    date_creation: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    model_config = ConfigDict(use_enum_values=True)



class TypeListe(str, Enum):
    """Type de liste d'utilisateurs prédéfinie"""
    DISTRIBUTION = "distribution"  # Liste de diffusion (CC, destinataires multiples)
    ATTRIBUTION = "attribution"  # Liste pour attribution de tâches
    E_SIGNATAIRES = "e_signataires"  # Liste de signataires prédéfinis pour workflows


class ListeUtilisateurs(BaseModel):
    """Liste prédéfinie d'utilisateurs pour faciliter les opérations courantes"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str  # Ex: "Direction Générale - Tous", "Signataires Budget"
    description: Optional[str] = None
    type_liste: TypeListe
    
    # Membres de la liste
    user_ids: List[str] = []  # IDs des utilisateurs membres
    user_noms: List[str] = []  # Noms pour affichage rapide
    
    # Métadonnées
    createur_id: str
    createur_nom: str
    est_publique: bool = True  # Si False, seul le créateur peut l'utiliser
    service_id: Optional[str] = None  # Si restreint à un service spécifique
    
    date_creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_modification: Optional[datetime] = None
    
    # Statistiques d'utilisation
    nombre_utilisations: int = 0



class PlanClassement(BaseModel):
    """
    Plan de classement hiérarchique pour organiser les documents
    Basé sur la structure gouvernementale DRC
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Ex: "ADM", "ADM.FIN", "ADM.FIN.COMPTA"
    nom: str  # Ex: "Administration", "Finances", "Comptabilité"
    description: Optional[str] = None
    
    # Hiérarchie
    niveau: int  # 1, 2, 3, etc.
    parent_id: Optional[str] = None  # ID du plan parent (None pour racine)
    chemin_complet: str  # Ex: "Administration > Finances > Comptabilité"
    
    # Métadonnées
    est_actif: bool = True
    ordre_affichage: int = 0  # Pour trier l'affichage
    icone: Optional[str] = None  # Emoji ou icône
    
    # Règles de classification
    duree_conservation_mois: Optional[int] = None  # Durée légale de conservation
    types_documents_acceptes: List[str] = []  # Types de documents autorisés
    
    date_creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    createur_id: Optional[str] = None



class TypeEntiteExterne(str, Enum):
    """Type d'entité externe"""
    ENTREPRISE = "entreprise"  # Entreprise privée
    ONG = "ong"  # Organisation non gouvernementale
    ORGANISME_PUBLIC = "organisme_public"  # Autre organisme public (hors MINEPST)
    PARTENAIRE_INTERNATIONAL = "partenaire_international"  # Partenaire international
    CITOYEN = "citoyen"  # Citoyen individuel
    AUTRE = "autre"


class EntiteExterne(BaseModel):
    """
    Entité externe au MINEPST (entreprises, ONG, organismes, citoyens)
    Pour la gestion des communications et documents externes
    """
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str  # Nom de l'entité ou de la personne
    type_entite: TypeEntiteExterne
    
    # Coordonnées
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    province: Optional[str] = None
    pays: str = "RDC"
    
    # Informations complémentaires
    numero_identification: Optional[str] = None  # RCCM, ID national, etc.
    secteur_activite: Optional[str] = None
    description: Optional[str] = None
    
    # Contact principal
    contact_principal_nom: Optional[str] = None
    contact_principal_fonction: Optional[str] = None
    contact_principal_email: Optional[str] = None
    contact_principal_telephone: Optional[str] = None
    
    # Métadonnées
    est_actif: bool = True
    est_partenaire: bool = False  # Partenaire régulier du MINEPST
    date_creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    createur_id: str
    createur_nom: str
    
    # Historique des interactions
    nombre_documents_recus: int = 0
    nombre_documents_envoyes: int = 0
    derniere_interaction: Optional[datetime] = None
    
    # Tags pour recherche
    tags: List[str] = []


class NotificationDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    user_id: str
    type_notification: str  # nouveau_document, rappel, rejet, validation
    message: str
    est_lu: bool = False
    date_envoi: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    model_config = ConfigDict(use_enum_values=True)


class RapportTrimestriel(BaseModel):
    """Rapport statistique trimestriel du GED"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    periode_debut: str  # Date de début du trimestre
    periode_fin: str  # Date de fin du trimestre
    trimestre: int  # 1, 2, 3, ou 4
    annee: int
    date_generation: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Statistiques globales
    total_documents_crees: int = 0
    total_documents_valides: int = 0
    total_documents_rejetes: int = 0
    total_documents_en_cours: int = 0
    total_documents_archives: int = 0
    
    # Statistiques par type
    stats_par_type: dict = {}  # {"administratif": {...}, "rh": {...}, ...}
    
    # Performance
    delai_moyen_validation_heures: float = 0.0
    delai_median_validation_heures: float = 0.0
    taux_validation: float = 0.0  # % de documents validés
    taux_rejet: float = 0.0  # % de documents rejetés
    
    # Documents en retard
    documents_en_retard: int = 0
    documents_en_retard_details: List[dict] = []
    
    # Top utilisateurs
    top_createurs: List[dict] = []  # Top 10 créateurs
    top_validateurs: List[dict] = []  # Top 10 validateurs
    utilisateurs_les_plus_lents: List[dict] = []  # Utilisateurs avec délais élevés
    
    # Statistiques par province
    stats_par_province: dict = {}
    
    # Tendances
    comparaison_trimestre_precedent: dict = {}
    
    # Métadonnées
    genere_par: str = "system"  # user_id ou "system"
    envoi_email_effectue: bool = False
    destinataires_email: List[str] = []
    
    model_config = ConfigDict(use_enum_values=True)



# ============================================
# MODULE SIRH (Gestion RH) - Models
# ============================================

class GradeEnseignant(str, Enum):
    """Grades des enseignants"""
    STAGIAIRE = "stagiaire"
    MECANISE = "mécanisé"
    QUALIFIE = "qualifié"
    DIPLOME = "diplômé"
    LICENCE = "licencié"
    MAITRE_ASSISTANT = "maître_assistant"
    CHEF_DE_TRAVAUX = "chef_de_travaux"


class TypeMutation(str, Enum):
    """Types de mutation"""
    GEOGRAPHIQUE = "geographique"  # Changement d'établissement/province
    PROMOTION = "promotion"  # Changement de grade
    DISCIPLINE = "discipline"  # Changement de matière enseignée


class StatutMutation(str, Enum):
    """Statuts d'une demande de mutation"""
    EN_ATTENTE = "en_attente"
    VALIDEE_DIRECTEUR = "validee_directeur"
    VALIDEE_DPE_ORIGINE = "validee_dpe_origine"
    VALIDEE_DPE_DESTINATION = "validee_dpe_destination"
    VALIDEE_SG = "validee_secretaire_general"
    APPROUVEE = "approuvee"  # Finale
    REJETEE = "rejetee"
    ANNULEE = "annulee"


class HistoriqueAffectation(BaseModel):
    """Historique des affectations géographiques d'un enseignant"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enseignant_id: str
    etablissement_id: str
    etablissement_nom: str
    province_id: str
    province_nom: str
    date_debut: str
    date_fin: Optional[str] = None  # None si affectation en cours
    motif: str  # "Première affectation", "Mutation", "Promotion", etc.
    mutation_id: Optional[str] = None  # Lien vers la demande de mutation si applicable
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HistoriquePromotion(BaseModel):
    """Historique des promotions (changements de grade)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enseignant_id: str
    ancien_grade: GradeEnseignant
    nouveau_grade: GradeEnseignant
    date_promotion: str
    motif: str  # "Ancienneté", "Mérite", "Formation", etc.
    decision_reference: str  # Référence de la décision administrative
    mutation_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HistoriqueMutationDiscipline(BaseModel):
    """Historique des mutations de discipline (changement de matière)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enseignant_id: str
    anciennes_matieres: List[str]
    nouvelles_matieres: List[str]
    date_mutation: str
    motif: str  # "Formation complémentaire", "Besoin de service", etc.
    mutation_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VerificationDINACOPE(BaseModel):
    """Vérification physique des données enseignant par DINACOPE"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enseignant_id: str
    agent_dinacope_id: str  # Utilisateur qui a initié la vérification
    agent_dinacope_nom: str
    
    # Statut
    statut: str = "en_attente"  # en_attente, verifie, expiree
    
    # Lien de vérification
    token_verification: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lien_verification: str = ""  # Généré automatiquement
    date_envoi: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    date_expiration: str  # 30 jours après envoi
    
    # Données vérifiées/mises à jour
    date_verification: Optional[str] = None
    donnees_avant: dict = {}  # Snapshot des données avant mise à jour
    donnees_apres: dict = {}  # Nouvelles données après mise à jour
    
    # Modifications effectuées
    champs_modifies: List[str] = []
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DonneesDINACOPE(BaseModel):
    """Données personnelles complètes de l'enseignant pour vérification DINACOPE"""
    # Coordonnées
    adresse_personnelle: str = ""
    telephone_personnel: str = ""
    email_personnel: str = ""
    
    # Situation familiale
    etat_civil: str = "celibataire"  # celibataire, marie, divorce, veuf
    nombre_enfants: int = 0
    conjoint_nom: str = ""
    
    # Coordonnées bancaires
    banque: str = ""
    numero_compte: str = ""
    
    # Photo
    photo_url: Optional[str] = None
    
    # Grade actuel
    grade: GradeEnseignant = GradeEnseignant.MECANISE


class DemandeMutation(BaseModel):
    """Demande de mutation d'un enseignant"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_reference: str  # MIN/MUTATION/2025/001
    
    # Informations de base
    enseignant_id: str
    enseignant_nom: str
    enseignant_matricule: str
    type_mutation: TypeMutation
    statut: StatutMutation = StatutMutation.EN_ATTENTE
    
    # Initiateur de la demande
    initiateur_id: str
    initiateur_nom: str
    initiateur_role: str
    
    # Situation actuelle
    etablissement_actuel_id: str
    etablissement_actuel_nom: str
    province_actuelle_id: str
    province_actuelle_nom: str
    
    # Mutation géographique
    etablissement_destination_id: Optional[str] = None
    etablissement_destination_nom: Optional[str] = None
    province_destination_id: Optional[str] = None
    province_destination_nom: Optional[str] = None
    
    # Mutation promotion
    grade_actuel: Optional[GradeEnseignant] = None
    grade_demande: Optional[GradeEnseignant] = None
    
    # Mutation discipline
    matieres_actuelles: List[str] = []
    matieres_demandees: List[str] = []
    
    # Circuit de validation
    circuit_validation: List[dict] = []  # [{role, user_id, user_nom, statut, date, commentaire}]
    
    # Justification
    motif: str
    justification: str = ""
    documents_joints: List[str] = []  # URLs des documents
    



# ============================================
# MODULE DINACOPE AVANCÉ - Paie et Viabilité
# ============================================

class GrileSalariale(BaseModel):
    """Grille salariale selon grade DINACOPE"""
    grade: GradeEnseignant
    echelon: int  # 1 à 15
    salaire_base: float
    prime_fonction: float = 0.0
    prime_anciennete: float = 0.0
    prime_responsabilite: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FichePaie(BaseModel):
    """Fiche de paie mensuelle d'un enseignant (format DINACOPE)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identification DINACOPE
    matricule_secope: str  # Matricule DINACOPE/SECOPE
    enseignant_id: str
    enseignant_nom: str
    
    # Période
    mois: int  # 1-12
    annee: int
    periode: str  # "2025-03" format YYYY-MM
    
    # Données personnelles DINACOPE
    date_naissance: Optional[str] = None
    date_diplome: Optional[str] = None
    date_engagement: Optional[str] = None
    sexe: str = "M"  # M ou F
    
    # Données professionnelles
    grade: GradeEnseignant
    echelon: int = 1
    fonction: str = "Enseignant"
    etablissement_id: str
    etablissement_nom: str
    province_id: str
    province_nom: str
    
    # Calcul paie
    salaire_base: float = 0.0
    prime_fonction: float = 0.0
    prime_anciennete: float = 0.0
    prime_responsabilite: float = 0.0
    retenues: float = 0.0  # Cotisations sociales, impôts
    salaire_net: float = 0.0
    
    # Statut
    statut_paiement: str = "en_attente"  # en_attente, paye, suspendu, bloque
    date_paiement: Optional[str] = None
    mode_paiement: str = "virement"  # virement, especes, mobile_money
    
    # Contrôle physique
    controle_physique_effectue: bool = False
    date_controle_physique: Optional[str] = None
    agent_controle_id: Optional[str] = None
    
    # Observations
    observations: str = ""
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    model_config = ConfigDict(use_enum_values=True)


class ControlePhysiqueMensuel(BaseModel):
    """Contrôle physique mensuel dans un établissement"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identification
    etablissement_id: str
    etablissement_nom: str
    province_id: str
    province_nom: str
    
    # Période
    mois: int
    annee: int
    periode: str  # "2025-03"
    
    # Agent contrôleur
    agent_dinacope_id: str
    agent_dinacope_nom: str
    
    # Résultats contrôle
    date_controle: str
    enseignants_presents: int = 0
    enseignants_absents: int = 0
    enseignants_total: int = 0
    taux_presence: float = 0.0
    
    # Enseignants vérifiés
    enseignants_verifies: List[dict] = []  # [{enseignant_id, nom, present, observations}]
    
    # Anomalies détectées
    anomalies: List[dict] = []  # [{type, description, gravite}]
    
    # Statut
    statut: str = "planifie"  # planifie, en_cours, termine, annule
    
    # Observations
    observations: str = ""
    rapport_pdf_url: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ViabiliteEtablissement(BaseModel):
    """Évaluation de la viabilité d'un établissement scolaire"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identification
    etablissement_id: str
    etablissement_nom: str
    province_id: str
    province_nom: str
    
    # Période d'évaluation
    date_evaluation: str
    annee_scolaire: str  # "2024-2025"
    
    # Critères effectifs
    nombre_eleves: int = 0
    nombre_enseignants: int = 0
    nombre_classes: int = 0
    ratio_eleves_enseignants: float = 0.0  # Idéal: 40-50 élèves/enseignant
    
    # Critères infrastructures
    salles_classes_fonctionnelles: int = 0
    salles_classes_necessaires: int = 0
    latrines_fonctionnelles: int = 0
    point_eau_disponible: bool = False
    electricite_disponible: bool = False
    cloture_perimetre: bool = False
    
    # Critères pédagogiques
    manuels_scolaires_suffisants: bool = False
    materiel_didactique_adequat: bool = False
    bibliotheque_presente: bool = False
    
    # Critères financiers
    frais_scolaires_conformes: bool = True
    subvention_etat_recue: bool = False
    budget_annuel_adequat: bool = False
    
    # Scoring viabilité
    score_effectifs: float = 0.0  # /25
    score_infrastructures: float = 0.0  # /25
    score_pedagogique: float = 0.0  # /25
    score_financier: float = 0.0  # /25
    score_total: float = 0.0  # /100
    
    # Niveau viabilité
    niveau_viabilite: str = "moyen"  # critique (<40), faible (40-60), moyen (60-80), bon (80-90), excellent (>90)
    
    # Recommandations
    recommandations: List[str] = []
    points_forts: List[str] = []
    points_amelioration: List[str] = []
    
    # Décision
    decision: str = "a_evaluer"  # viable, sous_surveillance, besoin_amelioration, fermeture_recommandee
    decision_prise_par: Optional[str] = None
    date_decision: Optional[str] = None
    
    # Observations
    observations: str = ""
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ExportDINACOPE(BaseModel):
    """Export de données au format DINACOPE standard"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Type export
    type_export: str  # "fichier_paie", "effectifs", "etablissements", "controles"
    
    # Période
    mois: int
    annee: int
    periode: str
    
    # Métadonnées
    nombre_enregistrements: int = 0
    format_fichier: str = "csv"  # csv, xlsx, json
    fichier_url: Optional[str] = None
    fichier_nom: str = ""
    
    # Statut
    statut: str = "en_cours"  # en_cours, termine, erreur
    date_generation: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    genere_par: str
    
    # Checksum pour intégrité
    checksum: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Dates
    date_demande: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    date_souhaitee: Optional[str] = None  # Date effective souhaitée
    date_effective: Optional[str] = None  # Date effective appliquée
    date_cloture: Optional[str] = None
    
    # Notifications
    enseignant_notifie: bool = False
    date_notification_enseignant: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    model_config = ConfigDict(use_enum_values=True)


class DetectionFraude(BaseModel):
    """Détection de fraudes et doublons dans les données enseignants"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type_fraude: str  # "matricule_doublon", "identite_doublon", "contact_doublon", "double_affectation"
    niveau_gravite: str = "moyen"  # faible, moyen, eleve, critique
    
    # Enseignants concernés
    enseignants_concernes: List[dict] = []  # [{id, nom, matricule, etablissement}]
    
    # Détails
    champ_problematique: str  # "matricule", "nom+prenom+date_naissance", "telephone", etc.
    valeur_problematique: str
    
    # Statut
    statut: str = "detectee"  # detectee, en_investigation, resolue, faux_positif
    resolu_par: Optional[str] = None  # user_id
    date_resolution: Optional[str] = None
    commentaire_resolution: str = ""
    
    date_detection: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())



# ============================================
# MODULE 3 - SCOLARITÉ (APIs Externes)
# ============================================

class APIClient(BaseModel):
    """Credentials pour systèmes externes"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    etablissement_id: Optional[str] = None  # Si lié à un établissement spécifique
    nom_systeme: str  # Ex: "Système Gestion École Primaire Kinshasa"
    permissions: List[str] = []  # Ex: ["notes", "presences", "inscriptions"]
    actif: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None


class APIClientCreate(BaseModel):
    username: str
    password: str
    etablissement_id: Optional[str] = None
    nom_systeme: str
    permissions: List[str] = []


class Presence(BaseModel):
    """Présences/Absences quotidiennes des élèves"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eleve_id: str
    classe_id: str
    etablissement_id: str
    date: str  # Format: YYYY-MM-DD
    present: bool
    justifie: bool = False
    motif: Optional[str] = None  # Ex: "Maladie", "Rendez-vous médical"
    api_client_id: Optional[str] = None  # Si reçu via API externe
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PresenceCreate(BaseModel):
    eleve_id: str
    classe_id: str
    etablissement_id: str
    date: str
    present: bool
    justifie: bool = False
    motif: Optional[str] = None


class LogAPIExterne(BaseModel):
    """Logs des appels API externes pour traçabilité"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_client_id: str
    endpoint: str
    methode: str  # POST, GET, etc.
    format_donnees: str  # JSON, XML, CSV
    statut: str  # "success", "error", "partial"
    nb_enregistrements: int = 0
    erreurs: List[str] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatistiquesPresence(BaseModel):
    """Statistiques d'assiduité calculées"""
    classe_id: Optional[str] = None
    etablissement_id: Optional[str] = None
    province_id: Optional[str] = None
    periode_debut: str
    periode_fin: str
    taux_presence: float  # Pourcentage
    nb_presences: int
    nb_absences: int
    nb_absences_justifiees: int
    nb_absences_injustifiees: int
    eleves_absenteisme_eleve: List[dict] = []  # [{eleve_id, nom, taux_absence}]


# ============================================
# MODULE 4 - PLATEFORME TEST & CERTIFICATIONS
# ============================================

class CategorieTest(str, Enum):
    EDUCATION = "education"
    TECHNOLOGIE = "technologie"
    SANTE = "sante"
    FINANCE = "finance"
    GOUVERNEMENT = "gouvernement"
    ASSOCIATIONS = "associations"


class Test(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    categorie: CategorieTest
    description: Optional[str] = None
    duree_minutes: Optional[int] = None
    niveau_requis: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestCreate(BaseModel):
    nom: str
    categorie: CategorieTest
    description: Optional[str] = None
    duree_minutes: Optional[int] = None
    niveau_requis: Optional[str] = None


class ResultatTest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    test_nom: str
    categorie: CategorieTest
    nombre_participants: int
    moyenne_globale: float  # Note moyenne sur 100
    
    # Répartition par sexe
    participants_masculin: int
    participants_feminin: int
    moyenne_masculin: float
    moyenne_feminin: float
    
    # Répartition par province administrative (26 provinces)
    resultats_par_province: dict  # {province: {participants, moyenne}}
    
    # Métadonnées
    date_test: datetime
    api_client_id: str  # ID du client API externe qui envoie les données
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResultatTestCreate(BaseModel):
    test_nom: str
    categorie: CategorieTest
    nombre_participants: int
    moyenne_globale: float
    participants_masculin: int
    participants_feminin: int
    moyenne_masculin: float
    moyenne_feminin: float
    resultats_par_province: dict
    date_test: datetime


class StatsTests(BaseModel):
    """Statistiques globales des tests"""
    total_tests: int
    total_participants: int
    moyenne_generale: float
    tests_par_categorie: dict
    etablissements_eligibles: dict  # {excellent: count, bon: count, total: count, pourcentage: float}


# ============================================
# API KEYS - Authentification externe
# ============================================

class APIKeyPermission(str, Enum):
    """Permissions pour les clés API"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class APIKey(BaseModel):
    """Clé API pour l'authentification externe"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # Nom descriptif de la clé
    key_hash: str  # Hash de la clé (on ne stocke jamais la clé en clair)
    key_prefix: str  # Premiers caractères de la clé pour identification (ex: "educon_abc123...")
    
    # Permissions granulaires par module
    permissions: dict = Field(default_factory=dict)  # {"documents": "read", "enseignants": "write", "stats": "read"}
    
    created_by: str  # ID de l'utilisateur qui a créé la clé
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # Optionnel : date d'expiration
    last_used_at: Optional[datetime] = None
    
    is_active: bool = True
    
    # Métadonnées
    description: Optional[str] = None
    ip_whitelist: Optional[List[str]] = None  # Liste d'IPs autorisées (optionnel)
    usage_count: int = 0


class APIKeyCreate(BaseModel):
    """Données pour créer une nouvelle clé API"""
    name: str = Field(..., min_length=3, max_length=100, description="Nom descriptif de la clé")
    description: Optional[str] = Field(None, max_length=500)
    permissions: dict = Field(..., description="Permissions par module: {'documents': 'read', 'enseignants': 'write'}")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Nombre de jours avant expiration (optionnel)")
    ip_whitelist: Optional[List[str]] = None


class APIKeyResponse(BaseModel):
    """Réponse lors de la création d'une clé (contient la clé en clair UNE SEULE FOIS)"""
    id: str
    name: str
    key: str  # ⚠️ Affiché UNE SEULE FOIS lors de la création
    key_prefix: str
    permissions: dict
    created_at: datetime
    expires_at: Optional[datetime]
    description: Optional[str]
    
    
class APIKeyInfo(BaseModel):
    """Informations publiques sur une clé API (sans la clé elle-même)"""
    id: str
    name: str
    key_prefix: str
    permissions: dict
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool
    usage_count: int
    description: Optional[str]


# ============================================
# CHAT / MESSAGERIE INTERNE (GED)
# ============================================

class MessageChat(BaseModel):
    """Message dans une conversation"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    expediteur_id: str  # ID de l'utilisateur qui envoie
    expediteur_nom: str  # Nom complet pour affichage
    expediteur_service: str  # Service de l'expéditeur
    contenu: str
    date_envoi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lu_par: List[str] = Field(default_factory=list)  # IDs des utilisateurs qui ont lu le message


class Conversation(BaseModel):
    """Conversation entre utilisateurs"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titre: str  # Sujet de la conversation
    participants: List[str]  # IDs des utilisateurs participants
    participants_info: List[dict] = Field(default_factory=list)  # [{id, nom, prenom, service, niveau}]
    createur_id: str
    createur_nom: str
    date_creation: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    derniere_activite: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)  # Pour catégoriser les conversations
    archive: bool = False  # Pour archiver (mais pas supprimer)
    
    # Nouveau : Statut de la conversation et contrôle hiérarchique
    statut: str = "active"  # "active" ou "terminee"
    terminee_par: Optional[str] = None  # ID du supérieur qui a terminé la conversation
    date_terminaison: Optional[datetime] = None
    
    # Référence à un document GED si la conversation est liée à un document
    document_lie_id: Optional[str] = None


class ConversationCreate(BaseModel):
    """Données pour créer une conversation"""
    titre: str = Field(..., min_length=3, max_length=200)
    participants_ids: List[str] = Field(..., min_items=1)  # Au moins un participant (en plus du créateur)
    premier_message: str = Field(..., min_length=1)
    tags: Optional[List[str]] = None
    document_lie_id: Optional[str] = None


class MessageCreate(BaseModel):
    """Données pour envoyer un message"""
    contenu: str = Field(..., min_length=1, max_length=5000)


