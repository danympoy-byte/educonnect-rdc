"""
Script de création de la structure organisationnelle complète du MINEPST
Basé sur l'organigramme officiel avec 5 niveaux hiérarchiques
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from models import Service, NiveauService
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


async def create_services():
    """Créer toute la structure organisationnelle du MINEPST"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Vider la collection services
    await db.services.delete_many({})
    print("🗑️  Collection 'services' vidée")
    
    services = []
    
    # ============================================
    # NIVEAU 1 : MINISTRE
    # ============================================
    ministre = Service(
        nom="Cabinet du Ministre",
        code="MIN",
        niveau=NiveauService.NIVEAU_1,
        parent_id=None,
        description="Ministre de l'Enseignement Primaire, Secondaire et Technique"
    )
    services.append(ministre.model_dump())
    ministre_id = ministre.id
    
    # ============================================
    # NIVEAU 2 : Services rattachés au Ministre
    # ============================================
    
    # Cabinet du Ministre
    cabinet = Service(
        nom="Cabinet du Ministre",
        code="CAB_MIN",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Cabinet et conseillers du Ministre"
    )
    services.append(cabinet.model_dump())
    
    # Conseillers techniques
    conseillers = Service(
        nom="Conseillers Techniques",
        code="CONS_TECH",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Conseillers techniques du Ministre"
    )
    services.append(conseillers.model_dump())
    
    # Secrétariat du Ministre
    secretariat_min = Service(
        nom="Secrétariat du Ministre",
        code="SEC_MIN",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Secrétariat particulier du Ministre"
    )
    services.append(secretariat_min.model_dump())
    
    # Inspection Générale de l'Éducation Nationale
    inspection_education = Service(
        nom="Inspection Générale de l'Éducation Nationale",
        code="IGEN",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Inspection et contrôle du système éducatif national"
    )
    services.append(inspection_education.model_dump())
    
    # Inspection Générale de la Pédagogie
    inspection_pedagogie = Service(
        nom="Inspection Générale de la Pédagogie",
        code="IGP",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Inspection et innovation pédagogique"
    )
    services.append(inspection_pedagogie.model_dump())
    
    # Inspection Générale de l'Administration
    inspection_admin = Service(
        nom="Inspection Générale de l'Administration",
        code="IGA",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Contrôle administratif et financier"
    )
    services.append(inspection_admin.model_dump())
    
    # Comité Supérieur National de l'Éducation
    comite_superieur = Service(
        nom="Comité Supérieur National de l'Éducation",
        code="CSNE",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Organe consultatif de l'éducation nationale"
    )
    services.append(comite_superieur.model_dump())
    
    # CRIPEN
    cripen = Service(
        nom="CRIPEN",
        code="CRIPEN",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Centre de Recherche et d'Innovation Pédagogique et Éducationnelle Nationale"
    )
    services.append(cripen.model_dump())
    
    # SECRÉTARIAT GÉNÉRAL
    secretariat_general = Service(
        nom="Secrétariat Général",
        code="SG",
        niveau=NiveauService.NIVEAU_2,
        parent_id=ministre_id,
        description="Coordination générale des services du Ministère"
    )
    services.append(secretariat_general.model_dump())
    sg_id = secretariat_general.id
    
    # ============================================
    # NIVEAU 3 : DIRECTIONS GÉNÉRALES (sous SG)
    # ============================================
    
    # 1. DIRECTION GÉNÉRALE DE L'ADMINISTRATION
    dga = Service(
        nom="Direction Générale de l'Administration",
        code="DGA",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Gestion administrative, RH et financière du Ministère"
    )
    services.append(dga.model_dump())
    dga_id = dga.id
    
    # Sous-directions DGA (Niveau 4)
    dga_finances = Service(
        nom="Direction des Finances",
        code="DGA_FIN",
        niveau=NiveauService.NIVEAU_4,
        parent_id=dga_id,
        description="Gestion financière et budgétaire"
    )
    services.append(dga_finances.model_dump())
    
    # Services sous Finances (Niveau 5)
    services.extend([
        Service(
            nom="Service Budget",
            code="DGA_FIN_BUD",
            niveau=NiveauService.NIVEAU_5,
            parent_id=dga_finances.id,
            description="Élaboration et suivi budgétaire"
        ).model_dump(),
        Service(
            nom="Service Comptabilité",
            code="DGA_FIN_COMPTA",
            niveau=NiveauService.NIVEAU_5,
            parent_id=dga_finances.id,
            description="Comptabilité générale et analytique"
        ).model_dump(),
    ])
    
    dga_rh = Service(
        nom="Direction des Ressources Humaines",
        code="DGA_RH",
        niveau=NiveauService.NIVEAU_4,
        parent_id=dga_id,
        description="Gestion du personnel et carrières"
    )
    services.append(dga_rh.model_dump())
    
    # Services sous RH (Niveau 5)
    services.extend([
        Service(
            nom="Service Recrutement et Carrières",
            code="DGA_RH_REC",
            niveau=NiveauService.NIVEAU_5,
            parent_id=dga_rh.id,
            description="Recrutement et gestion des carrières"
        ).model_dump(),
        Service(
            nom="Service Formation",
            code="DGA_RH_FORM",
            niveau=NiveauService.NIVEAU_5,
            parent_id=dga_rh.id,
            description="Formation continue du personnel"
        ).model_dump(),
    ])
    
    dga_patrimoine = Service(
        nom="Direction du Patrimoine et Équipements",
        code="DGA_PAT",
        niveau=NiveauService.NIVEAU_4,
        parent_id=dga_id,
        description="Gestion du patrimoine mobilier et immobilier"
    )
    services.append(dga_patrimoine.model_dump())
    
    dga_services_internes = Service(
        nom="Services Internes",
        code="DGA_SI",
        niveau=NiveauService.NIVEAU_4,
        parent_id=dga_id,
        description="Services généraux et logistique"
    )
    services.append(dga_services_internes.model_dump())
    
    # 2. DIRECTION GÉNÉRALE DE LA SCOLARISATION ET DE L'ENSEIGNEMENT GÉNÉRAL
    dgeg = Service(
        nom="Direction Générale de la Scolarisation et de l'Enseignement Général",
        code="DGEG",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Pilotage de l'enseignement primaire et secondaire général"
    )
    services.append(dgeg.model_dump())
    dgeg_id = dgeg.id
    
    # Sous-directions DGEG (Niveau 4)
    services.extend([
        Service(
            nom="Direction des Enseignements Fondamentaux",
            code="DGEG_FOND",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgeg_id,
            description="Enseignement primaire et maternel"
        ).model_dump(),
        Service(
            nom="Direction des Enseignements Secondaires",
            code="DGEG_SEC",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgeg_id,
            description="Enseignement secondaire général"
        ).model_dump(),
        Service(
            nom="Direction de la Vie Scolaire",
            code="DGEG_VS",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgeg_id,
            description="Animation et encadrement de la vie scolaire"
        ).model_dump(),
        Service(
            nom="Direction de l'Orientation",
            code="DGEG_ORIENT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgeg_id,
            description="Orientation scolaire et professionnelle"
        ).model_dump(),
    ])
    
    # 3. DIRECTION GÉNÉRALE DE L'ENSEIGNEMENT TECHNIQUE ET FORMATION PROFESSIONNELLE
    dgetfp = Service(
        nom="Direction Générale de l'Enseignement Technique et de la Formation Professionnelle",
        code="DGETFP",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Enseignement technique et formation professionnelle"
    )
    services.append(dgetfp.model_dump())
    dgetfp_id = dgetfp.id
    
    # Sous-directions DGETFP (Niveau 4)
    services.extend([
        Service(
            nom="Direction de la Formation Technique",
            code="DGETFP_TECH",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgetfp_id,
            description="Enseignement technique secondaire"
        ).model_dump(),
        Service(
            nom="Direction de la Formation Professionnelle",
            code="DGETFP_PROF",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgetfp_id,
            description="Formation professionnelle et apprentissage"
        ).model_dump(),
        Service(
            nom="Direction des Partenariats",
            code="DGETFP_PART",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgetfp_id,
            description="Partenariats avec le secteur privé"
        ).model_dump(),
        Service(
            nom="Direction de l'Insertion",
            code="DGETFP_INS",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgetfp_id,
            description="Insertion professionnelle des diplômés"
        ).model_dump(),
    ])
    
    # 4. DIRECTION GÉNÉRALE DES EXAMENS ET CONCOURS
    dgec = Service(
        nom="Direction Générale des Examens et Concours",
        code="DGEC",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Organisation des examens d'État et concours"
    )
    services.append(dgec.model_dump())
    dgec_id = dgec.id
    
    # Sous-directions DGEC (Niveau 4)
    services.extend([
        Service(
            nom="Direction de l'Organisation des Examens",
            code="DGEC_ORG",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgec_id,
            description="Logistique et organisation des examens"
        ).model_dump(),
        Service(
            nom="Direction des Corrections",
            code="DGEC_CORR",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgec_id,
            description="Correction et délibérations"
        ).model_dump(),
        Service(
            nom="Direction des Résultats",
            code="DGEC_RES",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgec_id,
            description="Publication et certification des résultats"
        ).model_dump(),
        Service(
            nom="Direction des Statistiques d'Examens",
            code="DGEC_STAT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgec_id,
            description="Analyse statistique des résultats"
        ).model_dump(),
    ])
    
    # 5. DIRECTION GÉNÉRALE DU CENTRE DE FORMATION DE L'ÉDUCATION (CFEE)
    dgcfee = Service(
        nom="Direction Générale du Centre de Formation de l'Éducation (CFEE)",
        code="DGCFEE",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Formation initiale et continue des enseignants"
    )
    services.append(dgcfee.model_dump())
    dgcfee_id = dgcfee.id
    
    # Sous-directions DGCFEE (Niveau 4)
    services.extend([
        Service(
            nom="Direction de la Formation Initiale",
            code="DGCFEE_INIT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgcfee_id,
            description="Formation initiale des enseignants"
        ).model_dump(),
        Service(
            nom="Direction de la Formation Continue",
            code="DGCFEE_CONT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgcfee_id,
            description="Perfectionnement des enseignants en exercice"
        ).model_dump(),
        Service(
            nom="Direction de l'Innovation Pédagogique",
            code="DGCFEE_INNOV",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgcfee_id,
            description="Recherche et innovation pédagogique"
        ).model_dump(),
    ])
    
    # 6. DIRECTION GÉNÉRALE DE LA PLANIFICATION ET DES DONNÉES
    dgpd = Service(
        nom="Direction Générale de la Planification et des Données",
        code="DGPD",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Planification stratégique et statistiques éducatives"
    )
    services.append(dgpd.model_dump())
    dgpd_id = dgpd.id
    
    # Sous-directions DGPD (Niveau 4)
    services.extend([
        Service(
            nom="Direction des Statistiques",
            code="DGPD_STAT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgpd_id,
            description="Collecte et analyse des données éducatives"
        ).model_dump(),
        Service(
            nom="Direction de la Planification",
            code="DGPD_PLAN",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgpd_id,
            description="Planification et programmation"
        ).model_dump(),
        Service(
            nom="Direction de l'Évaluation",
            code="DGPD_EVAL",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgpd_id,
            description="Évaluation des politiques éducatives"
        ).model_dump(),
    ])
    
    # 7. DIRECTION GÉNÉRALE DU DÉVELOPPEMENT DES TIC
    dgtic = Service(
        nom="Direction Générale du Développement des TIC",
        code="DGTIC",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Technologies de l'information et de la communication"
    )
    services.append(dgtic.model_dump())
    dgtic_id = dgtic.id
    
    # Sous-directions DGTIC (Niveau 4)
    services.extend([
        Service(
            nom="Direction Informatique",
            code="DGTIC_INFO",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgtic_id,
            description="Infrastructure et développement informatique"
        ).model_dump(),
        Service(
            nom="Direction des Systèmes d'Information",
            code="DGTIC_SI",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgtic_id,
            description="SIGE et systèmes d'information (Édu-Connect)"
        ).model_dump(),
        Service(
            nom="Direction Maintenance",
            code="DGTIC_MAINT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgtic_id,
            description="Maintenance et support technique"
        ).model_dump(),
        Service(
            nom="Direction des Archives Numériques",
            code="DGTIC_ARCH",
            niveau=NiveauService.NIVEAU_4,
            parent_id=dgtic_id,
            description="Archivage et GED numérique"
        ).model_dump(),
    ])
    
    # 8. DIRECTIONS DÉCONCENTRÉES / RÉGIONALES
    directions_deconcentrees = Service(
        nom="Directions Déconcentrées et Régionales",
        code="DDR",
        niveau=NiveauService.NIVEAU_3,
        parent_id=sg_id,
        description="Services territoriaux du Ministère"
    )
    services.append(directions_deconcentrees.model_dump())
    ddr_id = directions_deconcentrees.id
    
    # Sous-directions DDR (Niveau 4)
    services.extend([
        Service(
            nom="Directions Provinciales",
            code="DDR_PROV",
            niveau=NiveauService.NIVEAU_4,
            parent_id=ddr_id,
            description="Directions provinciales de l'éducation (26 provinces)"
        ).model_dump(),
        Service(
            nom="Directions Départementales",
            code="DDR_DEPT",
            niveau=NiveauService.NIVEAU_4,
            parent_id=ddr_id,
            description="Sous-divisions provinciales"
        ).model_dump(),
        Service(
            nom="Services Locaux",
            code="DDR_LOC",
            niveau=NiveauService.NIVEAU_4,
            parent_id=ddr_id,
            description="Services de proximité et établissements"
        ).model_dump(),
    ])
    
    # Insérer tous les services
    await db.services.insert_many(services)
    
    print(f"\n✅ {len(services)} services créés avec succès!")
    print(f"   - Niveau 1 (Ministre): 1 service")
    print(f"   - Niveau 2 (Cabinet, SG, Inspections): 9 services")
    print(f"   - Niveau 3 (Directions Générales): 8 DG")
    print(f"   - Niveau 4 (Directions): {sum(1 for s in services if s['niveau'] == 'niveau_4')} directions")
    print(f"   - Niveau 5 (Services): {sum(1 for s in services if s['niveau'] == 'niveau_5')} services")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_services())
