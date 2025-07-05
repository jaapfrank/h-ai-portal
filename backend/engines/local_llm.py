"""
Local LLM Integration for RTX 5080 GPU
Supports: Ollama, vLLM, TGI (Text Generation Interface)
"""
import httpx
import json
from typing import Dict, Any, Optional, List
import os

class LocalLLMEngine:
    """Local LLM engine for RTX 5080 GPU"""
    
    def __init__(self, llm_type: str = "ollama", base_url: str = "http://localhost:11434"):
        self.llm_type = llm_type.lower()
        self.base_url = base_url
        self.available_models = []
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if local LLM server is running"""
        try:
            if self.llm_type == "ollama":
                response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    self.available_models = [model["name"] for model in models]
                    return True
            elif self.llm_type == "vllm":
                response = httpx.get(f"{self.base_url}/v1/models", timeout=5)
                return response.status_code == 200
            elif self.llm_type == "tgi":
                response = httpx.get(f"{self.base_url}/info", timeout=5)
                return response.status_code == 200
        except Exception as e:
            print(f"Local LLM not available: {e}")
        return False
    
    async def generate_sql_query(self, user_question: str, schema_info: str, business_rules: str, learned_context: str = "") -> str:
        """Generate SQL query using local LLM"""
        
        prompt = f"""You are an expert SQL developer for Hoeflon ERP database (SQL Server).

USER QUESTION: {user_question}

DATABASE SCHEMA:
{schema_info}

BUSINESS RULES:
{business_rules}

{learned_context}

Generate ONLY the SQL query, no explanations. Use proper SQL Server syntax."""

        try:
            if self.llm_type == "ollama":
                return await self._generate_ollama(prompt)
            elif self.llm_type == "vllm":
                return await self._generate_vllm(prompt)
            elif self.llm_type == "tgi":
                return await self._generate_tgi(prompt)
        except Exception as e:
            print(f"Local LLM generation failed: {e}")
            return None
    
    async def _generate_ollama(self, prompt: str, model: str = "llama3.1:8b") -> str:
        """Generate using Ollama"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                }
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
        return None
    
    async def _generate_vllm(self, prompt: str, model: str = "microsoft/DialoGPT-medium") -> str:
        """Generate using vLLM"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": 500,
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            )
            if response.status_code == 200:
                result = response.json()
                choices = result.get("choices", [])
                if choices:
                    return choices[0].get("text", "").strip()
        return None
    
    async def _generate_tgi(self, prompt: str) -> str:
        """Generate using Text Generation Interface"""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 500,
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "do_sample": True
                    }
                }
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("generated_text", "").strip()
        return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get local LLM system information"""
        return {
            "llm_type": self.llm_type,
            "base_url": self.base_url,
            "available": len(self.available_models) > 0,
            "models": self.available_models,
            "gpu_optimized": True,
            "recommended_models": self._get_recommended_models()
        }
    
    def _get_recommended_models(self) -> List[str]:
        """Get recommended models for RTX 5080"""
        return {
            "ollama": [
                "llama3.1:8b",      # Great for general tasks
                "codellama:7b",     # Excellent for SQL generation  
                "mistral:7b",       # Fast and efficient
                "qwen2.5:7b",       # Good multilingual support
                "llama3.2:3b"       # Fastest option
            ],
            "vllm": [
                "microsoft/DialoGPT-medium",
                "codellama/CodeLlama-7b-hf",
                "mistralai/Mistral-7B-v0.1"
            ],
            "tgi": [
                "bigcode/starcoder",
                "Salesforce/codegen-2B-mono",
                "microsoft/CodeGPT-small-java"
            ]
        }.get(self.llm_type, [])

# Installation instructions for RTX 5080
INSTALLATION_GUIDE = """
🚀 LOCAL LLM SETUP FOR RTX 5080

1. OLLAMA (Recommended - Easiest):
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama3.1:8b
   ollama pull codellama:7b
   ollama serve

2. vLLM (High Performance):
   pip install vllm
   python -m vllm.entrypoints.api_server --model microsoft/DialoGPT-medium --gpu-memory-utilization 0.8

3. Text Generation Interface:
   docker run --gpus all -p 8080:80 -v $PWD:/data ghcr.io/huggingface/text-generation-inference:latest --model-id microsoft/DialoGPT-medium

GPU Memory Usage (RTX 5080 - 16GB VRAM):
- 3B models: ~6GB VRAM
- 7B models: ~14GB VRAM  
- 8B models: ~16GB VRAM (full utilization)

Recommended for SQL generation: codellama:7b
"""

# Global instance
local_llm = LocalLLMEngine()

if __name__ == "__main__":
    print("🖥️ Local LLM Engine for RTX 5080")
    print(INSTALLATION_GUIDE)
    
    # Test connection
    engine = LocalLLMEngine()
    info = engine.get_system_info()
    print(f"\n📊 System Info: {json.dumps(info, indent=2)}")