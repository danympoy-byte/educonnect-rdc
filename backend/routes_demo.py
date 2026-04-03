"""
Routes de gestion des utilisateurs éphémères (comptes de démonstration)
- Création de comptes Test01..TestN valides 24h après première connexion
- Nettoyage automatique des comptes expirés
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
from auth import get_password_hash, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/demo", tags=["Utilisateurs éphémères"])


class DemoUsersRequest(BaseModel):
    nombre: int = 5
    service_code: Optional[str] = "DGA"
    password: str = "Demo2026!"


@router.post("/generer")
async def generer_utilisateurs_demo(
    data: DemoUsersRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Génère des utilisateurs éphémères pour les présentations.
    Chaque compte expire 24h après sa première connexion.
    Accessible uniquement aux administrateurs / ministre / SG.
    """
    from dependencies import get_db
    db = get_db()

    # Vérifier les droits
    role = current_user.get("role")
    if role not in ["ministre", "secretaire_general", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    if data.nombre < 1 or data.nombre > 20:
        raise HTTPException(status_code=400, detail="Le nombre doit être entre 1 et 20")

    # Trouver le service cible
    service = await db.services.find_one({"code": data.service_code}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail=f"Service avec code '{data.service_code}' non trouvé")

    # Supprimer les anciens comptes éphémères existants (nettoyage)
    deleted = await db.users.delete_many({"is_ephemeral": True})

    # Déterminer le prochain numéro
    created_users = []
    hashed_pw = get_password_hash(data.password)

    for i in range(1, data.nombre + 1):
        numero = f"{i:02d}"
        user_id = f"demo_test_{numero}"
        telephone = f"+243 900 000 {numero}"

        user_doc = {
            "id": user_id,
            "nom": f"Test{numero}",
            "postnom": "Demo",
            "prenom": f"Utilisateur",
            "sexe": "masculin",
            "etat_civil": "celibataire",
            "date_naissance": "2000-01-01",
            "lieu_naissance": "Kinshasa",
            "telephone": telephone,
            "adresse": "Compte de démonstration",
            "email": f"test{numero}@demo.educonnect.cd",
            "diplomes": [],
            "experiences": [],
            "service_profiles": [{
                "id": f"prof_demo_{numero}",
                "user_id": user_id,
                "service_id": service["id"],
                "service_nom": service["nom"],
                "service_code": service["code"],
                "poste": "Agent de démonstration",
                "est_responsable": False,
                "date_affectation": datetime.now(timezone.utc).isoformat()
            }],
            "service_actif_id": service["id"],
            "numero_compte_bancaire": None,
            "banque": None,
            "photo_url": None,
            "hashed_password": hashed_pw,
            "is_active": True,
            "profil_complete": True,
            "is_ephemeral": True,
            "first_login_at": None,
            "expires_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        created_users.append(user_doc)

    if created_users:
        await db.users.insert_many(created_users)

    return {
        "message": f"{len(created_users)} comptes de démonstration créés",
        "anciens_supprimes": deleted.deleted_count,
        "comptes": [
            {
                "nom": u["nom"],
                "telephone": u["telephone"],
                "email": u["email"],
                "password": data.password,
                "service": u["service_profiles"][0]["service_nom"],
                "validite": "24h après première connexion"
            }
            for u in created_users
        ],
        "mot_de_passe_commun": data.password
    }


@router.get("/liste")
async def lister_utilisateurs_demo(current_user: dict = Depends(get_current_user)):
    """Liste tous les comptes de démonstration actifs."""
    from dependencies import get_db
    db = get_db()

    demos = await db.users.find(
        {"is_ephemeral": True},
        {"_id": 0, "hashed_password": 0}
    ).to_list(100)

    maintenant = datetime.now(timezone.utc)
    result = []
    for u in demos:
        statut = "actif"
        temps_restant = None
        if u.get("expires_at"):
            expires = datetime.fromisoformat(u["expires_at"]) if isinstance(u["expires_at"], str) else u["expires_at"]
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if maintenant > expires:
                statut = "expiré"
            else:
                delta = expires - maintenant
                heures = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                temps_restant = f"{heures}h{minutes:02d}m"
        elif u.get("first_login_at") is None:
            statut = "jamais connecté"

        result.append({
            "nom": u["nom"],
            "telephone": u["telephone"],
            "email": u.get("email"),
            "statut": statut,
            "temps_restant": temps_restant,
            "first_login_at": u.get("first_login_at"),
            "expires_at": u.get("expires_at"),
            "service": u["service_profiles"][0]["service_nom"] if u.get("service_profiles") else None
        })

    return {"comptes": result, "total": len(result)}


@router.delete("/supprimer")
async def supprimer_utilisateurs_demo(current_user: dict = Depends(get_current_user)):
    """Supprime tous les comptes de démonstration."""
    from dependencies import get_db
    db = get_db()

    role = current_user.get("role")
    if role not in ["ministre", "secretaire_general", "admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    result = await db.users.delete_many({"is_ephemeral": True})
    return {"message": f"{result.deleted_count} comptes de démonstration supprimés"}
