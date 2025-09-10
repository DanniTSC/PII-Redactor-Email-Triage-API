# tests/test_actions.py
from app.pipelines.actions import suggest_actions

def test_actions_billing_refund():
    txt = "Please refund to [IBAN]."
    acts = suggest_actions("billing", txt)
    types = [a.type for a in acts]
    assert "create_ticket" in types
    assert "request_refund_details" in types

def test_actions_tech_error():
    txt = "I get an error when opening the app."
    acts = suggest_actions("tech", txt)
    types = [a.type for a in acts]
    assert "create_ticket" in types
    assert "request_debug_info" in types

def test_actions_sales_offer():
    txt = "Do you have a discount or an offer?"
    acts = suggest_actions("sales", txt)
    types = [a.type for a in acts]
    assert "notify_team" in types
    assert "propose_followup" in types

def test_actions_other_fallback():
    acts = suggest_actions("other", "Thanks!")
    types = [a.type for a in acts]
    assert types == ["route_to_human"]
