from forge_agent.ask_options import parse_ask_options
from forge_agent.ask_service import build_ask_plan
from forge_agent.ask_task_card import build_task_card_for_plan
from forge_agent.brain import BrainAdapter


def test_organize_ask_plan_includes_task_card_metadata(tmp_path):
    options = parse_ask_options(["organize", "my", "invoices", "--json"])

    plan = build_ask_plan("organize my invoices", workspace=str(tmp_path), options=options)

    card = plan.metadata["task_card"]
    assert card["title"] == "Organize your files"
    assert card["user_request"] == "organize my invoices"
    assert card["status"] == "preview"
    assert "Look at the selected folder" in card["plan"]
    assert card["impacts"][0]["summary"] == "File locations may change after you approve the plan"
    assert "I will not upload files" in card["boundaries"]


def test_content_ask_card_uses_local_artifact_language():
    plan = BrainAdapter().plan("make a report about project status")

    card = build_task_card_for_plan(plan).to_dict()

    assert card["title"] == "Create a report draft"
    assert card["status"] == "preview"
    assert "Create a local report draft" in card["plan"]
    assert card["impacts"][0]["summary"] == "A local artifact file will be created"
    assert "I will not send the report anywhere" in card["boundaries"]


def test_fallback_ask_card_does_not_promise_app_access():
    plan = BrainAdapter().plan("help me with something unusual")

    card = build_task_card_for_plan(plan).to_dict()

    assert card["title"] == "Prepare this task"
    assert "Record the task locally" in card["plan"]
    assert "I will not use outside apps without a clear next step" in card["boundaries"]


def test_ask_task_card_avoids_internal_jargon(tmp_path):
    options = parse_ask_options(["create", "a", "storyboard"])

    plan = build_ask_plan("create a storyboard", workspace=str(tmp_path), options=options)
    summary = build_task_card_for_plan(plan).human_summary().lower()

    assert "rollback" not in summary
    assert "audit" not in summary
    assert "manifest" not in summary
    assert "permission" not in summary
