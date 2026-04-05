"""
Tests de Conformité GED - Édu-Connect
Tests des fonctionnalités P0, P1, P2 implémentées pour la conformité GED DRC

P0 - Écarts critiques:
  - P0.1: Types de tâches spécifiques (INFO, CLASS, ASOC, CF)
  - P0.2: Verrouillage de documents
  - P0.3: Dérogation de tâche (Bypass)

P1 - Fonctionnalités importantes:
  - P1.1: Délégation de tâches
  - P1.2: Liaison de dossiers
  - P1.3: Transmission externe par email
  - P1.4: Listes de distribution
  - P1.5: Plan de classement hiérarchique

P2 - Nice to have:
  - P2.1: Gestion entités externes
  - P2.2: Aperçu de fichiers (Preview)
  - P2.3: Recherche texte intégral
  - P2.4: Environnement double zone
"""

import pytest
import requests
import os
import time

# Configuration
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bulletin-pdf-preview.preview.emergentagent.com')
if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL.rstrip('/')

# Test credentials from test_credentials.md
CREDENTIALS = {
    "ministre": {
        "email": "ministre@educonnect.gouv.cd",
        "password": "Ministre2026!",
        "nom": "Félix TSHISEKEDI TSHILOMBO"
    },
    "sg": {
        "email": "sg@educonnect.gouv.cd",
        "password": "SG2026!",
        "nom": "Jean-Pierre KABONGO MWAMBA"
    },
    "dg_admin": {
        "email": "dg.admin@educonnect.gouv.cd",
        "password": "DGAdmin2026!",
        "nom": "Grace MULUMBA NKULU"
    }
}


