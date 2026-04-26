from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from parser import extract_text_from_url
from validator import validate
from ai_engine import agent_approve, agent_reject, reflection

app = FastAPI()

# ✅ CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ClaimRequest(BaseModel):
    policy_url: str
    claim_url: str

# Health check
@app.get("/")
def home():
    return {"message": "API running"}

# Main API
@app.post("/process")
def process_claim(data: ClaimRequest):
    try:
        policy_text = extract_text_from_url(data.policy_url)
        claim_text = extract_text_from_url(data.claim_url)

        print("===== POLICY TEXT =====")
        print(policy_text[:2000])

        print("===== CLAIM TEXT =====")
        print(claim_text[:2000])

        is_valid, errors = validate(policy_text, claim_text)

        if not is_valid:
            return {
                "status": "rejected",
                "errors": errors
            }

        approve_output = agent_approve(policy_text, claim_text)
        reject_output = agent_reject(policy_text, claim_text)

        final = reflection(approve_output, reject_output)

        return {
            "status": "processed",
            "approve_agent": approve_output,
            "reject_agent": reject_output,
            "final": final
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
