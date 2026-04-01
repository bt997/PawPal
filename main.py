from pawpal_system import Owner, Pet, Task, Scheduler


# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", age=4, special_needs=["joint supplement with dinner"])
luna = Pet(name="Luna", species="Cat", age=2)

# --- Owner ---
alex = Owner(name="Alex", time_available=120, preferences=["morning walks"])
alex.pet = buddy  # primary pet tracked in schedule

# --- Tasks ---
morning_walk = Task(name="Morning Walk",    duration=30, priority="high",   frequency="daily")
feeding      = Task(name="Feeding",         duration=10, priority="high",   frequency="daily")
grooming     = Task(name="Grooming",        duration=20, priority="medium", frequency="daily")
playtime     = Task(name="Playtime",        duration=25, priority="medium", frequency="daily")
vet_checkup  = Task(name="Vet Check-up",    duration=60, priority="low",    frequency="as-needed")

# Add tasks to owner
for task in [morning_walk, feeding, grooming, playtime, vet_checkup]:
    alex.add_task(task)

# --- Schedule ---
scheduler = Scheduler(owner=alex, time_limit=alex.time_available)
plan = scheduler.generate_plan()

# --- Print Today's Schedule ---
print("=" * 40)
print("        PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 40)
print(f"Owner : {alex.name}")
print(f"Pets  : {buddy.name} ({buddy.species}), {luna.name} ({luna.species})")
print(f"Time  : {alex.time_available} min available")
print("-" * 40)

if not plan:
    print("No tasks fit within the available time.")
else:
    total = 0
    for i, task in enumerate(plan, start=1):
        print(f"{i}. {task.name:<20} {task.duration:>3} min  [{task.priority}]")
        total += task.duration
    print("-" * 40)
    print(f"   {'Total':<20} {total:>3} min")

skipped = [t for t in scheduler.prioritize_tasks() if t not in plan]
if skipped:
    print("\nSkipped (out of time):")
    for task in skipped:
        print(f"  - {task.name} ({task.duration} min)")

if buddy.special_needs:
    print(f"\nReminder for {buddy.name}: {', '.join(buddy.special_needs)}")

print("=" * 40)