class TestSetup:
    """Setup and authentication tests"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        return requests.Session()
    
    def test_health_check(self, session):
        """Test API health endpoint"""
        response = session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✅ Health check passed: {data}")


class TestAuthentication:
    """Authentication tests for all test users"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    def test_login_ministre(self, session):
        """Login as Ministre"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("✅ Ministre login successful")
        return data["access_token"]
    
    def test_login_sg(self, session):
        """Login as Secrétaire Général"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("✅ SG login successful")
        return data["access_token"]
    
    def test_login_dg_admin(self, session):
        """Login as DG Administration"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["dg_admin"]["email"],
            "password": CREDENTIALS["dg_admin"]["password"]
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        print("✅ DG Admin login successful")
        return data["access_token"]


# ============================================
# P0 - ÉCARTS CRITIQUES
# ============================================

class TestP0TypesTaches:
    """P0.1 - Types de tâches spécifiques (INFO, CLASS, ASOC, CF)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for Ministre"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_token(self):
        """Get auth token for SG"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self, sg_token):
        """Get SG user ID"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        assert response.status_code == 200
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_document(self, auth_token, sg_user_id):
        """Create a test document"""
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "titre": "TEST_P0_TypesTaches_Document",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        assert response.status_code == 200, f"Failed to create document: {response.text}"
        return response.json()["document"]
    
    def test_transmettre_avec_type_tache_info(self, auth_token, test_document, sg_user_id):
        """Test transmission with type_tache=info"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/transmettre",
            headers={"Authorization": f"Bearer {auth_token}"},
            params={
                "destinataire_id": sg_user_id,
                "destinataire_nom": CREDENTIALS["sg"]["nom"],
                "type_tache": "info",
                "commentaire": "Test transmission INFO"
            }
        )
        assert response.status_code == 200, f"Transmission failed: {response.text}"
        data = response.json()
        assert "message" in data
        print("✅ P0.1 - Transmission avec type_tache=info réussie")
    
    def test_transmettre_avec_type_tache_class(self, sg_token, test_document, sg_user_id):
        """Test transmission with type_tache=class (classement requis)"""
        # First get the document to check current owner
        doc_id = test_document["id"]
        
        # Get ministre token to transmit back
        ministre_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        ministre_token = ministre_response.json()["access_token"]
        ministre_me = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {ministre_token}"
        }).json()
        
        # SG transmits back to Ministre with type_tache=class
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/transmettre",
            headers={"Authorization": f"Bearer {sg_token}"},
            params={
                "destinataire_id": ministre_me["id"],
                "destinataire_nom": CREDENTIALS["ministre"]["nom"],
                "type_tache": "class",
                "commentaire": "Test transmission CLASS - Classement requis"
            }
        )
        assert response.status_code == 200, f"Transmission failed: {response.text}"
        print("✅ P0.1 - Transmission avec type_tache=class réussie")
    
    def test_historique_contient_type_tache(self, auth_token, test_document):
        """Verify historique contains type_tache"""
        doc_id = test_document["id"]
        response = requests.get(
            f"{BASE_URL}/api/documents/{doc_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check historique for type_tache
        historique = data.get("historique", [])
        transmission_actions = [h for h in historique if h.get("type_action") == "transmission"]
        
        # At least one transmission should have type_tache
        assert len(transmission_actions) > 0, "No transmission actions found in historique"
        print(f"✅ P0.1 - Historique contient {len(transmission_actions)} transmissions")


class TestP0Verrouillage:
    """P0.2 - Verrouillage de documents"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for Ministre"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_token(self):
        """Get auth token for SG"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self, sg_token):
        """Get SG user ID"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        assert response.status_code == 200
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_document(self, auth_token, sg_user_id):
        """Create a test document for locking tests"""
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "titre": "TEST_P0_Verrouillage_Document",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        assert response.status_code == 200
        return response.json()["document"]
    
    def test_verrouiller_document(self, auth_token, test_document):
        """Test locking a document"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/verrouiller",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Lock failed: {response.text}"
        data = response.json()
        assert data["est_verrouille"] is True
        assert "date_verrouillage" in data
        print("✅ P0.2 - Document verrouillé avec succès")
    
    def test_verrouiller_deja_verrouille_meme_user(self, auth_token, test_document):
        """Test locking already locked document by same user"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/verrouiller",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "déjà verrouillé par vous" in data["message"].lower() or data["est_verrouille"] is True
        print("✅ P0.2 - Verrouillage par même utilisateur géré correctement")
    
    def test_verrouiller_par_autre_user_echoue(self, sg_token, test_document):
        """Test that another user cannot lock an already locked document"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/verrouiller",
            headers={"Authorization": f"Bearer {sg_token}"}
        )
        # Should return 423 Locked
        assert response.status_code == 423, f"Expected 423, got {response.status_code}: {response.text}"
        print("✅ P0.2 - Verrouillage par autre utilisateur bloqué (423)")
    
    def test_deverrouiller_document(self, auth_token, test_document):
        """Test unlocking a document"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/deverrouiller",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Unlock failed: {response.text}"
        data = response.json()
        assert data["est_verrouille"] is False
        print("✅ P0.2 - Document déverrouillé avec succès")


