from validator import validate

def test_valid():
    p = "Policy No: ABC123"
    c = "Claim No: ABC123-1"

    valid, _ = validate(p, c)
    assert valid
