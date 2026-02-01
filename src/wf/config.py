"""Config file handling for active workflow tracking."""

import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILENAME = ".wf.json"


@dataclass
class WfConfig:
    """Configuration for wf CLI."""

    active_workflow: str | None = None
    extra: dict = field(default_factory=dict)


def get_config_path() -> Path:
    """Get the path to the config file in current directory."""
    return Path.cwd() / CONFIG_FILENAME


def load_config() -> WfConfig:
    """Load config from .wf.json file."""
    config_path = get_config_path()

    if not config_path.exists():
        return WfConfig()

    with open(config_path) as f:
        data = json.load(f)

    active_workflow = data.get("active_workflow")
    known_keys = {"active_workflow"}
    extra = {k: v for k, v in data.items() if k not in known_keys}

    return WfConfig(active_workflow=active_workflow, extra=extra)


def save_config(config: WfConfig) -> None:
    """Save config to .wf.json file."""
    config_path = get_config_path()

    data: dict = {}
    data.update(config.extra)

    if config.active_workflow is not None:
        data["active_workflow"] = config.active_workflow

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def get_active_workflow() -> Path | None:
    """Get the active workflow path."""
    config = load_config()
    if config.active_workflow is None:
        return None
    return Path(config.active_workflow)


def set_active_workflow(path: Path) -> None:
    """Set the active workflow path."""
    config = load_config()
    config.active_workflow = str(path)
    save_config(config)
