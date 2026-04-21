"""
Git hook unit tests — T-077 to T-080.
Phase: v2 🔒 LOCKED (until CLI tests pass)
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="Git hooks not yet implemented — "
           "build hooks/ and complete CLI tests first."
)


def test_hook_installs_in_under_30s():
    """T-077: `python hooks/install_hooks.py` completes in <30s."""
    pass


def test_hook_is_executable():
    """T-078: hooks/post-commit has executable permissions."""
    pass


def test_hook_triggers_on_commit():
    """T-079: A git commit in a tracked repo triggers post-commit hook."""
    pass


def test_incremental_reindex_under_2s():
    """T-080: Hook re-indexes changed files in <2s."""
    pass
