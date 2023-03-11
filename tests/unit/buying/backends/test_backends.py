from apps.buying.backends import BACKENDS, AppleBackend, DummyBackend


def test_backends():
    assert BACKENDS == {"dummy": DummyBackend, "apple": AppleBackend}
