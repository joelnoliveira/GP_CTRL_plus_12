"""
Shared pytest fixtures and configuration
"""

import pytest
import os
from dotenv import load_dotenv

# Load environment variables for testing
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.test")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Set default test environment variables
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-testing-only"
    os.environ["REACT_APP_RECAPTCHA_SECRET_KEY"] = "test-recaptcha-secret"


@pytest.fixture(scope="session")
def test_settings():
    """Provide test configuration"""
    return {
        "database_url": os.getenv("DATABASE_URL", "sqlite:///:memory:"),
        "secret_key": os.getenv("AUTH_SECRET_KEY", "test-secret-key"),
        "recaptcha_secret": os.getenv("REACT_APP_RECAPTCHA_SECRET_KEY", "test-secret"),
    }


# Suppress SQLAlchemy echo for cleaner test output
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
