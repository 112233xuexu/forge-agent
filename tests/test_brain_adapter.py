import json
import sys

from forge_agent.brain import BrainAdapter
from forge_agent.entrypoint import cli_entrypoint


def test_brain_adapter_plans_file_organization():
    plan = BrainAdapter().plan("organize my invoices and receipts by month")
    assert plan.intent == "organize_files"
    assert plan.next_step == "preview organize plan"
    assert plan.needs_user_approval is False
    assert "dry run first" in plan.notes


def test_brain_adapter_plans_content_artifact():
    plan = BrainAdapter().plan("make a ppt for the project status update")
    assert plan.intent == "make_ppt"
    assert plan.confidence >= 0.7


def test_brain_adapter_empty_goal_is_safe_unknown():
    plan = BrainAdapter().plan("   ")
    assert plan.intent == "unknown"
    assert plan.confidence == 0.0
    assert plan.needs_user_approval is False


def test_cli_ask_json_outputs_structured_plan(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "ask", "organize", "my", "receipts", "--json"])
    exit_code = cli_entrypoint()
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "organize_files"
    assert data["next_step"] == "preview organize plan"
    assert data["needs_user_approval"] is False
