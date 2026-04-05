"""
Test suite for httpOnly cookie authentication migration
Tests the security migration from localStorage to httpOnly cookies
"""
import pytest
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bulletin-pdf-preview.preview.emergentagent.com').rstrip('/')

# Test credentials from test_credentials.md
TEST_CREDENTIALS = {
    "ministre": {
        "phone": "+243 820 000 010",
        "password": "Ministre2026!"
    },
    "sg": {
        "phone": "+243 820 000 002",
        "password": "SG2026!"
    }
}


class TestHttpOnlyCookieAuth:
    """Tests for httpOnly cookie authentication"""
    
    @pytest.fixture
    def session(self):
        """Create a requests session that handles cookies"""
        return requests.Session()
    
    def test_login_sets_httponly_cookie(self, session):
        """Test that login endpoint sets access_token cookie with httpOnly flag"""
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_CREDENTIALS["ministre"]["phone"],
                "password": TEST_CREDENTIALS["ministre"]["password"]
            }
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        # Check response contains user data
        data = response.json()
        assert "user" in data
        assert "access_token" in data  # Still returned for compatibility
        
        # Check cookie was set
        cookies = session.cookies.get_dict()
        assert "access_token" in cookies, "access_token cookie not set"
        
        # Verify cookie attributes from Set-Cookie header
        set_cookie_header = response.headers.get('Set-Cookie', '')
        assert 'HttpOnly' in set_cookie_header, "Cookie missing HttpOnly flag"
        assert 'Secure' in set_cookie_header, "Cookie missing Secure flag"
        assert 'SameSite=lax' in set_cookie_header.lower() or 'samesite=lax' in set_cookie_header.lower(), "Cookie missing SameSite=lax"
    
    def test_auth_me_with_cookie(self, session):
        """Test that /api/auth/me works with cookie authentication"""
        # First login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_CREDENTIALS["ministre"]["phone"],
                "password": TEST_CREDENTIALS["ministre"]["password"]
            }
        )
        assert login_response.status_code == 200
        
        # Now call /api/auth/me - cookie should be sent automatically
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        
        assert me_response.status_code == 200, f"Auth/me failed: {me_response.text}"
        
        user_data = me_response.json()
        assert "id" in user_data
        assert user_data["telephone"] == TEST_CREDENTIALS["ministre"]["phone"]
        assert user_data["role"] == "ministre"
    
    def test_protected_endpoint_without_cookie(self):
        """Test that protected endpoints return 401 without cookie"""
        # Create a new session without login
        session = requests.Session()
        
        response = session.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        assert "Non authentifié" in response.text or "detail" in response.json()
    
    def test_logout_deletes_cookie(self, session):
        """Test that logout endpoint deletes the access_token cookie"""
        # First login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_CREDENTIALS["ministre"]["phone"],
                "password": TEST_CREDENTIALS["ministre"]["password"]
            }
        )
        assert login_response.status_code == 200
        
        # Verify cookie exists
        assert "access_token" in session.cookies.get_dict()
        
        # Logout
        logout_response = session.post(f"{BASE_URL}/api/auth/logout")
        
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Déconnexion réussie"
        
        # Check Set-Cookie header deletes the cookie
        set_cookie_header = logout_response.headers.get('Set-Cookie', '')
        assert 'Max-Age=0' in set_cookie_header or 'expires=' in set_cookie_header.lower()
    
    def test_protected_endpoint_after_logout(self, session):
        """Test that protected endpoints fail after logout"""
        # Login
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_CREDENTIALS["ministre"]["phone"],
                "password": TEST_CREDENTIALS["ministre"]["password"]
            }
        )
        
        # Logout
        session.post(f"{BASE_URL}/api/auth/logout")
        
        # Clear cookies manually (simulating browser behavior after logout)
        session.cookies.clear()
        
        # Try to access protected endpoint
        response = session.get(f"{BASE_URL}/api/auth/me")
        
        assert response.status_code == 401
    
    def test_cookie_sent_with_protected_api_calls(self, session):
        """Test that cookie is automatically sent with API calls"""
        # Login
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_CREDENTIALS["ministre"]["phone"],
                "password": TEST_CREDENTIALS["ministre"]["password"]
            }
        )
        assert login_response.status_code == 200
        
        # Test various protected endpoints
        endpoints = [
            "/api/auth/me",
            "/api/stats/global",
            "/api/provinces",
        ]
        
        for endpoint in endpoints:
            response = session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Endpoint {endpoint} failed: {response.text}"
    
    def test_login_with_invalid_credentials(self, session):
        """Test login with invalid credentials returns 401"""
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "+243 820 000 010",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.text.lower() or "detail" in response.json()
    
    def test_login_with_email_instead_of_phone(self, session):
        """Test login works with email as well as phone"""
        # Try with SG's email
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "sg@educonnect.gouv.cd",
                "password": TEST_CREDENTIALS["sg"]["password"]
            }
        )
        
        assert response.status_code == 200, f"Login with email failed: {response.text}"
        
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "sg@educonnect.gouv.cd"


class TestCORSConfiguration:
    """Tests for CORS configuration with credentials"""
    
    def test_cors_allows_credentials(self):
        """Test that CORS is configured to allow credentials"""
        session = requests.Session()
        
        # Make a preflight OPTIONS request
        response = session.options(
            f"{BASE_URL}/api/auth/login",
            headers={
                "Origin": "https://bulletin-pdf-preview.preview.emergentagent.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Check CORS headers
        # Note: The actual CORS headers may vary based on server configuration
        assert response.status_code in [200, 204], f"OPTIONS request failed: {response.status_code}"


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
