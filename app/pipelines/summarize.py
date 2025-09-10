from __future__ import annotations
import re

GREETING_RE = re.compile(r"^\s*(hi|hello|hey|salut|bun[ăa])[,!\s:-]*", re.IGNORECASE)

def _normalize(text: str) -> str:
    # spații + linii la un singur spațiu
    return " ".join(text.split())

def _strip_greeting(text: str) -> str:
    # scoate salutul de la începutul mesajului (opțional)
    return GREETING_RE.sub("", text, count=1)

def _first_sentence(text: str) -> str:
    # sparge în „fraze” simple după ., !, ?
    # păstrăm delimitatorul pentru lizibilitate
    parts = re.split(r"(?<=[.!?])\s+", text)
    for p in parts:
        p = p.strip()
        if p:
            return p
    return text.strip()

def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    trimmed = " ".join(words[:max_words]).rstrip(",;")
    # punct la final, dacă nu există deja
    return trimmed + ("." if not re.search(r"[.!?]$", trimmed) else "")

def summarize_text(text: str, max_words: int = 30) -> str:
    """
    Heuristică deterministică:
      1) normalizează whitespace
      2) taie salutul la început (ex: 'Salut,' / 'Hello,')
      3) ia prima propoziție
      4) limitează la max_words
    """
    if not text or not text.strip():
        return ""
    t = _normalize(text)
    t = _strip_greeting(t)
    sent = _first_sentence(t)
    return _truncate_words(sent, max_words)
