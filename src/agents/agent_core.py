from dataclasses import dataclass
import os, importlib, json

@dataclass
class LLMConfig:
    provider: str = os.getenv("AE_LLM_PROVIDER","gemini")
    model: str = os.getenv("AE_LLM_MODEL","gemini-2.5-flash")
    key: str = os.getenv("AE_LLM_KEY","")

class LLMError(RuntimeError): pass

def _mod(name):
    try: return importlib.import_module(name)
    except Exception as e: raise LLMError(f"SDK {name} not installed: {e}")

def _gemini_rest(prompt: str, model: str, api_key: str) -> str:
    """Fallback: call Gemini via REST API when no SDK is installed."""
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data["candidates"][0]["content"]["parts"][0]["text"]

def _gemini_call(prompt: str, model: str, api_key: str) -> str:
    """Try new SDK -> old SDK -> REST API for Gemini calls."""
    # Strategy 1: google-genai (new, recommended SDK)
    try:
        genai = _mod("google.genai")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text
    except LLMError:
        pass

    # Strategy 2: google-generativeai (old, deprecated SDK)
    try:
        g = _mod("google.generativeai")
        g.configure(api_key=api_key)
        m = g.GenerativeModel(model)
        return m.generate_content(prompt).text
    except LLMError:
        pass

    # Strategy 3: REST API (stdlib-only, no SDK needed)
    return _gemini_rest(prompt, model, api_key)

def call_llm(prompt: str, cfg: LLMConfig) -> str:
    prov = (cfg.provider or "gemini").lower()
    if prov == "gemini":
        api_key = cfg.key or os.getenv("GEMINI_API_KEY","") or os.getenv("GOOGLE_API_KEY","")
        return _gemini_call(prompt, cfg.model, api_key)
    if prov == "openai":
        o = _mod("openai"); client = o.OpenAI(api_key=cfg.key or os.getenv("OPENAI_API_KEY",""))
        resp = client.chat.completions.create(model=cfg.model, messages=[{"role":"user","content":prompt}])
        return resp.choices[0].message.content
    if prov == "anthropic":
        a = _mod("anthropic"); client = a.Anthropic(api_key=cfg.key or os.getenv("ANTHROPIC_API_KEY",""))
        msg = client.messages.create(model=cfg.model, max_tokens=4000, messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    if prov == "mock":
        return "[]"
    raise LLMError(f"Unsupported provider {prov}")