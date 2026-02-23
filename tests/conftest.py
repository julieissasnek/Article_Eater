import os
import tempfile
from pathlib import Path
import pytest
from app.db import ensure_db # ensure the test DB has the minimal schema

@pytest.fixture(scope="session", autouse=True)
def setup_test_db(tmp_path_factory):
    # Create a temporary sqlite database file for tests
    temp_dir = tmp_path_factory.mktemp("db")
    test_db_path = temp_dir / "test_ae.db"
    
    # Set the environment variable so app.db.connect uses it
    os.environ["AE_DB_PATH"] = str(test_db_path)
    
    # Actually create the schema in the temporary database
    ensure_db()
    
    yield
    
    # Cleanup if needed
    pass
