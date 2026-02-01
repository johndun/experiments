"""Tests for wf.cli module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from wf.cli import (
    CloseCmd,
    ReadyCmd,
    ResetCmd,
    get_workflow_path,
    handle_close,
    handle_ready,
    handle_reset,
)
from wf.config import CONFIG_FILENAME


@pytest.fixture
def temp_dir():
    """Create a temporary directory and change to it."""
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(original_dir)


@pytest.fixture
def sample_workflow_file(temp_dir):
    """Create a sample workflow file."""
    workflow_path = temp_dir / "workflow.yaml"
    workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
      - id: task2
        title: Task 2
        blocked_by:
          - task1
      - id: task3
        title: Task 3
        blocked_by:
          - task1
  - id: story2
    title: Story 2
    tasks:
      - id: task4
        title: Task 4
""")
    return workflow_path


class TestGetWorkflowPath:
    """Tests for get_workflow_path function."""

    def test_provided_path(self, temp_dir):
        """Test with provided path."""
        provided = Path("/some/path.yaml")
        result = get_workflow_path(provided)
        assert result == provided

    def test_active_workflow(self, temp_dir):
        """Test falling back to active workflow."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(json.dumps({"active_workflow": "/active/workflow.yaml"}))

        result = get_workflow_path(None)
        assert result == Path("/active/workflow.yaml")

    def test_no_workflow(self, temp_dir):
        """Test when no workflow is available."""
        result = get_workflow_path(None)
        assert result is None


class TestHandleReady:
    """Tests for handle_ready function."""

    def test_ready_with_workflow(self, temp_dir, sample_workflow_file, capsys):
        """Test ready command with workflow file."""
        cmd = ReadyCmd(workflow=sample_workflow_file)
        exit_code = handle_ready(cmd)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Ready tasks" in captured.out
        assert "[task1]" in captured.out
        assert "[task4]" in captured.out

    def test_ready_shows_active_workflow(self, temp_dir, sample_workflow_file, capsys):
        """Test that ready shows active workflow path."""
        cmd = ReadyCmd(workflow=sample_workflow_file)
        handle_ready(cmd)

        captured = capsys.readouterr()
        assert f"Active workflow: {sample_workflow_file}" in captured.out

    def test_ready_sets_active_workflow(self, temp_dir, sample_workflow_file):
        """Test that ready sets active workflow."""
        cmd = ReadyCmd(workflow=sample_workflow_file)
        handle_ready(cmd)

        config_path = temp_dir / CONFIG_FILENAME
        with open(config_path) as f:
            data = json.load(f)

        assert data["active_workflow"] == str(sample_workflow_file)

    def test_ready_no_workflow(self, temp_dir, capsys):
        """Test ready command without workflow."""
        cmd = ReadyCmd(workflow=None)
        exit_code = handle_ready(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No workflow specified" in captured.err

    def test_ready_nonexistent_file(self, temp_dir, capsys):
        """Test ready with nonexistent file."""
        cmd = ReadyCmd(workflow=Path("/nonexistent/workflow.yaml"))
        exit_code = handle_ready(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_ready_shows_blocked_by(self, temp_dir, capsys):
        """Test that blocked_by is shown in output."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
      - id: task2
        title: Task 2
        blocked_by:
          - task1
status:
  closed_tasks:
    - task1
""")
        cmd = ReadyCmd(workflow=workflow_path)
        handle_ready(cmd)

        captured = capsys.readouterr()
        assert "blocked_by: task1" in captured.out

    def test_ready_shows_description(self, temp_dir, capsys):
        """Test that description is shown in output."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
        description: This is a detailed description
""")
        cmd = ReadyCmd(workflow=workflow_path)
        handle_ready(cmd)

        captured = capsys.readouterr()
        assert "This is a detailed description" in captured.out

    def test_ready_shows_skills(self, temp_dir, capsys):
        """Test that skills are shown in output."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    skills:
      - python
    tasks:
      - id: task1
        title: Task 1
        skills:
          - pytest
