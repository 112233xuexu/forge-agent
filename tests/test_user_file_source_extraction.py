from forge_agent.user_file_flow import maybe_run_file_goal


def test_file_goal_extracts_dash_path(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()

    result = maybe_run_file_goal(f"organize invoices --path {source}", workspace=tmp_path / "state", mode="explain")

    assert result is not None
    assert result.status == "explained"
    assert result.source == str(source)


def test_file_goal_extracts_path_equals(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()

    result = maybe_run_file_goal(f"organize files path={source}", workspace=tmp_path / "state", mode="explain")

    assert result is not None
    assert result.status == "explained"
    assert result.source == str(source)


def test_file_goal_extracts_source_equals(tmp_path):
    source = tmp_path / "receipts"
    source.mkdir()

    result = maybe_run_file_goal(f"sort receipts source={source}", workspace=tmp_path / "state", mode="explain")

    assert result is not None
    assert result.status == "explained"
    assert result.source == str(source)
