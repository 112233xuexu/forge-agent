from forge_agent.skills import SkillStore


def test_skill_lifecycle_auto_promotes_from_draft_to_tested_and_validated(tmp_path):
    store = SkillStore(tmp_path)
    skill = store.create_draft("organize invoices by month")
    assert skill.status == "draft"

    first = store.mark_used(skill.skill_id, success=True)
    assert first is not None
    assert first.status == "tested"
    assert first.success_count == 1
    assert first.uses == 1

    store.mark_used(skill.skill_id, success=True)
    third = store.mark_used(skill.skill_id, success=True)
    assert third is not None
    assert third.status == "validated"
    assert third.success_count == 3
    assert third.uses == 3


def test_skill_lifecycle_quarantines_repeated_failures(tmp_path):
    store = SkillStore(tmp_path)
    skill = store.create_draft("unsafe shell automation")

    store.mark_used(skill.skill_id, success=False)
    store.mark_used(skill.skill_id, success=False)
    failed = store.mark_used(skill.skill_id, success=False)

    assert failed is not None
    assert failed.status == "quarantined"
    assert failed.failure_count == 3
    assert failed.success_count == 0


def test_quarantined_skill_is_not_matched(tmp_path):
    store = SkillStore(tmp_path)
    skill = store.create_draft("organize receipts by month")
    store.set_status(skill.skill_id, "quarantined", reason="unsafe test")

    assert store.find("organize receipts") is None


def test_manual_status_controls_accept_short_skill_id(tmp_path):
    store = SkillStore(tmp_path)
    skill = store.create_draft("draft monthly report")

    updated = store.set_status(skill.skill_id[:8], "promoted", reason="maintainer approved")

    assert updated.status == "promoted"
    assert "maintainer approved" in " ".join(updated.metadata["lifecycle"])
    assert store.get(skill.skill_id[:8]) is not None


def test_deprecated_skill_is_not_matched(tmp_path):
    store = SkillStore(tmp_path)
    skill = store.create_draft("summarize invoices")
    store.set_status(skill.skill_id, "deprecated", reason="replaced by better skill")

    assert store.find("summarize invoices") is None
