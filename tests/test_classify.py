from app.pipelines.classify import classify_text

def test_classify_billing_basic():
    t = "My invoice is wrong, please issue a refund."
    assert classify_text(t) == "billing"

def test_classify_tech_basic():
    t = "I get an error when I try to login. Please fix the bug."
    assert classify_text(t) == "tech"

def test_classify_sales_basic():
    t = "What's the price and do you have any discount or an offer?"
    assert classify_text(t) == "sales"

def test_classify_other_fallback():
    t = "Thanks a lot, have a great day!"
    assert classify_text(t) == "other"

def test_classify_billing_hint_from_redaction():
    t = "Please send the refund to [IBAN]."
    assert classify_text(t) == "billing"
