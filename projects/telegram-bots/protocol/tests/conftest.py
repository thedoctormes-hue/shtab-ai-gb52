"""Pytest configuration."""
import sys
from pathlib import Path

# Add LabDoctorM root to path BEFORE any imports
ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "shared"))