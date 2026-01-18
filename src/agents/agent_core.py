from dataclasses import dataclass
import os, importlib

@dataclass
class LLMConfig:
    provider: str = os.getenv("AE_LLM_PROVIDER","gemini")
    model: str = os.getenv("AE_LLM_MODEL","gemini-1.5-pro")
    key: str = os.getenv("AE_LLM_KEY","")

class LLMError(RuntimeError): pass

def _mod(name):
    try: return importlib.import_module(name)
    except Exception as e: raise LLMError(f"SDK {name} not installed: {e}")

def call_llm(prompt: str, cfg: LLMConfig) -> str:
    prov = (cfg.provider or "gemini").lower()
    if prov == "gemini":
        g = _mod("google.generativeai"); g.configure(api_key=cfg.key or os.getenv("GEMINI_API_KEY",""))
        model = g.GenerativeModel(cfg.model); return model.generate_content(prompt).text
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