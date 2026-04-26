import re

def extract_fields(text):
    policy = re.search(r'Policy\s*(No|Number)?\s*[:\-]?\s*([A-Z0-9\-]+)', text, re.I)
    claim = re.search(r'Claim\s*(No|Number)?\s*[:\-]?\s*([A-Z0-9\-]+)', text, re.I)
    amount = re.search(r'(Amount|Claim Amount)\s*[:\-]?\s*([\d,]+)', text, re.I)

    return {
        "policy_no": policy.group(2) if policy else None,
        "claim_no": claim.group(2) if claim else None,
        "amount": amount.group(2) if amount else None
    }

def validate(policy_text, claim_text):
    p = extract_fields(policy_text)
    c = extract_fields(claim_text)

    errors = []

    if not p["policy_no"]:
        errors.append("Missing policy number")

    if not c["claim_no"]:
        errors.append("Missing claim number")

    if not c["amount"]:
        errors.append("Missing claim amount")

    if p["policy_no"] and p["policy_no"] not in claim_text:
        errors.append("Policy mismatch")

    return len(errors) == 0, errors
