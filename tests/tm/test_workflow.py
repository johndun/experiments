"""Tests for tm.workflow module."""

import tempfile
from pathlib import Path

import pytest

from tm.models import Story, Task, Workflow, WorkflowStatus
from tm.workflow import (
    close_tasks,
    get_all_task_ids,
    get_effective_skills,
    get_ready_tasks,
    load_workflow,
    reset_workflow,
    save_workflow,
    validate_task_ids,
)


@pytest.fixture
def sample_workflow():
    """Create a sample workflow for testing."""
    return Workflow(
        stories=[
            Story(
                id="story1",
                title="Story 1",
                tasks=[
                    Task(id="task1", title="Task 1"),
                    Task(id="task2", title="Task 2", blocked_by=["task1"]),
                    Task(id="task3", title="Task 3", blocked_by=["task1"]),
                ],
            ),
            Story(
                id="story2",
                title="Story 2",
                tasks=[
                    Task(id="task4", title="Task 4"),
                    Task(id="task5", title="Task 5", blocked_by=["task4", "task2"]),
                ],
            ),
        ],
        status=WorkflowStatus(),
    )


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
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
""")
        f.flush()
        yield Path(f.name)


class TestLoadWorkflow:
    """Tests for load_workflow function."""

    def test_load_basic_workflow(self, temp_yaml_file):
        """Test loading a basic workflow."""
        workflow = load_workflow(temp_yaml_file)
        assert len(workflow.stories) == 1
        assert workflow.stories[0].id == "story1"
        assert len(workflow.stories[0].tasks) == 2
        assert workflow.stories[0].tasks[1].blocked_by == ["task1"]

    def test_load_workflow_with_status(self):
        """Test loading workflow with status."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
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
            f.flush()
            workflow = load_workflow(Path(f.name))

        assert workflow.status.closed_tasks == ["task1"]

    def test_load_workflow_preserves_extra_keys(self):
        """Test that unknown keys are preserved."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
custom_field: custom_value
stories: []
""")
            f.flush()
            workflow = load_workflow(Path(f.name))

        assert workflow._extra == {"custom_field": "custom_value"}

    def test_load_empty_file(self):
        """Test loading an empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            workflow = load_workflow(Path(f.name))

        assert workflow.stories == []
        assert workflow.status.closed_tasks == []

    def test_load_workflow_with_skills(self):
        """Test loading workflow with skills on stories and tasks."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
stories:
  - id: story1
    title: Story 1
    skills:
      - python
      - testing
    tasks:
      - id: task1
        title: Task 1
        skills:
          - pytest
