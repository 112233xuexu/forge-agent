import json
import sys

from forge_agent.brain import BrainAdapter
from forge_agent.entrypoint import cli_entrypoint


def test_brain_adapter_plans_file_organization():
    plan = BrainAdapter().plan("organize my invoices and receipts by month")
    assert plan.intent == "organize_files"
    assert plan.next_step == "preview organize plan"
    assert plan.needs_user_approval is False
    assert plan.safety_level == "dry_run_first"
    assert plan.suggested_command == "forge-agent organize <folder>"
    assert "dry run first" in plan.notes


def test_brain_adapter_plans_content_artifact():
    plan = BrainAdapter().plan("make a ppt for the project status update")
    assert plan.intent == "make_ppt"
    assert plan.safety_level == "local_artifact"
    assert plan.confidence >= 0.7


def test_brain_adapter_plans_report():
    plan = BrainAdapter().plan("write a monthly validation report")
    assert plan.intent == "make_report"
    assert plan.next_step == "create local report"
    assert plan.safety_level == "local_artifact"


def test_brain_adapter_plans_storyboard_from_chinese_request():
    plan = BrainAdapter().plan("给我做一个视频分镜脚本")
    assert plan.intent == "make_storyboard"
    assert plan.next_step == "create local storyboard"
    assert plan.safety_level == "template_only"


def test_brain_adapter_unknown_goal_falls_back_to_local_task():
    plan = BrainAdapter().plan("remember to compare the two project names")
    assert plan.intent == "local_task"
    assert plan.next_step == "record local task"
    assert plan.safety_level == "safe_preview"
    assert plan.confidence == 0.45


def test_brain_adapter_empty_goal_is_safe_unknown():
    plan = BrainAdapter().plan("   ")
    assert plan.intent == "unknown"
    assert plan.confidence == 0.0
    assert plan.needs_user_approval is False
    assert plan.suggested_command == "forge-agent doctor"


def test_brain_adapter_metadata_identifies_local_planner():
    plan = BrainAdapter().plan("make a news brief about AI agents")
    assert plan.metadata["planner"] == "local-deterministic"
    assert plan.intent == "make_news"
    assert "does not fetch live news" in plan.notes


def test_cli_ask_json_outputs_structured_plan(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "ask", "organize", "my", "receipts", "--json"])
    exit_code = cli_entrypoint()
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "organize_files"
    assert data["next_step"] == "preview organize plan"
    assert data["needs_user_approval"] is False
    assert data["safety_level"] == "dry_run_first"
