"""Basic smoke tests for MusicTool."""

import sys
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that basic imports work."""
    import musictool
    assert musictool.__version__ == "0.1.0"


def test_app_imports():
    """Test that the main app can be imported."""
    import app
    assert hasattr(app, "main")
    assert callable(app.main)
