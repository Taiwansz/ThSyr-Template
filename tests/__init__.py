"""
ThSyr Test Suite
Configura isolamento hermetico para testes unitarios, redirecionando THSYR_ENV=test
e impedindo mutacao do estado do repositorio.
"""

import os
import tempfile
from pathlib import Path

os.environ["THSYR_ENV"] = "test"
if "THSYR_STATE_DIR" not in os.environ:
    test_state = Path(tempfile.gettempdir()) / f"thsyr_test_state_{os.getpid()}"
    test_state.mkdir(parents=True, exist_ok=True)
    os.environ["THSYR_STATE_DIR"] = str(test_state)
