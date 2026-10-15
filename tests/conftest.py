"""
Root conftest forwarder for workspace test runners.
Resolves `tests.conftest` seamlessly whether tests are run from root or from backend/.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
backend_tests_dir = backend_dir / "tests"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(backend_tests_dir) not in sys.path:
    sys.path.insert(0, str(backend_tests_dir))

from backend.tests.conftest import *
