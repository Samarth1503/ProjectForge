import pytest
from projectforge.errors import ProjectForgeError, ConfigurationError, MissingAPIKeyError

def test_error_hierarchy():
    err = MissingAPIKeyError("Key is missing")
    assert isinstance(err, ConfigurationError)
    assert isinstance(err, ProjectForgeError)
    assert isinstance(err, Exception)
    assert str(err) == "Key is missing"
