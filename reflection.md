# PawPal+ Project Reflection

## 1. System Design
The three core actions I have identified are adding pet info, creating tasks needed to be done, and display today's tasks.

**a. Initial design**

- Briefly describe your initial UML design.

initially it uses five classes. Pet and Owner classes are significant that are actually data handling entities defining Pet being cared by the Owner who's the caretaker. Scheduler class is the core logic layer where it has functions to add/edit tasks, priortizes according to owner availability. Dailyplan is the output object that contains resulting schedule and Task is a single activity to be done.


- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

Yes, several refinements were made during implementation to improve efficiency and prevent logic bottlenecks:

1. **Added `last_completed` to Task** — The frequency field alone wasn't enough to determine if a task should run today. By tracking when a task was last completed, `is_mandatory()` can now properly check if a weekly task is overdue or if a daily task was already done today.

2. **Added plan tracking to Owner** — Owner now maintains `current_plan` (today's schedule) and `plan_history` (all past plans). This allows users to view and review their schedule history, which was missing from the initial design.

3. **Added owner and pet context to DailyPlan** — DailyPlan now stores references to its Owner and Pet. This ensures the schedule knows which pet/owner it belongs to, which is critical for logging, context, and preventing orphaned plans.

4. **Added task status tracking to DailyPlan** — Added `completed_tasks` and `skipped_tasks` lists alongside `scheduled_tasks`. This allows the app to track partial completion or changes to the plan throughout the day.

5. **Clarified time_slot parameter** — Changed vague parameter name `time_slot: int` to `start_time_minutes: int` with clear documentation: "minutes from midnight, e.g., 480 = 8am". This prevents confusion and makes the API less error-prone.

6. **Combined rank+fit logic into `generate_ranked_and_fitted_tasks()`** — The original design had separate `rank_tasks()` and `fit_tasks_in_time()` methods. These are almost always used together in sequence, creating a bottleneck where someone could call them independently or out of order. The new combined method ensures proper sequencing and reduces redundant computation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
1. **Available time** (owner.available_time) — Hard limit; most critical
2. **Task priority** (1-5 scale) — Determines sort order; highest prioritized first
3. **Task duration** (minutes) — Secondary sort; shorter tasks pack better
4. **Task frequency** (daily/weekly/as-needed) — Determines if task is mandatory today
5. **Task dependencies** (depends_on) — Must satisfy before dependents
6. **Time-of-day preferences** (preferred_times) — Soft constraint via categorization
7. **Pet-specific conflicts** — Prevent same pet multi-tasking

**Decision**: Time and priority matter most because available time is a hard constraint (owner can't do unlimited tasks), and priority reflects what the owner deemed urgent. Frequency determines what *must* happen today.

**b. Tradeoffs**

**Tradeoff 1: Greedy Bin-Packing vs. Optimal Packing**
- Greedy approach being O(n log n) is fast and produces good results for typical cases meanwhile optimal approach is NP-hard and overkill for UX
- **Why reasonable**: Users need instant feedback; greedy provides 85-95% optimal results with instant scheduling

**Tradeoff 2: Non-Blocking Warnings vs. Hard Failures**
- Non-blocking allows schedule with conflicts but alerts user whereas hard failure prevents conflicting schedule in other ways blocks plan generation
- **Why reasonable**: Owner wants visibility into conflicts, not blockers. They can adjust if needed.

**Tradeoff 3: Auto-Recurrence vs. Manual Entry**
- Auto-recurrence creates next occurrence automatically at completion and manual owner re-enters each task manually
- **Why reasonable**: Reduces friction; owner doesn't re-type "Daily Walk" 365 times/year

---

## 3. AI Collaboration

**a. How you used AI**

- **Design brainstorming**: Identified core classes (Pet, Task, Owner, Scheduler, DailyPlan)
- **Architecture review**: AI helped spot missing relations for example oowner and  task bidirectional lookup
- **Debugging**: Why tests failed? Fixed is_complete mutation issue by isolating state to DailyPlan
- **Feature expansion**: Added 8 advanced methods (conflict detection, recurring task expansion, topological sorting)

**Most helpful prompts:**
- "Why is this object missing from the architecture?"
- "What went wrong in the test output?" (led to identifying state mutation bug)
- "What scheduling algorithms exist?" (led to bin-packing, topological sort, conflict detection)

**b. Judgment and verification**

**Rejected suggestion:** AI suggested mutating `task.last_completed = date.today()` in `mark_task_completed()` to track completion globally.

**Why I rejected it:** This would pollute shared task objects. If I regenerate the schedule tomorrow, the same task would incorrectly show as "not mandatory" because its global state was changed.

**How I verified:** Ran `main.py` test after making the change—saw Cat Feeding show as "optional" after completion, which violated the invariant. Created a comment explaining the fix and verified all tasks still showed as "MANDATORY" after completion.

---

## 4. Testing and Verification

**a. What you tested**

- **Task.is_mandatory()**: Daily/weekly frequency detection with last_completed dates
- **Task.mark_complete()**: Completion state tracking
- **Pet.add_task() & get_tasks()**: Task aggregation per pet
- **Owner.get_all_tasks()**: Aggregation across multiple pets
- **Scheduler.generate_daily_plan()**: Full pipeline ranking → fitting → reasoning
- **DailyPlan feasibility**: Schedule fits in available_time
- **Conflict detection**: Same-pet multi-tasking prevention

**Why important:** Core behaviors (mandatory detection, scheduling logic) break if wrong; UI won't matter if backend is broken.

**b. Confidence**

**Confidence level: 7/10**
- Core ranking/fitting logic works (verified in main.py with 6 tasks)
- Recurring task detection works (daily tasks correctly marked mandatory)
- Conflict detection runs without crashing
- Time-slot specificity not tested (currently set to 0 in add_task_to_schedule)
- Dependency ordering not tested (feature added but no unit test)
- Edge cases: circular dependencies, zero available time, empty pet list

**Edge cases to test next:**
- Circular task dependencies (A depends on B, B depends on A)
- Owner with zero available time
- Owner with no pets
- Recurring task with past completion date (7+ days ago for weekly)
- Multiple pets with overlapping preferred times

---

## 5. Reflection

**a. What went well**

**Most satisfied with:** The architecture separation of concerns
- Scheduler doesn't know HOW to mutate Owner; it calls methods
- DailyPlan doesn't mutate Task objects globally
- Owner aggregates Pet tasks cleanly
- Each class has ONE responsibility

This made debugging easy: when tests failed, I knew exactly where the issue was (not scattered across files).

**b. What you would improve**

1. **Specific time-slot assignment**: Currently `start_time_minutes` is simplified to 0. Should implement actual clock time scheduling (7am for walks, 5pm for dinner)
2. **Dependency testing**: Added topological sorting but no test coverage
3. **Multi-day planning**: Expand recurring tasks into week/month views before scheduling
4. **Preference learning**: Track which time windows owner actually uses; bias scheduling there

**c. Key takeaway**

**Good system design saves debugging time.** 

When I fixed the state mutation bug, it took 5 minutes because the architecture was clear: "DailyPlan owns task state, not shared Task objects." If I'd made Task globally mutable, that bug would have cascaded through 10 different methods and been a nightmare.

Lesson: Spend time on UML and relationships up front. The 20 minutes on design saved 2 hours of debugging.
