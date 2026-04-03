"""
Test suite for Édu-Connect Demo Users (Ephemeral Users) Feature
Tests:
- Demo user generation (POST /api/demo/generer)
- Demo user listing (GET /api/demo/liste)
- Demo user login and 24h expiry
- Demo user deletion (DELETE /api/demo/supprimer)
- Minister login regression
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
MINISTER_PHONE = "+243 820 000 010"
MINISTER_PASSWORD = "Ministre2026!"
DEMO_PASSWORD = "Demo2026!"


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print("✅ Health check passed - API is healthy")


class TestMinisterLogin:
    """Test minister login (regression test)"""
    
    def test_minister_login_success(self):
        """REGRESSION: Normal login with minister credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": MINISTER_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["telephone"] == MINISTER_PHONE
        assert data["user"]["nom"] == "Malu"
        print(f"✅ Minister login successful - User: {data['user']['prenom']} {data['user']['nom']}")
        
        return data["access_token"]
    
    def test_minister_login_invalid_password(self):
        """Test login with wrong password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": "WrongPassword123!"}
        )
        assert response.status_code == 401
        print("✅ Invalid password correctly rejected")


class TestDemoUserGeneration:
    """Test demo user generation endpoint"""
    
    @pytest.fixture
    def minister_session(self):
        """Get authenticated session as minister"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": MINISTER_PASSWORD}
        )
        assert response.status_code == 200, f"Minister login failed: {response.text}"
        return session
    
    def test_generate_demo_users(self, minister_session):
        """NEW FEATURE: Generate 3 demo users"""
        response = minister_session.post(
            f"{BASE_URL}/api/demo/generer",
            json={
                "nombre": 3,
                "service_code": "DGA",
                "password": DEMO_PASSWORD
            }
        )
        assert response.status_code == 200, f"Demo generation failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "comptes" in data
        assert len(data["comptes"]) == 3
        assert data["mot_de_passe_commun"] == DEMO_PASSWORD
        
        # Verify user names
        user_names = [u["nom"] for u in data["comptes"]]
        assert "Test01" in user_names
        assert "Test02" in user_names
        assert "Test03" in user_names
        
        # Verify phone numbers
        phones = [u["telephone"] for u in data["comptes"]]
        assert "+243 900 000 01" in phones
        assert "+243 900 000 02" in phones
        assert "+243 900 000 03" in phones
        
        print(f"✅ Generated {len(data['comptes'])} demo users: {user_names}")
        return data
    
    def test_generate_demo_users_unauthorized(self):
        """Test that unauthenticated users cannot generate demo users"""
        response = requests.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 3, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        assert response.status_code == 401
        print("✅ Unauthorized demo generation correctly rejected")
    
    def test_generate_demo_users_invalid_count(self, minister_session):
        """Test validation of demo user count"""
        # Too many users
        response = minister_session.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 25, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        assert response.status_code == 400
        
        # Zero users
        response = minister_session.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 0, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        assert response.status_code == 400
        print("✅ Invalid demo user count correctly rejected")


