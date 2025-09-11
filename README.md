PII-Redactor & Email-Triage API

Privacy-first service that takes a raw email/ticket, redacts PII, classifies it (billing | tech | sales | other), summarizes it (≤30 words), and returns actionable JSON (e.g., create_ticket, request_refund_details). Built with FastAPI + Pydantic. Optional Hugging Face zero-shot classifier with a safe rules fallback.

✨ Features
PII redaction (email, phone, IBAN, CNP, address) → [EMAIL], [PHONE], [IBAN], [CNP], [ADDRESS]
Classification
Fast rules baseline (keywords EN/RO + [IBAN] hint)
Optional LLM zero-shot (MNLI) with heuristic gate (called only when rules are inconclusive)
Deterministic summarization (first meaningful sentence, ≤30 words)
Action suggestions as structured JSON the backend can consume
Strict schema validation on input/output (Pydantic)
OpenAPI/Swagger docs at /docs
Eval harness with metrics (validity, accuracy, PII recall, latency)

# from project root
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt

# run API
uvicorn app.main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs

Enable LLM in PowerShell:
$env:USE_LLM_CLASSIFIER="1"

Disable (rules only):
Remove-Item Env:USE_LLM_CLASSIFIER -ErrorAction SilentlyContinue
uvicorn app.main:app --reload

For Evaluation Run:
python -m evals.eval

For Testing Run:
python -m pytest -q

Example request 
{
  "text": "Please refund to IBAN RO49AAAA1B31007593840000. Phone +40 721 123 456."
}
{
  "text": "Hello, my invoice 123 is wrong. Please refund to IBAN RO49AAAA1B31007593840000. Call me at +40 721 123 456."
}
{
  "text": "Login error when accessing the dashboard. Please reset my password."
}
{
  "text": "Login error when accessing the dashboard. Please reset my password."
}
{
  "text": "Do you have a discount or an offer for the premium plan? What's the price?"
}
{
  "text": "We need a reimbursement for a duplicate charge on our account."
}
