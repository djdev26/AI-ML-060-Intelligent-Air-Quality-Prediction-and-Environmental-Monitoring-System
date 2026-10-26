"""
Pytest configuration for AI-ML-060:
Ensures root directory is on sys.path for test modules.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
