"""Tests for tm.models module."""

from tm.models import Story, Task, Workflow, WorkflowStatus


def test_task_creation():
    """Test creating a task with defaults."""
    task = Task(id="task1", title="Test Task")
    assert task.id == "task1"
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.blocked_by == []


def test_task_with_blocked_by():
    """Test creating a task with blocked_by."""
    task = Task(
        id="task2",
        title="Blocked Task",
        description="A task that is blocked",
        blocked_by=["task1"],
    )
    assert task.id == "task2"
    assert task.blocked_by == ["task1"]


def test_story_creation():
    """Test creating a story with defaults."""
    story = Story(id="story1", title="Test Story")
    assert story.id == "story1"
    assert story.title == "Test Story"
    assert story.description == ""
    assert story.tasks == []


def test_story_with_tasks():
    """Test creating a story with tasks."""
    tasks = [
        Task(id="task1", title="Task 1"),
        Task(id="task2", title="Task 2", blocked_by=["task1"]),
    ]
    story = Story(
        id="story1",
        title="Test Story",
        description="A test story",
        tasks=tasks,
    )
    assert len(story.tasks) == 2
    assert story.tasks[0].id == "task1"
    assert story.tasks[1].blocked_by == ["task1"]


def test_workflow_status_defaults():
    """Test WorkflowStatus defaults."""
    status = WorkflowStatus()
    assert status.closed_tasks == []
    assert status.closed_stories == []


def test_workflow_status_with_values():
    """Test WorkflowStatus with values."""
    status = WorkflowStatus(
        closed_tasks=["task1", "task2"],
        closed_stories=["story1"],
    )
    assert status.closed_tasks == ["task1", "task2"]
    assert status.closed_stories == ["story1"]


def test_workflow_defaults():
    """Test Workflow defaults."""
    workflow = Workflow()
    assert workflow.stories == []
    assert workflow.status.closed_tasks == []
    assert workflow.status.closed_stories == []
    assert workflow._extra == {}


def test_workflow_with_stories():
    """Test Workflow with stories."""
    stories = [
        Story(
            id="story1",
            title="Story 1",
            tasks=[Task(id="task1", title="Task 1")],
        ),
    ]
    workflow = Workflow(
        stories=stories,
        status=WorkflowStatus(closed_tasks=["task1"]),
        _extra={"custom_key": "custom_value"},
    )
    assert len(workflow.stories) == 1
    assert workflow.stories[0].id == "story1"
    assert workflow.status.closed_tasks == ["task1"]
    assert workflow._extra == {"custom_key": "custom_value"}
