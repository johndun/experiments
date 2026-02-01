"""CLI entry point with tyro subcommands."""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from tm.config import get_active_workflow, set_active_workflow
from tm.workflow import (
    close_tasks,
    get_effective_skills,
    get_ready_tasks,
    load_workflow,
    reset_workflow,
    save_workflow,
    validate_task_ids,
)


@dataclass
class ReadyCmd:
    """Show unblocked open tasks and activate workflow."""

    workflow: Annotated[Path | None, tyro.conf.Positional] = None


@dataclass
class ResetCmd:
    """Reset workflow task statuses."""

    workflow: Annotated[Path | None, tyro.conf.Positional] = None


@dataclass
class CloseCmd:
    """Close tasks and show next ready tasks."""

    task_ids: Annotated[tuple[str, ...], tyro.conf.Positional]


Command = (
    Annotated[ReadyCmd, tyro.conf.subcommand(name="ready")]
    | Annotated[ResetCmd, tyro.conf.subcommand(name="reset")]
    | Annotated[CloseCmd, tyro.conf.subcommand(name="close")]
)


def get_workflow_path(provided: Path | None) -> Path | None:
    """Get workflow path from provided argument or active workflow."""
    if provided is not None:
        return provided
    return get_active_workflow()


def print_ready_tasks(workflow_path: Path) -> None:
    """Load workflow and print ready tasks in consolidated view."""
    workflow = load_workflow(workflow_path)
    ready = get_ready_tasks(workflow)

    if not ready:
        print("No ready tasks.")
        return

    print(f"Ready tasks ({len(ready)}):")
    print()

    for story, task in ready:
        # Task header with id and title
        print(f"[{task.id}] {task.title}")

        # Description (if present)
        if task.description:
            print(f"  {task.description}")

        # Blocked by (if present)
        if task.blocked_by:
            blockers = ", ".join(task.blocked_by)
            print(f"  blocked_by: {blockers}")

        # Skills (inherited from story + task-specific)
        effective_skills = get_effective_skills(story, task)
        if effective_skills:
            skills_str = ", ".join(effective_skills)
            print(f"  skills: {skills_str}")

        print()


def handle_ready(cmd: ReadyCmd) -> int:
    """Handle the ready command."""
    workflow_path = get_workflow_path(cmd.workflow)

    if workflow_path is None:
        print(
            "Error: No workflow specified and no active workflow set.",
            file=sys.stderr,
        )
        print("Usage: tm ready path/to/workflow.yaml", file=sys.stderr)
        return 1

    if not workflow_path.exists():
        print(f"Error: Workflow file not found: {workflow_path}", file=sys.stderr)
        return 1

    # Set as active workflow
    set_active_workflow(workflow_path)

    print(f"Active workflow: {workflow_path}")
    print()
    print_ready_tasks(workflow_path)
    return 0


def handle_reset(cmd: ResetCmd) -> int:
    """Handle the reset command."""
    workflow_path = get_workflow_path(cmd.workflow)

    if workflow_path is None:
        print(
            "Error: No workflow specified and no active workflow set.",
            file=sys.stderr,
        )
        print("Usage: tm reset path/to/workflow.yaml", file=sys.stderr)
        return 1

    if not workflow_path.exists():
        print(f"Error: Workflow file not found: {workflow_path}", file=sys.stderr)
        return 1

    workflow = load_workflow(workflow_path)
    reset_workflow(workflow)
    save_workflow(workflow, workflow_path)

    print(f"Reset workflow: {workflow_path}")
    print()
    print_ready_tasks(workflow_path)
    return 0


def handle_close(cmd: CloseCmd) -> int:
    """Handle the close command."""
    if not cmd.task_ids:
        print("Error: No task IDs provided.", file=sys.stderr)
        print("Usage: tm close task1 task2 ...", file=sys.stderr)
        return 1

    workflow_path = get_active_workflow()

    if workflow_path is None:
        print("Error: No active workflow set.", file=sys.stderr)
        print("Run 'tm ready path/to/workflow.yaml' first.", file=sys.stderr)
        return 1

    if not workflow_path.exists():
        print(
            f"Error: Active workflow file not found: {workflow_path}",
            file=sys.stderr,
        )
        return 1

    workflow = load_workflow(workflow_path)

    # Validate task IDs
    task_ids = list(cmd.task_ids)
    invalid_ids = validate_task_ids(workflow, task_ids)
    if invalid_ids:
        print(f"Error: Unknown task IDs: {', '.join(invalid_ids)}", file=sys.stderr)
        return 1

    # Close tasks
    auto_closed_stories = close_tasks(workflow, task_ids)
    save_workflow(workflow, workflow_path)

    # Print active workflow and what was closed
    print(f"Active workflow: {workflow_path}")
    print(f"Closed tasks: {', '.join(task_ids)}")
    if auto_closed_stories:
        print(f"Completed stories: {', '.join(auto_closed_stories)}")
    print()

    # Show next ready tasks
    print_ready_tasks(workflow_path)
    return 0


def main() -> None:
    """Main entry point."""
    cmd = tyro.cli(Command)

    if isinstance(cmd, ReadyCmd):
        exit_code = handle_ready(cmd)
    elif isinstance(cmd, ResetCmd):
        exit_code = handle_reset(cmd)
    elif isinstance(cmd, CloseCmd):
        exit_code = handle_close(cmd)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
