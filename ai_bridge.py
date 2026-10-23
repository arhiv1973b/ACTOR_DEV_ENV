#!/usr/bin/env python3
"""
Cross-Platform AI Handshake Handler
Routes requests to: Gemini API (cloud) + Ollama (local) + LM Studio (local)
Windows ↔ WSL Ubuntu transparent bridge
"""

import os
import json
import asyncio
import httpx
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum

API_KEY = os.environ.get("SECRET_VAR")

class AIProvider(Enum):
    """Available AI providers."""
    GEMINI = "gemini"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

class CrossPlatformAIBridge:
    """Routes AI requests across Windows, WSL, local, and cloud."""
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", API_KEY)
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.lm_studio_host = os.environ.get("LM_STUDIO_HOST", "http://127.0.0.1:1234")
        self.timeout = 30

    async def query_gemini(self, prompt: str, model: str = "gemini-3.5-flash") -> str:
        """Query Google Gemini API (cloud)."""
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Gemini error: {e}"

    async def query_ollama(self, prompt: str, model: str = "mistral") -> str:
        """Query Ollama local model (WSL/Linux)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False}
                )
                if response.status_code == 200:
                    return response.json().get("response", "No response")
                else:
                    return f"Ollama error: {response.status_code}"
        except Exception as e:
            return f"Ollama connection failed: {e}"

    async def query_lm_studio(self, prompt: str) -> str:
        """Query LM Studio local API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.lm_studio_host}/api/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 256
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"LM Studio error: {response.status_code}"
        except Exception as e:
            return f"LM Studio connection failed: {e}"

    async def route_query(
        self,
        prompt: str,
        provider: AIProvider = AIProvider.GEMINI,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route query to appropriate provider."""
        result = {
            "prompt": prompt,
            "provider": provider.value,
            "model": model or "default",
            "response": None,
            "error": None
        }

        try:
            if provider == AIProvider.GEMINI:
                result["response"] = await self.query_gemini(
                    prompt,
                    model=model or "gemini-3.5-flash"
                )
            elif provider == AIProvider.OLLAMA:
                result["response"] = await self.query_ollama(
                    prompt,
                    model=model or "mistral"
                )
            elif provider == AIProvider.LM_STUDIO:
                result["response"] = await self.query_lm_studio(prompt)
        except Exception as e:
            result["error"] = str(e)

        return result

    async def hybrid_query(self, prompt: str, prioritize_local: bool = False) -> Dict[str, Any]:
        """Try multiple providers in priority order."""
        if prioritize_local:
            providers = [
                (AIProvider.OLLAMA, "mistral"),
                (AIProvider.LM_STUDIO, None),
                (AIProvider.GEMINI, "gemini-3.5-flash")
            ]
        else:
            providers = [
                (AIProvider.GEMINI, "gemini-3.5-flash"),
                (AIProvider.OLLAMA, "mistral"),
                (AIProvider.LM_STUDIO, None)
            ]

        results = []
        for provider, model in providers:
            result = await self.route_query(prompt, provider, model)
            results.append(result)
            if result["response"] and not result["error"]:
                break

        return {
            "prompt": prompt,
            "prioritize_local": prioritize_local,
            "attempts": results,
            "winner": results[0] if results else None
        }

async def main():
    """Demo and CLI."""
    import sys

    bridge = CrossPlatformAIBridge()

    print("═"*60)
    print("🌉 Cross-Platform AI Handshake Bridge")
    print("═"*60)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 ai_bridge.py <prompt> [--provider gemini|ollama|lm_studio]")
        print("  python3 ai_bridge.py <prompt> --hybrid [--local-first]")
        print("\nExamples:")
        print('  python3 ai_bridge.py "What is 2+2?" --provider gemini')
        print('  python3 ai_bridge.py "Hello" --hybrid --local-first')
        sys.exit(0)

    prompt = sys.argv[1]
    provider = AIProvider.GEMINI
    hybrid = False
    local_first = False

    for arg in sys.argv[2:]:
        if arg == "--hybrid":
            hybrid = True
        elif arg == "--local-first":
            local_first = True
        elif arg.startswith("--provider="):
            provider_name = arg.split("=")[1]
            provider = AIProvider(provider_name)

    print(f"\n📝 Prompt: {prompt}")

    if hybrid:
        result = await bridge.hybrid_query(prompt, prioritize_local=local_first)
        print(f"\n🏆 Provider: {result['winner']['provider']}")
        print(f"   Response: {result['winner']['response'][:200]}...")
    else:
        result = await bridge.route_query(prompt, provider)
        print(f"\n🤖 Provider: {result['provider']}")
        print(f"   Response: {result['response'][:200]}...")

    print("\n" + "═"*60)

if __name__ == "__main__":
    asyncio.run(main())
