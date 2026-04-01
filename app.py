import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Initialize session state ---
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner & Pet Setup ─────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

owner_name    = st.text_input("Owner name", value="Jordan")
pet_name      = st.text_input("Pet name", value="Mochi")
species       = st.selectbox("Species", ["dog", "cat", "other"])
time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=120)

if st.button("Save Owner & Pet"):
    pet   = Pet(name=pet_name, species=species, age=0)
    owner = Owner(name=owner_name, time_available=int(time_available))
    owner.pet = pet
    st.session_state.owner = owner
    st.success(f"Saved! {owner.name}'s pet is {pet.name} the {pet.species}.")

st.divider()

# ── Add Tasks ─────────────────────────────────────────────────────────────────
st.subheader("Add a Task")

if st.session_state.owner is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        task_name  = st.text_input("Task name", value="Morning walk")
    with col2:
        duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority   = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        frequency  = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
    with col5:
        task_time  = st.text_input("Start time (HH:MM)", value="08:00")

    if st.button("Add Task"):
        task = Task(
            name=task_name,
            duration=int(duration),
            priority=priority,
            frequency=frequency,
            time=task_time,
            due_date=date.today().isoformat(),
        )
        st.session_state.owner.add_task(task)
        st.success(f"Added: **{task.name}** at {task.time}")

st.divider()

# ── Current Task List (sorted + filtered) ────────────────────────────────────
st.subheader("Current Tasks")

if st.session_state.owner is None or not st.session_state.owner.tasks:
    st.info("No tasks yet. Add one above.")
else:
    owner     = st.session_state.owner
    scheduler = Scheduler(owner=owner, time_limit=owner.time_available)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Completed"],
            key="filter_status",
        )
    with col_f2:
        filter_pet = st.text_input("Filter by pet name (leave blank for all)", key="filter_pet")

    # Resolve filter args
    completed_filter = {"All": None, "Incomplete": False, "Completed": True}[filter_status]
    pet_filter       = filter_pet.strip() if filter_pet.strip() else None

    filtered = scheduler.filter_tasks(completed=completed_filter, pet_name=pet_filter)
    sorted_tasks = scheduler.sort_by_time(filtered)

    if not sorted_tasks:
        st.warning("No tasks match the current filters.")
    else:
        st.caption(f"Showing {len(sorted_tasks)} task(s) — sorted by start time")
        st.table([
            {
                "Start": t.time,
                "Task": t.name,
                "Duration (min)": t.duration,
                "Priority": t.priority.capitalize(),
                "Frequency": t.frequency,
                "Due": t.due_date or "today",
                "Done": "✓" if t.is_completed else "",
            }
            for t in sorted_tasks
        ])

st.divider()

# ── Generate Schedule ─────────────────────────────────────────────────────────
st.subheader("Today's Schedule")

if st.button("Generate Schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an owner and pet first.")
    elif not st.session_state.owner.tasks:
        st.warning("Please add at least one task first.")
    else:
        owner     = st.session_state.owner
        scheduler = Scheduler(owner=owner, time_limit=owner.time_available)
        plan      = scheduler.generate_plan()

        if not plan:
            st.error("No tasks could fit within the available time.")
        else:
            # ── Conflict warnings ─────────────────────────────────────────
            conflicts = scheduler.detect_conflicts(plan)
            if conflicts:
                for w in conflicts:
                    st.warning(w)
            else:
                st.success(f"Schedule generated — no conflicts detected.")

            # ── Scheduled tasks table ─────────────────────────────────────
            total_min = sum(t.duration for t in plan)
            st.caption(f"**{total_min} / {owner.time_available} min** scheduled")
            st.table([
                {
                    "Start": t.time,
                    "Task": t.name,
                    "Duration (min)": t.duration,
                    "Priority": t.priority.capitalize(),
                }
                for t in plan
            ])

            # ── Skipped tasks ─────────────────────────────────────────────
            skipped = [t for t in scheduler.prioritize_tasks() if t not in plan]
            if skipped:
                with st.expander(f"Skipped tasks ({len(skipped)}) — not enough time"):
                    st.table([
                        {"Task": t.name, "Duration (min)": t.duration, "Priority": t.priority.capitalize()}
                        for t in skipped
                    ])

            # ── Pet reminders ─────────────────────────────────────────────
            if owner.pet and owner.pet.special_needs:
                st.info(f"**Reminder for {owner.pet.name}:** {', '.join(owner.pet.special_needs)}")
