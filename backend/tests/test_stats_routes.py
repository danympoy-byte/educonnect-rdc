"""
Test suite for stats routes (routes_stats.py)
Tests the 5 stats endpoints extracted from server.py:
- /api/stats/global
- /api/stats/sexe
- /api/stats/evolution
- /api/stats/notes
- /api/stats/province/{province_id}
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@educonnect.cd"
ADMIN_PASSWORD = "Admin@EduConnect2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestStatsGlobal:
    """Tests for /api/stats/global endpoint"""
    
    def test_stats_global_returns_200(self, auth_headers):
        """Test that global stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_stats_global_has_required_fields(self, auth_headers):
        """Test that global stats has all required fields"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        data = response.json()
        
        required_fields = [
            "total_etablissements",
            "total_enseignants",
            "total_eleves",
            "total_eleves_primaire",
            "total_eleves_secondaire",
            "total_classes",
            "repartition_par_province",
            "repartition_par_niveau"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_stats_global_has_26_provinces(self, auth_headers):
        """Test that repartition_par_province has 26 entries (all DRC provinces)"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        data = response.json()
        
        provinces = data.get("repartition_par_province", {})
        assert len(provinces) == 26, f"Expected 26 provinces, got {len(provinces)}"
    
    def test_stats_global_has_953_etablissements(self, auth_headers):
        """Test that total_etablissements is 953 as expected"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        data = response.json()
        
        assert data["total_etablissements"] == 953, f"Expected 953 etablissements, got {data['total_etablissements']}"
    
    def test_stats_global_counts_are_positive(self, auth_headers):
        """Test that all counts are positive integers"""
        response = requests.get(f"{BASE_URL}/api/stats/global", headers=auth_headers)
        data = response.json()
        
        assert data["total_etablissements"] > 0
        assert data["total_enseignants"] > 0
        assert data["total_eleves"] > 0
        assert data["total_classes"] > 0


class TestStatsNotes:
    """Tests for /api/stats/notes endpoint"""
    
    def test_stats_notes_returns_200(self, auth_headers):
        """Test that notes stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_stats_notes_has_required_structure(self, auth_headers):
        """Test that notes stats has par_matiere, distribution, par_trimestre arrays"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        data = response.json()
        
        assert "par_matiere" in data, "Missing par_matiere"
        assert "distribution" in data, "Missing distribution"
        assert "par_trimestre" in data, "Missing par_trimestre"
        
        assert isinstance(data["par_matiere"], list), "par_matiere should be a list"
        assert isinstance(data["distribution"], list), "distribution should be a list"
        assert isinstance(data["par_trimestre"], list), "par_trimestre should be a list"
    
    def test_stats_notes_par_matiere_has_data(self, auth_headers):
        """Test that par_matiere has data with correct structure"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        data = response.json()
        
        assert len(data["par_matiere"]) > 0, "par_matiere should have data"
        
        # Check first item structure
        first_item = data["par_matiere"][0]
        assert "matiere" in first_item
        assert "moyenne" in first_item
        assert "count" in first_item
    
    def test_stats_notes_par_trimestre_has_data(self, auth_headers):
        """Test that par_trimestre has data"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        data = response.json()
        
        assert len(data["par_trimestre"]) > 0, "par_trimestre should have data"


class TestStatsEvolution:
    """Tests for /api/stats/evolution endpoint"""
    
    def test_stats_evolution_returns_200(self, auth_headers):
        """Test that evolution stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    def test_stats_evolution_has_mois_array(self, auth_headers):
        """Test that evolution stats has mois array with 12 months"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        data = response.json()
        
        assert "mois" in data, "Missing mois"
        assert isinstance(data["mois"], list), "mois should be a list"
        assert len(data["mois"]) == 12, f"Expected 12 months, got {len(data['mois'])}"
    
    def test_stats_evolution_has_cumul_data(self, auth_headers):
        """Test that evolution stats has cumul data with eleves, enseignants, etablissements"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        data = response.json()
        
        assert "cumul" in data, "Missing cumul"
        cumul = data["cumul"]
        
        assert "eleves" in cumul, "Missing cumul.eleves"
        assert "enseignants" in cumul, "Missing cumul.enseignants"
        assert "etablissements" in cumul, "Missing cumul.etablissements"
        
        # Each should have 12 data points
        assert len(cumul["eleves"]) == 12
        assert len(cumul["enseignants"]) == 12
        assert len(cumul["etablissements"]) == 12


