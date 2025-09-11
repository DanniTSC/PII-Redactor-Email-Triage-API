from __future__ import annotations
from typing import List
from app.schemas import Action #action is the Pydantic model that gives the output as a JSON 

def suggest_actions(category: str, text: str) -> List[Action]:
    """
    Input: category and text, output list of actions that the system could do 
    Outputul trebuie să fie mereu JSON-valid conform Action.
    """
    t = (text or "").lower()
    acts: List[Action] = []

    if category == "billing":
        # întotdeauna creăm tichet în coada 'billing'
        acts.append(Action(type="create_ticket", params={"queue": "billing", "priority": "normal"}))
        # dacă pare ramburs/IBAN
        if "[iban]" in t or "refund" in t or "ramburs" in t:
            acts.append(Action(type="request_refund_details", params={"required": ["amount", "currency"]}))
    elif category == "tech":
        acts.append(Action(type="create_ticket", params={"queue": "tech", "priority": "normal"}))
        # indicii pentru login/eroare => cere log-uri sau reset
        if "login" in t or "parola" in t:
            acts.append(Action(type="send_reset_instructions", params={"channel": "email"}))
        if "error" in t or "eroare" in t or "crash" in t:
            acts.append(Action(type="request_debug_info", params={"fields": ["timestamp", "steps", "screenshot"]}))
    elif category == "sales":
        # rutează către echipa de vânzări; dacă există „price/offer/discount” -> propune follow-up
        acts.append(Action(type="notify_team", params={"team": "sales"}))
        if "price" in t or "preț" in t or "pret" in t or "offer" in t or "ofert" in t or "discount" in t:
            acts.append(Action(type="propose_followup", params={"channel": "email"}))
    else:
        # fallback sigur
        acts.append(Action(type="route_to_human", params={"queue": "general"}))

    return acts
