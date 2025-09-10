# tests/test_summarize.py
from app.pipelines.summarize import summarize_text

def test_summarize_single_sentence():
    t = "Please help, my invoice is wrong and I need a refund."
    out = summarize_text(t, max_words=30)
    assert out == "Please help, my invoice is wrong and I need a refund."

def test_summarize_multiple_sentences_picks_first():
    t = "Login error when accessing the dashboard. It happens on mobile too."
    out = summarize_text(t, max_words=30)
    assert out == "Login error when accessing the dashboard."

def test_summarize_truncates_to_max_words():
    t = " ".join(["word"] * 50)  # 50 cuvinte
    out = summarize_text(t, max_words=10)
    assert len(out.split()) == 10
    assert out.endswith(".")  # adaugă punct dacă nu există

def test_summarize_strips_greeting():
    t = "Salut, am o problemă cu factura și vreau ramburs."
    out = summarize_text(t, max_words=30)
    assert out.lower().startswith("am o problemă") or out.lower().startswith("am o problema")

def test_summarize_empty_safe():
    assert summarize_text("") == ""
    assert summarize_text("   ") == ""
