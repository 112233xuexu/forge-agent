from forge_agent.default_tools import default_user_tools
from forge_agent.plugin_registry import PluginCapability, PluginRegistry, default_plugin_registry, register_plugin_tools


def test_default_plugin_registry_lists_local_capabilities():
    registry = default_plugin_registry()

    names = [capability.name for capability in registry.list()]
    assert names == ["draft-follow-up", "rewrite-text", "summarize-notes", "translate-text"]
    assert registry.get("summarize-notes").tool_name == "summarize_notes"


def test_plugin_registry_finds_capabilities_for_goal():
    registry = default_plugin_registry()

    matches = registry.find_for_goal("rewrite this in a warmer tone")

    assert matches[0].name == "rewrite-text"


def test_plugin_registry_roundtrip():
    registry = PluginRegistry()
    registry.register(PluginCapability("demo", "demo_tool", "Demo tool", inputs=["text"], examples=["demo text"]))

    restored = PluginRegistry.from_dict(registry.to_dict())

    assert restored.get("demo").inputs == ["text"]


def test_register_plugin_tools_reports_missing_tools():
    missing = register_plugin_tools(default_plugin_registry(), default_user_tools())

    assert missing == []
