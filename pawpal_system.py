from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def get_care_requirements(self) -> List[str]:
        pass

    def update_info(self, **_kwargs) -> None:
        pass


@dataclass
class Task:
    name: str
    duration: int          # in minutes
    priority: str          # "high", "medium", "low"
    frequency: str         # "daily", "weekly", etc.
    is_completed: bool = False

    def mark_complete(self) -> None:
        pass

    def edit(self, **kwargs) -> None:
        pass

    def is_due(self) -> bool:
        pass


class Owner:
    def __init__(self, name: str, time_available: int, preferences: List[str] = None):
        self.name = name
        self.time_available = time_available   # in minutes
        self.preferences = preferences or []
        self.pet: Pet = None
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_available_time(self) -> int:
        pass


class Scheduler:
    def __init__(self, owner: Owner, time_limit: int):
        self.owner = owner
        self.task_list: List[Task] = []
        self.time_limit = time_limit           # in minutes

    def generate_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def check_constraints(self) -> bool:
        pass

    def prioritize_tasks(self) -> List[Task]:
        pass
