from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", age=4, special_needs=["joint supplement with dinner"])
luna  = Pet(name="Luna",  species="Cat", age=2)

# --- Owner ---
alex = Owner(name="Alex", time_available=120, preferences=["morning walks"])
alex.pet = buddy

# --- Tasks (added out of order by time; due_date = today) ---
today = date.today().isoformat()

vet_checkup   = Task(name="Vet Check-up",   duration=60, priority="low",    frequency="as-needed", time="14:00", due_date=today)
playtime      = Task(name="Playtime",        duration=25, priority="medium", frequency="daily",     time="11:00", due_date=today)
feeding       = Task(name="Feeding",         duration=10, priority="high",   frequency="daily",     time="07:00", due_date=today)
grooming      = Task(name="Grooming",        duration=20, priority="medium", frequency="daily",     time="09:30", due_date=today)
morning_walk  = Task(name="Morning Walk",    duration=30, priority="high",   frequency="daily",     time="08:00", due_date=today)
luna_brushing = Task(name="Luna Brushing",   duration=15, priority="medium", frequency="daily",     time="10:00", due_date=today)
luna_feeding  = Task(name="Luna Feeding",    duration=10, priority="high",   frequency="weekly",    time="07:30", due_date=today)

for task in [vet_checkup, playtime, feeding, grooming, morning_walk, luna_brushing, luna_feeding]:
    alex.add_task(task)

scheduler = Scheduler(owner=alex, time_limit=alex.time_available)


def print_task_list(tasks, title):
    print(f"\n{'=' * 54}")
    print(f"  {title}")
    print(f"{'=' * 54}")
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        status = "✓" if t.is_completed else " "
        due    = f"due {t.due_date}" if t.due_date else "no date"
        print(f"  [{status}] {t.time}  {t.name:<20} {t.duration:>3} min  [{t.priority:<6}]  {due}")


# ── 1. Raw insertion order ───────────────────────────────────────────────────
print_task_list(alex.tasks, "1. RAW INSERTION ORDER")

# ── 2. Sorted by time ────────────────────────────────────────────────────────
print_task_list(scheduler.sort_by_time(alex.tasks), "2. SORTED BY TIME")

# ── 3. Complete two tasks via Scheduler (auto-spawn next occurrence) ─────────
print(f"\n{'=' * 54}")
print("  3. COMPLETING TASKS — auto-spawn next occurrence")
print(f"{'=' * 54}")

for task in [feeding, luna_feeding]:
    next_t = scheduler.complete_task(task)
    freq_label = f"(+1 {'day' if task.frequency == 'daily' else 'week'})"
    if next_t:
        print(f"  ✓ Completed : {task.name:<20}  due {task.due_date}")
        print(f"    → Spawned  : {next_t.name:<20}  due {next_t.due_date}  {freq_label}")
    else:
        print(f"  ✓ Completed : {task.name:<20}  (as-needed — no next occurrence spawned)")

# ── 4. Filter: incomplete only ───────────────────────────────────────────────
print_task_list(
    scheduler.filter_tasks(completed=False),
    "4. FILTER: incomplete tasks"
)

# ── 5. Filter: completed only ────────────────────────────────────────────────
print_task_list(
    scheduler.filter_tasks(completed=True),
    "5. FILTER: completed tasks"
)

# ── 6. Filter: Luna's tasks (all, sorted by time) ───────────────────────────
print_task_list(
    scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")),
    "6. FILTER: Luna's tasks (sorted by time)"
)

# ── 7. Generated schedule after completions ──────────────────────────────────
print(f"\n{'=' * 54}")
print("  7. TODAY'S SCHEDULE (after completions)")
print(f"{'=' * 54}")
print(f"  Owner: {alex.name}  |  {alex.time_available} min available")
print(f"  {'-' * 50}")
plan = scheduler.generate_plan()
total = 0
for i, t in enumerate(plan, 1):
    print(f"  {i}. {t.time}  {t.name:<20} {t.duration:>3} min  [{t.priority}]")
    total += t.duration
print(f"  {'-' * 50}")
print(f"  {'Total':<26} {total:>3} / {alex.time_available} min")

skipped = [t for t in scheduler.prioritize_tasks() if t not in plan]
if skipped:
    print("\n  Skipped (out of time):")
    for t in skipped:
        print(f"    - {t.name} ({t.duration} min)")

if buddy.special_needs:
    print(f"\n  Reminder for {buddy.name}: {', '.join(buddy.special_needs)}")

print("=" * 54)

# ── 8. Conflict detection — no conflicts expected in clean plan ──────────────
print(f"\n{'=' * 54}")
print("  8. CONFLICT DETECTION — clean plan (no overlaps)")
print(f"{'=' * 54}")
conflicts = scheduler.detect_conflicts(plan)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# ── 9. Conflict detection — intentional overlap injected ────────────────────
print(f"\n{'=' * 54}")
print("  9. CONFLICT DETECTION — overlapping tasks injected")
print(f"{'=' * 54}")
# Grooming starts 09:30 (20 min) → ends 09:50
# Overlap task starts 09:40 (15 min) → ends 09:55 — same-pet conflict
# Luna task starts 09:45 (10 min) → ends 09:55 — cross-pet conflict
overlap_same = Task(name="Buddy Bath",    duration=15, priority="medium", frequency="daily", time="09:40", due_date=today)
overlap_luna = Task(name="Luna Vet Trip", duration=10, priority="high",   frequency="daily", time="09:45", due_date=today)
conflicting_plan = plan + [overlap_same, overlap_luna]

conflicts = scheduler.detect_conflicts(conflicting_plan)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")
