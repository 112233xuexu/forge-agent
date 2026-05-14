import json
import sys

from forge_agent.entrypoint import cli_entrypoint


def test_ask_help_outputs_usage(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "ask", "--help"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "usage: forge-agent ask" in captured.out
    assert "organize my invoices" in captured.out


def test_ask_missing_request_text_error(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "ask"])

    exit_code = cli_entrypoint()

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Forge Agent ask error" in captured.err
    assert "provide a request" in captured.err


def test_ask_missing_request_json_error(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "ask", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.err)
    assert data["error"] == "missing_request"
    assert "Provide a request" in data["message"]
