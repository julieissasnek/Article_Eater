
from __future__ import annotations
import os, json, requests

class LLMClient:
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.google_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.base = os.environ.get("OPENAI_BASE", "https://api.openai.com/v1")
        self.gemini = "https://generativelanguage.googleapis.com/v1beta/models"
        self.ollama_base = os.environ.get("OLLAMA_BASE", "http://localhost:11434")

    def complete_gemini(self, model: str, system: str, user: str, temperature: float=0.1, max_tokens: int=8192):
        assert self.google_key, "Missing GOOGLE_API_KEY for Gemini"
        url = f"{self.gemini}/{model}:generateContent?key={self.google_key}"
        payload = {"contents":[{"parts":[{"text": system}, {"text": user}]}], "generationConfig":{"temperature":temperature, "maxOutputTokens":max_tokens}}
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def complete_ollama(self, model: str, system: str, user: str, temperature: float=0.1, max_tokens: int=8192):
        url = f"{self.ollama_base}/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": False,
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["message"]["content"]

    def complete_openai(self, model: str, system: str, user: str, temperature: float=0.1, max_tokens: int=8192):
        if not self.openai_key and not (self.base.startswith("http://localhost") or self.base.startswith("http://127.0.0.1")):
            raise AssertionError("Missing OPENAI_API_KEY")
        url = f"{self.base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}"} if self.openai_key else {}
        payload = {"model": model, "messages":[{"role":"system","content":system},{"role":"user","content":user}], "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