class TestStatsProvinceNew:
    """Tests for /api/stats/province/{province_id} - NEW provinces (16 newly seeded)"""
    
    def test_province_maniema_returns_200(self, auth_headers):
        """Test that Maniema province stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/province/maniema", headers=auth_headers)
        assert response.status_code == 200
    
    def test_province_maniema_has_nonzero_counts(self, auth_headers):
        """Test that Maniema (new province) has non-zero counts"""
        response = requests.get(f"{BASE_URL}/api/stats/province/maniema", headers=auth_headers)
        data = response.json()
        
        assert data["province_id"] == "maniema"
        assert data["total_etablissements"] > 0, "Maniema should have etablissements"
        assert data["total_enseignants"] > 0, "Maniema should have enseignants"
        assert data["total_eleves"] > 0, "Maniema should have eleves"
    
    def test_province_sankuru_has_nonzero_counts(self, auth_headers):
        """Test that Sankuru (new province) has non-zero counts"""
        response = requests.get(f"{BASE_URL}/api/stats/province/sankuru", headers=auth_headers)
        data = response.json()
        
        assert data["province_id"] == "sankuru"
        assert data["total_etablissements"] > 0, "Sankuru should have etablissements"
        assert data["total_enseignants"] > 0, "Sankuru should have enseignants"
        assert data["total_eleves"] > 0, "Sankuru should have eleves"
    
    def test_province_lualaba_has_nonzero_counts(self, auth_headers):
        """Test that Lualaba (new province) has non-zero counts"""
        response = requests.get(f"{BASE_URL}/api/stats/province/lualaba", headers=auth_headers)
        data = response.json()
        
        assert data["province_id"] == "lualaba"
        assert data["total_etablissements"] > 0, "Lualaba should have etablissements"
        assert data["total_enseignants"] > 0, "Lualaba should have enseignants"
        assert data["total_eleves"] > 0, "Lualaba should have eleves"


class TestStatsProvinceExisting:
    """Tests for /api/stats/province/{province_id} - EXISTING provinces"""
    
    def test_province_kinshasa_returns_200(self, auth_headers):
        """Test that Kinshasa province stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/province/kinshasa", headers=auth_headers)
        assert response.status_code == 200
    
    def test_province_kinshasa_has_nonzero_counts(self, auth_headers):
        """Test that Kinshasa (existing province) has non-zero counts"""
        response = requests.get(f"{BASE_URL}/api/stats/province/kinshasa", headers=auth_headers)
        data = response.json()
        
        assert data["province_id"] == "kinshasa"
        assert data["total_etablissements"] > 0, "Kinshasa should have etablissements"
        assert data["total_enseignants"] > 0, "Kinshasa should have enseignants"
        assert data["total_eleves"] > 0, "Kinshasa should have eleves"
    
    def test_province_response_structure(self, auth_headers):
        """Test that province stats response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/stats/province/kinshasa", headers=auth_headers)
        data = response.json()
        
        required_fields = ["province_id", "total_etablissements", "total_enseignants", "total_eleves"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestStatsAuthentication:
    """Tests for authentication requirements on stats endpoints"""
    
    def test_stats_global_requires_auth(self):
        """Test that global stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stats/global")
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_stats_notes_requires_auth(self):
        """Test that notes stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stats/notes")
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_stats_evolution_requires_auth(self):
        """Test that evolution stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution")
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_stats_province_requires_auth(self):
        """Test that province stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stats/province/kinshasa")
        assert response.status_code in [401, 403], "Should require authentication"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
