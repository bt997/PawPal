# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Task Management
- Add tasks with a name, duration, priority (high / medium / low), frequency (daily, weekly, as-needed), and a scheduled start time in HH:MM format
- Filter the task list by completion status or pet name
- Tasks are displayed sorted chronologically by start time

### Smart Scheduling
- Generates a daily plan using a greedy algorithm that respects a configurable time budget
- Tasks are prioritized high → medium → low, with start time used as a tiebreaker within each tier
- Skipped tasks (not enough time) are shown in a collapsible section

### Recurring Tasks
- Completing a daily task automatically creates a new instance due the following day
- Completing a weekly task schedules the next occurrence seven days out
- As-needed tasks are marked complete without spawning a follow-up

### Conflict Detection
- Detects overlapping time windows across all scheduled tasks (same-pet or cross-pet)
- Surfaces each conflict as a warning in the UI without crashing the app
- Back-to-back tasks that share only a boundary are not flagged

### Streamlit UI
- Owner and pet setup with time budget input
- Live task table with status, due date, and priority columns
- Schedule view with time usage summary, conflict warnings, and pet care reminders

### Tests
- 16 pytest tests covering sorting correctness, recurring task logic, and conflict detection edge cases
- Run with: `python -m pytest tests/test_pawpal.py -v`

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
