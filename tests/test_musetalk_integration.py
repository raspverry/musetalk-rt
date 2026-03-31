"""Discovery shim so `python -m unittest discover -s tests -p 'test_*.py'` picks up runtime/session tests."""

from tests.runtime.session.test_musetalk_integration import MuseTalkIntegrationTests

__all__ = ["MuseTalkIntegrationTests"]
