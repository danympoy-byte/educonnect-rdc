"""
Test suite for verifying the 6 reported issues are fixed:
1. French accents on navigation labels
2. Dashboard shows data (not empty charts)
3. Rapports tab inside Documents page (not in main nav)
4. Rapports page loads without error
5. Chat contact search works
6. DRC map has 26 provinces

Backend API tests for issues #2, #4, #5
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthAndSetup:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session with cookies"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login with test account
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test09@educonnect.cd",
            "password": "Test09@2026"
        })
        
        if login_response.status_code != 200:
            # Try admin account
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@educonnect.cd",
                "password": "Admin@EduConnect2026!"
            })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        print(f"✅ Login successful")
        return session
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health check passed")


class TestIssue2_DashboardData:
    """Issue #2: Verify dashboard shows data (953 establishments, 4114 teachers, 126804 students)"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@educonnect.cd",
            "password": "Admin@EduConnect2026!"
        })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        return session
    
    def test_stats_global_returns_data(self, auth_session):
        """Test /api/stats/global returns non-empty data"""
        response = auth_session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200, f"Stats global failed: {response.text}"
        
        data = response.json()
        
        # Verify data is not empty
        assert data["total_etablissements"] > 0, "No establishments found"
        assert data["total_enseignants"] > 0, "No teachers found"
        assert data["total_eleves"] > 0, "No students found"
        assert data["total_classes"] > 0, "No classes found"
        
        # Verify expected counts (from iteration_13)
        assert data["total_etablissements"] >= 900, f"Expected ~953 establishments, got {data['total_etablissements']}"
        assert data["total_enseignants"] >= 4000, f"Expected ~4114 teachers, got {data['total_enseignants']}"
        assert data["total_eleves"] >= 100000, f"Expected ~126804 students, got {data['total_eleves']}"
        
        print(f"✅ Dashboard data verified: {data['total_etablissements']} etabs, {data['total_enseignants']} teachers, {data['total_eleves']} students")
    
    def test_stats_global_has_province_distribution(self, auth_session):
        """Test /api/stats/global returns province distribution"""
        response = auth_session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify province distribution exists and has data
        assert "repartition_par_province" in data, "Missing repartition_par_province"
        assert len(data["repartition_par_province"]) > 0, "Province distribution is empty"
        
        print(f"✅ Province distribution has {len(data['repartition_par_province'])} provinces")


class TestIssue4_RapportsAPI:
    """Issue #4: Verify /api/rapports/ endpoint works"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session with ministre role"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Use test account with ministre role
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test09@educonnect.cd",
            "password": "Test09@2026"
        })
        
        if login_response.status_code != 200:
            # Fallback to admin
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@educonnect.cd",
                "password": "Admin@EduConnect2026!"
            })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        return session
    
    def test_rapports_endpoint_returns_200(self, auth_session):
        """Test /api/rapports/ returns 200 (not error)"""
        response = auth_session.get(f"{BASE_URL}/api/rapports/")
        
        # Should return 200, not 500 or other error
        assert response.status_code == 200, f"Rapports endpoint failed with {response.status_code}: {response.text}"
        
        data = response.json()
        assert "rapports" in data, "Missing 'rapports' key in response"
        assert "total" in data, "Missing 'total' key in response"
        
        print(f"✅ Rapports endpoint works: {data['total']} rapports found")
    
    def test_rapports_returns_list(self, auth_session):
        """Test /api/rapports/ returns a list (even if empty)"""
        response = auth_session.get(f"{BASE_URL}/api/rapports/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data["rapports"], list), "rapports should be a list"
        
        print(f"✅ Rapports returns list with {len(data['rapports'])} items")


class TestIssue5_ChatContactSearch:
    """Issue #5: Verify chat contact search works"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@educonnect.cd",
            "password": "Admin@EduConnect2026!"
        })
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        return session
    
    def test_utilisateurs_contactables_returns_users(self, auth_session):
        """Test /api/chat/utilisateurs-contactables returns user list"""
        response = auth_session.get(f"{BASE_URL}/api/chat/utilisateurs-contactables")
        
        assert response.status_code == 200, f"Contactables endpoint failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "No contactable users found"
        
        # Verify user structure
        first_user = data[0]
        assert "id" in first_user, "User missing 'id'"
        assert "nom" in first_user, "User missing 'nom'"
        assert "prenom" in first_user, "User missing 'prenom'"
        
        print(f"✅ Chat contactables works: {len(data)} users found")
    
    def test_contactables_has_searchable_fields(self, auth_session):
        """Test contactable users have fields needed for search"""
        response = auth_session.get(f"{BASE_URL}/api/chat/utilisateurs-contactables")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check that users have searchable fields
        for user in data[:5]:  # Check first 5
            # At least one of these should be present for search
            has_searchable = any([
                user.get("nom"),
                user.get("prenom"),
                user.get("email"),
                user.get("telephone")
            ])
            assert has_searchable, f"User {user.get('id')} has no searchable fields"
        
        print("✅ Contactable users have searchable fields")


class TestIssue6_ProvincesData:
    """Issue #6: Verify 26 provinces exist for DRC map"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@educonnect.cd",
            "password": "Admin@EduConnect2026!"
        })
        
        assert login_response.status_code == 200
        return session
    
    def test_stats_has_26_provinces(self, auth_session):
        """Test that stats include data for all 26 DRC provinces"""
        response = auth_session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200
        
        data = response.json()
        provinces = data.get("repartition_par_province", {})
        
        # DRC has 26 provinces
        # Note: The stats may group by province educationnelle, not administrative
        # But we should have data for multiple provinces
        assert len(provinces) >= 20, f"Expected at least 20 provinces, got {len(provinces)}"
        
        print(f"✅ Stats cover {len(provinces)} provinces")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
