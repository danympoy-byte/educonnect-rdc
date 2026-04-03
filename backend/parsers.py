"""
Parsers pour gérer les différents formats de données (JSON, XML, CSV)
"""
import json
import csv
import io
import xmltodict
from typing import List, Dict, Any
from fastapi import HTTPException, UploadFile


class DataParser:
    """Classe pour parser les données multi-format"""
    
    @staticmethod
    def parse_json(content: str) -> List[Dict[str, Any]]:
        """Parse les données JSON"""
        try:
            data = json.loads(content)
            # Si c'est un objet unique, le mettre dans une liste
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError("Format JSON invalide")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur parsing JSON: {str(e)}")
    
    @staticmethod
    def parse_xml(content: str) -> List[Dict[str, Any]]:
        """Parse les données XML"""
        try:
            data = xmltodict.parse(content)
            
            # Extraire les données selon la structure XML
            # Supporte plusieurs formats courants
            if 'data' in data:
                items = data['data']
            elif 'items' in data:
                items = data['items']
            elif 'records' in data:
                items = data['records']
            else:
                # Prendre la première clé racine
                root_key = list(data.keys())[0]
                items = data[root_key]
            
            # Gérer item unique vs liste
            if isinstance(items, dict):
                # Chercher une sous-clé qui contient une liste
                for key, value in items.items():
                    if isinstance(value, list):
                        return value
                    elif isinstance(value, dict):
                        return [value]
                return [items]
            elif isinstance(items, list):
                return items
            else:
                return [items]
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur parsing XML: {str(e)}")
    
    @staticmethod
    async def parse_csv(file: UploadFile) -> List[Dict[str, Any]]:
        """Parse un fichier CSV"""
        try:
            content = await file.read()
            decoded = content.decode('utf-8')
            
            # Utiliser DictReader pour avoir des dictionnaires
            csv_reader = csv.DictReader(io.StringIO(decoded))
            data = list(csv_reader)
            
            if not data:
                raise ValueError("Fichier CSV vide")
            
            return data
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur parsing CSV: {str(e)}")
    
    @staticmethod
    def detect_format(content_type: str) -> str:
        """Détecte le format à partir du Content-Type"""
        if 'json' in content_type.lower():
            return 'json'
        elif 'xml' in content_type.lower():
            return 'xml'
        elif 'csv' in content_type.lower():
            return 'csv'
        else:
            # Par défaut, essayer JSON
            return 'json'


class DataValidator:
    """Validation des données reçues"""
    
    @staticmethod
    def validate_note(data: dict) -> dict:
        """Valide les données d'une note"""
        required = ['eleve_id', 'classe_id', 'matiere', 'note', 'trimestre', 'annee_scolaire', 'enseignant_id']
        
        for field in required:
            if field not in data:
                raise ValueError(f"Champ obligatoire manquant: {field}")
        
        # Valider que la note est entre 0 et 20
        note = float(data['note'])
        if note < 0 or note > 20:
            raise ValueError(f"Note invalide: {note} (doit être entre 0 et 20)")
        
        data['note'] = note
        data['coefficient'] = float(data.get('coefficient', 1.0))
        
        return data
    
    @staticmethod
    def validate_presence(data: dict) -> dict:
        """Valide les données de présence"""
        required = ['eleve_id', 'classe_id', 'etablissement_id', 'date', 'present']
        
        for field in required:
            if field not in data:
                raise ValueError(f"Champ obligatoire manquant: {field}")
        
        # Convertir present en boolean si c'est une string
        if isinstance(data['present'], str):
            data['present'] = data['present'].lower() in ['true', '1', 'oui', 'yes']
        
        if isinstance(data.get('justifie'), str):
            data['justifie'] = data['justifie'].lower() in ['true', '1', 'oui', 'yes']
        
        return data
    
    @staticmethod
    def validate_inscription(data: dict) -> dict:
        """Valide les données d'inscription d'élève"""
        required = ['nom', 'prenom', 'email', 'etablissement_id', 'niveau', 'sexe', 'date_naissance']
        
        for field in required:
            if field not in data:
                raise ValueError(f"Champ obligatoire manquant: {field}")
        
        return data
    
    @staticmethod
    def validate_affectation(data: dict) -> dict:
        """Valide les données d'affectation d'enseignant"""
        required = ['enseignant_id', 'etablissement_id', 'date_debut']
        
        for field in required:
            if field not in data:
                raise ValueError(f"Champ obligatoire manquant: {field}")
        
        return data
