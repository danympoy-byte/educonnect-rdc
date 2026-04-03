import secrets
import string
from datetime import datetime


def generate_matricule_enseignant(db_collection) -> str:
    """
    Génère un matricule unique pour un enseignant
    Format: ENS-XXXXXX (où X est un chiffre)
    """
    while True:
        number = ''.join(secrets.choice(string.digits) for _ in range(6))
        matricule = f"ENS-{number}"
        
        # Vérifier l'unicité
        existing = db_collection.find_one({"matricule": matricule})
        if not existing:
            return matricule


def generate_ine(db_collection) -> str:
    """
    Génère un INE (Identifiant National Élève) unique
    Format: INE-XXXXXXXX (où X est un chiffre)
    """
    while True:
        number = ''.join(secrets.choice(string.digits) for _ in range(8))
        ine = f"INE-{number}"
        
        # Vérifier l'unicité
        existing = db_collection.find_one({"ine": ine})
        if not existing:
            return ine


def generate_code_etablissement(db_collection, province_code: str) -> str:
    """
    Génère un code unique pour un établissement
    Format: {PROVINCE_CODE}-ETB-XXXX
    """
    while True:
        number = ''.join(secrets.choice(string.digits) for _ in range(4))
        code = f"{province_code}-ETB-{number}"
        
        # Vérifier l'unicité
        existing = db_collection.find_one({"code_etablissement": code})
        if not existing:
            return code


def serialize_datetime(obj):
    """Convertit les objets datetime en string ISO pour MongoDB"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def deserialize_datetime(obj):
    """Convertit les strings ISO en objets datetime"""
    if isinstance(obj, str):
        try:
            return datetime.fromisoformat(obj)
        except ValueError:
            return obj
    return obj


def calculate_moyenne(notes: list) -> float:
    """
    Calcule la moyenne pondérée d'une liste de notes
    notes: [{note: float, coefficient: float}, ...]
    """
    if not notes:
        return 0.0
    
    total_points = sum(note["note"] * note["coefficient"] for note in notes)
    total_coefficients = sum(note["coefficient"] for note in notes)
    
    if total_coefficients == 0:
        return 0.0
    
    return round(total_points / total_coefficients, 2)


def get_appreciation(moyenne: float) -> str:
    """Retourne une appréciation selon la moyenne"""
    if moyenne >= 16:
        return "Très bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"