""")
        cmd = ReadyCmd(workflow=workflow_path)
        handle_ready(cmd)

        captured = capsys.readouterr()
        assert "skills: python, pytest" in captured.out

    def test_ready_shows_workflow_complete(self, temp_dir, capsys):
        """Test that ready shows workflow complete message."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
status:
  closed_tasks:
    - task1
  closed_stories:
    - story1
""")
        cmd = ReadyCmd(workflow=workflow_path)
        handle_ready(cmd)

        captured = capsys.readouterr()
        assert "Workflow complete!" in captured.out


class TestHandleReset:
    """Tests for handle_reset function."""

    def test_reset_clears_status(self, temp_dir, capsys):
        """Test that reset clears status."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
status:
  closed_tasks:
    - task1
""")

        cmd = ResetCmd(workflow=workflow_path)
        exit_code = handle_reset(cmd)

        assert exit_code == 0

        # Verify file was updated
        with open(workflow_path) as f:
            content = f.read()
        assert "closed_tasks" not in content or "[]" in content

    def test_reset_no_workflow(self, temp_dir, capsys):
        """Test reset without workflow."""
        cmd = ResetCmd(workflow=None)
        exit_code = handle_reset(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No workflow specified" in captured.err


class TestHandleClose:
    """Tests for handle_close function."""

    def test_close_task(self, temp_dir, sample_workflow_file, capsys):
        """Test closing a task."""
        # Set active workflow
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": str(sample_workflow_file)})
        )

        cmd = CloseCmd(task_ids=("task1",))
        exit_code = handle_close(cmd)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Closed tasks: task1" in captured.out
        assert "[task2]" in captured.out  # Now ready
        assert "[task3]" in captured.out  # Now ready

    def test_close_shows_active_workflow(self, temp_dir, sample_workflow_file, capsys):
        """Test that close shows active workflow path."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": str(sample_workflow_file)})
        )

        cmd = CloseCmd(task_ids=("task1",))
        handle_close(cmd)

        captured = capsys.readouterr()
        assert f"Active workflow: {sample_workflow_file}" in captured.out

    def test_close_multiple_tasks(self, temp_dir, sample_workflow_file, capsys):
        """Test closing multiple tasks."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": str(sample_workflow_file)})
        )

        cmd = CloseCmd(task_ids=("task1", "task4"))
        exit_code = handle_close(cmd)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "task1" in captured.out
        assert "task4" in captured.out

    def test_close_no_active_workflow(self, temp_dir, capsys):
        """Test close without active workflow."""
        cmd = CloseCmd(task_ids=("task1",))
        exit_code = handle_close(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No active workflow" in captured.err

    def test_close_invalid_task(self, temp_dir, sample_workflow_file, capsys):
        """Test closing invalid task ID."""
        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(
            json.dumps({"active_workflow": str(sample_workflow_file)})
        )

        cmd = CloseCmd(task_ids=("invalid_task",))
        exit_code = handle_close(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Unknown task IDs" in captured.err

    def test_close_no_task_ids(self, temp_dir, capsys):
        """Test close without task IDs."""
        cmd = CloseCmd(task_ids=())
        exit_code = handle_close(cmd)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "No task IDs provided" in captured.err

    def test_close_auto_closes_story(self, temp_dir, capsys):
        """Test that closing all tasks auto-closes story."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
""")

        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(json.dumps({"active_workflow": str(workflow_path)}))

        cmd = CloseCmd(task_ids=("task1",))
        exit_code = handle_close(cmd)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Completed stories: story1" in captured.out

    def test_close_shows_workflow_complete(self, temp_dir, capsys):
        """Test that closing last tasks shows workflow complete."""
        workflow_path = temp_dir / "workflow.yaml"
        workflow_path.write_text("""
stories:
  - id: story1
    title: Story 1
    tasks:
      - id: task1
        title: Task 1
""")

        config_path = temp_dir / CONFIG_FILENAME
        config_path.write_text(json.dumps({"active_workflow": str(workflow_path)}))

        cmd = CloseCmd(task_ids=("task1",))
        handle_close(cmd)

        captured = capsys.readouterr()
        assert "Workflow complete!" in captured.out