""")
            f.flush()
            workflow = load_workflow(Path(f.name))

        assert workflow.stories[0].skills == ["python", "testing"]
        assert workflow.stories[0].tasks[0].skills == ["pytest"]


class TestSaveWorkflow:
    """Tests for save_workflow function."""

    def test_save_and_load_roundtrip(self, sample_workflow):
        """Test that save and load produces the same workflow."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            path = Path(f.name)

        save_workflow(sample_workflow, path)
        loaded = load_workflow(path)

        assert len(loaded.stories) == len(sample_workflow.stories)
        assert loaded.stories[0].id == sample_workflow.stories[0].id
        assert len(loaded.stories[0].tasks) == len(sample_workflow.stories[0].tasks)

    def test_save_preserves_extra_keys(self):
        """Test that extra keys are preserved on save."""
        workflow = Workflow(
            stories=[],
            _extra={"custom_key": "custom_value"},
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            path = Path(f.name)

        save_workflow(workflow, path)
        loaded = load_workflow(path)

        assert loaded._extra == {"custom_key": "custom_value"}

    def test_save_with_status(self, sample_workflow):
        """Test saving workflow with closed tasks."""
        sample_workflow.status.closed_tasks = ["task1"]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            path = Path(f.name)

        save_workflow(sample_workflow, path)
        loaded = load_workflow(path)

        assert loaded.status.closed_tasks == ["task1"]

    def test_save_with_skills(self):
        """Test saving workflow with skills on stories and tasks."""
        workflow = Workflow(
            stories=[
                Story(
                    id="story1",
                    title="Story 1",
                    skills=["python", "testing"],
                    tasks=[
                        Task(id="task1", title="Task 1", skills=["pytest"]),
                    ],
                ),
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            path = Path(f.name)

        save_workflow(workflow, path)
        loaded = load_workflow(path)

        assert loaded.stories[0].skills == ["python", "testing"]
        assert loaded.stories[0].tasks[0].skills == ["pytest"]


class TestGetAllTaskIds:
    """Tests for get_all_task_ids function."""

    def test_get_all_task_ids(self, sample_workflow):
        """Test getting all task IDs."""
        task_ids = get_all_task_ids(sample_workflow)
        assert task_ids == {"task1", "task2", "task3", "task4", "task5"}

    def test_empty_workflow(self):
        """Test with empty workflow."""
        workflow = Workflow()
        assert get_all_task_ids(workflow) == set()


class TestGetReadyTasks:
    """Tests for get_ready_tasks function."""

    def test_initial_ready_tasks(self, sample_workflow):
        """Test getting ready tasks when no tasks are closed."""
        ready = get_ready_tasks(sample_workflow)
        ready_ids = [task.id for _, task in ready]

        # Only unblocked tasks should be ready
        assert "task1" in ready_ids
        assert "task4" in ready_ids
        assert "task2" not in ready_ids
        assert "task3" not in ready_ids
        assert "task5" not in ready_ids

    def test_ready_after_closing_blocker(self, sample_workflow):
        """Test that blocked tasks become ready after blocker is closed."""
        sample_workflow.status.closed_tasks = ["task1"]
        ready = get_ready_tasks(sample_workflow)
        ready_ids = [task.id for _, task in ready]

        # task2 and task3 should now be ready
        assert "task2" in ready_ids
        assert "task3" in ready_ids
        assert "task1" not in ready_ids  # Already closed

    def test_closed_story_excluded(self, sample_workflow):
        """Test that tasks from closed stories are excluded."""
        sample_workflow.status.closed_stories = ["story1"]
        ready = get_ready_tasks(sample_workflow)
        ready_ids = [task.id for _, task in ready]

        # Only story2 tasks should be considered
        assert "task1" not in ready_ids
        assert "task4" in ready_ids

    def test_multiple_blockers(self, sample_workflow):
        """Test task with multiple blockers."""
        # task5 is blocked by task4 and task2
        sample_workflow.status.closed_tasks = ["task1", "task4"]
        ready = get_ready_tasks(sample_workflow)
        ready_ids = [task.id for _, task in ready]

        # task5 still blocked by task2
        assert "task5" not in ready_ids
        assert "task2" in ready_ids

        # Now close task2
        sample_workflow.status.closed_tasks.append("task2")
        ready = get_ready_tasks(sample_workflow)
        ready_ids = [task.id for _, task in ready]

        assert "task5" in ready_ids


class TestCloseTasks:
    """Tests for close_tasks function."""

    def test_close_single_task(self, sample_workflow):
        """Test closing a single task."""
        close_tasks(sample_workflow, ["task1"])
        assert "task1" in sample_workflow.status.closed_tasks

    def test_close_multiple_tasks(self, sample_workflow):
        """Test closing multiple tasks."""
        close_tasks(sample_workflow, ["task1", "task4"])
        assert "task1" in sample_workflow.status.closed_tasks
        assert "task4" in sample_workflow.status.closed_tasks

    def test_auto_close_story(self, sample_workflow):
        """Test that story is auto-closed when all tasks are done."""
        # Close all tasks in story2
        auto_closed = close_tasks(sample_workflow, ["task4", "task5"])

        assert "story2" in auto_closed
        assert "story2" in sample_workflow.status.closed_stories

    def test_no_duplicate_closes(self, sample_workflow):
        """Test that closing same task twice doesn't duplicate."""
        close_tasks(sample_workflow, ["task1"])
        close_tasks(sample_workflow, ["task1"])

        assert sample_workflow.status.closed_tasks.count("task1") == 1


class TestResetWorkflow:
    """Tests for reset_workflow function."""

    def test_reset_clears_status(self, sample_workflow):
        """Test that reset clears all status."""
        sample_workflow.status.closed_tasks = ["task1", "task2"]
        sample_workflow.status.closed_stories = ["story1"]

        reset_workflow(sample_workflow)

        assert sample_workflow.status.closed_tasks == []
        assert sample_workflow.status.closed_stories == []


class TestValidateTaskIds:
    """Tests for validate_task_ids function."""

    def test_valid_ids(self, sample_workflow):
        """Test with valid task IDs."""
        invalid = validate_task_ids(sample_workflow, ["task1", "task2"])
        assert invalid == []

    def test_invalid_ids(self, sample_workflow):
        """Test with invalid task IDs."""
        invalid = validate_task_ids(sample_workflow, ["task1", "invalid_task"])
        assert invalid == ["invalid_task"]

    def test_all_invalid(self, sample_workflow):
        """Test with all invalid IDs."""
        invalid = validate_task_ids(sample_workflow, ["foo", "bar"])
        assert invalid == ["foo", "bar"]


class TestGetEffectiveSkills:
    """Tests for get_effective_skills function."""

    def test_task_only_skills(self):
        """Test task with skills but story without."""
        story = Story(id="story1", title="Story 1", skills=[])
        task = Task(id="task1", title="Task 1", skills=["python", "testing"])

        skills = get_effective_skills(story, task)
        assert skills == ["python", "testing"]

    def test_story_only_skills(self):
        """Test story with skills but task without."""
        story = Story(id="story1", title="Story 1", skills=["python", "testing"])
        task = Task(id="task1", title="Task 1", skills=[])

        skills = get_effective_skills(story, task)
        assert skills == ["python", "testing"]

    def test_inherited_skills(self):
        """Test task inherits skills from story."""
        story = Story(id="story1", title="Story 1", skills=["python", "testing"])
        task = Task(id="task1", title="Task 1", skills=["pytest"])

        skills = get_effective_skills(story, task)
        # Story skills come first, then task-specific skills
        assert skills == ["python", "testing", "pytest"]

    def test_duplicate_skills_deduplicated(self):
        """Test that duplicate skills are deduplicated."""
        story = Story(id="story1", title="Story 1", skills=["python", "testing"])
        task = Task(id="task1", title="Task 1", skills=["testing", "pytest"])

        skills = get_effective_skills(story, task)
        # "testing" appears in both, should only appear once
        assert skills == ["python", "testing", "pytest"]

    def test_no_skills(self):
        """Test when neither story nor task has skills."""
        story = Story(id="story1", title="Story 1", skills=[])
        task = Task(id="task1", title="Task 1", skills=[])

        skills = get_effective_skills(story, task)
        assert skills == []
