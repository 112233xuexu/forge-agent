from forge_agent.ask_presenter import print_ask_plan
from forge_agent.brain import BrainPlan
from forge_agent.task_card import TaskCardImpact, make_preview_card


def test_print_ask_plan_uses_task_card_for_human_output(capsys):
    plan = BrainPlan(
        goal="organize my invoices",
        intent="organize_files",
        next_step="preview organize plan",
        needs_user_approval=False,
        confidence=0.75,
        metadata={
            "task_card": make_preview_card(
                title="Organize your files",
                user_request="organize my invoices",
                plan=["Look at the selected folder", "Show the file move plan before changing files"],
                impacts=[TaskCardImpact(summary="File locations may change after you approve the plan", level="medium", reversible=True)],
                boundaries=["I will not upload files"],
                needs_confirmation=False,
            ).to_dict()
        },
    )

    print_ask_plan(plan, wants_json=False)

    output = capsys.readouterr().out
    assert "Organize your files" in output
    assert "You asked: organize my invoices" in output
    assert "I will do:" in output
    assert "This may affect:" in output
    assert "I will not:" in output
    assert "Forge Agent brain plan" not in output
    assert "Intent:" not in output
    assert "Confidence:" not in output


def test_print_ask_plan_json_preserves_full_plan(capsys):
    plan = BrainPlan(
        goal="make a report",
        intent="make_report",
        next_step="create local report",
        needs_user_approval=False,
        confidence=0.70,
        metadata={"task_card": {"title": "Create a report draft"}},
    )

    print_ask_plan(plan, wants_json=True)

    output = capsys.readouterr().out
    assert '"intent": "make_report"' in output
    assert '"task_card"' in output
    assert '"title": "Create a report draft"' in output


def test_print_ask_plan_memory_language_is_plain(capsys):
    plan = BrainPlan(
        goal="organize invoices",
        intent="organize_files",
        next_step="preview organize plan",
        needs_user_approval=False,
        confidence=0.75,
        metadata={
            "task_card": make_preview_card(
                title="Organize your files",
                user_request="organize invoices",
                plan=["Look at the selected folder"],
                needs_confirmation=False,
            ).to_dict(),
            "memory_used": [{"id": "mem_1", "scope": "project", "wing": "skills", "score": 2.0}],
        },
    )

    print_ask_plan(plan, wants_json=False)

    output = capsys.readouterr().out.lower()
    assert "what i remembered for this task" in output
    assert "memory used" not in output
    assert "rollback" not in output
    assert "audit" not in output
    assert "manifest" not in output


def test_print_ask_plan_shows_context_focus_path(capsys):
    plan = BrainPlan(
        goal="organize invoices",
        intent="organize_files",
        next_step="preview organize plan",
        needs_user_approval=False,
        confidence=0.75,
        metadata={
            "task_card": make_preview_card(
                title="Organize your files",
                user_request="organize invoices",
                plan=["Look at the selected folder"],
                needs_confirmation=False,
            ).to_dict(),
            "memory_used": [{"id": "mem_1", "scope": "project", "wing": "project", "score": 2.0}],
            "context_focus_path": "project/customers/acme/invoices",
        },
    )

    print_ask_plan(plan, wants_json=False)

    output = capsys.readouterr().out
    assert "Context path: project/customers/acme/invoices" in output
