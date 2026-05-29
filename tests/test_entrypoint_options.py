from forge_agent.entrypoint import _parse_supported_global_options, _strip_supported_global_options


def test_parse_supported_global_options_defaults_to_workspace():
    options = _parse_supported_global_options(["ask", "hello"])

    assert options.workspace == ".forge-agent"
    assert options.command_argv == ["ask", "hello"]


def test_parse_supported_global_options_accepts_workspace_pair():
    options = _parse_supported_global_options(["--workspace", ".state", "ask", "hello"])

    assert options.workspace == ".state"
    assert options.command_argv == ["ask", "hello"]


def test_parse_supported_global_options_accepts_workspace_equals():
    options = _parse_supported_global_options(["--workspace=.state", "ask", "hello"])

    assert options.workspace == ".state"
    assert options.command_argv == ["ask", "hello"]


def test_parse_supported_global_options_stops_at_first_command_token():
    options = _parse_supported_global_options(["ask", "--workspace", ".state", "hello"])

    assert options.workspace == ".forge-agent"
    assert options.command_argv == ["ask", "--workspace", ".state", "hello"]


def test_strip_supported_global_options_remains_backward_compatible():
    assert _strip_supported_global_options(["--workspace", ".state", "ask", "hello"]) == ["ask", "hello"]
