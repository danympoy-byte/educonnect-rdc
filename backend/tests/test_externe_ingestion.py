"""
Test suite for external data ingestion endpoints (Module 3 - Scolarité)
Tests: POST /api/externe/presences, /api/externe/evaluations, /api/externe/effectifs
       GET /api/externe/sources/status, /api/externe/logs
       Basic Auth verification, logging to logs_api_externe collection
"""
import pytest
import requests
import os
from datetime import datetime
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials - loaded from environment
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@educonnect.cd")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "Admin@EduConnect2026!")
API_CLIENT_USERNAME = os.getenv("TEST_API_CLIENT_USERNAME", "gestion_scolaire_test")
API_CLIENT_PASSWORD = os.getenv("TEST_API_CLIENT_PASSWORD", "TestApiKey2026!")
REAL_ETABLISSEMENT_ID = "cbba70b6-c421-4686-a619-91964953e52d"


class TestBasicAuthRejection:
    """Test that POST endpoints reject requests without Basic Auth"""
    
    def test_presences_without_auth_returns_401(self):
        """POST /api/externe/presences without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/externe/presences",
            json=[{"eleve_id": "test", "date": "2026-01-15", "present": True}],
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/externe/presences without auth returns 401")
    
    def test_evaluations_without_auth_returns_401(self):
        """POST /api/externe/evaluations without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/externe/evaluations",
            json=[{"matiere": "Math", "notes": []}],
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/externe/evaluations without auth returns 401")
    
    def test_effectifs_without_auth_returns_401(self):
        """POST /api/externe/effectifs without auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/externe/effectifs",
            json=[{"etablissement_id": "test", "total_eleves": 100}],
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/externe/effectifs without auth returns 401")
    
    def test_invalid_credentials_returns_401(self):
        """POST with invalid Basic Auth should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/externe/presences",
            json=[{"eleve_id": "test", "date": "2026-01-15", "present": True}],
            headers={"Content-Type": "application/json"},
            auth=("wrong_user", "wrong_password")
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST with invalid credentials returns 401")


