"""Validate truthful partial-handoff and compensation claims."""


def validate_handoff(handoff):
    if not isinstance(handoff, dict) or not handoff.get("step_id"):
        return False
    if handoff.get("status") == "partial":
        if handoff.get("atomicity_claimed") is True:
            return False
        if not handoff.get("compensation_ref"):
            return False
    return True


def test_valid_partial_handoff(handoff_data):
    assert validate_handoff(handoff_data["valid_handoff"]) is True


def test_false_atomicity_blocked(handoff_data):
    assert validate_handoff(handoff_data["false_atomicity"]) is False


def test_partial_without_compensation_blocked(handoff_data):
    handoff = dict(handoff_data["valid_handoff"], compensation_ref=None)
    assert validate_handoff(handoff) is False
