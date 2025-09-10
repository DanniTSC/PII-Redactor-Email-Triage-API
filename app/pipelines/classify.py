from typing import Dict

# Cuvinte-cheie de bază per categorie (EN + RO).
# Simplu, dar stabil și ușor de explicat în interviu.
CATEGORY_KEYWORDS: Dict[str, tuple[str, ...]] = {
    "billing": (
        "invoice", "receipt", "refund", "charge", "payment", "card", "iban",
        "factura", "plată", "plata", "ramburs", "cont", "bancă", "[iban]"
    ),
    "tech": (
        "error", "bug", "issue", "crash", "fail", "server", "api", "login",
        "password", "parola", "conectare", "eroare"
    ),
    "sales": (
        "price", "quote", "offer", "trial", "subscription", "upgrade",
        "discount", "promo", "abonament", "preț", "pret", "ofertă", "oferta"
    ),
    # "other" nu are keywords — e fallback.
}

CATEGORIES = ("billing", "tech", "sales", "other")

def classify_text(text: str) -> str:
    """
    Heuristică simplă: scor pe apariții de cuvinte-cheie.
    Dacă nu găsim nimic → 'other'.
    """
    if not text:
        return "other"

    s = text.lower()
    scores = {c: 0 for c in CATEGORIES}

    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in s:
                scores[cat] += 1

    # alegem cea mai mare categorie; dacă toate 0 -> other
    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "other"
