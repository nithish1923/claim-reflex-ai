import re
from datetime import datetime

# ==========================================================
# CLAIM REFLEX AI - FULL & FINAL validator.py
# Covers:
# ✔ Policy Number Match
# ✔ Claim Number Check
# ✔ Mandatory Holder Names
# ✔ Fuzzy Name Matching
# ✔ Case Insensitive Checks
# ✔ OCR / Extra Spaces Handling
# ✔ Policy Expiry Check
# ✔ Missing Fields
# ✔ Claim Amount Check
# ✔ Clean Date Parsing
# ✔ Separate Policy / Claim Extraction
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

    # Exact match
    if n1 == n2:
        return True

    # Partial match
    if n1 in n2 or n2 in n1:
        return True

    # Word overlap match
    words1 = set(n1.split())
    words2 = set(n2.split())

    if len(words1.intersection(words2)) >= 2:
        return True

    return False


def parse_date(date_str):

    if not date_str:
        return None

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d %b %Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            pass

    return None


def find(patterns, text):

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip()

    return None


# ----------------------------------------------------------
# EXTRACT POLICY DATA
# ----------------------------------------------------------

def extract_policy(text):

    text = clean_text(text)

    return {
        "policy_no": find([
            r'policy\s*(?:no|number)?\s*:\s*([A-Z0-9\-\/]+)'
        ], text),

        "holder_name": find([
            r'policy holder name\s*:\s*([A-Za-z ]+?)\s*(?:policy no|vehicle|plan|valid|sum insured|terms|$)'
        ], text),

        "valid_to": find([
            r'valid to\s*:\s*([0-9\-\/]+)'
        ], text)
    }


# ----------------------------------------------------------
# EXTRACT CLAIM DATA
# ----------------------------------------------------------

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
            r'claimant name\s*:\s*([A-Za-z ]+?)\s*(?:incident|claim amount|reason|garage|documents|$)'
        ], text),

        "claim_amount": find([
            r'claim amount\s*:\s*₹?\s*([\d,]+)',
            r'amount\s*:\s*₹?\s*([\d,]+)',
            r'₹\s*([\d,]+)'
        ], text)
    }


# ----------------------------------------------------------
# MAIN VALIDATION
# ----------------------------------------------------------

def validate(policy_text, claim_text):

    policy = extract_policy(policy_text)
    claim = extract_claim(claim_text)

    errors = []

    # ------------------------------------------------------
    # REQUIRED FIELD CHECKS
    # ------------------------------------------------------

    if not policy["policy_no"]:
        errors.append("Missing policy number")

    if not claim["claim_no"]:
        errors.append("Missing claim number")

    if not claim["policy_no"]:
        errors.append("Missing policy number in claim")

    if not claim["claim_amount"]:
        errors.append("Missing claim amount")

    if not policy["holder_name"]:
        errors.append("Missing policy holder name")

    if not claim["claim_name"]:
        errors.append("Missing claimant name")

    # ------------------------------------------------------
    # POLICY NUMBER MATCH
    # ------------------------------------------------------

    if policy["policy_no"] and claim["policy_no"]:
        if normalize(policy["policy_no"]) != normalize(claim["policy_no"]):
            errors.append("Policy number mismatch")

    # ------------------------------------------------------
    # HOLDER NAME MATCH
    # ------------------------------------------------------

    if policy["holder_name"] and claim["claim_name"]:
        if not names_match(policy["holder_name"], claim["claim_name"]):
            errors.append("Holder name mismatch")

    # ------------------------------------------------------
    # POLICY EXPIRY CHECK
    # ------------------------------------------------------

    if policy["valid_to"]:
        expiry = parse_date(policy["valid_to"])

        if expiry and datetime.today() > expiry:
            errors.append("Policy expired")

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    if errors:
        return False, errors

    return True, []
