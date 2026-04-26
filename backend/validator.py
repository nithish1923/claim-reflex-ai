import re
from datetime import datetime

# ==========================================================
# CLAIM REFLEX AI - ENTERPRISE VALIDATOR
# Covers:
# ✔ Policy Number
# ✔ Claim Number
# ✔ Holder Name
# ✔ Date Expiry
# ✔ Claim Amount
# ✔ Policy Number Match
# ✔ Name Fuzzy Match
# ✔ Future Claim Date
# ✔ Duplicate Basic Checks
# ✔ Upper/lower case
# ✔ Extra spaces
# ✔ Missing fields
# ✔ Different label formats
# ==========================================================


# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

def clean_text(text):
    if not text:
        return ""
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize(value):
    if not value:
        return ""
    return re.sub(r'[^a-z0-9]', '', value.lower())


def normalize_name(name):
    if not name:
        return ""

    name = name.lower()
    name = re.sub(r'[^a-z ]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def names_match(name1, name2):

    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    # exact
    if n1 == n2:
        return True

    # contains
    if n1 in n2 or n2 in n1:
        return True

    # token overlap
    s1 = set(n1.split())
    s2 = set(n2.split())

    common = s1.intersection(s2)

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
        "%d-%m-%y",
        "%d/%m/%y"
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


# ----------------------------------------------------------
# Field Extraction
# ----------------------------------------------------------

def extract_fields(text):

    text = clean_text(text)

    policy_no = find_value([
        r'policy\s*(?:no|number|id)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    claim_no = find_value([
        r'claim\s*(?:no|number|id|reference)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    holder_name = find_value([
        r'(?:policy holder name|holder name|insured name|customer name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    claim_name = find_value([
        r'(?:claimant name|claim holder name|customer name|insured name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    valid_from = find_value([
        r'valid from\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    valid_to = find_value([
        r'valid to\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)',
        r'expiry date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    claim_date = find_value([
        r'incident date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)',
        r'claim date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    claim_amount = find_value([
        r'claim amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'₹\s*([\d,]+)',
        r'rs\.?\s*([\d,]+)',
        r'inr\s*([\d,]+)'
    ], text)

    return {
        "policy_no": policy_no,
        "claim_no": claim_no,
        "holder_name": holder_name,
        "claim_name": claim_name,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "claim_date": claim_date,
        "claim_amount": claim_amount
    }


# ----------------------------------------------------------
# Main Validation Engine
# ----------------------------------------------------------

def validate(policy_text, claim_text):

    policy = extract_fields(policy_text)
    claim = extract_fields(claim_text)

    errors = []
    warnings = []

    # ======================================================
    # REQUIRED FIELD CHECKS
    # ======================================================

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

    # ======================================================
    # POLICY NUMBER MATCH
    # ======================================================

    if policy["policy_no"]:
        if normalize(policy["policy_no"]) not in normalize(claim_text):
            errors.append("Policy number mismatch")

    # ======================================================
    # HOLDER NAME MATCH
    # ======================================================

    if policy["holder_name"] and claim["claim_name"]:
        if not names_match(policy["holder_name"], claim["claim_name"]):
            errors.append("Holder name mismatch")

    # ======================================================
    # POLICY DATE VALIDATION
    # ======================================================

    today = datetime.today()

    if policy["valid_to"]:

        expiry = parse_date(policy["valid_to"])

        if expiry:
            if today > expiry:
                errors.append("Policy expired")

    if policy["valid_from"]:

        start = parse_date(policy["valid_from"])

        if start:
            if today < start:
                errors.append("Policy not active yet")

    # ======================================================
    # CLAIM DATE CHECK
    # ======================================================

    if claim["claim_date"]:

        cdate = parse_date(claim["claim_date"])

        if cdate:
            if cdate > today:
                errors.append("Claim date is in future")

            if policy["valid_from"] and policy["valid_to"]:

                start = parse_date(policy["valid_from"])
                end = parse_date(policy["valid_to"])

                if start and end:
                    if cdate < start or cdate > end:
                        errors.append("Claim date outside policy coverage period")

    # ======================================================
    # CLAIM AMOUNT CHECK
    # ======================================================

    if claim["claim_amount"]:

        amt = int(claim["claim_amount"].replace(",", ""))

        if amt <= 0:
            errors.append("Invalid claim amount")

        if amt > 10000000:
            warnings.append("Very high claim amount")

    # ======================================================
    # DUPLICATE BASIC SANITY
    # ======================================================

    if policy["policy_no"] and claim["claim_no"]:
        if normalize(policy["policy_no"]) == normalize(claim["claim_no"]):
            warnings.append("Claim number same as policy number")

    # ======================================================
    # FINAL RESULT
    # ======================================================

    if errors:
        return False, errors

    return True, warnings
