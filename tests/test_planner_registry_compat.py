from forge_agent.planner import SimplePlanner
from forge_agent.tool_registry import ToolRegistry


def summarize_notes(notes: str):
    return {"action_items": [item.strip() for item in notes.split(";") if item.strip()], "summary": notes}


def draft_followup(customer: str, action_items: list[str]):
    return f"note to {customer}: {', '.join(action_items)}"


def translate_text(text: str, target_language: str):
    return f"[{target_language}] {text}"


def paraphrase_text(text: str, style: str = "clear"):
    return f"[{style}] {text}"


def make_registry() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register("summarize_notes", summarize_notes)
    tools.register("draft_followup", draft_followup)
    tools.register("translate_text", translate_text)
    tools.register("paraphrase_text", paraphrase_text)
    return tools


def test_simple_planner_builds_followup_translate_plan():
    result = SimplePlanner(make_registry()).build_plan(
        "Summarize these call notes, write a follow-up for Acme, and translate it into spanish",
        inputs={"notes": "send pricing", "customer": "Acme"},
    )

    assert result.plan is not None
    assert result.plan.meta["intent"] == "followup_translate"
    assert [step.tool_name for step in result.plan.steps] == ["summarize_notes", "draft_followup", "translate_text"]
    assert result.plan.steps[2].args["text"] == {"$ref": {"step": "draft reply", "path": []}}


def test_simple_planner_reports_translation_missing_input_and_extracts_quoted_text():
    planner = SimplePlanner(make_registry())

    assert planner.build_plan("Translate this into spanish").missing_inputs == ["text"]
    result = planner.build_plan('Translate "Need signature today" into spanish')

    assert result.plan is not None
    assert result.missing_inputs == []
    assert result.plan.objective == "translate text"


def test_simple_planner_builds_paraphrase_plan_with_style():
    result = SimplePlanner(make_registry()).build_plan('Rewrite "Need approval by Friday" in a warmer tone')

    assert result.plan is not None
    assert result.plan.meta["intent"] == "paraphrase_text"
    assert result.plan.steps[0].tool_name == "paraphrase_text"
    assert result.plan.steps[0].args["style"] == {"$var": "style"}


def test_tool_registry_metadata_and_run():
    tools = make_registry()

    assert tools.has("translate_text") is True
    assert tools.run("translate_text", text="hello", target_language="french") == "[french] hello"
    assert "text" in tools.get("translate_text").parameters
    assert tools.list_tools() == ["draft_followup", "paraphrase_text", "summarize_notes", "translate_text"]
