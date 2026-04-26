import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def agent_approve(policy_text, claim_text):
    return "Documents match. Policy active. Claim details valid. Recommend approval."

def agent_reject(policy_text, claim_text):
    return "No major mismatch found. No rejection reason detected."

def reflection(approve_output, reject_output):

    approve_score = 0.85
    reject_score = 0.15

    if approve_score > reject_score:
        return {
            "decision": "Approved",
            "confidence": approve_score,
            "reason": approve_output
        }

    return {
        "decision": "Rejected",
        "confidence": reject_score,
        "reason": reject_output
    }
