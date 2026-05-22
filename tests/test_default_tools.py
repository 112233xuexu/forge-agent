from forge_agent.default_tools import default_user_tools, draft_followup, paraphrase_text, summarize_notes, translate_text


def test_default_user_tools_registers_planner_tools():
    tools = default_user_tools()

    assert tools.has("summarize_notes")
    assert tools.has("paraphrase_text")
    assert tools.has("translate_text")
    assert tools.has("draft_followup")


def test_summarize_notes_returns_summary_bullets_and_actions():
    result = summarize_notes("Prepare launch update. Review invoices. Send recap.")

    assert result["summary"] == "Prepare launch update"
    assert result["bullets"] == ["Prepare launch update", "Review invoices", "Send recap"]
    assert result["action_items"] == ["Prepare launch update", "Review invoices", "Send recap"]


def test_paraphrase_text_styles_are_deterministic():
    assert paraphrase_text("Need approval", "warm") == "Thanks — Need approval."
    assert paraphrase_text("Need approval", "professional") == "Please note: Need approval."
    assert paraphrase_text("Need approval", "concise") == "Need approval."


def test_translate_text_is_local_placeholder():
    assert translate_text("Hello", "Japanese") == "[japanese] Hello"


def test_draft_followup_formats_items():
    result = draft_followup("Acme", ["Prepare update", "Review invoice"])

    assert "Hi Acme" in result
    assert "- Prepare update" in result
    assert "- Review invoice" in result
