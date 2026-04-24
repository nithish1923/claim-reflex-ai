from fastapi import FastAPI
from pydantic import BaseModel
from parser import extract_text_from_url
from validator import validate
from ai_engine import agent_approve, agent_reject, reflection

app = FastAPI()

class ClaimRequest(BaseModel):
    policy_url: str
    claim_url: str


@app.get("/")
def home():
    return {"message": "API running"}


@app.post("/process")
def process_claim(data: ClaimRequest):
    policy_text = extract_text_from_url(data.policy_url)
    claim_text = extract_text_from_url(data.claim_url)

    is_valid, errors = validate(policy_text, claim_text)

    if not is_valid:
        return {"status": "rejected", "errors": errors}

    a = agent_approve(policy_text, claim_text)
    b = agent_reject(policy_text, claim_text)

    final = reflection(a, b)

    return {
        "status": "processed",
        "final": final
    }
