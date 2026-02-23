from src.extraction.row_classifier_codex import classify_row_content, normalize_ocr_text


def test_normalize_ocr_text_collapses_doubled_pairs():
    text = "ttaaccttiillee exxppeerriimmeenntt"
    out = normalize_ocr_text(text)
    assert "tactile" in out.lower()
    assert "experiment" in out.lower()


def test_classify_row_content_detects_stat_row():
    row = "Task condition F(1, 60) = 4.00, p = 0.03"
    profile = classify_row_content(row)
    assert profile.label == "STAT_ROW"


def test_classify_row_content_detects_citation_row():
    row = "Kaplan et al. (1995). Journal of Environmental Psychology, Vol. 3, pp. 10-20."
    profile = classify_row_content(row)
    assert profile.label == "CITATION_ROW"


def test_classify_row_content_flags_junk_row():
    row = "ffititttiningg thhee sseennssoorrss samplephotoofroomwithhighsalience"
    profile = classify_row_content(row)
    assert profile.label == "JUNK_ROW"
