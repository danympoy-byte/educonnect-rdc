"""
Tests for GED (Gestion Électronique de Documents) Template functionality
- Test creating documents with save_as_template
- Test listing templates
- Test loading from template when creating new document
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials - use environment variables for security
TEST_EMAIL = os.environ.get('TEST_EMAIL', 'admin@rie.cd')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD', 'test_password_placeholder')


class TestGEDTemplates:
    """Test GED Template functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    @pytest.fixture(scope="class")
    def user_info(self, auth_token):
        """Get current user info"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        return response.json()
    
    def test_01_login_success(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful for {TEST_EMAIL}")
    
    def test_02_list_templates_empty_or_existing(self, auth_headers):
        """Test listing templates endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/documents/templates/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Templates should be a list"
        print(f"✓ Templates list returned {len(data)} templates")
    
    def test_03_create_document_as_template(self, auth_headers, user_info):
        """Test creating a document and saving it as a template"""
        # Get a user to be the destinataire
        user_id = user_info.get("id")
        user_nom = f"{user_info.get('prenom', '')} {user_info.get('nom', '')}"
        
        # Create document as template using form data
        form_data = {
            "titre": "TEST_Template_Circulaire_Administrative",
            "description": "Modèle de circulaire administrative pour tests",
            "type_document": "administratif",
            "categorie": "circulaire",
            "destinataire_final_id": user_id,
            "destinataire_final_nom": user_nom,
            "circuit_validation": "",
            "niveau_diffusion": "service",
            "mode_livraison": "interne",
            "niveau_confidentialite": "public",
            "necessite_signature": "false",
            "cc_user_ids": "",
            "mots_cles": "test,template,circulaire",
            "save_as_template": "true",
            "template_name": "TEST_Circulaire_Type",
            "template_description": "Modèle de circulaire pour tests automatisés"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers=auth_headers,
            data=form_data
        )
        
        assert response.status_code == 200, f"Create template failed: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        
        # Verify template fields
        assert doc["is_template"] == True, "Document should be marked as template"
        assert doc["template_name"] == "TEST_Circulaire_Type"
        assert doc["template_description"] == "Modèle de circulaire pour tests automatisés"
        assert doc["type_document"] == "administratif"
        
        print(f"✓ Template created: {doc['numero_reference']} - {doc['template_name']}")
        return doc["id"]
    
    def test_04_verify_template_in_list(self, auth_headers):
        """Verify the created template appears in templates list"""
        response = requests.get(
            f"{BASE_URL}/api/documents/templates/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        templates = response.json()
        
        # Find our test template
        test_templates = [t for t in templates if t.get("template_name") == "TEST_Circulaire_Type"]
        assert len(test_templates) > 0, "Test template not found in list"
        
        template = test_templates[0]
        assert template["is_template"] == True
        assert template["type_document"] == "administratif"
        
        print(f"✓ Template found in list: {template['template_name']}")
        return template["id"]
    
    def test_05_create_document_from_template(self, auth_headers, user_info):
        """Test creating a new document by loading from a template
        
        NOTE: Currently type_document is required by the API even when loading from template.
        This is a known limitation - the frontend pre-fills the field from template before submission.
        """
        # First get the template ID
        response = requests.get(
            f"{BASE_URL}/api/documents/templates/list",
            headers=auth_headers
        )
        assert response.status_code == 200
        templates = response.json()
        
        test_templates = [t for t in templates if t.get("template_name") == "TEST_Circulaire_Type"]
        assert len(test_templates) > 0, "Test template not found"
        template = test_templates[0]
        template_id = template["id"]
        
        # Create new document from template
        # Note: type_document must be provided (required field) - frontend pre-fills from template
        user_id = user_info.get("id")
        user_nom = f"{user_info.get('prenom', '')} {user_info.get('nom', '')}"
        
        form_data = {
            "titre": "TEST_Document_From_Template",
            "description": template.get("description", ""),  # Pre-filled from template
            "type_document": template.get("type_document", "administratif"),  # Pre-filled from template (required)
            "categorie": template.get("categorie", ""),  # Pre-filled from template
            "destinataire_final_id": user_id,
            "destinataire_final_nom": user_nom,
            "circuit_validation": "",
            "niveau_diffusion": "prive",
            "mode_livraison": "interne",
            "niveau_confidentialite": "public",
            "necessite_signature": "false",
            "cc_user_ids": "",
            "mots_cles": "",
            "save_as_template": "false",
            "load_from_template_id": template_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/",
            headers=auth_headers,
            data=form_data
        )
        
        assert response.status_code == 200, f"Create from template failed: {response.text}"
        data = response.json()
        assert "document" in data
        doc = data["document"]
        
        # Verify document is NOT a template
        assert doc["is_template"] == False, "Document should not be a template"
        
        # Verify title was provided (not from template)
        assert doc["titre"] == "TEST_Document_From_Template"
        
        # Verify type_document matches template
        assert doc["type_document"] == template.get("type_document", "administratif")
        
        print(f"✓ Document created from template: {doc['numero_reference']}")
    
    def test_06_list_all_documents(self, auth_headers):
        """Test listing all documents"""
        response = requests.get(
            f"{BASE_URL}/api/documents/",
            headers=auth_headers
        )
        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)
        
        # Find our test documents
        test_docs = [d for d in documents if d.get("titre", "").startswith("TEST_")]
        print(f"✓ Found {len(test_docs)} test documents out of {len(documents)} total")
    
    def test_07_get_document_details(self, auth_headers):
        """Test getting document details"""
        # First get a document ID
        response = requests.get(
            f"{BASE_URL}/api/documents/",
            headers=auth_headers
        )
        assert response.status_code == 200
        documents = response.json()
        
        if len(documents) > 0:
            doc_id = documents[0]["id"]
            response = requests.get(
                f"{BASE_URL}/api/documents/{doc_id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "document" in data
            assert "historique" in data
            print(f"✓ Document details retrieved: {data['document']['numero_reference']}")
    
    def test_08_get_dashboard_stats(self, auth_headers):
        """Test getting dashboard statistics"""
        response = requests.get(
            f"{BASE_URL}/api/documents/stats/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        stats = response.json()
        
        assert "en_attente" in stats
        assert "mes_documents" in stats
        assert "traites" in stats
        
        print(f"✓ Dashboard stats: {stats}")


class TestReactRouterNavigation:
    """Test React Router navigation endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_provinces_endpoint(self, auth_headers):
        """Test provinces endpoint for navigation"""
        response = requests.get(f"{BASE_URL}/api/provinces", headers=auth_headers)
        assert response.status_code == 200
        print(f"✓ Provinces endpoint: {len(response.json())} provinces")
    
    def test_etablissements_endpoint(self, auth_headers):
        """Test etablissements endpoint for navigation"""
        response = requests.get(f"{BASE_URL}/api/etablissements", headers=auth_headers)
        assert response.status_code == 200
        print(f"✓ Etablissements endpoint: {len(response.json())} etablissements")
    
    def test_sous_divisions_endpoint(self, auth_headers):
        """Test sous-divisions endpoint for navigation"""
        response = requests.get(f"{BASE_URL}/api/sous-divisions", headers=auth_headers)
        assert response.status_code == 200
        print(f"✓ Sous-divisions endpoint: {len(response.json())} sous-divisions")
    
    def test_stats_global_endpoint(self, auth_headers):
        """Test global stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        assert response.status_code == 200
        stats = response.json()
        assert "total_etablissements" in stats
        print(f"✓ Global stats: {stats['total_etablissements']} etablissements")
    
    def test_stats_sexe_endpoint(self, auth_headers):
        """Test sexe stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats/sexe", headers=auth_headers)
        assert response.status_code == 200
        print("✓ Sexe stats endpoint working")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check: healthy")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
