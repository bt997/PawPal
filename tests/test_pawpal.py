import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task


def test_mark_complete_changes_status():
    task = Task(name="Morning Walk", duration=30, priority="high", frequency="daily")
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_increases_count():
    owner = Owner(name="Alex", time_available=120)
    task = Task(name="Feeding", duration=10, priority="high", frequency="daily")
    assert len(owner.tasks) == 0
    owner.add_task(task)
    assert len(owner.tasks) == 1
