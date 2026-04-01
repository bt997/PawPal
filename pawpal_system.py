from dataclasses import dataclass, field
from typing import List


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def get_care_requirements(self) -> List[str]:
        """Returns base care requirements plus any special needs."""
        requirements = ["feeding", "fresh water", "exercise"]
        if self.special_needs:
            requirements.extend(self.special_needs)
        return requirements

    def update_info(self, **kwargs) -> None:
        """Update any Pet attribute by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Task:
    name: str
    duration: int          # in minutes
    priority: str          # "high", "medium", "low"
    frequency: str         # "daily", "weekly", "as-needed"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def edit(self, **kwargs) -> None:
        """Update any Task attribute by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_due(self) -> bool:
        """Daily and as-needed tasks are always considered due."""
        return self.frequency in ("daily", "as-needed")


class Owner:
    def __init__(self, name: str, time_available: int, preferences: List[str] = None):
        self.name = name
        self.time_available = time_available   # in minutes
        self.preferences = preferences or []
        self.pet: Pet = None
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task if it isn't already in the list."""
        if task not in self.tasks:
            self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_available_time(self) -> int:
        """Returns total minutes available minus time already spent on completed tasks."""
        time_spent = sum(t.duration for t in self.tasks if t.is_completed)
        return self.time_available - time_spent


class Scheduler:
    def __init__(self, owner: Owner, time_limit: int):
        self.owner = owner
        self.task_list: List[Task] = owner.tasks
        self.time_limit = time_limit           # in minutes

    def check_constraints(self) -> bool:
        """Returns True if all due tasks can fit within the time limit."""
        due_tasks = [t for t in self.task_list if t.is_due()]
        total_time = sum(t.duration for t in due_tasks)
        return total_time <= self.time_limit

    def prioritize_tasks(self) -> List[Task]:
        """Returns due, incomplete tasks sorted by priority (high → medium → low)."""
        due_tasks = [t for t in self.task_list if t.is_due() and not t.is_completed]
        return sorted(due_tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def generate_plan(self) -> List[Task]:
        """Greedily fills the schedule with prioritized tasks that fit in the time limit."""
        prioritized = self.prioritize_tasks()
        plan = []
        time_used = 0
        for task in prioritized:
            if time_used + task.duration <= self.time_limit:
                plan.append(task)
                time_used += task.duration
        return plan

    def explain_plan(self) -> str:
        """Returns a human-readable summary of the generated plan."""
        plan = self.generate_plan()
        if not plan:
            return "No tasks could be scheduled within the available time."

        lines = [f"Daily plan for {self.owner.pet.name if self.owner.pet else 'your pet'}:\n"]
        time_used = 0
        for task in plan:
            lines.append(f"  - {task.name} ({task.duration} min) [{task.priority} priority]")
            time_used += task.duration

        skipped = [t for t in self.prioritize_tasks() if t not in plan]
        lines.append(f"\nTotal time: {time_used} / {self.time_limit} min")
        if skipped:
            skipped_names = ", ".join(t.name for t in skipped)
            lines.append(f"Skipped (no time): {skipped_names}")

        return "\n".join(lines)
