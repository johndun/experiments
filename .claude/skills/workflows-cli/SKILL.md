---
name: workflows-cli
description: Track progress on long-running tasks using workflow YAML files
---

# wf (Workflow Manager)

A CLI tool for tracking progress on long-running tasks using workflow YAML files.

## Commands

### Show Ready Tasks

```bash
wf ready path/to/workflow.yaml
```

Shows all unblocked open tasks and sets the workflow as active.

### Close Tasks

```bash
wf close task1 task2 ...
```

Closes the specified tasks and shows the next ready tasks. Requires an active workflow (set via `wf ready`).

### Reset Workflow

```bash
wf reset path/to/workflow.yaml
```

Resets all task and story statuses, clearing `closed_tasks` and `closed_stories`.

## Workflow YAML Schema

```yaml
stories:
  - id: story1
    title: Story Title
    description: Optional description
    tasks:
      - id: task1
        title: Task Title
        description: Optional description
      - id: task2
        title: Blocked Task
        blocked_by:
          - task1

status:
  closed_tasks:
    - task1
  closed_stories:
    - story1
```

### Fields

| Field | Description |
|-------|-------------|
| `stories` | List of stories containing tasks |
| `stories[].id` | Unique story identifier |
| `stories[].title` | Story title |
| `stories[].description` | Optional story description |
| `stories[].tasks` | List of tasks in the story |
| `tasks[].id` | Unique task identifier |
| `tasks[].title` | Task title |
| `tasks[].description` | Optional task description |
| `tasks[].blocked_by` | List of task IDs that must be closed first |
| `status.closed_tasks` | List of closed task IDs |
| `status.closed_stories` | List of closed story IDs (auto-populated) |

## Examples

### Create a workflow file

```yaml
# project-workflow.yaml
stories:
  - id: auth
    title: User Authentication
    tasks:
      - id: user-model
        title: Create user model
      - id: register
        title: Implement registration
        blocked_by:
          - user-model
      - id: login
        title: Implement login
        blocked_by:
          - user-model

  - id: api
    title: API Endpoints
    tasks:
      - id: setup-routes
        title: Set up route handlers
      - id: add-auth
        title: Add authentication middleware
        blocked_by:
          - setup-routes
          - login
```

### Start working on the workflow

```bash
wf ready project-workflow.yaml
```

Output:
```
Ready tasks (2):

[auth] User Authentication
  [user-model] Create user model

[api] API Endpoints
  [setup-routes] Set up route handlers
```

### Close a task

```bash
wf close user-model
```

Output:
```
Closed tasks: user-model

Ready tasks (3):

[auth] User Authentication
  [register] Implement registration (after: user-model)
  [login] Implement login (after: user-model)

[api] API Endpoints
  [setup-routes] Set up route handlers
```

### Close multiple tasks

```bash
wf close register login setup-routes
```

### Reset progress

```bash
wf reset project-workflow.yaml
```

## Behavior

- **Ready tasks**: A task is ready when it's not closed and all its `blocked_by` dependencies are closed
- **Auto-close stories**: When all tasks in a story are closed, the story is automatically marked as closed
- **Active workflow**: The `ready` command sets a `.wf.json` config file to track the active workflow, so `close` doesn't need the workflow path
- **Preserves unknown keys**: Any extra YAML keys in your workflow file are preserved when saving

## Config File

The tool creates a `.wf.json` file in the current directory to track the active workflow:

```json
{
  "active_workflow": "path/to/workflow.yaml"
}
```
