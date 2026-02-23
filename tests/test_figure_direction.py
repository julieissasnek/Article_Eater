from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.extraction import figure_direction


class _FakePage:
    def __init__(self, text: str, drawings: list[dict]):
        self._text = text
        self._drawings = drawings

    def get_text(self, _mode: str) -> str:
        return self._text

    def get_drawings(self) -> list[dict]:
        return self._drawings


class _FakeDoc:
    def __init__(self, pages: list[_FakePage]):
        self._pages = pages

    def __len__(self) -> int:
        return len(self._pages)

    def __getitem__(self, idx: int) -> _FakePage:
        return self._pages[idx]

    def close(self) -> None:
        return None


class _FakeFitz:
    def __init__(self, pages: list[_FakePage]):
        self._pages = pages

    def open(self, _path: str) -> _FakeDoc:
        return _FakeDoc(self._pages)


def _line(x1: float, y1: float, x2: float, y2: float):
    return ("l", SimpleNamespace(x=x1, y=y1), SimpleNamespace(x=x2, y=y2))


def test_infer_direction_from_pdf_figures_increase(monkeypatch, tmp_path: Path):
    pdf_path = tmp_path / "fake.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%%EOF\n")

    drawings = [
        {"width": 1.0, "items": [_line(0, 10, 10, 0), _line(2, 12, 12, 2), _line(4, 14, 14, 4)]},
        {"width": None, "items": [_line(0, 0, 1, 1)]},  # ignored
    ]
    fake_pages = [_FakePage("Figure 1. stress vs noise", drawings)]
    monkeypatch.setattr(figure_direction, "fitz", _FakeFitz(fake_pages))

    claim = {"iv_raw": "noise", "dv_raw": "stress"}
    res = figure_direction.infer_direction_from_pdf_figures(pdf_path, claim, max_pages=3)
    assert res.direction == "increase"
    assert res.source_page == 1
    assert res.confidence > 0.5


def test_infer_direction_from_pdf_figures_unknown_when_weak(monkeypatch, tmp_path: Path):
    pdf_path = tmp_path / "fake2.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%%EOF\n")

    drawings = [
        {"width": 1.0, "items": [_line(0, 0, 10, 0)]},  # horizontal only
    ]
    fake_pages = [_FakePage("Figure 2. no diagonal trend", drawings)]
    monkeypatch.setattr(figure_direction, "fitz", _FakeFitz(fake_pages))

    claim = {"iv_raw": "noise", "dv_raw": "stress"}
    res = figure_direction.infer_direction_from_pdf_figures(pdf_path, claim, max_pages=3)
    assert res.direction == "unknown"
    assert res.confidence == 0.0

