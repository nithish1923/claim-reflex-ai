import re
from datetime import datetime

# -----------------------------------
# Helpers
# -----------------------------------

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def normalize(value):
    if not value:
        return ""
    return re.sub(r'[^a-z0-9]', '', value.lower())


def normalize_name(name):
    if not name:
        return ""

    name = name.lower()
    name = re.sub(r'[^a-z ]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def names_match(name1, name2):
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    # Exact match
    if n1 == n2:
        return True

    # Contains match
    if n1 in n2 or n2 in n1:
        return True

    # Word overlap match
    words1 = set(n1.split())
    words2 = set(n2.split())

    common = words1.intersection(words2)

    if len(common) >= 2:
        return True

    return False


def parse_date(date_str):
    if not date_str:
        return None

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%Y-%m-%d",
        "%d-%m-%y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            pass

    return None


def find_value(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


# -----------------------------------
# Extract Fields
# -----------------------------------

def extract_fields(text):

    text = clean_text(text)

    policy_no = find_value([
        r'policy\s*(?:no|number|id)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    claim_no = find_value([
        r'claim\s*(?:no|number|id)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    holder_name = find_value([
        r'(?:policy holder name|holder name|insured name|customer name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    claim_name = find_value([
        r'(?:claimant name|claim holder name|customer name|insured name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    valid_to = find_value([
        r'valid\s*to\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)',
        r'expiry\s*date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    claim_amount = find_value([
        r'claim amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'₹\s*([\d,]+)',
        r'rs\.?\s*([\d,]+)'
    ], text)

    return {
        "policy_no": policy_no,
        "claim_no": claim_no,
        "holder_name": holder_name,
        "claim_name": claim_name,
        "valid_to": valid_to,
        "claim_amount": claim_amount
    }


# -----------------------------------
# Main Validation
# -----------------------------------

def validate(policy_text, claim_text):

    policy = extract_fields(policy_text)
    claim = extract_fields(claim_text)

    errors = []

    # Required checks
    if not policy["policy_no"]:
        errors.append("Missing policy number")

    if not claim["claim_no"]:
        errors.append("Missing claim number")

    if not policy["holder_name"]:
        errors.append("Missing policy holder name")

    if not claim["claim_name"]:
        errors.append("Missing claim holder name")

    if not claim["claim_amount"]:
        errors.append("Missing claim amount")

    # Policy number match
    if policy["policy_no"]:
        if normalize(policy["policy_no"]) not in normalize(claim_text):
            errors.append("Policy number mismatch")

    # Name match (fixed)
    if policy["holder_name"] and claim["claim_name"]:
        if not names_match(policy["holder_name"], claim["claim_name"]):
            errors.append("Holder name mismatch")

    # Expiry check
    if policy["valid_to"]:
        expiry = parse_date(policy["valid_to"])

        if expiry:
            today = datetime.today()

            if today > expiry:
                errors.append("Policy expired")

    # Final result
    if errors:
        return False, errors

    return True, []
