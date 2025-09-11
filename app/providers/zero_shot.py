# app/providers/zero_shot.py
import os
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

# Toggle și configurare
USE_LLM = os.getenv("USE_LLM_CLASSIFIER", "0") == "1"
MODEL_NAME = os.getenv("ZSC_MODEL", "typeform/distilbert-base-uncased-mnli")
MIN_CONF = float(os.getenv("ZSC_MIN_CONF", "0.55"))
HYPOTHESIS_TEMPLATE = os.getenv("ZSC_TEMPLATE", "This message is about {}.")

# Grupăm sinonime/parafoaze pe categorii; scorul categoriei = MAX(scoruri din grup)
CANDIDATE_GROUPS: Dict[str, List[str]] = {
    "billing": [
        "billing", "payments", "payment problems", "refund", "reimbursement",
        "chargeback", "invoice issue", "incorrect invoice"
    ],
    "tech": [
        "technical support", "bug", "error", "api issue", "login problem",
        "authentication problem", "sign in problem", "password reset"
    ],
    "sales": [
        "sales", "pricing", "quote", "subscription", "plan upgrade", "enterprise plan",
        "trial request", "discount"
    ],
    "other": [
        "general inquiry", "other"
    ],
}

ALL_LABELS: List[str] = [l for group in CANDIDATE_GROUPS.values() for l in group]

@lru_cache(maxsize=1)
def _get_pipeline():
    if not USE_LLM:
        return None
    from transformers import pipeline
    # device=-1 => CPU (pe Windows e cel mai safe)
    return pipeline("zero-shot-classification", model=MODEL_NAME, device=-1)

def classify_llm(text: str) -> Optional[Tuple[str, float]]:
    """
    Întoarce (best_category, best_score) folosind grupuri de etichete.
    Dacă LLM e dezactivat -> None.
    """
    zsc = _get_pipeline()
    if zsc is None or not text:
        return None

    out = zsc(
        text,
        candidate_labels=ALL_LABELS,
        multi_label=False,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
    )
    labels: List[str] = out["labels"]
    scores: List[float] = [float(s) for s in out["scores"]]
    score_by_label = {lab: sc for lab, sc in zip(labels, scores)}

    # agregăm pe categorii: scorul categoriei = MAX scor dintre etichetele ei
    best_cat = "other"
    best_score = 0.0
    for cat, labs in CANDIDATE_GROUPS.items():
        cat_score = max((score_by_label.get(l, 0.0) for l in labs), default=0.0)
        if cat_score > best_score:
            best_cat, best_score = cat, cat_score

    return best_cat, best_score

#zero shot entailment textul si etichetele si alege ce se potriveste cel mai bine 
#rapid, memorie mica, acuratete ok,
#sensibil la etichetel 
