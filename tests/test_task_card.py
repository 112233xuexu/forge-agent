from forge_agent.task_card import TaskCardImpact, make_done_card, make_preview_card


def test_preview_card_uses_plain_language_fields():
    card = make_preview_card(
        title="Organize your invoices",
        user_request="organize my invoices by month",
        plan=["Scan the selected folder", "Group invoice files by month", "Show you the plan before moving files"],
        impacts=[TaskCardImpact(summary="File locations may change", level="medium", reversible=True)],
        boundaries=["I will not change file contents", "I will not upload files"],
    )

    data = card.to_dict()

    assert data["status"] == "needs_confirmation"
    assert data["user_request"] == "organize my invoices by month"
    assert data["plan"] == ["Scan the selected folder", "Group invoice files by month", "Show you the plan before moving files"]
    assert data["impacts"] == [{"summary": "File locations may change", "level": "medium", "reversible": True}]
    assert data["boundaries"] == ["I will not change file contents", "I will not upload files"]
    assert [button["label"] for button in data["buttons"]] == ["Confirm", "Edit", "Stop"]


def test_preview_card_human_summary_is_ordinary_user_facing():
    card = make_preview_card(
        title="Create a repository",
        user_request="create a GitHub repo for my project",
        plan=["Create the repository", "Add a README", "Show you the link"],
        impacts=[TaskCardImpact(summary="A new repository will be created", level="medium", reversible=False)],
        boundaries=["I will not delete anything"],
    )

    text = card.human_summary()

    assert "You asked: create a GitHub repo for my project" in text
    assert "I will do:" in text
    assert "This may affect:" in text
    assert "I will not:" in text
    assert "Options:" in text
    assert "rollback" not in text.lower()
    assert "audit" not in text.lower()
    assert "manifest" not in text.lower()


def test_done_card_can_offer_record_and_restore():
    card = make_done_card(
        title="Organized your invoices",
        user_request="organize my invoices",
        plan=["Moved invoice files into month folders"],
        result_summary="Moved 23 files and skipped 2 uncertain files.",
        record_id="op_123",
        restore_available=True,
    )

    data = card.to_dict()

    assert data["status"] == "done"
    assert data["result_summary"] == "Moved 23 files and skipped 2 uncertain files."
    assert data["record_id"] == "op_123"
    assert data["restore_available"] is True
    assert [button["kind"] for button in data["buttons"]] == ["view_record", "restore"]
    assert "You can restore this if needed." in card.human_summary()


def test_preview_card_can_be_non_confirming_preview():
    card = make_preview_card(
        title="Summarize notes",
        user_request="summarize this note",
        plan=["Read the note", "Create a short summary"],
        needs_confirmation=False,
    )

    assert card.status == "preview"
    assert card.buttons == []
