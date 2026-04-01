# PawPal+ Project Reflection

## 1. System Design

The user should be able to add/edit their and their pet's names.
The user should be able to add/edit care tasks for their pet.
The user should be able to have the application give them a plan on how to achieve those care tasks based on known time restrictions and task priority.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I have a Pet dataclass with the name, species, age and any special needs that the pet has when taking care of it. It also has get_care_requirements and update_info methods.

There is also a Task dataclass that has the name, duration, priority, frequency and if the task is completed or not. The methods for that are to mark_complete, edit and is_due to check if and when the task needs to be added to a schedule.

Next is the Owner class that holds the owner's name, time avaliable, preferences, Pet and a list of Tasks. Owner classes can add_task, remove_task and get_avalaible_time.

Finally there is the Scheduler class that holds an Owner, task list and time limit. It can generate_plan, explain_plan, check_constraints and prioritize_tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes the design changed based on the spec. A spawn_next method was added to Task because when a daily task is completed, a new task for the following days should be added.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

A time constraint that makes sure that total task duration doesn't exceed the time limit.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

A tradeoff that the scheduler makes is in prioritizing higher priority tasks over the total number of tasks completed. Even if more medium or low priority tasks can get completed in the time that it takes to complete one high priority task, the scheduler will still schedule the high priority task.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I asked the AI to plan first and then explain the plan before implementing it.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI didn't have a relationship between Owner and Pet in the UML diagram. I verified this on mermaid.live when I was looking at the UMl diagram. I asked the AI to change it so that Owners could have Pets.

---

## 4. Testing and Verification
## Testing PawPal+
The command to run tests is:
python -m pytest tests/test_pawpal.py

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The behaviors tested were that tasks were sorted into correct chronological order that completing a daily or weekly task automatically creates the next occurrence with the right due date, and that the conflict detector flags overlapping time windows without false positives on back-to-back tasks. 

These tests were important because those behaviors can cause errors that aren't detected.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

On a scale of 1-5, I would say my confidence level is a 4.

Another edge case to test would be completing a task with no due_date set.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I was most satisfied with the conflict handling between different tasks.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would make the frontend more colorful. Right now it's kind of boring.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The st.session_state was an interesting thing I learned and I didn't know that streamlit was stateless until I worked on this project.
