# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import AnalyzeResponse

client = TestClient(app)

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_analyze_billing_flow():
    payload = {
        "text": "Hello, my invoice 123 is wrong. Please refund to IBAN RO49AAAA1B31007593840000. Call me at +40 721 123 456."
    }
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    # header util pentru corelare/loguri
    assert "X-Request-ID" in r.headers

    data = r.json()

    # validăm schema cu Pydantic (failă dacă forma nu corespunde)
    parsed = AnalyzeResponse(**data)

    # redactare corectă
    assert "[IBAN]" in parsed.redacted_text
    assert "[PHONE]" in parsed.redacted_text

    # categorie corectă
    assert parsed.category in {"billing", "tech", "sales", "other"}
    assert parsed.category == "billing"

    # sumar ne-gol, scurt
    assert isinstance(parsed.summary, str) and len(parsed.summary) > 0
    assert len(parsed.summary.split()) <= 30

    # acțiuni coerente pt. billing
    types = [a["type"] if isinstance(a, dict) else a.type for a in data["actions"]]
    assert "create_ticket" in types

def test_analyze_validation_error():
    # text prea scurt/invalid -> 422 (din Pydantic/validation)
    r = client.post("/analyze", json={"text": ""})
    assert r.status_code == 422
