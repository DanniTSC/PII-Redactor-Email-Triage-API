# app/pipelines/classify.py
from typing import Dict
from app.providers.zero_shot import classify_llm, USE_LLM, MIN_CONF

# Cuvinte-cheie (EN + RO) + hint din redacție ([iban])
CATEGORY_KEYWORDS: Dict[str, tuple[str, ...]] = {
    "billing": (
        "invoice", "receipt", "refund", "charge", "payment", "card", "iban",
        "factura", "factură", "plata", "plată", "ramburs", "cont", "banca", "bancă",
        "[iban]"
    ),
    "tech": (
        "error", "bug", "issue", "crash", "fail", "server", "api", "login",
        "password", "parola", "parolă", "conectare", "eroare", "reset"
    ),
    "sales": (
        "price", "quote", "offer", "trial", "subscription", "upgrade",
        "discount", "promo", "abonament", "pret", "preț", "oferta", "ofertă"
    ),
}
CATEGORIES = ("billing", "tech", "sales", "other")

def _rule_scores(text: str) -> Dict[str, int]:
    s = (text or "").lower()
    scores = {c: 0 for c in CATEGORIES}
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in s:
                scores[cat] += 1
    return scores

def classify_text(text: str) -> str:
    """
    Heuristic gate:
      - Dacă regulile au un învingător clar -> returnăm regula (rapid).
      - Dacă e egalitate sau zero potriviri -> apelăm LLM (dacă e activ și suficient de încrezător).
      - Altfel -> fallback pe regula/other.
    """
    scores = _rule_scores(text)
    # ordonăm scorurile pentru a vedea topul și locul 2
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_cat, top = ordered[0]
    second = ordered[1][1] if len(ordered) > 1 else 0

    ambiguous = (top == 0) or (top == second)

    # 1) Dacă nu e ambiguu -> regula e suficientă
    if not ambiguous:
        return best_cat

    # 2) Dacă e ambiguu -> încercăm LLM (dacă e activ)
    if USE_LLM:
        res = classify_llm(text or "")
        if res is not None:
            label, score = res
            if label in CATEGORIES and score >= MIN_CONF:
                return label  # LLM decide
            # dacă scor mic / label necunoscut -> cădem la reguli

    # 3) Fallback determinist
    return best_cat if top > 0 else "other"
