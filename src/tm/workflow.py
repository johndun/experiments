"""Core workflow operations for loading, saving, and managing workflows."""

from pathlib import Path

import yaml

from tm.models import Story, Task, Workflow, WorkflowStatus


def load_workflow(path: Path) -> Workflow:
    """Load a workflow from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    stories = []
    for story_data in data.get("stories", []):
        tasks = []
        for task_data in story_data.get("tasks", []):
            task = Task(
                id=task_data["id"],
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                blocked_by=task_data.get("blocked_by", []),
                skills=task_data.get("skills", []),
            )
            tasks.append(task)

        story = Story(
            id=story_data["id"],
            title=story_data.get("title", ""),
            description=story_data.get("description", ""),
            tasks=tasks,
            skills=story_data.get("skills", []),
        )
        stories.append(story)

    status_data = data.get("status", {})
    status = WorkflowStatus(
        closed_tasks=status_data.get("closed_tasks", []),
        closed_stories=status_data.get("closed_stories", []),
    )

    # Preserve unknown keys
    known_keys = {"stories", "status"}
    extra = {k: v for k, v in data.items() if k not in known_keys}

    return Workflow(stories=stories, status=status, _extra=extra)


def save_workflow(workflow: Workflow, path: Path) -> None:
    """Save a workflow to a YAML file."""
    data: dict = {}

    # Add extra keys first to preserve order
    data.update(workflow._extra)

    # Add stories
    stories_data = []
    for story in workflow.stories:
        story_dict: dict = {
            "id": story.id,
            "title": story.title,
        }
        if story.description:
            story_dict["description"] = story.description
        if story.skills:
            story_dict["skills"] = story.skills

        tasks_data = []
        for task in story.tasks:
            task_dict: dict = {
                "id": task.id,
                "title": task.title,
            }
            if task.description:
                task_dict["description"] = task.description
            if task.blocked_by:
                task_dict["blocked_by"] = task.blocked_by
            if task.skills:
                task_dict["skills"] = task.skills
            tasks_data.append(task_dict)

        if tasks_data:
            story_dict["tasks"] = tasks_data
        stories_data.append(story_dict)

    if stories_data:
        data["stories"] = stories_data

    # Add status
    status_dict: dict = {}
    if workflow.status.closed_tasks:
        status_dict["closed_tasks"] = workflow.status.closed_tasks
    if workflow.status.closed_stories:
        status_dict["closed_stories"] = workflow.status.closed_stories

    if status_dict:
        data["status"] = status_dict

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def ensure_status(workflow: Workflow) -> None:
    """Ensure status fields exist in workflow (modifies in place)."""
    if workflow.status is None:
        workflow.status = WorkflowStatus()


def get_all_task_ids(workflow: Workflow) -> set[str]:
    """Get all task IDs in the workflow."""
    task_ids = set()
    for story in workflow.stories:
        for task in story.tasks:
            task_ids.add(task.id)
    return task_ids


def get_ready_tasks(workflow: Workflow) -> list[tuple[Story, Task]]:
    """Return tasks that are ready to work on.

    A task is ready if:
    - It is not in closed_tasks
    - All its blocked_by tasks are in closed_tasks
    - Its parent story is not in closed_stories
    """
    closed_tasks = set(workflow.status.closed_tasks)
    closed_stories = set(workflow.status.closed_stories)

    ready = []
    for story in workflow.stories:
        if story.id in closed_stories:
            continue

        for task in story.tasks:
            if task.id in closed_tasks:
                continue

            # Check if all blocking tasks are closed
            blockers_cleared = all(
                blocker in closed_tasks for blocker in task.blocked_by
            )

            if blockers_cleared:
                ready.append((story, task))

    return ready


def close_tasks(workflow: Workflow, task_ids: list[str]) -> list[str]:
    """Close tasks and auto-close stories when all tasks are done.

    Returns list of auto-closed story IDs.
    """
    closed_stories = []

    for task_id in task_ids:
        if task_id not in workflow.status.closed_tasks:
            workflow.status.closed_tasks.append(task_id)

    # Check if any stories should be auto-closed
    closed_task_set = set(workflow.status.closed_tasks)
    for story in workflow.stories:
        if story.id in workflow.status.closed_stories:
            continue

        all_tasks_closed = all(task.id in closed_task_set for task in story.tasks)
        if story.tasks and all_tasks_closed:
            workflow.status.closed_stories.append(story.id)
            closed_stories.append(story.id)

    return closed_stories


def reset_workflow(workflow: Workflow) -> None:
    """Reset all task and story statuses."""
    workflow.status.closed_tasks = []
    workflow.status.closed_stories = []


def validate_task_ids(workflow: Workflow, task_ids: list[str]) -> list[str]:
    """Return list of invalid task IDs."""
    all_ids = get_all_task_ids(workflow)
    return [tid for tid in task_ids if tid not in all_ids]


def is_workflow_complete(workflow: Workflow) -> bool:
    """Check if all stories in the workflow are complete."""
    if not workflow.stories:
        return True
    closed_stories = set(workflow.status.closed_stories)
    return all(story.id in closed_stories for story in workflow.stories)


def get_effective_skills(story: Story, task: Task) -> list[str]:
    """Get effective skills for a task, including inherited skills from parent story.

    Returns deduplicated list with story skills first, then task-specific skills.
    """
    seen = set()
    result = []

    # Story skills first
    for skill in story.skills:
        if skill not in seen:
            seen.add(skill)
            result.append(skill)

    # Task skills second
    for skill in task.skills:
        if skill not in seen:
            seen.add(skill)
            result.append(skill)

    return result
