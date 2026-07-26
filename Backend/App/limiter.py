import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared slowapi rate limiter instance (disabled during pytest)
is_testing = os.getenv("TESTING", "false").lower() == "true" or "PYTEST_CURRENT_TEST" in os.environ
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"], enabled=not is_testing)
