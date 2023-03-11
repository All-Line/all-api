from apps.buying.backends.apple import AppleBackend
from apps.buying.backends.dummy import DummyBackend

BACKENDS = {"dummy": DummyBackend, "apple": AppleBackend}
