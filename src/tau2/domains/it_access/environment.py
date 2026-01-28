# Copyright Sierra

from pathlib import Path
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.it_access.data_model import ItAccessDB, get_db
from tau2.domains.it_access.tools import ItAccessTools
from tau2.domains.it_access.utils import (
    IT_ACCESS_POLICY_PATH,
    IT_ACCESS_TASK_SET_PATH,
)
from tau2.environment.environment import Environment
from tau2.utils import load_file


def get_environment(
    db: Optional[ItAccessDB] = None,
    solo_mode: bool = False,
) -> Environment:
    """Factory function to create IT Access & Permissions environment."""
    if solo_mode:
        raise ValueError("IT Access domain does not support solo mode")
    if db is None:
        db = get_db()
    tools = ItAccessTools(db)
    with open(IT_ACCESS_POLICY_PATH, "r") as fp:
        policy = fp.read()
    return Environment(
        domain_name="it_access",
        policy=policy,
        tools=tools,
    )


def get_tasks(task_split_name: Optional[str] = "base") -> list[Task]:
    """Load all tasks for the it_access domain."""
    tasks = load_file(IT_ACCESS_TASK_SET_PATH)
    tasks = [Task.model_validate(task) for task in tasks]
    if task_split_name is None:
        return tasks
    task_splits = get_tasks_split()
    if task_split_name not in task_splits:
        raise ValueError(
            f"Invalid task split name: {task_split_name}. Valid splits are: {task_splits.keys()}"
        )
    return [task for task in tasks if task.id in task_splits[task_split_name]]


def get_tasks_split() -> dict[str, list[str]]:
    """Return task splits for the it_access domain."""
    split_file = (
        Path(IT_ACCESS_TASK_SET_PATH).parent
        / f"split_{Path(IT_ACCESS_TASK_SET_PATH).stem}.json"
    )
    if split_file.exists():
        return load_file(split_file)
    return {"base": ["access_grant_task", "access_revoke_task"]}
