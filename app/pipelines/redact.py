import re

# Regex-uri robuste 
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# Phone: 
PHONE_RE = re.compile(
    r"(?<!\w)(?:(?:\+|00)\d{1,3}[\s.\-]?)?(?:\(?\d{2,4}\)?[\s.\-]?)?\d{3}[\s.\-]?\d{3,4}(?!\w)"
)
# IBAN 
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
# CNP 
CNP_RE = re.compile(r"\b[1-8]\d{12}\b")
# Adrese 
ADDRESS_RE = re.compile(
    r"(?i)\b(?:str(?:ada)?|bd\.?|bulevardul|aleea)\s+[A-Za-z0-9\-\.' ]+(?:\s+nr\.?\s*\d+[A-Za-z]?)?\b"
)

def redact_pii(text: str) -> str:
    if not text:
        return text

    red = EMAIL_RE.sub("[EMAIL]", text)

    # 1) Mai întâi tipurile SPECIFICE:
    red = IBAN_RE.sub("[IBAN]", red)
    red = CNP_RE.sub("[CNP]", red)

    # 2) Apoi telefonul (mai „greedy”)
    def _phone_sub(m):
        raw = m.group(0)
        digits = re.sub(r"\D", "", raw)
        # Heuristică anti-false-positive:
        # - să aibă separatori/semn + (să semene cu telefon) 
        # - să nu fie un CNP „perfect” (13 cifre 1-8xxxxxxxxxxxx)
        has_sep = bool(re.search(r"[+\-\s().]", raw))
        if len(digits) >= 9 and has_sep and not CNP_RE.fullmatch(digits):
            return "[PHONE]"
        return raw

    red = PHONE_RE.sub(_phone_sub, red)

    red = ADDRESS_RE.sub("[ADDRESS]", red)
    return red
