import re
from datetime import datetime

# ==========================================================
# CLAIM REFLEX AI - FINAL ROBUST VALIDATOR
# Covers:
# ✔ Policy Number Match
# ✔ Claim Number
# ✔ Holder Name Match (fuzzy)
# ✔ Case insensitive
# ✔ Spaces / hyphen / slash issues
# ✔ Policy Expiry
# ✔ Policy Start Date
# ✔ Claim Date Future Check
# ✔ Claim Date Within Coverage
# ✔ Claim Amount Validation
# ✔ Missing Fields
# ✔ OCR / PDF messy spacing support
# ✔ Multiple label formats
# ==========================================================


# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------

def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize(value):
    if not value:
        return ""

    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalize_name(name):
    if not name:
        return ""

    name = name.lower()
    name = re.sub(r"[^a-z ]", " ", name)
    name = re.sub(r"\s+", " ", name)
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
        "%d-%m-%y",
        "%d/%m/%y",
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
# FIELD EXTRACTION
# ----------------------------------------------------------

def extract_fields(text):

    text = clean_text(text)

    data = {}

    # Policy Number
    data["policy_no"] = find_value([
        r'policy\s*(?:no|number|id)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    # Claim Number
    data["claim_no"] = find_value([
        r'claim\s*(?:no|number|id|reference)?\s*[:\-]?\s*([A-Z0-9\-\/]+)'
    ], text)

    # Policy holder
    data["holder_name"] = find_value([
        r'(?:policy holder name|holder name|insured name|customer name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    # Claim holder
    data["claim_name"] = find_value([
        r'(?:claimant name|claim holder name|insured name|customer name)\s*[:\-]?\s*([A-Za-z ]+)'
    ], text)

    # Valid from
    data["valid_from"] = find_value([
        r'valid from\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    # Valid to
    data["valid_to"] = find_value([
        r'valid to\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)',
        r'expiry date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    # Claim date
    data["claim_date"] = find_value([
        r'incident date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)',
        r'claim date\s*[:\-]?\s*([0-9A-Za-z\/\- ]+)'
    ], text)

    # Amount
    data["claim_amount"] = find_value([
        r'claim amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'amount\s*[:\-]?\s*₹?\s*([\d,]+)',
        r'₹\s*([\d,]+)',
        r'rs\.?\s*([\d,]+)',
        r'inr\s*([\d,]+)'
    ], text)

    return data


# ----------------------------------------------------------
# MAIN VALIDATION
# ----------------------------------------------------------

def validate(policy_text, claim_text):

    policy = extract_fields(policy_text)
    claim = extract_fields(claim_text)

    errors = []
    warnings = []

    today = datetime.today()

    # ======================================================
    # REQUIRED CHECKS
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

    claim_policy = claim["policy_no"]

    if policy["policy_no"] and claim_policy:
        if normalize(policy["policy_no"]) != normalize(claim_policy):
            errors.append("Policy number mismatch")

    # ======================================================
    # HOLDER NAME MATCH
    # ======================================================

    if policy["holder_name"] and claim["claim_name"]:
        if not names_match(policy["holder_name"], claim["claim_name"]):
            errors.append("Holder name mismatch")

    # ======================================================
    # POLICY START CHECK
    # ======================================================

    if policy["valid_from"]:
        start_date = parse_date(policy["valid_from"])

        if start_date and today < start_date:
            errors.append("Policy not active yet")

    # ======================================================
    # POLICY EXPIRY CHECK
    # ======================================================

    if policy["valid_to"]:
        expiry = parse_date(policy["valid_to"])

        if expiry and today > expiry:
            errors.append("Policy expired")

    # ======================================================
    # CLAIM DATE CHECK
    # ======================================================

    if claim["claim_date"]:
        cdate = parse_date(claim["claim_date"])

        if cdate:

            if cdate > today:
                errors.append("Claim date in future")

            start = parse_date(policy["valid_from"]) if policy["valid_from"] else None
            end = parse_date(policy["valid_to"]) if policy["valid_to"] else None

            if start and cdate < start:
                errors.append("Claim before policy start date")

            if end and cdate > end:
                errors.append("Claim after policy expiry")

    # ======================================================
    # CLAIM AMOUNT CHECK
    # ======================================================

    if claim["claim_amount"]:
        try:
            amount = int(claim["claim_amount"].replace(",", ""))

            if amount <= 0:
                errors.append("Invalid claim amount")

            if amount > 10000000:
                warnings.append("Very high claim amount")

        except:
            errors.append("Invalid claim amount format")

    # ======================================================
    # DUPLICATE SANITY CHECK
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
