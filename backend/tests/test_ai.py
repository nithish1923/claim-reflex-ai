from ai_engine import reflection

def test_reflection():
    res = reflection("Approve", "Reject")

    assert "decision" in res
    assert "confidence" in res
