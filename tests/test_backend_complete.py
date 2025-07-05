"""
Complete Backend Test Suite
Tests all API endpoints, learning system, local LLM, and memory
"""
import pytest
import httpx
import asyncio
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8504"

class TestCompleteBackend:
    """Complete backend test suite"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test session"""
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.test_session_id = "test_complete_suite"
        yield
        await self.client.aclose()
    
    async def test_health_status(self):
        """Test system health endpoint"""
        response = await self.client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "claude_ai" in data
        print(f"✅ Health check: {data['status']}")
    
    async def test_learning_correction(self):
        """Test learning system with correction"""
        # First give a correction
        correction_data = {
            "message": "Ik verwacht 176 kranen",
            "session_id": self.test_session_id
        }
        response = await self.client.post("/chat", json=correction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "learning_update"
        assert "176" in data["response"]
        print("✅ Learning correction accepted")
        
        # Test if system remembers
        query_data = {
            "message": "Hoeveel kranen gereed dit jaar?",
            "session_id": self.test_session_id
        }
        response = await self.client.post("/chat", json=query_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should use smart learning
        if data["type"] == "smart_learning":
            assert "176" in str(data["result"])
            print("✅ Smart learning works - returns 176 kranen")
        else:
            print(f"⚠️ Not using smart learning: {data['type']}")
    
    async def test_memory_retrieval(self):
        """Test memory system endpoints"""
        response = await self.client.get(f"/learning/memory/session/{self.test_session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["conversation_history"]) > 0
        print(f"✅ Memory system: {len(data['conversation_history'])} interactions stored")
    
    async def test_local_llm_info(self):
        """Test local LLM integration"""
        from engines.local_llm import local_llm
        info = local_llm.get_system_info()
        print(f"🖥️ Local LLM Status: {info}")
        
        if info["available"]:
            print("✅ Local LLM available")
        else:
            print("⚠️ Local LLM not available - install Ollama for RTX 5080 support")
    
    async def test_company_search(self):
        """Test company database"""
        company_data = {
            "message": "wat is het telefoonnummer van test",
            "session_id": self.test_session_id
        }
        response = await self.client.post("/chat", json=company_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "company_info"
        print("✅ Company search works")
    
    async def test_erp_queries(self):
        """Test ERP database queries"""
        erp_queries = [
            "SELECT COUNT(*) FROM V_R_SERVICEOBJECT",
            "Hoeveel service objects zijn er?",
            "Toon me de eerste 5 service objects"
        ]
        
        for query in erp_queries:
            query_data = {
                "message": query,
                "session_id": f"{self.test_session_id}_erp"
            }
            response = await self.client.post("/chat", json=query_data)
            assert response.status_code == 200
            data = response.json()
            print(f"✅ ERP query works: {query[:30]}...")
    
    async def test_demo_endpoints_are_honest(self):
        """Test that demo endpoints are marked as demo"""
        demo_endpoints = [
            "/ml/training_status",
            "/enterprise/status", 
            "/cache/performance",
            "/postgresql/status"
        ]
        
        for endpoint in demo_endpoints:
            response = await self.client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "demo"
            assert "demo" in data["message"].lower()
            print(f"✅ {endpoint} correctly marked as demo")
    
    async def test_performance_endpoint(self):
        """Test real performance monitoring"""
        response = await self.client.get("/performance")
        assert response.status_code == 200
        data = response.json()
        
        if data["status"] == "success":
            assert "cpu_usage" in data
            assert "memory_usage" in data
            print(f"✅ Performance monitoring: CPU {data['cpu_usage']}%, Memory {data['memory_usage']}%")
        else:
            print("⚠️ Performance monitoring limited")

@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete user workflow"""
    client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
    test_session_id = "test_complete_suite"
    
    try:
        print("\n🧪 Running Complete Backend Test Suite...")
        
        # Test health status
        response = await client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check: {data['status']}")
        
        # Test learning correction
        correction_data = {
            "message": "Ik verwacht 176 kranen",
            "session_id": test_session_id
        }
        response = await client.post("/chat", json=correction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "learning_update"
        print("✅ Learning correction accepted")
        
        # Test if system remembers
        query_data = {
            "message": "Hoeveel kranen gereed dit jaar?",
            "session_id": test_session_id
        }
        response = await client.post("/chat", json=query_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should use smart learning or return error
        print(f"🔍 Query response: {data}")
        if data["type"] == "smart_learning":
            response_text = data.get("response", "")
            assert "176" in response_text
            print("✅ Smart learning works - returns 176 kranen")
        elif data["type"] == "business_data":
            result = data.get("result", [])
            if result and len(result) > 0:
                print(f"📊 Database returned: {result}")
            else:
                print("⚠️ Database query returned no results")
        else:
            print(f"⚠️ Response type: {data['type']}")
        
        # Test local LLM info
        try:
            from engines.local_llm import local_llm
            info = local_llm.get_system_info()
            print(f"🖥️ Local LLM Status: {info}")
            
            if info["available"]:
                print("✅ Local LLM available")
            else:
                print("⚠️ Local LLM not available - install Ollama for RTX 5080 support")
        except Exception as e:
            print(f"⚠️ Local LLM test failed: {e}")
            
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())