class TestDemoUserLogin:
    """Test demo user login and expiry"""
    
    @pytest.fixture
    def setup_demo_users(self):
        """Generate demo users before testing login"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": MINISTER_PASSWORD}
        )
        assert response.status_code == 200
        
        # Generate demo users
        response = session.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 3, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        assert response.status_code == 200
        return session
    
    def test_demo_user_login(self, setup_demo_users):
        """NEW FEATURE: Login as demo user Test01"""
        demo_phone = "+243 900 000 01"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": demo_phone, "password": DEMO_PASSWORD}
        )
        assert response.status_code == 200, f"Demo user login failed: {response.text}"
        data = response.json()
        
        # Verify response
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["nom"] == "Test01"
        assert data["user"]["is_ephemeral"] == True
        
        print(f"✅ Demo user Test01 login successful")
        return data
    
    def test_demo_user_status_after_login(self, setup_demo_users):
        """NEW FEATURE: Verify demo user status shows 'actif' with ~24h remaining"""
        minister_session = setup_demo_users
        
        # First login as demo user to activate the 24h timer
        demo_phone = "+243 900 000 01"
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": demo_phone, "password": DEMO_PASSWORD}
        )
        assert response.status_code == 200
        
        # Now check the list as minister
        response = minister_session.get(f"{BASE_URL}/api/demo/liste")
        assert response.status_code == 200, f"Demo list failed: {response.text}"
        data = response.json()
        
        # Find Test01 in the list
        test01 = None
        for compte in data["comptes"]:
            if compte["nom"] == "Test01":
                test01 = compte
                break
        
        assert test01 is not None, "Test01 not found in demo list"
        assert test01["statut"] == "actif", f"Expected 'actif', got '{test01['statut']}'"
        assert test01["temps_restant"] is not None, "temps_restant should be set"
        assert "h" in test01["temps_restant"], f"Expected time format like '23h59m', got '{test01['temps_restant']}'"
        
        print(f"✅ Demo user Test01 status: {test01['statut']}, temps_restant: {test01['temps_restant']}")


class TestDemoUserListing:
    """Test demo user listing endpoint"""
    
    @pytest.fixture
    def minister_session_with_demos(self):
        """Get authenticated session and generate demo users"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": MINISTER_PASSWORD}
        )
        assert response.status_code == 200
        
        # Generate demo users
        session.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 3, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        return session
    
    def test_list_demo_users(self, minister_session_with_demos):
        """NEW FEATURE: List all demo users"""
        response = minister_session_with_demos.get(f"{BASE_URL}/api/demo/liste")
        assert response.status_code == 200, f"Demo list failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "comptes" in data
        assert "total" in data
        assert data["total"] == 3
        
        # Verify each user has required fields
        for compte in data["comptes"]:
            assert "nom" in compte
            assert "telephone" in compte
            assert "statut" in compte
            assert "service" in compte
        
        print(f"✅ Listed {data['total']} demo users")


class TestDemoUserDeletion:
    """Test demo user deletion endpoint"""
    
    @pytest.fixture
    def minister_session_with_demos(self):
        """Get authenticated session and generate demo users"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": MINISTER_PHONE, "password": MINISTER_PASSWORD}
        )
        assert response.status_code == 200
        
        # Generate demo users
        session.post(
            f"{BASE_URL}/api/demo/generer",
            json={"nombre": 3, "service_code": "DGA", "password": DEMO_PASSWORD}
        )
        return session
    
    def test_delete_demo_users(self, minister_session_with_demos):
        """NEW FEATURE: Delete all demo users"""
        response = minister_session_with_demos.delete(f"{BASE_URL}/api/demo/supprimer")
        assert response.status_code == 200, f"Demo deletion failed: {response.text}"
        data = response.json()
        
        # Verify deletion
        assert "message" in data
        assert "3" in data["message"] or "supprimés" in data["message"]
        
        # Verify users are actually deleted
        response = minister_session_with_demos.get(f"{BASE_URL}/api/demo/liste")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        
        print("✅ All demo users deleted successfully")
    
    def test_delete_demo_users_unauthorized(self):
        """Test that unauthenticated users cannot delete demo users"""
        response = requests.delete(f"{BASE_URL}/api/demo/supprimer")
        assert response.status_code == 401
        print("✅ Unauthorized demo deletion correctly rejected")


class TestServicesEndpoint:
    """Test services endpoint (used by inscription step 2)"""
    
    def test_services_dropdown_cascade(self):
        """BUG FIX: Services dropdown cascade should work without auth"""
        response = requests.get(f"{BASE_URL}/api/services/dropdown-cascade")
        assert response.status_code == 200, f"Services endpoint failed: {response.text}"
        data = response.json()
        
        # Verify we have services (8 Directions Générales)
        assert len(data) >= 8, f"Expected at least 8 DGs, got {len(data)}"
        
        # Verify structure
        for dg in data:
            assert "id" in dg
            assert "nom" in dg
            assert "code" in dg
            assert "niveau" in dg
            assert dg["niveau"] == "niveau_3"
            assert "directions" in dg
        
        # Check for specific DGs
        dg_codes = [dg["code"] for dg in data]
        assert "DGA" in dg_codes, "DGA (Direction Générale de l'Administration) not found"
        
        print(f"✅ Services dropdown cascade returned {len(data)} Directions Générales")
        return data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
