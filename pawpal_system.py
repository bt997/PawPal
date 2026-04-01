from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


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
    time: str = "00:00"        # scheduled start time in "HH:MM" format
    due_date: str = ""         # "YYYY-MM-DD"; empty means today
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

    def spawn_next(self) -> Optional["Task"]:
        """Return a new incomplete Task for the next occurrence.

        Returns None for 'as-needed' tasks since they have no fixed recurrence.
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        base = date.fromisoformat(self.due_date) if self.due_date else date.today()
        next_date = base + delta
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            time=self.time,
            due_date=next_date.isoformat(),
            is_completed=False,
        )


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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-schedule the next occurrence.

        For daily/weekly tasks, a new Task is created with the next due date
        and added to the owner's task list automatically.

        Returns the newly spawned Task, or None for as-needed tasks.
        """
        task.mark_complete()
        next_task = task.spawn_next()
        if next_task is not None:
            self.owner.add_task(next_task)
        return next_task

    def check_constraints(self) -> bool:
        """Returns True if all due tasks can fit within the time limit."""
        due_tasks = [t for t in self.task_list if t.is_due()]
        total_time = sum(t.duration for t in due_tasks)
        return total_time <= self.time_limit

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """Filter tasks by completion status and/or pet name tag.

        Args:
            completed: True for completed only, False for incomplete only, None for all.
            pet_name: If provided, only return tasks whose name contains the pet's name (case-insensitive).
        """
        result = self.task_list
        if completed is not None:
            result = [t for t in result if t.is_completed == completed]
        if pet_name is not None:
            result = [t for t in result if pet_name.lower() in t.name.lower()]
        return result

    @staticmethod
    def _start_minutes(task: Task) -> int:
        """Convert a task's HH:MM time string to an absolute minute offset."""
        h, m = task.time.split(":")
        return int(h) * 60 + int(m)

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Check a list of scheduled tasks for time-window overlaps.

        Two tasks conflict when their intervals [start, start+duration) overlap.
        Returns a list of human-readable warning strings — one per conflict pair.
        Returns an empty list when no conflicts are found.
        """
        warnings = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                a_start, a_end = self._start_minutes(a), self._start_minutes(a) + a.duration
                b_start, b_end = self._start_minutes(b), self._start_minutes(b) + b.duration
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"WARNING: '{a.name}' ({a.time}, {a.duration} min) overlaps "
                        f"'{b.name}' ({b.time}, {b.duration} min)"
                    )
        return warnings

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by their 'time' attribute in HH:MM format."""
        return sorted(tasks, key=lambda t: (int(t.time.split(":")[0]), int(t.time.split(":")[1])))

    def prioritize_tasks(self) -> List[Task]:
        """Returns due, incomplete tasks sorted by priority then by start time within each tier."""
        due_tasks = [t for t in self.task_list if t.is_due() and not t.is_completed]
        return sorted(due_tasks, key=lambda t: (
            PRIORITY_ORDER.get(t.priority, 99),
            int(t.time.split(":")[0]),
            int(t.time.split(":")[1])
        ))

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
