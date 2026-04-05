"""
Test file for Iteration 15 - Testing 5 reported issues:
1. Mutations page - GET /api/sirh/mutations should return 200
2. French accents on Partage de Données page
3. Dashboard shows data (953 etabs, 4114 teachers, 126804 students)
4. Chat contacts search
5. Map provinces data
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestIssue1Mutations:
    """Issue #1: Mutations page - GET /api/sirh/mutations should return 200"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth cookies"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@educonnect.cd", "password": "Admin@EduConnect2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.auth_data = login_response.json()
    
    def test_mutations_endpoint_returns_200(self):
        """Test that /api/sirh/mutations returns 200 (not 500)"""
        response = self.session.get(f"{BASE_URL}/api/sirh/mutations")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data, "Response should have 'total' field"
        assert "mutations" in data, "Response should have 'mutations' field"
        assert isinstance(data["mutations"], list), "mutations should be a list"
        print(f"✓ Mutations endpoint returns 200 with {data['total']} mutations")


class TestIssue3DashboardData:
    """Issue #3: Dashboard shows data - verify stats"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth cookies"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@educonnect.cd", "password": "Admin@EduConnect2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    def test_global_stats_returns_expected_data(self):
        """Test that /api/stats/global returns expected counts"""
        response = self.session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify expected counts
        assert data.get("total_etablissements") == 953, f"Expected 953 establishments, got {data.get('total_etablissements')}"
        assert data.get("total_enseignants") == 4114, f"Expected 4114 teachers, got {data.get('total_enseignants')}"
        assert data.get("total_eleves") == 126804, f"Expected 126804 students, got {data.get('total_eleves')}"
        assert data.get("total_classes") == 3276, f"Expected 3276 classes, got {data.get('total_classes')}"
        
        print(f"✓ Dashboard stats: {data['total_etablissements']} etabs, {data['total_enseignants']} teachers, {data['total_eleves']} students, {data['total_classes']} classes")
    
    def test_global_stats_has_province_distribution(self):
        """Test that stats include province distribution for charts"""
        response = self.session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200
        
        data = response.json()
        assert "repartition_par_province" in data, "Should have province distribution"
        
        provinces = data["repartition_par_province"]
        assert len(provinces) == 26, f"Expected 26 provinces, got {len(provinces)}"
        
        # Check some specific provinces
        assert "Kinshasa" in provinces, "Should have Kinshasa"
        assert provinces["Kinshasa"] > 0, "Kinshasa should have establishments"
        
        print(f"✓ Province distribution has {len(provinces)} provinces")


class TestIssue4ChatContacts:
    """Issue #4: Chat contacts search - verify contacts load"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth cookies"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@educonnect.cd", "password": "Admin@EduConnect2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    def test_contactable_users_returns_list(self):
        """Test that /api/chat/utilisateurs-contactables returns user list"""
        response = self.session.get(f"{BASE_URL}/api/chat/utilisateurs-contactables")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one contactable user"
        
        # Verify user structure
        first_user = data[0]
        assert "id" in first_user, "User should have id"
        assert "nom" in first_user, "User should have nom"
        assert "prenom" in first_user, "User should have prenom"
        
        print(f"✓ Contactable users: {len(data)} users found")
    
    def test_contactable_users_have_searchable_fields(self):
        """Test that users have fields for search functionality"""
        response = self.session.get(f"{BASE_URL}/api/chat/utilisateurs-contactables")
        assert response.status_code == 200
        
        data = response.json()
        for user in data[:5]:  # Check first 5 users
            # At least one of these should be present for search
            has_searchable = any([
                user.get("nom"),
                user.get("prenom"),
                user.get("email"),
                user.get("telephone")
            ])
            assert has_searchable, f"User {user.get('id')} should have searchable fields"
        
        print("✓ Users have searchable fields (nom, prenom, email, telephone)")


class TestIssue5MapProvinces:
    """Issue #5: Map provinces - verify province data structure"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth cookies"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@educonnect.cd", "password": "Admin@EduConnect2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    def test_provinces_endpoint_returns_data(self):
        """Test that /api/provinces returns province list"""
        response = self.session.get(f"{BASE_URL}/api/provinces")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Could be list or dict with provinces key
        if isinstance(data, dict):
            provinces = data.get("provinces", data.get("items", []))
        else:
            provinces = data
        
        assert len(provinces) > 0, "Should have provinces"
        print(f"✓ Provinces endpoint returns {len(provinces)} provinces")
    
    def test_stats_has_province_data_for_map(self):
        """Test that stats endpoint has province data for map display"""
        response = self.session.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code == 200
        
        data = response.json()
        assert "repartition_par_province" in data, "Should have province distribution"
        
        # The map uses static PROVINCES_EDUCATIONNELLES data, but backend should have matching provinces
        provinces = data["repartition_par_province"]
        
        # Check that key provinces exist
        expected_provinces = ["Kinshasa", "Nord-Kivu", "Sud-Kivu", "Haut-Katanga"]
        for prov in expected_provinces:
            assert prov in provinces, f"Province {prov} should be in distribution"
        
        print(f"✓ Stats has province data for map with {len(provinces)} provinces")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✓ Health endpoint returns 200")
    
    def test_login_with_admin_credentials(self):
        """Test login with admin credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@educonnect.cd", "password": "Admin@EduConnect2026!"}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data, "Should have access_token"
        assert "user" in data, "Should have user info"
        assert data["user"]["email"] == "admin@educonnect.cd"
        
        print("✓ Admin login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
