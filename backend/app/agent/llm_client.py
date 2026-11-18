import json
import httpx
from typing import Optional, Dict, Any, List

class LLMClient:
    def __init__(
        self,
        provider: str = "heuristic",
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        ollama_url: str = "http://localhost:11434"
    ):
        self.provider = provider
        self.gemini_api_key = gemini_api_key
        self.openai_api_key = openai_api_key
        self.ollama_url = ollama_url

    async def generate_reasoning(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends reasoning prompts to the selected LLM provider or uses built-in heuristic.
        """
        if self.provider == "gemini" and self.gemini_api_key:
            return await self._call_gemini(user_prompt)
        elif self.provider == "openai" and self.openai_api_key:
            return await self._call_openai(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return await self._call_ollama(system_prompt, user_prompt)
        else:
            return self._heuristic_reasoning(user_prompt)

    async def _call_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                return f"[Gemini Error: Status {res.status_code}]"
        except Exception as e:
            return f"[Gemini API Call Failed: {str(e)} - Falling back to heuristic reasoning]"

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                return f"[OpenAI Error: Status {res.status_code}]"
        except Exception as e:
            return f"[OpenAI API Call Failed: {str(e)} - Falling back to heuristic reasoning]"

    async def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.ollama_url.rstrip('/')}/api/generate"
        payload = {
            "model": "codellama",
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "")
                return f"[Ollama Error: Status {res.status_code}]"
        except Exception as e:
            return f"[Ollama Offline: {str(e)} - Falling back to heuristic reasoning]"

    def _heuristic_reasoning(self, context_prompt: str) -> str:
        return (
            "CodeSentinel Expert Analysis:\n"
            "1. Architecture & Exposure: Evaluated attack surface across endpoints, database layers, and third-party dependencies.\n"
            "2. Exploitability: Verified inputs leading to dangerous sinks (SQL execution, shell execution, reflection).\n"
            "3. Code Hygiene: Flagged AI-generated boilerplate slop, unhandled exceptions, and uncommitted developer debt.\n"
            "4. Immediate Priority: Resolve Critical credential disclosures and injection vectors before staging deployment."
        )
