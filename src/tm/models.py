"""Dataclasses for workflow schema."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A task within a story."""

    id: str
    title: str
    description: str = ""
    blocked_by: list[str] = field(default_factory=list)


@dataclass
class Story:
    """A story containing multiple tasks."""

    id: str
    title: str
    description: str = ""
    tasks: list[Task] = field(default_factory=list)


@dataclass
class WorkflowStatus:
    """Status tracking for closed tasks and stories."""

    closed_tasks: list[str] = field(default_factory=list)
    closed_stories: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    """A workflow containing stories and status."""

    stories: list[Story] = field(default_factory=list)
    status: WorkflowStatus = field(default_factory=WorkflowStatus)
    _extra: dict = field(default_factory=dict)
