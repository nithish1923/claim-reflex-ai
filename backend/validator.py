import re

def extract_fields(text):
    data = {}

    # More flexible patterns
    policy_no = re.search(
        r'(policy\s*(no|number|id)?|policy id)\s*[:\-]?\s*([A-Z0-9\-\/]+)',
        text,
        re.IGNORECASE
    )

    claim_no = re.search(
        r'(claim\s*(no|number|id)?|reference\s*no)\s*[:\-]?\s*([A-Z0-9\-\/]+)',
        text,
        re.IGNORECASE
    )

    customer = re.search(
        r'(name|customer name|insured name)\s*[:\-]?\s*([A-Za-z ]+)',
        text,
        re.IGNORECASE
    )

    amount = re.search(
        r'(amount|claim amount|total)\s*[:\-]?\s*([\d,]+)',
        text,
        re.IGNORECASE
    )

    data["policy_no"] = policy_no.group(3).strip() if policy_no else None
    data["claim_no"] = claim_no.group(3).strip() if claim_no else None
    data["customer_name"] = customer.group(2).strip() if customer else None
    data["amount"] = amount.group(2).strip() if amount else None

    return data


def validate(policy_text, claim_text):

    p = extract_fields(policy_text)
    c = extract_fields(claim_text)

    errors = []

    # Mandatory checks
    if not p["policy_no"]:
        errors.append("Missing policy number")

    if not c["claim_no"]:
        errors.append("Missing claim number")

    # Smart comparison
    if p["policy_no"] and c["claim_no"]:
        if p["policy_no"] not in claim_text:
            errors.append("Policy number not linked in claim file")

    # Optional checks
    if c["amount"] is None:
        errors.append("Missing claim amount")

    return len(errors) == 0, errors
