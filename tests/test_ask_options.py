from forge_agent.ask_options import parse_ask_options


def test_parse_ask_options_defaults_to_memory_enabled():
    options = parse_ask_options(["organize", "my", "invoices", "--json"])

    assert options.wants_json is True
    assert options.memory_enabled is True
    assert options.memory_limit == 5
    assert options.include_sensitive_memory is False
    assert options.memory_scopes == set()
    assert options.memory_wings == set()
    assert options.goal_parts == ["organize", "my", "invoices"]


def test_parse_ask_options_memory_controls():
    options = parse_ask_options([
        "--no-memory",
        "--memory-limit",
        "2",
        "--include-sensitive-memory",
        "--memory-scope",
        "project",
        "--memory-wing",
        "skills",
        "organize",
        "invoices",
    ])

    assert options.memory_enabled is False
    assert options.memory_limit == 2
    assert options.include_sensitive_memory is True
    assert options.memory_scopes == {"project"}
    assert options.memory_wings == {"skills"}
    assert options.goal_parts == ["organize", "invoices"]


def test_parse_ask_options_equals_forms_and_repeated_filters():
    options = parse_ask_options([
        "--memory-limit=3",
        "--memory-scope=project",
        "--memory-scope=skill",
        "--memory-wing=skills",
        "--memory-wing=operations",
        "make",
        "report",
    ])

    assert options.memory_limit == 3
    assert options.memory_scopes == {"project", "skill"}
    assert options.memory_wings == {"skills", "operations"}
    assert options.goal_parts == ["make", "report"]


def test_parse_ask_options_invalid_memory_limit_marks_error():
    options = parse_ask_options(["--memory-limit", "not-a-number", "organize", "invoices"])

    assert options.memory_limit == -1
    assert options.goal_parts == ["organize", "invoices"]


def test_parse_ask_options_missing_memory_limit_marks_error():
    options = parse_ask_options(["--memory-limit"])

    assert options.memory_limit == -1
    assert options.goal_parts == []


def test_parse_ask_options_missing_filter_value_does_not_crash():
    options = parse_ask_options(["--memory-scope", "--memory-wing"])

    assert options.memory_scopes == {"--memory-wing"}
    assert options.memory_wings == set()
    assert options.goal_parts == []
