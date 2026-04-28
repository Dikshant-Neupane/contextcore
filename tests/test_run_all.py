from __future__ import annotations

from tests import run_all


def test_print_gate_verdict_returns_gate_failure_code(capsys) -> None:
    summary = {"passed": 3, "failed": 1, "skipped": 0, "errors": 0, "total": 4}

    exit_code = run_all.print_gate_verdict(summary, exit_code=1, mode="gate")

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Phase gate is blocked" in captured.out


def test_print_gate_verdict_uses_full_mode_label(capsys) -> None:
    summary = {"passed": 10, "failed": 0, "skipped": 2, "errors": 0, "total": 10}

    exit_code = run_all.print_gate_verdict(summary, exit_code=0, mode="full")

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "FULL TEST SUITE PASSED" in captured.out