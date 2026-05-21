from __future__ import annotations

from forge_agent.app_capabilities import AppCapability, AppCapabilityCatalog


def build_default_capability_catalog() -> AppCapabilityCatalog:
    catalog = AppCapabilityCatalog()
    catalog.add(AppCapability(name="local_files.organize_by_month", description="Organize local invoice or receipt files by month after a preview.", inputs=["folder"], effects=["File locations may change after confirmation"], needs_confirmation=True, reversible=True))
    catalog.add(AppCapability(name="content.create_report", description="Create a local report draft from a topic.", inputs=["topic"], effects=["A local artifact file is created"], needs_confirmation=False, reversible=True))
    catalog.add(AppCapability(name="content.create_slide_outline", description="Create a local slide outline from a topic.", inputs=["topic"], effects=["A local artifact file is created"], needs_confirmation=False, reversible=True))
    catalog.add(AppCapability(name="account.prepare_project_space", description="Prepare a new project space after showing a preview.", inputs=["name"], effects=["A new project space may be created after confirmation"], needs_confirmation=True, reversible=False))
    catalog.add(AppCapability(name="message.prepare_note", description="Prepare a message note for review.", inputs=["recipient", "message"], effects=["A local note may be created"], needs_confirmation=True, reversible=True))
    catalog.add(AppCapability(name="schedule.prepare_item", description="Prepare a schedule item for review.", inputs=["title", "time"], effects=["A schedule item may be created after confirmation"], needs_confirmation=True, reversible=True))
    return catalog
