import re

def extract_fields(text):
    data = {}

    policy_no = re.search(r'Policy\s*No[:\-]?\s*(\w+)', text)
    claim_no = re.search(r'Claim\s*No[:\-]?\s*(\w+)', text)

    data["policy_no"] = policy_no.group(1) if policy_no else None
    data["claim_no"] = claim_no.group(1) if claim_no else None

    return data


def validate(policy_text, claim_text):
    p = extract_fields(policy_text)
    c = extract_fields(claim_text)

    errors = []

    if not p["policy_no"]:
        errors.append("Missing policy number")

    if not c["claim_no"]:
        errors.append("Missing claim number")

    if p["policy_no"] and c["claim_no"]:
        if p["policy_no"] not in c["claim_no"]:
            errors.append("Policy & Claim mismatch")

    return len(errors) == 0, errors
