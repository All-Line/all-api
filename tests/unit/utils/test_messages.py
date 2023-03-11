from utils.messages import LOGIN_ERROR, NO_VERIFIED_USER


def test_messages():
    assert LOGIN_ERROR == "The data entered is incorrect."
    assert NO_VERIFIED_USER == "This account is not verified."
