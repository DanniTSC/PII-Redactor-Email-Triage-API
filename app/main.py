from fastapi import FastAPI

app = FastAPI(title="PII Redactor & Email Triage API", version="0.1.0")

@app.get("/health")
def health():
    """
    Simplu healthcheck pentru orchestrare/monitorizare.
    """
    return {"status": "ok"}
