from pathlib import Path
from src.agents.agent_core import call_llm, LLMConfig
from src.agents.json_utils import parse_and_validate
from src.contracts.schemas import SevenPanelArtifact, SevenPanelItem

def _load_prompt(name='7panel_pass2_findings.md') -> str:
    p = Path('prompts')/name
    return p.read_text(encoding='utf-8', errors='ignore') if p.exists() else ''

def extract_seven_panel(pdf_text: str, abstract: str|None) -> SevenPanelArtifact:
    cfg = LLMConfig()
    inst = _load_prompt('7panel_pass2_findings.md')
    full = f"""You are extracting a 7-panel from an academic article.

Abstract:
{abstract or ''}

PDF (possibly truncated):
{(pdf_text or '')[:20000]}

Instructions:
{inst}
"""
    raw = call_llm(full, cfg)
    items = parse_and_validate(raw)
    return SevenPanelArtifact(items=[SevenPanelItem(**i) for i in items],
                              provider=cfg.provider, model=cfg.model)