import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_owner(time_available=180):
    owner = Owner(name="Alex", time_available=time_available)
    owner.pet = Pet(name="Buddy", species="Dog", age=3)
    return owner


def make_scheduler(tasks, time_available=180):
    owner = make_owner(time_available)
    for t in tasks:
        owner.add_task(t)
    return Scheduler(owner=owner, time_limit=time_available)


# ── Existing tests (unchanged) ────────────────────────────────────────────────

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


# ── Sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back sorted earliest-first."""
    tasks = [
        Task(name="Playtime",     duration=25, priority="medium", frequency="daily", time="11:00"),
        Task(name="Feeding",      duration=10, priority="high",   frequency="daily", time="07:00"),
        Task(name="Morning Walk", duration=30, priority="high",   frequency="daily", time="08:00"),
        Task(name="Grooming",     duration=20, priority="medium", frequency="daily", time="09:30"),
    ]
    scheduler = make_scheduler(tasks)
    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times), f"Expected chronological order, got: {times}"


def test_sort_by_time_handles_same_hour_different_minutes():
    """Tasks in the same hour must sort by minute, not just hour."""
    tasks = [
        Task(name="Task B", duration=10, priority="medium", frequency="daily", time="07:45"),
        Task(name="Task A", duration=10, priority="high",   frequency="daily", time="07:15"),
        Task(name="Task C", duration=10, priority="low",    frequency="daily", time="07:00"),
    ]
    scheduler = make_scheduler(tasks)
    sorted_tasks = scheduler.sort_by_time(tasks)
    assert [t.time for t in sorted_tasks] == ["07:00", "07:15", "07:45"]


def test_sort_by_time_single_task_unchanged():
    """A one-item list should be returned as-is without error."""
    tasks = [Task(name="Feeding", duration=10, priority="high", frequency="daily", time="08:00")]
    scheduler = make_scheduler(tasks)
    assert scheduler.sort_by_time(tasks) == tasks


def test_sort_by_time_empty_list():
    """An empty list should return an empty list without error."""
    scheduler = make_scheduler([])
    assert scheduler.sort_by_time([]) == []


# ── Recurring task / spawn_next ───────────────────────────────────────────────

def test_complete_daily_task_spawns_next_day():
    """Completing a daily task via Scheduler should add a new task due tomorrow."""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    task = Task(name="Feeding", duration=10, priority="high", frequency="daily",
                time="07:00", due_date=today)
    scheduler = make_scheduler([task])

    next_task = scheduler.complete_task(task)

    assert next_task is not None, "Expected a new task to be spawned"
    assert next_task.due_date == tomorrow
    assert next_task.is_completed is False
    assert next_task.name == task.name


def test_complete_daily_task_adds_to_owner_list():
    """The spawned task should be automatically added to the owner's task list."""
    today = date.today().isoformat()
    task = Task(name="Feeding", duration=10, priority="high", frequency="daily",
                time="07:00", due_date=today)
    scheduler = make_scheduler([task])
    initial_count = len(scheduler.owner.tasks)

    scheduler.complete_task(task)

    assert len(scheduler.owner.tasks) == initial_count + 1


def test_complete_weekly_task_spawns_seven_days_later():
    """Completing a weekly task should schedule the next one 7 days out."""
    today = date.today()
    task = Task(name="Bath Time", duration=20, priority="medium", frequency="weekly",
                time="10:00", due_date=today.isoformat())
    scheduler = make_scheduler([task])

    next_task = scheduler.complete_task(task)

    expected = (today + timedelta(weeks=1)).isoformat()
    assert next_task is not None
    assert next_task.due_date == expected


def test_as_needed_task_does_not_spawn():
    """Completing an as-needed task should NOT create a follow-up instance."""
    task = Task(name="Vet Check-up", duration=60, priority="low", frequency="as-needed",
                time="14:00", due_date=date.today().isoformat())
    scheduler = make_scheduler([task])
    initial_count = len(scheduler.owner.tasks)

    next_task = scheduler.complete_task(task)

    assert next_task is None
    assert len(scheduler.owner.tasks) == initial_count


def test_spawn_next_preserves_task_attributes():
    """The spawned task should carry over all fields except is_completed and due_date."""
    today = date.today().isoformat()
    task = Task(name="Grooming", duration=20, priority="medium", frequency="daily",
                time="09:30", due_date=today)
    next_task = task.spawn_next()

    assert next_task.name == task.name
    assert next_task.duration == task.duration
    assert next_task.priority == task.priority
    assert next_task.frequency == task.frequency
    assert next_task.time == task.time
    assert next_task.is_completed is False


# ── Conflict detection ────────────────────────────────────────────────────────

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose windows overlap should produce exactly one warning."""
    # Grooming: 09:30 → 09:50  |  Bath: 09:40 → 09:55  — 10-minute overlap
    tasks = [
        Task(name="Grooming", duration=20, priority="medium", frequency="daily", time="09:30"),
        Task(name="Bath",     duration=15, priority="medium", frequency="daily", time="09:40"),
    ]
    scheduler = make_scheduler(tasks)
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1
    assert "Grooming" in warnings[0]
    assert "Bath" in warnings[0]


def test_detect_conflicts_no_warning_for_back_to_back_tasks():
    """A task that starts exactly when the previous one ends is NOT a conflict."""
    # Walk: 08:00 → 08:30  |  Feeding: 08:30 → 08:40  — touching but not overlapping
    tasks = [
        Task(name="Morning Walk", duration=30, priority="high",   frequency="daily", time="08:00"),
        Task(name="Feeding",      duration=10, priority="high",   frequency="daily", time="08:30"),
    ]
    scheduler = make_scheduler(tasks)
    assert scheduler.detect_conflicts(tasks) == []


def test_detect_conflicts_clean_plan_returns_empty():
    """A well-spaced plan should return no warnings."""
    tasks = [
        Task(name="Feeding",      duration=10, priority="high",   frequency="daily", time="07:00"),
        Task(name="Morning Walk", duration=30, priority="high",   frequency="daily", time="08:00"),
        Task(name="Grooming",     duration=20, priority="medium", frequency="daily", time="09:30"),
    ]
    scheduler = make_scheduler(tasks)
    assert scheduler.detect_conflicts(tasks) == []


def test_detect_conflicts_multiple_pairs():
    """Three mutually overlapping tasks should produce three warnings (one per pair)."""
    tasks = [
        Task(name="Task A", duration=60, priority="high",   frequency="daily", time="09:00"),
        Task(name="Task B", duration=60, priority="medium", frequency="daily", time="09:30"),
        Task(name="Task C", duration=60, priority="low",    frequency="daily", time="09:45"),
    ]
    scheduler = make_scheduler(tasks)
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 3


def test_detect_conflicts_single_task_no_warning():
    """A single task can never conflict with itself."""
    tasks = [Task(name="Feeding", duration=10, priority="high", frequency="daily", time="07:00")]
    scheduler = make_scheduler(tasks)
    assert scheduler.detect_conflicts(tasks) == []