class TestPresencesEndpoint:
    """Test POST /api/externe/presences endpoint"""
    
    def test_presences_with_valid_auth_accepts_json(self):
        """POST /api/externe/presences with valid auth should accept JSON array"""
        test_eleve_id = f"TEST_eleve_{uuid.uuid4().hex[:8]}"
        test_classe_id = f"TEST_classe_{uuid.uuid4().hex[:8]}"
        
        payload = [
            {
                "eleve_id": test_eleve_id,
                "classe_id": test_classe_id,
                "etablissement_id": REAL_ETABLISSEMENT_ID,
                "date": "2026-01-15",
                "present": True,
                "justifie": False
            },
            {
                "eleve_id": test_eleve_id,
                "classe_id": test_classe_id,
                "etablissement_id": REAL_ETABLISSEMENT_ID,
                "date": "2026-01-16",
                "present": False,
                "justifie": True,
                "motif": "Maladie"
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/presences",
            json=payload,
            headers={"Content-Type": "application/json"},
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert data.get("success") is True, "Response should have success=True"
        assert "nb_presences_inserees" in data, "Response should have nb_presences_inserees"
        assert data["nb_presences_inserees"] == 2, f"Expected 2 presences inserted, got {data['nb_presences_inserees']}"
        assert "message" in data, "Response should have message"
        
        print(f"✓ POST /api/externe/presences accepted JSON array, inserted {data['nb_presences_inserees']} records")
    
    def test_presences_returns_success_count(self):
        """POST /api/externe/presences should return correct success count"""
        test_eleve_id = f"TEST_eleve_{uuid.uuid4().hex[:8]}"
        
        payload = [
            {"eleve_id": test_eleve_id, "classe_id": "c1", "etablissement_id": REAL_ETABLISSEMENT_ID, "date": "2026-01-17", "present": True},
            {"eleve_id": test_eleve_id, "classe_id": "c1", "etablissement_id": REAL_ETABLISSEMENT_ID, "date": "2026-01-18", "present": True},
            {"eleve_id": test_eleve_id, "classe_id": "c1", "etablissement_id": REAL_ETABLISSEMENT_ID, "date": "2026-01-19", "present": False}
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/presences",
            json=payload,
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nb_presences_inserees"] == 3, f"Expected 3, got {data['nb_presences_inserees']}"
        print(f"✓ Presences endpoint returns correct success count: {data['nb_presences_inserees']}")


class TestEvaluationsEndpoint:
    """Test POST /api/externe/evaluations endpoint"""
    
    def test_evaluations_accepts_grouped_format(self):
        """POST /api/externe/evaluations should accept grouped format with notes array"""
        test_eleve_1 = f"TEST_eleve_{uuid.uuid4().hex[:8]}"
        test_eleve_2 = f"TEST_eleve_{uuid.uuid4().hex[:8]}"
        
        payload = [
            {
                "etablissement_id": REAL_ETABLISSEMENT_ID,
                "classe_id": "TEST_classe_eval",
                "matiere": "Mathematiques",
                "trimestre": "trimestre_1",
                "annee_scolaire": "2025-2026",
                "enseignant_id": "TEST_enseignant",
                "notes": [
                    {"eleve_id": test_eleve_1, "note": 15.5, "commentaire": "Bon travail"},
                    {"eleve_id": test_eleve_2, "note": 12.0, "commentaire": "Peut mieux faire"}
                ]
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/evaluations",
            json=payload,
            headers={"Content-Type": "application/json"},
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert "nb_notes_inserees" in data
        assert data["nb_notes_inserees"] == 2, f"Expected 2 notes inserted, got {data['nb_notes_inserees']}"
        
        print(f"✓ POST /api/externe/evaluations accepted grouped format, inserted {data['nb_notes_inserees']} notes")
    
    def test_evaluations_validates_note_range(self):
        """POST /api/externe/evaluations should reject invalid note values"""
        payload = [
            {
                "etablissement_id": REAL_ETABLISSEMENT_ID,
                "classe_id": "TEST_classe",
                "matiere": "Francais",
                "trimestre": "trimestre_1",
                "annee_scolaire": "2025-2026",
                "enseignant_id": "TEST_ens",
                "notes": [
                    {"eleve_id": "TEST_eleve", "note": 25.0}  # Invalid: > 20
                ]
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/evaluations",
            json=payload,
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200  # Partial success
        data = response.json()
        assert data["nb_erreurs"] > 0, "Should have errors for invalid note"
        print(f"✓ Evaluations endpoint validates note range, reported {data['nb_erreurs']} errors")


class TestEffectifsEndpoint:
    """Test POST /api/externe/effectifs endpoint"""
    
    def test_effectifs_with_valid_etablissement(self):
        """POST /api/externe/effectifs should accept valid etablissement_id"""
        payload = [
            {
                "etablissement_id": REAL_ETABLISSEMENT_ID,
                "total_eleves": 450,
                "total_enseignants": 28,
                "total_classes": 12,
                "date_maj": "2026-01-15",
                "details_par_niveau": {
                    "1ere_annee_primaire": 45,
                    "2eme_annee_primaire": 50
                }
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/effectifs",
            json=payload,
            headers={"Content-Type": "application/json"},
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") is True
        assert "nb_etablissements_traites" in data
        assert data["nb_etablissements_traites"] == 1
        
        print(f"✓ POST /api/externe/effectifs accepted valid etablissement, processed {data['nb_etablissements_traites']}")
    
    def test_effectifs_rejects_invalid_etablissement(self):
        """POST /api/externe/effectifs should reject non-existent etablissement_id"""
        payload = [
            {
                "etablissement_id": "non-existent-id-12345",
                "total_eleves": 100,
                "total_enseignants": 10,
                "total_classes": 5
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/effectifs",
            json=payload,
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200  # Returns 200 with errors
        data = response.json()
        
        assert data["nb_etablissements_traites"] == 0, "Should not process invalid etablissement"
        assert data["nb_erreurs"] > 0, "Should report error for invalid etablissement"
        assert "introuvable" in str(data["erreurs"]).lower() or "not found" in str(data["erreurs"]).lower(), \
            f"Error should mention etablissement not found: {data['erreurs']}"
        
        print(f"✓ Effectifs endpoint rejects invalid etablissement_id with error: {data['erreurs'][0]}")
    
    def test_effectifs_missing_etablissement_id(self):
        """POST /api/externe/effectifs should reject missing etablissement_id"""
        payload = [
            {
                "total_eleves": 100,
                "total_enseignants": 10
            }
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/externe/effectifs",
            json=payload,
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nb_erreurs"] > 0, "Should report error for missing etablissement_id"
        print("✓ Effectifs endpoint reports error for missing etablissement_id")


class TestSourcesStatusEndpoint:
    """Test GET /api/externe/sources/status endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Could not get auth token")
    
    def test_sources_status_returns_all_endpoints(self, auth_token):
        """GET /api/externe/sources/status should return status of all 6 endpoints"""
        response = requests.get(
            f"{BASE_URL}/api/externe/sources/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate structure
        assert "nb_clients_api_actifs" in data
        assert "sources" in data
        assert "stats_globales" in data
        
        # Should have 6 endpoints
        sources = data["sources"]
        assert len(sources) == 6, f"Expected 6 sources, got {len(sources)}"
        
        # Validate each source has required fields
        expected_endpoints = [
            "/api/externe/notes", "/api/externe/evaluations",
            "/api/externe/presences", "/api/externe/effectifs",
            "/api/externe/inscriptions", "/api/externe/affectations"
        ]
        
        actual_endpoints = [s["endpoint"] for s in sources]
        for ep in expected_endpoints:
            assert ep in actual_endpoints, f"Missing endpoint: {ep}"
        
        # Validate source structure
        for source in sources:
            assert "endpoint" in source
            assert "nom" in source
            assert "nb_appels" in source
            assert "nb_enregistrements_total" in source
            assert "dernier_statut" in source
        
        print("✓ GET /api/externe/sources/status returns all 6 endpoints with call counts")
        print(f"  - Active API clients: {data['nb_clients_api_actifs']}")
        print(f"  - Total API calls: {data['stats_globales']['total_appels_api']}")
    
    def test_sources_status_shows_call_counts(self, auth_token):
        """GET /api/externe/sources/status should show accurate call counts"""
        response = requests.get(
            f"{BASE_URL}/api/externe/sources/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        data = response.json()
        
        # Find presences endpoint (we made calls to it)
        presences_source = next((s for s in data["sources"] if s["endpoint"] == "/api/externe/presences"), None)
        assert presences_source is not None
        assert presences_source["nb_appels"] >= 0, "Should have call count"
        assert presences_source["nb_enregistrements_total"] >= 0, "Should have record count"
        
        print(f"✓ Sources status shows call counts - presences: {presences_source['nb_appels']} calls, {presences_source['nb_enregistrements_total']} records")


class TestLogsEndpoint:
    """Test GET /api/externe/logs endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Could not get auth token")
    
    def test_logs_returns_recent_calls(self, auth_token):
        """GET /api/externe/logs should return recent API call logs"""
        response = requests.get(
            f"{BASE_URL}/api/externe/logs?limit=20",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        
        # If we have logs, validate structure
        if data["logs"]:
            log = data["logs"][0]
            assert "endpoint" in log
            assert "timestamp" in log
            assert "statut" in log
            assert "nb_enregistrements" in log
        
        print(f"✓ GET /api/externe/logs returns {data['total']} recent logs")
    
    def test_logs_filter_by_endpoint(self, auth_token):
        """GET /api/externe/logs should filter by endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/presences&limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All logs should be for presences endpoint
        for log in data["logs"]:
            assert log["endpoint"] == "/api/externe/presences", f"Expected presences endpoint, got {log['endpoint']}"
        
        print("✓ Logs endpoint filters by endpoint correctly")


class TestLoggingToCollection:
    """Test that POST endpoints log calls to logs_api_externe collection"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Could not get auth token")
    
    def test_presences_creates_log_entry(self, auth_token):
        """POST /api/externe/presences should create log entry"""
        # Get current log count
        before_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/presences&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        before_count = before_response.json()["total"]
        
        # Make a POST request
        test_id = f"TEST_log_{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/externe/presences",
            json=[{"eleve_id": test_id, "classe_id": "c1", "etablissement_id": REAL_ETABLISSEMENT_ID, "date": "2026-01-20", "present": True}],
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        # Check log count increased
        after_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/presences&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        after_count = after_response.json()["total"]
        
        assert after_count > before_count, f"Log count should increase: before={before_count}, after={after_count}"
        print(f"✓ POST /api/externe/presences creates log entry (count: {before_count} -> {after_count})")
    
    def test_evaluations_creates_log_entry(self, auth_token):
        """POST /api/externe/evaluations should create log entry"""
        before_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/evaluations&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        before_count = before_response.json()["total"]
        
        test_id = f"TEST_log_{uuid.uuid4().hex[:8]}"
        requests.post(
            f"{BASE_URL}/api/externe/evaluations",
            json=[{"matiere": "Test", "notes": [{"eleve_id": test_id, "note": 10}]}],
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        after_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/evaluations&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        after_count = after_response.json()["total"]
        
        assert after_count > before_count, "Log count should increase"
        print("✓ POST /api/externe/evaluations creates log entry")
    
    def test_effectifs_creates_log_entry(self, auth_token):
        """POST /api/externe/effectifs should create log entry"""
        before_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/effectifs&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        before_count = before_response.json()["total"]
        
        requests.post(
            f"{BASE_URL}/api/externe/effectifs",
            json=[{"etablissement_id": REAL_ETABLISSEMENT_ID, "total_eleves": 100}],
            auth=(API_CLIENT_USERNAME, API_CLIENT_PASSWORD)
        )
        
        after_response = requests.get(
            f"{BASE_URL}/api/externe/logs?endpoint=/api/externe/effectifs&limit=100",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        after_count = after_response.json()["total"]
        
        assert after_count > before_count, "Log count should increase"
        print("✓ POST /api/externe/effectifs creates log entry")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
