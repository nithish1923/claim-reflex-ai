import re
from datetime import datetime


# -----------------------------------
# Helpers
# -----------------------------------

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize(value):
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def parse_date(date_str):
    if not date_str:
        return None

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%b-%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            pass

    return None


def find(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).strip()
    return None


# -----------------------------------
# Extract fields
# -----------------------------------

def extract_policy(text):
    text = clean_text(text)

    return {
        "policy_no": find([
            r'policy\s*(?:no|number)?\s*:\s*([A-Z0-9\-\/]+)'
        ], text),

        "holder_name": find([
            r'policy holder name\s*:\s*([A-Za-z ]+)'
        ], text),

        "valid_to": find([
            r'valid to\s*:\s*([0-9\-\/]+)'
        ], text)
    }


def extract_claim(text):
    text = clean_text(text)

    return {
        "claim_no": find([
            r'claim\s*(?:no|number)?\s*:\s*([A-Z0-9\-\/]+)'
        ], text),

        "policy_no": find([
            r'policy\s*(?:no|number)?\s*:\s*([A-Z0-9\-\/]+)'
        ], text),

        "claim_name": find([
            r'claimant name\s*:\s*([A-Za-z ]+)'
        ], text),

        "claim_amount": find([
            r'claim amount\s*:\s*₹?\s*([\d,]+)'
        ], text)
    }


# -----------------------------------
# Main validate
# -----------------------------------

def validate(policy_text, claim_text):

    policy = extract_policy(policy_text)
    claim = extract_claim(claim_text)

    errors = []

    # Required fields
    if not policy["policy_no"]:
        errors.append("Missing policy number")

    if not claim["claim_no"]:
        errors.append("Missing claim number")

    if not claim["policy_no"]:
        errors.append("Missing policy number in claim")

    if not claim["claim_amount"]:
        errors.append("Missing claim amount")

    # Policy number exact compare
    if policy["policy_no"] and claim["policy_no"]:
        if normalize(policy["policy_no"]) != normalize(claim["policy_no"]):
            errors.append("Policy number mismatch")

    # Name compare
    if policy["holder_name"] and claim["claim_name"]:
        if normalize(policy["holder_name"]) != normalize(claim["claim_name"]):
            errors.append("Holder name mismatch")

    # Expiry
    if policy["valid_to"]:
        dt = parse_date(policy["valid_to"])
        if dt and datetime.today() > dt:
            errors.append("Policy expired")

    if errors:
        return False, errors

    return True, []
