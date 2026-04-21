"""
CLI unit tests — T-071 to T-076.
Phase: v2 🔒 LOCKED (until builder + querier tests pass)
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="CLI not yet implemented — "
           "build src/contextcore/cli/ and complete Layer 4 tests first."
)


def test_index_command_runs():
    """T-071: `contextcore index ./project` exits 0 and creates .contextcore/."""
    pass


def test_query_command_runs():
    """T-072: `contextcore query "..."` exits 0 and prints Markdown."""
    pass


def test_status_command_runs():
    """T-073: `contextcore status` exits 0 and prints graph summary."""
    pass


def test_diff_command_runs():
    """T-074: `contextcore diff` exits 0 and reports changed nodes."""
    pass


def test_query_output_is_markdown():
    """T-075: Query output starts with a Markdown header."""
    pass


def test_json_flag_returns_json():
    """T-076: `contextcore query --json` returns valid JSON."""
    pass
