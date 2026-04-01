import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Initialize session state ---
if "owner" not in st.session_state:
    st.session_state.owner = None

# --- Owner + Pet Setup ---
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
time_available = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=120)

if st.button("Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species, age=0)
    owner = Owner(name=owner_name, time_available=int(time_available))
    owner.pet = pet
    st.session_state.owner = owner
    st.success(f"Saved! {owner.name}'s pet is {pet.name} the {pet.species}.")

st.divider()

# --- Add Tasks ---
st.subheader("Tasks")

if st.session_state.owner is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add Task"):
        task = Task(name=task_name, duration=int(duration), priority=priority, frequency="daily")
        st.session_state.owner.add_task(task)
        st.success(f"Added task: {task.name}")

    if st.session_state.owner.tasks:
        st.write("Current tasks:")
        st.table([
            {"Task": t.name, "Duration (min)": t.duration, "Priority": t.priority, "Done": t.is_completed}
            for t in st.session_state.owner.tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate Schedule"):
    if st.session_state.owner is None:
        st.warning("Please save an owner and pet first.")
    elif not st.session_state.owner.tasks:
        st.warning("Please add at least one task first.")
    else:
        owner = st.session_state.owner
        scheduler = Scheduler(owner=owner, time_limit=owner.time_available)
        plan = scheduler.generate_plan()

        if not plan:
            st.error("No tasks could fit within the available time.")
        else:
            st.success("Schedule generated!")
            st.table([
                {"Task": t.name, "Duration (min)": t.duration, "Priority": t.priority}
                for t in plan
            ])
            st.markdown("**Explanation**")
            st.text(scheduler.explain_plan())
