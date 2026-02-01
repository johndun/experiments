"""Tests for tm.config module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from tm.config import (
    CONFIG_FILENAME,
    TmConfig,
    get_active_workflow,
    get_config_path,
    load_config,
    save_config,
    set_active_workflow,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory and change to it."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(original_dir)


class TestTmConfig:
    """Tests for TmConfig dataclass."""

    def test_defaults(self):
        """Test default values."""
        config = TmConfig()
        assert config.active_workflow is None
        assert config.extra == {}

    def test_with_values(self):
        """Test with provided values."""
        config = TmConfig(
            active_workflow="/path/to/workflow.yaml",
            extra={"custom": "value"},
        )
        assert config.active_workflow == "/path/to/workflow.yaml"
        assert config.extra == {"custom": "value"}


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_returns_path_in_cwd(self, temp_dir):
        """Test that config path is in current directory."""
        path = get_config_path()
        # Use resolve() to handle macOS /private symlink
        assert path.resolve() == (temp_dir / CONFIG_FILENAME).resolve()


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_nonexistent(self, temp_dir):
        """Test loading when config doesn't exist."""
        config = load_config()
        assert config.active_workflow is None
        assert config.extra == {}

    def test_load_existing(self, temp_dir):
        """Test loading existing config."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": "/path/to/workflow.yaml"})
        )

        config = load_config()
        assert config.active_workflow == "/path/to/workflow.yaml"

    def test_load_preserves_extra(self, temp_dir):
        """Test that extra keys are preserved."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps(
                {
                    "active_workflow": "/path/to/workflow.yaml",
                    "custom_key": "custom_value",
                }
            )
        )

        config = load_config()
        assert config.extra == {"custom_key": "custom_value"}


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_creates_file(self, temp_dir):
        """Test that save creates the config file."""
        config = TmConfig(active_workflow="/path/to/workflow.yaml")
        save_config(config)

        config_path = temp_dir / CONFIG_FILENAME
        assert config_path.exists()

        with open(config_path) as f:
            data = json.load(f)
        assert data["active_workflow"] == "/path/to/workflow.yaml"

    def test_save_preserves_extra(self, temp_dir):
        """Test that extra keys are preserved on save."""
        config = TmConfig(
            active_workflow="/path/to/workflow.yaml",
            extra={"custom": "value"},
        )
        save_config(config)

        config_path = temp_dir / CONFIG_FILENAME
        with open(config_path) as f:
            data = json.load(f)

        assert data["custom"] == "value"


class TestGetActiveWorkflow:
    """Tests for get_active_workflow function."""

    def test_no_active_workflow(self, temp_dir):
        """Test when no active workflow is set."""
        result = get_active_workflow()
        assert result is None

    def test_with_active_workflow(self, temp_dir):
        """Test when active workflow is set."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": "/path/to/workflow.yaml"})
        )

        result = get_active_workflow()
        assert result == Path("/path/to/workflow.yaml")


class TestSetActiveWorkflow:
    """Tests for set_active_workflow function."""

    def test_set_active_workflow(self, temp_dir):
        """Test setting active workflow."""
        workflow_path = Path("/path/to/workflow.yaml")
        set_active_workflow(workflow_path)

        config_path = temp_dir / CONFIG_FILENAME
        with open(config_path) as f:
            data = json.load(f)

        assert data["active_workflow"] == "/path/to/workflow.yaml"

    def test_set_preserves_existing_config(self, temp_dir):
        """Test that setting workflow preserves other config."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(json.dumps({"custom_key": "custom_value"}))

        set_active_workflow(Path("/path/to/workflow.yaml"))

        with open(config_path) as f:
            data = json.load(f)

        assert data["active_workflow"] == "/path/to/workflow.yaml"
        assert data["custom_key"] == "custom_value"
