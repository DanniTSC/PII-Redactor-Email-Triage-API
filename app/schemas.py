from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field

# Categoriile pe care le folosim în triere
Category = Literal["billing", "tech", "sales", "other"]

class AnalyzeRequest(BaseModel):
    """
    Inputul endpoint-ului /analyze.
    """
    text: str = Field(..., min_length=3, max_length=8000, description="Raw user message/email/ticket text")

class Action(BaseModel):
    """
    O acțiune recomandată de sistem, consumabilă de un backend (ex. creează tichet).
    """
    type: str = Field(..., description="Action name, e.g. 'create_ticket'")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters, e.g. {'queue':'billing'}")

class AnalyzeResponse(BaseModel):
    """
    Outputul endpoint-ului /analyze.
    """
    redacted_text: str
    category: Category
    summary: str
    actions: List[Action] = Field(default_factory=list)

#contract, cum sa arate datele 
#fast api foloseste clasele sa valideze json urile 



