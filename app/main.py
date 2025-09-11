from uuid import uuid4
from fastapi import FastAPI, HTTPException, Response
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.pipelines.redact import redact_pii
from app.pipelines.classify import classify_text
from app.pipelines.summarize import summarize_text
from app.pipelines.actions import suggest_actions

app = FastAPI(
    title="PII Redactor & Email Triage API",
    version="0.2.0",
    description="Analyze user text → redact PII → classify → summarize → suggest actions.",
)


#api ul propriu zis 
#primeste text intoarce un json cu Personal Identifiable Information, category, rezumat si actions 
@app.post("/analyze", response_model=AnalyzeResponse, tags=["analyze"])
def analyze(req: AnalyzeRequest, response: Response):
    """
    Pipeline end-to-end (determinist, privacy-first):
    1) redact PII
    2) classify (pe textul redacționat — avem hint-uri ca [IBAN])
    3) summarize (≤30 cuvinte, fără PII)
    4) suggest actions (JSON validat)
    """
    try:
        # request id în header (util pt. loguri/observabilitate)
        response.headers["X-Request-ID"] = str(uuid4())

        # 1) Privacy-first
        red = redact_pii(req.text or "")

        # 2) Clasificare pe textul redacționat (ex: [IBAN] ajută la 'billing')
        category = classify_text(red) or "other"

        # 3) Sumarizare deterministă (fără PII)
        summary = summarize_text(red, max_words=30)

        # 4) Acțiuni deterministe + schemă strictă
        actions = suggest_actions(category, red)

        # 5) Validare de schemă & răspuns JSON
        return AnalyzeResponse(
            redacted_text=red,
            category=category,  # Literal restrictiv: billing|tech|sales|other
            summary=summary,
            actions=actions,
        )
    except Exception as e:
        # în prod ai pune log intern (fără PII); aici răspuns standardizat
        raise HTTPException(status_code=500, detail="internal-error") from e
