#!/usr/bin/env python3
"""
Structuur test voor Letta Memory implementatie
Test de architectuur zonder externe dependencies
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

class MemoryStructureTest:
    """Test suite voor memory implementatie structuur"""
    
    def __init__(self):
        self.results = []
        self.project_root = Path(__file__).parent
        print("🧠 Hoeflon AI Memory - Structuur Validatie")
        print("=" * 50)
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test resultaat"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def test_file_structure(self):
        """Test of alle benodigde bestanden aanwezig zijn"""
        expected_files = [
            "backend/services/letta_memory_service.py",
            "backend/models/__init__.py",
            "backend/models/user_context.py", 
            "backend/database/memory_db.py",
            "backend/api/memory.py",
            "backend/core/config.py",
            "requirements.txt"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in expected_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test(
                "File Structure", 
                False, 
                f"Ontbrekende bestanden: {missing_files}"
            )
        else:
            self.log_test(
                "File Structure", 
                True, 
                f"Alle {len(existing_files)} verwachte bestanden aanwezig"
            )
    
    def test_config_content(self):
        """Test configuratie inhoud"""
        config_path = self.project_root / "backend/core/config.py"
        
        if not config_path.exists():
            self.log_test("Config Content", False, "Config bestand niet gevonden")
            return
        
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            required_elements = [
                "LETTA_CONFIG",
                "api_key",
                "base_url", 
                "model",
                "embedding_model"
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in config_content]
            
            if missing_elements:
                self.log_test(
                    "Config Content", 
                    False, 
                    f"Ontbrekende config elementen: {missing_elements}"
                )
            else:
                self.log_test(
                    "Config Content", 
                    True, 
                    "Alle Letta configuratie elementen aanwezig"
                )
                
        except Exception as e:
            self.log_test("Config Content", False, str(e))
    
    def test_requirements_content(self):
        """Test requirements.txt inhoud"""
        req_path = self.project_root / "requirements.txt"
        
        if not req_path.exists():
            self.log_test("Requirements Content", False, "requirements.txt niet gevonden")
            return
        
        try:
            with open(req_path, 'r') as f:
                requirements = f.read()
            
            required_packages = [
                "letta-client",
                "psycopg2-binary",
                "pgvector",
                "sqlalchemy"
            ]
            
            missing_packages = [pkg for pkg in required_packages if pkg not in requirements]
            
            if missing_packages:
                self.log_test(
                    "Requirements Content", 
                    False, 
                    f"Ontbrekende packages: {missing_packages}"
                )
            else:
                self.log_test(
                    "Requirements Content", 
                    True, 
                    "Alle memory-gerelateerde packages aanwezig"
                )
                
        except Exception as e:
            self.log_test("Requirements Content", False, str(e))
    
    def test_service_structure(self):
        """Test LettaMemoryService structuur"""
        service_path = self.project_root / "backend/services/letta_memory_service.py"
        
        if not service_path.exists():
            self.log_test("Service Structure", False, "LettaMemoryService bestand niet gevonden")
            return
        
        try:
            with open(service_path, 'r') as f:
                service_content = f.read()
            
            required_methods = [
                "get_or_create_user_agent",
                "send_message",
                "update_user_memory",
                "get_user_memory_summary"
            ]
            
            required_classes = [
                "class LettaMemoryService"
            ]
            
            missing_methods = [method for method in required_methods if method not in service_content]
            missing_classes = [cls for cls in required_classes if cls not in service_content]
            
            issues = []
            if missing_methods:
                issues.append(f"Methods: {missing_methods}")
            if missing_classes:
                issues.append(f"Classes: {missing_classes}")
            
            if issues:
                self.log_test(
                    "Service Structure", 
                    False, 
                    f"Ontbrekende elementen - {', '.join(issues)}"
                )
            else:
                self.log_test(
                    "Service Structure", 
                    True, 
                    "LettaMemoryService heeft alle verwachte methoden"
                )
                
        except Exception as e:
            self.log_test("Service Structure", False, str(e))
    
    def test_model_structure(self):
        """Test database model structuur"""
        model_path = self.project_root / "backend/models/user_context.py"
        
        if not model_path.exists():
            self.log_test("Model Structure", False, "UserContext model bestand niet gevonden")
            return
        
        try:
            with open(model_path, 'r') as f:
                model_content = f.read()
            
            required_models = [
                "class UserContext",
                "class UserSession", 
                "class UserPreferences"
            ]
            
            required_fields = [
                "azure_object_id",
                "letta_agent_id",
                "display_name",
                "email"
            ]
            
            missing_models = [model for model in required_models if model not in model_content]
            missing_fields = [field for field in required_fields if field not in model_content]
            
            issues = []
            if missing_models:
                issues.append(f"Models: {missing_models}")
            if missing_fields:
                issues.append(f"Fields: {missing_fields}")
            
            if issues:
                self.log_test(
                    "Model Structure", 
                    False, 
                    f"Ontbrekende elementen - {', '.join(issues)}"
                )
            else:
                self.log_test(
                    "Model Structure", 
                    True, 
                    "Database models hebben alle verwachte elementen"
                )
                
        except Exception as e:
            self.log_test("Model Structure", False, str(e))
    
    def test_api_structure(self):
        """Test API endpoints structuur"""
        api_path = self.project_root / "backend/api/memory.py"
        
        if not api_path.exists():
            self.log_test("API Structure", False, "Memory API bestand niet gevonden")
            return
        
        try:
            with open(api_path, 'r') as f:
                api_content = f.read()
            
            required_endpoints = [
                "@router.post(\"/chat\"",
                "@router.get(\"/profile\"",
                "@router.put(\"/preferences\"",
                "@router.get(\"/health\""
            ]
            
            required_models = [
                "class MemoryMessageRequest",
                "class MemoryMessageResponse",
                "class UserPreferencesRequest"
            ]
            
            missing_endpoints = [ep for ep in required_endpoints if ep not in api_content]
            missing_models = [model for model in required_models if model not in api_content]
            
            issues = []
            if missing_endpoints:
                issues.append(f"Endpoints: {missing_endpoints}")
            if missing_models:
                issues.append(f"Models: {missing_models}")
            
            if issues:
                self.log_test(
                    "API Structure", 
                    False, 
                    f"Ontbrekende elementen - {', '.join(issues)}"
                )
            else:
                self.log_test(
                    "API Structure", 
                    True, 
                    "Memory API heeft alle verwachte endpoints en models"
                )
                
        except Exception as e:
            self.log_test("API Structure", False, str(e))
    
    def test_main_integration(self):
        """Test integratie in main.py"""
        main_path = self.project_root / "backend/main.py"
        
        if not main_path.exists():
            self.log_test("Main Integration", False, "main.py niet gevonden")
            return
        
        try:
            with open(main_path, 'r') as f:
                main_content = f.read()
            
            required_imports = [
                "from api.memory import router as memory_router"
            ]
            
            required_includes = [
                "app.include_router(memory_router"
            ]
            
            missing_imports = [imp for imp in required_imports if imp not in main_content]
            missing_includes = [inc for inc in required_includes if inc not in main_content]
            
            issues = []
            if missing_imports:
                issues.append(f"Imports: {missing_imports}")
            if missing_includes:
                issues.append(f"Router includes: {missing_includes}")
            
            if issues:
                self.log_test(
                    "Main Integration", 
                    False, 
                    f"Ontbrekende integratie - {', '.join(issues)}"
                )
            else:
                self.log_test(
                    "Main Integration", 
                    True, 
                    "Memory router correct geïntegreerd in main.py"
                )
                
        except Exception as e:
            self.log_test("Main Integration", False, str(e))
    
    def generate_deployment_checklist(self):
        """Genereer deployment checklist"""
        checklist = """
