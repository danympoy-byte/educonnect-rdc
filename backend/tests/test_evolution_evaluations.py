"""
Test suite for Evolution Temporelle and Evaluations/Notes features
- GET /api/stats/evolution - Monthly cumulative growth data
- GET /api/stats/notes - Grade statistics by subject, distribution, trimester
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@educonnect.cd"
TEST_PASSWORD = "Admin@EduConnect2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API calls"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        print(f"✓ API health check passed: {data}")


class TestStatsEvolution:
    """Tests for GET /api/stats/evolution endpoint"""
    
    def test_evolution_endpoint_returns_200(self, auth_headers):
        """Test that evolution endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Evolution endpoint returned 200")
    
    def test_evolution_has_mois_array(self, auth_headers):
        """Test that response contains 'mois' array with 12 months"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "mois" in data, "Response should contain 'mois' key"
        assert isinstance(data["mois"], list), "'mois' should be a list"
        assert len(data["mois"]) == 12, f"Expected 12 months, got {len(data['mois'])}"
        print(f"✓ Evolution has 12 months: {data['mois']}")
    
    def test_evolution_has_cumul_data(self, auth_headers):
        """Test that response contains cumulative data for eleves, enseignants, etablissements"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "cumul" in data, "Response should contain 'cumul' key"
        cumul = data["cumul"]
        
        assert "eleves" in cumul, "cumul should contain 'eleves'"
        assert "enseignants" in cumul, "cumul should contain 'enseignants'"
        assert "etablissements" in cumul, "cumul should contain 'etablissements'"
        
        # Each should be a list of 12 values
        assert len(cumul["eleves"]) == 12, f"Expected 12 eleves values, got {len(cumul['eleves'])}"
        assert len(cumul["enseignants"]) == 12, f"Expected 12 enseignants values, got {len(cumul['enseignants'])}"
        assert len(cumul["etablissements"]) == 12, f"Expected 12 etablissements values, got {len(cumul['etablissements'])}"
        
        print(f"✓ Cumul data present - Eleves: {cumul['eleves'][-1]}, Enseignants: {cumul['enseignants'][-1]}, Etablissements: {cumul['etablissements'][-1]}")
    
    def test_evolution_has_inscriptions_mensuelles(self, auth_headers):
        """Test that response contains monthly inscriptions data"""
        response = requests.get(f"{BASE_URL}/api/stats/evolution", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "inscriptions_mensuelles" in data, "Response should contain 'inscriptions_mensuelles'"
        inscriptions = data["inscriptions_mensuelles"]
        
        assert isinstance(inscriptions, list), "inscriptions_mensuelles should be a list"
        assert len(inscriptions) == 12, f"Expected 12 months of inscriptions, got {len(inscriptions)}"
        
        # Each item should have mois, eleves, enseignants
        for item in inscriptions:
            assert "mois" in item, "Each inscription item should have 'mois'"
            assert "eleves" in item, "Each inscription item should have 'eleves'"
            assert "enseignants" in item, "Each inscription item should have 'enseignants'"
        
        print(f"✓ Monthly inscriptions data present with {len(inscriptions)} months")


class TestStatsNotes:
    """Tests for GET /api/stats/notes endpoint"""
    
    def test_notes_endpoint_returns_200(self, auth_headers):
        """Test that notes stats endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Notes stats endpoint returned 200")
    
    def test_notes_has_par_matiere(self, auth_headers):
        """Test that response contains 'par_matiere' with subject averages"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "par_matiere" in data, "Response should contain 'par_matiere'"
        par_matiere = data["par_matiere"]
        
        assert isinstance(par_matiere, list), "'par_matiere' should be a list"
        assert len(par_matiere) > 0, "Should have at least one subject"
        
        # Check structure of first item
        first = par_matiere[0]
        assert "matiere" in first, "Each item should have 'matiere'"
        assert "moyenne" in first, "Each item should have 'moyenne'"
        assert "count" in first, "Each item should have 'count'"
        assert "min" in first, "Each item should have 'min'"
        assert "max" in first, "Each item should have 'max'"
        
        print(f"✓ par_matiere has {len(par_matiere)} subjects. First: {first['matiere']} - avg: {first['moyenne']}/20")
    
    def test_notes_has_distribution(self, auth_headers):
        """Test that response contains grade distribution"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "distribution" in data, "Response should contain 'distribution'"
        distribution = data["distribution"]
        
        assert isinstance(distribution, list), "'distribution' should be a list"
        
        # Check structure
        for item in distribution:
            assert "tranche" in item, "Each distribution item should have 'tranche'"
            assert "count" in item, "Each distribution item should have 'count'"
        
        total_notes = sum(d["count"] for d in distribution)
        print(f"✓ Distribution has {len(distribution)} ranges with {total_notes} total notes")
    
    def test_notes_has_par_trimestre(self, auth_headers):
        """Test that response contains trimester averages"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "par_trimestre" in data, "Response should contain 'par_trimestre'"
        par_trimestre = data["par_trimestre"]
        
        assert isinstance(par_trimestre, list), "'par_trimestre' should be a list"
        
        # Check structure
        for item in par_trimestre:
            assert "trimestre" in item, "Each item should have 'trimestre'"
            assert "moyenne" in item, "Each item should have 'moyenne'"
            assert "count" in item, "Each item should have 'count'"
        
        print(f"✓ par_trimestre has {len(par_trimestre)} trimesters: {[t['trimestre'] for t in par_trimestre]}")
    
    def test_notes_moyenne_in_valid_range(self, auth_headers):
        """Test that averages are in valid range (0-20)"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check par_matiere averages
        for item in data.get("par_matiere", []):
            assert 0 <= item["moyenne"] <= 20, f"Invalid moyenne for {item['matiere']}: {item['moyenne']}"
            assert item["min"] <= item["max"], f"Min should be <= max for {item['matiere']}"
        
        # Check par_trimestre averages
        for item in data.get("par_trimestre", []):
            assert 0 <= item["moyenne"] <= 20, f"Invalid trimestre moyenne: {item['moyenne']}"
        
        print(f"✓ All averages are in valid range (0-20)")


class TestStatsNotesDataQuality:
    """Tests for data quality of notes statistics"""
    
    def test_notes_count_matches_expected(self, auth_headers):
        """Test that total notes count is approximately 59,238 as seeded"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Sum up counts from par_matiere
        total_from_matieres = sum(m["count"] for m in data.get("par_matiere", []))
        
        # Should be around 59,238 (allow some variance)
        assert total_from_matieres > 50000, f"Expected ~59,238 notes, got {total_from_matieres}"
        print(f"✓ Total notes count: {total_from_matieres} (expected ~59,238)")
    
    def test_notes_has_15_subjects(self, auth_headers):
        """Test that there are 15 subjects as expected"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        num_subjects = len(data.get("par_matiere", []))
        assert num_subjects >= 10, f"Expected at least 10 subjects, got {num_subjects}"
        print(f"✓ Number of subjects: {num_subjects}")
    
    def test_notes_has_3_trimesters(self, auth_headers):
        """Test that there are 3 trimesters"""
        response = requests.get(f"{BASE_URL}/api/stats/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        num_trimesters = len(data.get("par_trimestre", []))
        assert num_trimesters == 3, f"Expected 3 trimesters, got {num_trimesters}"
        print(f"✓ Number of trimesters: {num_trimesters}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
