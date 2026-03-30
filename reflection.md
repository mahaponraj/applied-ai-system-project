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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**
- Describe one tradeoff your scheduler makes.
The scheduler implements a round-robin scheduling with time quantums, which trades off between strict fairness (equal CPU time for all processes) and responsiveness (quick response to high-priority or I/O-bound tasks)

- Why is that tradeoff reasonable for this scenario?
1. **Balanced Approach**: Round-robin ensures no process starves indefinitely while maintaining reasonable responsiveness for interactive tasks through appropriate time quantum selection.

2. **Predictability**: All processes receive guaranteed CPU time within a predictable interval, making system behavior more deterministic and fair for batch processing scenarios.

3. **Simplicity**: Easier to implement and understand compared to complex priority-based schemes, reducing maintenance overhead and potential bugs.

4. **Practical Performance**: For the typical course scenario (educational context with moderate workloads), this tradeoff provides acceptable performance without the complexity of sophisticated scheduling algorithms like multi-level feedback queues.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
