from app.pipelines.redact import redact_pii

def test_redact_email():
    t = "Contact me at john.doe@example.com for details."
    assert "[EMAIL]" in redact_pii(t)

def test_redact_phone():
    t = "Telefon: +40 721 123 456 te sun maine."
    out = redact_pii(t)
    assert "[PHONE]" in out

def test_redact_iban():
    t = "IBAN: RO49AAAA1B31007593840000"
    out = redact_pii(t)
    assert "[IBAN]" in out

def test_redact_cnp():
    t = "CNP-ul meu este 1980101123456 dar nu vreau sa-l stie nimeni."
    out = redact_pii(t)
    assert "[CNP]" in out

def test_redact_address():
    t = "Ne vedem pe Strada Aviatorilor nr. 10 la 18:00."
    out = redact_pii(t)
    assert "[ADDRESS]" in out
