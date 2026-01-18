from dataclasses import dataclass
from pathlib import Path
import json, os

@dataclass
class LLMConfig:
    provider: str = os.getenv('AE_LLM_PROVIDER','gemini')  # 'gemini'|'openai'|'anthropic'
    model: str = os.getenv('AE_LLM_MODEL','gemini-1.5-pro')
    key: str = os.getenv('AE_LLM_KEY','')  # or use provider-specific env vars

def load_prompt(name='7panel_pass2_findings.md') -> str:
    p = Path('prompts')/name
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''

def call_llm(prompt: str, cfg: LLMConfig) -> str:
    """
    Provider-agnostic shim. At runtime, install & enable your SDK:
      - Gemini:  google-generativeai  (env: GEMINI_API_KEY or AE_LLM_KEY)
      - OpenAI:  openai               (env: OPENAI_API_KEY or AE_LLM_KEY)
      - Anthropic: anthropic          (env: ANTHROPIC_API_KEY or AE_LLM_KEY)
    Returns raw string; caller parses JSON.
    """
    # Example wiring (commented so repo runs without SDKs preinstalled):
    # if cfg.provider == 'gemini':
    #   import google.generativeai as genai
    #   genai.configure(api_key=cfg.key or os.getenv('GEMINI_API_KEY',''))
    #   model = genai.GenerativeModel(cfg.model)
    #   resp = model.generate_content(prompt)
    #   return resp.text
    # elif cfg.provider == 'openai':
    #   from openai import OpenAI
    #   client = OpenAI(api_key=cfg.key or os.getenv('OPENAI_API_KEY',''))
    #   resp = client.chat.completions.create(model=cfg.model, messages=[{'role':'user','content':prompt}])
    #   return resp.choices[0].message.content
    # elif cfg.provider == 'anthropic':
    #   import anthropic, os
    #   client = anthropic.Anthropic(api_key=cfg.key or os.getenv('ANTHROPIC_API_KEY',''))
    #   msg = client.messages.create(model=cfg.model, max_tokens=4000, messages=[{'role':'user','content':prompt}])
    #   return msg.content[0].text
    return '{"error":"LLM not connected in this environment"}'

def extract_seven_panel(pdf_text: str, abstract: str|None, cfg: LLMConfig) -> dict:
    inst = load_prompt('7panel_pass2_findings.md')
    full_prompt = f"""You are extracting a 7-panel from an academic article.

Abstract:
{abstract or ''}

PDF (possibly truncated):
{(pdf_text or '')[:20000]}

Instructions:
{inst}

Return JSON only (no commentary).
"""
    raw = call_llm(full_prompt, cfg)
    try:
        data = json.loads(raw)
    except Exception:
        data = {'error':'llm_json_parse_failed','raw':raw}
    return {'panels': data, 'raw_abstract': abstract}

def run(query: str, pdf_text: str, abstract: str|None) -> dict:
    cfg = LLMConfig()
    out = extract_seven_panel(pdf_text, abstract, cfg)
    out['query'] = query
    return out