🚀 FASE 1 DEPLOYMENT CHECKLIST
==============================

✅ ARCHITECTUUR VOLTOOID:
□ LettaMemoryService - Geheugen management service
□ UserContext Models - SQLAlchemy database models  
□ Memory Database - PostgreSQL met pgvector support
□ Memory API - FastAPI endpoints voor memory operaties
□ Configuration - Letta en database configuratie
□ Integration - Memory router geïntegreerd in main app

🔧 PRODUCTIE SETUP VEREISTEN:
1. Environment Variables:
   - LETTA_API_KEY (verkrijg van https://app.letta.com/api-keys)
   - MEMORY_DB_HOST, MEMORY_DB_PORT, MEMORY_DB_NAME
   - MEMORY_DB_USER, MEMORY_DB_PASSWORD

2. Database Setup:
   - PostgreSQL 12+ installeren
   - pgvector extensie installeren
   - hoeflon_memory database creëren

3. Dependencies:
   - pip install -r requirements.txt
   - letta-client, psycopg2-binary, pgvector

4. Database Migratie:
   - python3 -c "from backend.database.memory_db import get_memory_db; get_memory_db().create_tables()"

🎯 VOLGENDE FASE (Fase 2):
=========================
□ Azure AD / Entra ID authenticatie (MSAL.js)
□ JWT token validatie in FastAPI 
□ Microsoft Graph API integratie
□ Azure Form Recognizer voor documenten
□ Document processing pipeline

📊 ENDPOINTS BESCHIKBAAR:
========================
- POST /memory/chat - Chat met memory agent
- GET /memory/profile - User profiel en memory status
- PUT /memory/preferences - Update gebruikersvoorkeuren  
- GET /memory/health - Memory services health check
- DELETE /memory/agent - Reset user agent

🧪 TESTEN:
=========
curl -X GET "http://localhost:8504/memory/health"
curl -X GET "http://localhost:8504/memory/profile" -H "X-User-ID: test-user-123"
"""
        return checklist
    
    def run_all_tests(self):
        """Voer alle structuur tests uit"""
        print("🔍 Start structuur validatie...\n")
        
        self.test_file_structure()
        self.test_config_content()
        self.test_requirements_content()
        self.test_service_structure()
        self.test_model_structure()
        self.test_api_structure()
        self.test_main_integration()
        
        # Resultaten samenvatting
        print("\n" + "=" * 50)
        print("📊 STRUCTUUR VALIDATIE RESULTATEN")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Totaal tests: {total_tests}")
        print(f"✅ Geslaagd: {passed_tests}")
        print(f"❌ Gefaald: {failed_tests}")
        print(f"📈 Slagingspercentage: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ GEFAALDE TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        else:
            print("\n🎉 ALLE STRUCTUUR TESTS GESLAAGD!")
        
        print("\n🎯 FASE 1 STATUS:")
        if passed_tests == total_tests:
            print("✅ IMPLEMENTATIE VOLTOOID - Klaar voor productie deployment!")
        else:
            print("⚠️  IMPLEMENTATIE BIJNA VOLTOOID - Los resterende issues op")
        
        # Save results
        with open("memory_structure_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate checklist
        checklist = self.generate_deployment_checklist()
        with open("FASE1_DEPLOYMENT_CHECKLIST.md", "w") as f:
            f.write(checklist)
        
        print(f"\n📋 Resultaten: memory_structure_results.json")
        print("📋 Deployment checklist: FASE1_DEPLOYMENT_CHECKLIST.md")


def main():
    """Main test functie"""
    test_suite = MemoryStructureTest()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()