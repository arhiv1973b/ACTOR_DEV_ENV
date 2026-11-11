import pytest
import sys

# Run pytest programmatically
exit_code = pytest.main(["-q", "tests/python/test_validator.py"])
sys.exit(exit_code)
