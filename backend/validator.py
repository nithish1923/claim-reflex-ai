import re

def find_match(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_fields(text):

    policy_no = find_match([
        r'Policy\s*No[:\-]?\s*([A-Z0-9\-\/]+)',
        r'Policy\s*Number[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    claim_no = find_match([
        r'Claim\s*No[:\-]?\s*([A-Z0-9\-\/]+)',
        r'Claim\s*Number[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    amount = find_match([
        r'₹\s*([\d,]+)',
        r'Rs\.?\s*([\d,]+)',
        r'INR\s*([\d,]+)',
        r'Amount[:\-]?\s*([\d,]+)'
    ], text)

    claim_policy = find_match([
        r'Policy\s*No[:\-]?\s*([A-Z0-9\-\/]+)',
        r'Policy\s*Number[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    return {
        "policy_no": policy_no,
        "claim_no": claim_no,
        "amount": amount,
        "claim_policy": claim_policy
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

    # Better policy compare
    if p["policy_no"] and c["claim_policy"]:
        if p["policy_no"].strip().lower() != c["claim_policy"].strip().lower():
            errors.append("Policy number mismatch")

    return len(errors) == 0, errors
