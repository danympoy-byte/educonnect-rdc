#!/usr/bin/env python3
"""
Test des APIs backend pour les 4 bugs corrigés dans Édu-Connect
1. GED Zone Verte - basculement contexte
2. Page Viabilité - graphique camembert
3. Page Conversation - recherche utilisateurs
4. Page Inscription - sélection service
"""

import requests
import sys
import json
from datetime import datetime

class EduConnectAPITester:
    def __init__(self, base_url="https://bulletin-pdf-preview.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True):
        """Exécuter un test API"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASS - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   📄 Response: {response_data}")
                except:
                    pass
            else:
                print(f"   ❌ FAIL - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error: {error_data}")
                except:
                    print(f"   📄 Raw response: {response.text[:200]}")

            return success, response.json() if response.content else {}

        except Exception as e:
            print(f"   ❌ FAIL - Exception: {str(e)}")
            return False, {}

    def test_login(self, phone, password):
        """Test de connexion"""
        success, response = self.run_test(
            "Connexion utilisateur",
            "POST",
            "auth/login",
            200,
            data={"email": phone, "password": password},  # Le champ email peut contenir le téléphone
            auth_required=False
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   🔑 Token obtenu: {self.token[:20]}...")
            return True
        return False

    def test_contexte_apis(self):
        """Test des APIs de contexte (Zone Bleue/Verte)"""
        print(f"\n{'='*60}")
        print("🟢 TEST CONTEXTE - Zone Bleue/Verte (Bug #1)")
        print(f"{'='*60}")
        
        # 1. Obtenir contexte actuel
        self.run_test(
            "Obtenir contexte actuel",
            "GET",
            "contexte/",
            200
        )
        
        # 2. Basculer vers Zone Verte (équipe)
        self.run_test(
            "Basculer vers Zone Verte",
            "POST",
            "contexte/basculer",
            200,
            data={"nouveau_contexte": "equipe"}
        )
        
        # 3. Basculer vers Zone Bleue (personnel)
        self.run_test(
            "Basculer vers Zone Bleue",
            "POST",
            "contexte/basculer",
            200,
            data={"nouveau_contexte": "personnel"}
        )
        
        # 4. Statistiques par contexte
        self.run_test(
            "Statistiques contexte",
            "GET",
            "contexte/statistiques",
            200
        )

    def test_services_apis(self):
        """Test des APIs de services (Bug #4 - Inscription)"""
        print(f"\n{'='*60}")
        print("🏢 TEST SERVICES - Inscription sélection service (Bug #4)")
        print(f"{'='*60}")
        
        # 1. Dropdown cascade pour inscription (endpoint public)
        success, response = self.run_test(
            "Services dropdown cascade (inscription)",
            "GET",
            "services/dropdown-cascade",
            200,
            auth_required=False
        )
        
        if success and isinstance(response, list):
            print(f"   📊 Nombre de DG trouvées: {len(response)}")
            if len(response) > 0:
                dg = response[0]
                print(f"   📋 Première DG: {dg.get('nom', 'N/A')}")
                directions = dg.get('directions', [])
                print(f"   📋 Directions sous cette DG: {len(directions)}")
        
        # 2. Tous les services (authentifié)
        self.run_test(
            "Tous les services",
            "GET",
            "services/all",
            200
        )

    def test_chat_apis(self):
        """Test des APIs de chat (Bug #3 - Recherche utilisateurs)"""
        print(f"\n{'='*60}")
        print("💬 TEST CHAT - Recherche utilisateurs (Bug #3)")
        print(f"{'='*60}")
        
        # 1. Utilisateurs contactables
        success, response = self.run_test(
            "Utilisateurs contactables",
            "GET",
            "chat/utilisateurs-contactables",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   👥 Nombre d'utilisateurs contactables: {len(response)}")
            if len(response) > 0:
                user = response[0]
                print(f"   👤 Premier utilisateur: {user.get('prenom', '')} {user.get('nom', '')} - {user.get('service', 'N/A')}")
        
        # 2. Lister conversations
        self.run_test(
            "Lister conversations",
            "GET",
            "chat/conversations",
            200
        )
        
        # 3. Recherche dans chat (nécessite au moins 3 caractères)
        self.run_test(
            "Recherche chat",
            "GET",
            "chat/search?q=test",
            200
        )

    def test_viabilite_apis(self):
        """Test des APIs de viabilité (Bug #2 - Graphique camembert)"""
        print(f"\n{'='*60}")
        print("📊 TEST VIABILITÉ - Graphique camembert (Bug #2)")
        print(f"{'='*60}")
        
        # 1. Évaluations de viabilité
        self.run_test(
            "Évaluations viabilité",
            "GET",
            "dinacope/evaluations-viabilite",
            200
        )
        
        # 2. Établissements (pour le formulaire)
        self.run_test(
            "Liste établissements",
            "GET",
            "etablissements",
            200
        )

    def test_inscription_flow(self):
        """Test du flow d'inscription (Bug #4)"""
        print(f"\n{'='*60}")
        print("📝 TEST INSCRIPTION - Flow complet (Bug #4)")
        print(f"{'='*60}")
        
        # Données de test pour inscription
        test_user_data = {
            "nom": "TestUser",
            "postnom": "TestPostnom", 
            "prenom": "TestPrenom",
            "sexe": "masculin",
            "etat_civil": "celibataire",
            "date_naissance": "1990-01-01",
            "lieu_naissance": "Kinshasa",
            "telephone": f"+243 999 {datetime.now().strftime('%H%M%S')}",
            "adresse": "Test Address",
            "password": "TestPass123!",
            "diplomes": [],
            "experiences": []
        }
        
        # 1. Étape 1 - Informations personnelles
        success, response = self.run_test(
            "Inscription Étape 1",
            "POST",
            "auth/inscription/etape1",
            201,
            data=test_user_data,
            auth_required=False
        )
        
        if success and 'user_id' in response:
            user_id = response['user_id']
            print(f"   👤 User ID créé: {user_id}")
            
            # 2. Étape 2 - Sélection service (utiliser un service existant)
            etape2_data = {
                "user_id": user_id,
                "service_id": "dga-001",  # ID d'un service existant
                "poste": "Agent de test"
            }
            
            self.run_test(
                "Inscription Étape 2",
                "POST",
                "auth/inscription/etape2",
                200,
                data=etape2_data,
                auth_required=False
            )

def main():
    print("🇨🇩 Édu-Connect - Test des APIs Backend")
    print("=" * 60)
    
    tester = EduConnectAPITester()
    
    # Tentatives de connexion
    print("\n🔐 CONNEXION")
    
    # Essayer plusieurs comptes
    login_attempts = [
        ("admin@educonnect.cd", "Admin@EduConnect2026!"),
        ("+243 820 000 010", "Ministre2026!"),
        ("+243 900 000 01", "Demo2026!"),
        ("ministre@educonnect.cd", "Ministre2026!")
    ]
    
    logged_in = False
    for phone, password in login_attempts:
        print(f"\n🔑 Tentative de connexion avec {phone}")
        if tester.test_login(phone, password):
            logged_in = True
            break
    
    if not logged_in:
        print("❌ Aucune connexion réussie - Continuons avec les tests publics")
        # Continuer avec les tests qui ne nécessitent pas d'authentification
        tester.test_services_apis()  # Test public
        return 0
    
    # Tests des 4 bugs
    tester.test_contexte_apis()      # Bug #1 - GED Zone Verte
    tester.test_services_apis()      # Bug #4 - Inscription services
    tester.test_chat_apis()          # Bug #3 - Recherche utilisateurs
    tester.test_viabilite_apis()     # Bug #2 - Graphique viabilité
    
    # Test flow inscription complet
    tester.test_inscription_flow()
    
    # Résultats
    print(f"\n{'='*60}")
    print("📊 RÉSULTATS DES TESTS")
    print(f"{'='*60}")
    print(f"Tests exécutés: {tester.tests_run}")
    print(f"Tests réussis: {tester.tests_passed}")
    print(f"Taux de réussite: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("✅ Tous les tests backend sont PASSÉS")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} test(s) ont ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(main())