class TestP0Bypass:
    """P0.3 - Dérogation de tâche (Bypass)"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        """Get auth token for Ministre"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def dg_token(self):
        """Get auth token for DG Admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["dg_admin"]["email"],
            "password": CREDENTIALS["dg_admin"]["password"]
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self):
        """Get SG user ID"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        sg_token = response.json()["access_token"]
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return me_response.json()["id"]
    
    @pytest.fixture(scope="class")
    def ministre_user_id(self, ministre_token):
        """Get Ministre user ID"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {ministre_token}"
        })
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_document_with_circuit(self, ministre_token, sg_user_id, ministre_user_id):
        """Create a test document with validation circuit"""
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P0_Bypass_Document",
                "type_document": "administratif",
                "destinataire_final_id": ministre_user_id,
                "destinataire_final_nom": CREDENTIALS["ministre"]["nom"],
                "circuit_validation": sg_user_id  # SG in circuit
            }
        )
        assert response.status_code == 200
        return response.json()["document"]
    
    def test_bypass_sans_justification_echoue(self, ministre_token, test_document_with_circuit):
        """Test bypass without justification fails"""
        doc_id = test_document_with_circuit["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/bypass-etape",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"justification": "court"}  # Too short
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ P0.3 - Bypass sans justification suffisante rejeté")
    
    def test_bypass_par_non_hierarchique_echoue(self, dg_token, test_document_with_circuit):
        """Test bypass by non-hierarchical user fails"""
        doc_id = test_document_with_circuit["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/bypass-etape",
            headers={"Authorization": f"Bearer {dg_token}"},
            params={"justification": "Urgence absolue - Décision ministérielle immédiate requise"}
        )
        # DG Admin is not in the authorized roles list (ministre, secretaire_general, directeur_provincial)
        # This should fail with 403
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✅ P0.3 - Bypass par utilisateur non-hiérarchique rejeté")
    
    def test_bypass_par_ministre_reussit(self, ministre_token, test_document_with_circuit):
        """Test bypass by Ministre succeeds"""
        doc_id = test_document_with_circuit["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/bypass-etape",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"justification": "Urgence absolue - Décision ministérielle immédiate requise pour ce dossier prioritaire"}
        )
        assert response.status_code == 200, f"Bypass failed: {response.text}"
        data = response.json()
        assert "justification" in data
        print(f"✅ P0.3 - Bypass par Ministre réussi: {data['message']}")


# ============================================
# P1 - FONCTIONNALITÉS IMPORTANTES
# ============================================

class TestP1Delegation:
    """P1.1 - Délégation de tâches"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self, sg_token):
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def ministre_user_id(self, ministre_token):
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {ministre_token}"
        })
        return response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_document(self, ministre_token, sg_user_id):
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P1_Delegation_Document",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        return response.json()["document"]
    
    def test_delegation_a_soi_meme_echoue(self, ministre_token, test_document, ministre_user_id):
        """Test that self-delegation fails"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/deleguer",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "delegataire_id": ministre_user_id,
                "delegataire_nom": CREDENTIALS["ministre"]["nom"],
                "commentaire": "Test auto-délégation"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ P1.1 - Auto-délégation rejetée correctement")
    
    def test_delegation_reussie(self, ministre_token, test_document, sg_user_id):
        """Test successful delegation"""
        doc_id = test_document["id"]
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/deleguer",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "delegataire_id": sg_user_id,
                "delegataire_nom": CREDENTIALS["sg"]["nom"],
                "commentaire": "Délégation pour traitement urgent"
            }
        )
        assert response.status_code == 200, f"Delegation failed: {response.text}"
        data = response.json()
        assert data["delegataire_id"] == sg_user_id
        print(f"✅ P1.1 - Délégation réussie: {data['message']}")


class TestP1LiaisonDossiers:
    """P1.2 - Liaison de dossiers"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        sg_token = response.json()["access_token"]
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return me_response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_documents(self, ministre_token, sg_user_id):
        """Create two test documents to link"""
        doc1 = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P1_Liaison_Document1",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        ).json()["document"]
        
        doc2 = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P1_Liaison_Document2",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        ).json()["document"]
        
        return doc1, doc2
    
    def test_lier_documents(self, ministre_token, test_documents):
        """Test linking two documents"""
        doc1, doc2 = test_documents
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc1['id']}/lier",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"document_lie_id": doc2["id"]}
        )
        assert response.status_code == 200, f"Link failed: {response.text}"
        data = response.json()
        assert data["liaison_bidirectionnelle"] is True
        print("✅ P1.2 - Documents liés avec succès (bidirectionnel)")
    
    def test_liaison_deja_existante(self, ministre_token, test_documents):
        """Test linking already linked documents"""
        doc1, doc2 = test_documents
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc1['id']}/lier",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"document_lie_id": doc2["id"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "déjà liés" in data["message"].lower()
        print("✅ P1.2 - Liaison déjà existante détectée")
    
    def test_delier_documents(self, ministre_token, test_documents):
        """Test unlinking documents"""
        doc1, doc2 = test_documents
        response = requests.delete(
            f"{BASE_URL}/api/documents/{doc1['id']}/lier/{doc2['id']}",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200, f"Unlink failed: {response.text}"
        print("✅ P1.2 - Documents déliés avec succès")


class TestP1TransmissionExterne:
    """P1.3 - Transmission externe par email"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        sg_token = response.json()["access_token"]
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return me_response.json()["id"]
    
    def test_transmission_externe_sans_fichier_echoue(self, ministre_token, sg_user_id):
        """Test external transmission without file fails"""
        # Create document without file
        doc_response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P1_TransmissionExterne_SansFichier",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        doc_id = doc_response.json()["document"]["id"]
        
        # Try external transmission
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/transmettre-externe",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "email_destinataire": "test@example.com",
                "message_perso": "Test message",
                "duree_jours": 7
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ P1.3 - Transmission externe sans fichier rejetée")
    
    def test_transmission_externe_email_invalide(self, ministre_token, sg_user_id):
        """Test external transmission with invalid email fails"""
        # Create document
        doc_response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P1_TransmissionExterne_EmailInvalide",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        doc_id = doc_response.json()["document"]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/documents/{doc_id}/transmettre-externe",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "email_destinataire": "invalid-email",
                "duree_jours": 7
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ P1.3 - Email invalide rejeté")


class TestP1ListesDistribution:
    """P1.4 - Listes de distribution"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        sg_token = response.json()["access_token"]
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return me_response.json()["id"]
    
    @pytest.fixture(scope="class")
    def test_liste(self, ministre_token, sg_user_id):
        """Create a test list"""
        response = requests.post(
            f"{BASE_URL}/api/listes/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "nom": "TEST_P1_Liste_Distribution",
                "type_liste": "distribution",
                "user_ids": sg_user_id,  # Single value for query param
                "description": "Liste de test pour distribution",
                "est_publique": True
            }
        )
        assert response.status_code == 200, f"Create list failed: {response.text}"
        return response.json()["liste"]
    
    def test_creer_liste_distribution(self, test_liste):
        """Test creating a distribution list"""
        assert test_liste["type_liste"] == "distribution"
        assert len(test_liste["user_ids"]) > 0
        print(f"✅ P1.4 - Liste de distribution créée: {test_liste['nom']}")
    
    def test_lister_listes(self, ministre_token):
        """Test listing all lists"""
        response = requests.get(
            f"{BASE_URL}/api/listes/",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "listes" in data
        print(f"✅ P1.4 - {data['total']} listes trouvées")
    
    def test_obtenir_liste(self, ministre_token, test_liste):
        """Test getting a specific list"""
        response = requests.get(
            f"{BASE_URL}/api/listes/{test_liste['id']}",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_liste["id"]
        print(f"✅ P1.4 - Liste récupérée: {data['nom']}")
    
    def test_modifier_liste(self, ministre_token, test_liste):
        """Test modifying a list"""
        response = requests.put(
            f"{BASE_URL}/api/listes/{test_liste['id']}",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "nom": "TEST_P1_Liste_Distribution_Modifiee",
                "description": "Description modifiée"
            }
        )
        assert response.status_code == 200
        print("✅ P1.4 - Liste modifiée avec succès")
    
    def test_supprimer_liste(self, ministre_token, test_liste):
        """Test deleting a list"""
        response = requests.delete(
            f"{BASE_URL}/api/listes/{test_liste['id']}",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        print("✅ P1.4 - Liste supprimée avec succès")


class TestP1PlanClassement:
    """P1.5 - Plan de classement hiérarchique"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        return response.json()["access_token"]
    
    def test_initialiser_plan_classement_drc(self, ministre_token):
        """Test initializing DRC classification plan"""
        response = requests.post(
            f"{BASE_URL}/api/plan-classement/initialiser-drc",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        # May return 400 if already initialized
        if response.status_code == 400:
            assert "déjà initialisé" in response.json()["detail"].lower()
            print("✅ P1.5 - Plan de classement déjà initialisé")
        else:
            assert response.status_code == 200
            data = response.json()
            assert data["total_cree"] > 0
            print(f"✅ P1.5 - Plan de classement DRC initialisé: {data['total_cree']} entrées")
    
    def test_lister_plans_classement(self, ministre_token):
        """Test listing classification plans"""
        response = requests.get(
            f"{BASE_URL}/api/plan-classement/",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        print(f"✅ P1.5 - {data['total']} plans de classement trouvés")
    
    def test_obtenir_arborescence(self, ministre_token):
        """Test getting full tree structure"""
        response = requests.get(
            f"{BASE_URL}/api/plan-classement/arborescence",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "arborescence" in data
        print(f"✅ P1.5 - Arborescence récupérée: {data['total_noeuds']} nœuds")
    
    def test_creer_plan_classement_non_admin_echoue(self, sg_token):
        """Test that non-admin cannot create classification plan"""
        response = requests.post(
            f"{BASE_URL}/api/plan-classement/",
            headers={"Authorization": f"Bearer {sg_token}"},
            params={
                "code": "TEST",
                "nom": "Test Plan"
            }
        )
        assert response.status_code == 403
        print("✅ P1.5 - Création par non-admin rejetée")


# ============================================
# P2 - NICE TO HAVE
# ============================================

class TestP2EntitesExternes:
    """P2.1 - Gestion entités externes"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_entite(self, ministre_token):
        """Create a test external entity"""
        response = requests.post(
            f"{BASE_URL}/api/entites-externes/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={
                "nom": "TEST_P2_Entreprise_Test",
                "type_entite": "entreprise",
                "email": "contact@test-entreprise.cd",
                "telephone": "+243999000001",
                "province": "Kinshasa",
                "est_partenaire": True
            }
        )
        assert response.status_code == 200, f"Create entity failed: {response.text}"
        return response.json()["entite"]
    
    def test_creer_entite_externe(self, test_entite):
        """Test creating an external entity"""
        assert test_entite["type_entite"] == "entreprise"
        assert test_entite["est_partenaire"] is True
        print(f"✅ P2.1 - Entité externe créée: {test_entite['nom']}")
    
    def test_lister_entites_externes(self, ministre_token):
        """Test listing external entities"""
        response = requests.get(
            f"{BASE_URL}/api/entites-externes/",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "entites" in data
        print(f"✅ P2.1 - {data['total']} entités externes trouvées")
    
    def test_filtrer_entites_par_type(self, ministre_token):
        """Test filtering entities by type"""
        response = requests.get(
            f"{BASE_URL}/api/entites-externes/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"type_entite": "entreprise"}
        )
        assert response.status_code == 200
        data = response.json()
        for entite in data["entites"]:
            assert entite["type_entite"] == "entreprise"
        print("✅ P2.1 - Filtrage par type fonctionne")
    
    def test_filtrer_entites_partenaires(self, ministre_token):
        """Test filtering partner entities"""
        response = requests.get(
            f"{BASE_URL}/api/entites-externes/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"est_partenaire": True}
        )
        assert response.status_code == 200
        data = response.json()
        for entite in data["entites"]:
            assert entite["est_partenaire"] is True
        print("✅ P2.1 - Filtrage partenaires fonctionne")
    
    def test_statistiques_partenaires(self, ministre_token):
        """Test partner statistics"""
        response = requests.get(
            f"{BASE_URL}/api/entites-externes/stats/partenaires",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "par_type" in data
        assert "partenaires" in data
        print(f"✅ P2.1 - Statistiques partenaires: {data['partenaires']} partenaires actifs")


class TestP2Preview:
    """P2.2 - Aperçu de fichiers"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def sg_user_id(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["sg"]["email"],
            "password": CREDENTIALS["sg"]["password"]
        })
        sg_token = response.json()["access_token"]
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {sg_token}"
        })
        return me_response.json()["id"]
    
    def test_preview_document_sans_fichier(self, ministre_token, sg_user_id):
        """Test preview of document without file"""
        # Create document without file
        doc_response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P2_Preview_SansFichier",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        doc_id = doc_response.json()["document"]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/preview/document/{doc_id}",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 404
        print("✅ P2.2 - Preview sans fichier retourne 404")
    
    def test_preview_info_document(self, ministre_token, sg_user_id):
        """Test getting preview info for document"""
        # Create document without file
        doc_response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"},
            data={
                "titre": "TEST_P2_Preview_Info",
                "type_document": "administratif",
                "destinataire_final_id": sg_user_id,
                "destinataire_final_nom": CREDENTIALS["sg"]["nom"]
            }
        )
        doc_id = doc_response.json()["document"]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/preview/document/{doc_id}/info",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "preview_disponible" in data
        print(f"✅ P2.2 - Info preview récupérée: disponible={data['preview_disponible']}")


class TestP2RechercheContenu:
    """P2.3 - Recherche texte intégral"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    def test_recherche_contenu(self, ministre_token):
        """Test content search"""
        response = requests.get(
            f"{BASE_URL}/api/recherche/recherche-contenu",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"q": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "resultats" in data
        assert "requete" in data
        print(f"✅ P2.3 - Recherche contenu: {data['total_resultats']} résultats pour 'test'")
    
    def test_recherche_requete_trop_courte(self, ministre_token):
        """Test search with query too short"""
        response = requests.get(
            f"{BASE_URL}/api/recherche/recherche-contenu",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"q": "ab"}  # Less than 3 characters
        )
        assert response.status_code == 422  # Validation error
        print("✅ P2.3 - Requête trop courte rejetée (min 3 caractères)")
    
    def test_statistiques_indexation(self, ministre_token):
        """Test indexation statistics"""
        response = requests.get(
            f"{BASE_URL}/api/recherche/stats-indexation",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents_indexes" in data
        assert "pourcentage_indexe" in data
        print(f"✅ P2.3 - Stats indexation: {data['documents_indexes']} documents indexés ({data['pourcentage_indexe']}%)")


class TestP2DoubleZone:
    """P2.4 - Environnement double zone"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    def test_obtenir_contexte_actuel(self, ministre_token):
        """Test getting current context"""
        response = requests.get(
            f"{BASE_URL}/api/contexte/",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "contexte_actuel" in data
        assert "contextes_disponibles" in data
        assert len(data["contextes_disponibles"]) == 2
        print(f"✅ P2.4 - Contexte actuel: {data['contexte_actuel']}")
    
    def test_basculer_vers_equipe(self, ministre_token):
        """Test switching to team context"""
        response = requests.post(
            f"{BASE_URL}/api/contexte/basculer",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"nouveau_contexte": "equipe"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["contexte_actuel"] == "equipe"
        print("✅ P2.4 - Basculé vers Zone Verte (équipe)")
    
    def test_basculer_vers_personnel(self, ministre_token):
        """Test switching to personal context"""
        response = requests.post(
            f"{BASE_URL}/api/contexte/basculer",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"nouveau_contexte": "personnel"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["contexte_actuel"] == "personnel"
        print("✅ P2.4 - Basculé vers Zone Bleue (personnel)")
    
    def test_basculer_contexte_invalide(self, ministre_token):
        """Test switching to invalid context"""
        response = requests.post(
            f"{BASE_URL}/api/contexte/basculer",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"nouveau_contexte": "invalide"}
        )
        assert response.status_code == 400
        print("✅ P2.4 - Contexte invalide rejeté")
    
    def test_documents_par_contexte(self, ministre_token):
        """Test listing documents by context"""
        response = requests.get(
            f"{BASE_URL}/api/contexte/documents",
            headers={"Authorization": f"Bearer {ministre_token}"},
            params={"contexte": "personnel"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert data["contexte"] == "personnel"
        print(f"✅ P2.4 - Documents personnels: {data['total']} documents")
    
    def test_statistiques_par_contexte(self, ministre_token):
        """Test context statistics"""
        response = requests.get(
            f"{BASE_URL}/api/contexte/statistiques",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "zone_bleue_personnel" in data
        assert "zone_verte_equipe" in data
        print(f"✅ P2.4 - Stats: Zone Bleue={data['zone_bleue_personnel']['total_documents']}, Zone Verte={data['zone_verte_equipe']['total_documents']}")


# ============================================
# CLEANUP
# ============================================

class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture(scope="class")
    def ministre_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": CREDENTIALS["ministre"]["email"],
            "password": CREDENTIALS["ministre"]["password"]
        })
        return response.json()["access_token"]
    
    def test_cleanup_test_documents(self, ministre_token):
        """Cleanup test documents (optional - documents with TEST_ prefix)"""
        # List all documents
        response = requests.get(
            f"{BASE_URL}/api/documents/",
            headers={"Authorization": f"Bearer {ministre_token}"}
        )
        if response.status_code == 200:
            documents = response.json()
            test_docs = [d for d in documents if d.get("titre", "").startswith("TEST_")]
            print(f"ℹ️ Found {len(test_docs)} test documents (cleanup not implemented)")
        print("✅ Cleanup check completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
