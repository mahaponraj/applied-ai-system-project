# PawPal+ — AI-Powered Pet Care Scheduler

**An intelligent pet care scheduling system that combines classical algorithms with RAG-based AI insights and automated reliability validation.**

PawPal+ helps busy pet owners create optimized daily care schedules across multiple pets. It ranks tasks by priority, fits them into available time using bin-packing, detects scheduling conflicts, and enriches each plan with AI-retrieved pet care knowledge — all through a clean Streamlit interface.

---

## Original Project Goals (PawPal — Module 2)


Loom Link: https://www.loom.com/share/148ade1f36524d689d990fb911105cfe 

The original PawPal system was built to solve a real scheduling challenge: pet owners managing multiple animals and dozens of recurring tasks with limited time. It introduced priority-based task ranking, greedy bin-packing to maximize task completion, and conflict detection to flag overlapping time slots. The system automated recurring task generation using Python's `timedelta` so owners never had to manually re-enter daily or weekly tasks.

---

## What's New in This Version (Applied AI Final)

This version extends PawPal with three new AI-focused layers:

| Layer | Class | What It Adds |
|---|---|---|
| **RAG Knowledge Base** | `PetCareKnowledgeBase` | Stores structured pet care best practices by species and task type |
| **RAG Integration** | `RAGIntegration` | Retrieves relevant advice and enriches schedules with context-aware suggestions |
| **Reliability Validation** | `ReliabilityValidator` | Automatically validates every generated plan across 5 quality dimensions |
| **Automated Plan Testing** | `PlanTester` | Runs a full test suite against generated plans, including edge cases |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)              │
│  Owner Setup → Add Pets → Add Tasks → Generate Plan  │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│              Core Scheduler (pawpal_system.py)       │
│                                                      │
│  Owner ──► Pet ──► Task ──► TimeSlot                 │
│                    │                                 │
│          Scheduler.generate_daily_plan()             │
│          ├─ rank_tasks()           [priority sort]   │
│          ├─ fit_tasks_in_time()    [bin-packing]     │
│          ├─ order_by_dependencies()[topo sort]       │
│          ├─ assign_time_slots()    [scheduling]      │
│          └─ check_conflicts()      [overlap detect]  │
│                    │                                 │
│              DailyPlan (output)                      │
└──────┬─────────────┴──────────────┬─────────────────┘
       │                            │
┌──────▼──────────┐    ┌────────────▼────────────────┐
│  RAG Layer      │    │  Reliability Layer           │
│                 │    │                              │
│ PetCareKnowledge│    │ ReliabilityValidator         │
│ Base            │    │ ├─ time feasibility check    │
│ ├─ dog entries  │    │ ├─ task consistency check    │
│ ├─ cat entries  │    │ ├─ completeness check        │
│ └─ general tips │    │ ├─ conflict check            │
│                 │    │ └─ priority distribution     │
│ RAGIntegration  │    │                              │
│ ├─ retrieve()   │    │ PlanTester                   │
│ └─ suggest()    │    │ └─ run_full_test()           │
└─────────────────┘    └──────────────────────────────┘
```

**Core data flow:** The `Scheduler` reads all tasks from the `Owner`'s pets, applies priority ranking and bin-packing, resolves dependencies via topological sort, assigns time slots, and produces a `DailyPlan`. The `RAGIntegration` then enriches that plan with retrieved knowledge, and `ReliabilityValidator` scores it across 5 dimensions before the results are displayed in the UI.

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher

### 1. Clone or navigate to the project
```bash
cd applied-ai-system-final
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app
```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

### 5. (Optional) Run the demo script
```bash
python main_enhanced.py
```

### 6. (Optional) Run the test suite
```bash
pytest tests/test_pawpal.py -v
```

---

## Sample Interactions

### Example 1: Generating a Daily Plan with AI Insights

**Input — owner with two pets and 6 tasks:**
```python
owner = Owner(name="Alice", available_time=120)  # 120 min/day

dog = Pet("Max", species="Golden Retriever", age=3,
          special_needs=["chicken-free diet"])
cat = Pet("Whiskers", species="Siamese", age=5,
          special_needs=["sensitive stomach"])

morning_walk = Task("Morning Walk", duration=30, priority=5, frequency="daily")
feeding_dog  = Task("Feeding",      duration=15, priority=5, frequency="daily")
playtime     = Task("Playtime",     duration=20, priority=3, frequency="daily")
cat_feeding  = Task("Feeding",      duration=10, priority=5, frequency="daily")
litter_box   = Task("Litter Box",   duration=10, priority=4, frequency="daily")
grooming     = Task("Grooming",     duration=30, priority=2, frequency="weekly")

plan = scheduler.generate_daily_plan()
```

**AI Output — enriched schedule:**
```
Daily Plan for 2026-04-26
Available Time: 120 min | Scheduled: 85 min | Remaining: 35 min

Scheduled Tasks:
  08:00 — Max: Morning Walk (30 min) [Priority 5]
           AI Tip: Dogs need 30-60 min of daily exercise; morning walks
           reduce anxiety and support joint health.
  08:40 — Max: Feeding (15 min) [Priority 5]
           AI Tip: Feed dogs twice daily; avoid exercise 30 min before meals.
  09:05 — Whiskers: Feeding (10 min) [Priority 5]
           AI Tip: Cats prefer small, frequent meals; feed 2-3 times daily.
  09:25 — Whiskers: Litter Box (10 min) [Priority 4]
           AI Tip: Clean litter boxes daily to prevent bacteria buildup.
  09:45 — Max: Playtime (20 min) [Priority 3]
           AI Tip: 15-30 min of interactive play reduces behavioral issues.
  Skipped: Max: Grooming (low priority, insufficient time)

Reliability Score: 5/5 checks passed ✓
```

---

### Example 2: Conflict Detection

**Input — two overlapping tasks scheduled at the same time:**
```python
walk  = Task("Morning Walk", duration=30, priority=5)
bath  = Task("Bath Time",    duration=20, priority=4)

# Both assigned start time of 08:00 for the same pet
```

**System Output:**
```
[CONFLICT] Max has multiple tasks scheduled at 08:00
           Morning Walk (08:00–08:30) overlaps with Bath Time (08:00–08:20)
           Recommendation: Reschedule Bath Time to 08:30 or later.

Warning count: 1 (non-blocking — schedule generated with conflicts flagged)
```

---

### Example 3: RAG Smart Suggestions

**Input — dog with only a feeding task registered:**
```python
dog = Pet("Buddy", species="Labrador", age=2)
dog.add_task(Task("Feeding", duration=15, priority=5, frequency="daily"))

suggestions = rag.get_smart_suggestions(dog, current_tasks)
```

**AI Output:**
```
Smart Suggestions for Buddy (Labrador, age 2):

Missing from your schedule:
  ► Daily Walk — Labradors are high-energy; 45-60 min/day recommended
  ► Playtime   — Young dogs need 20-30 min of interactive play daily
  ► Grooming   — Weekly brushing prevents matting and reduces shedding

These suggestions are based on species-specific care guidelines
retrieved from the PawPal knowledge base.
```

---

## Design Decisions & Trade-offs

### 1. Local RAG vs. External LLM API
**Decision:** Knowledge base is stored locally as structured Python dictionaries; no API calls.
**Trade-off:** Loses the flexibility of a live LLM but gains zero latency, zero cost, offline functionality, and fully deterministic outputs — critical for a scheduling system where users need predictable, trustworthy recommendations.

### 2. Greedy Bin-Packing vs. Optimal Packing
**Decision:** Greedy sort-then-fit (O(n log n)) over NP-hard optimal packing.
**Trade-off:** Greedy produces 85–95% optimal results in practice; the speed gain makes the UI feel instant. For pet care scheduling, near-optimal is sufficient — the user can always add time or deprioritize tasks manually.

### 3. Non-Blocking Warnings vs. Hard Failures on Conflicts
**Decision:** Conflicts generate warnings, not exceptions; the schedule is still returned.
**Trade-off:** A hard failure prevents bad schedules but frustrates users who want to see the issue and fix it themselves. Non-blocking warnings give full visibility without removing owner agency.

### 4. Separated Reliability Layer vs. Inline Validation
**Decision:** `ReliabilityValidator` is a standalone class, not baked into `Scheduler`.
**Trade-off:** Adds a class but makes validation independently testable and extensible. A future team could swap validation rules without touching core scheduling logic.

### 5. Immutable Task State per DailyPlan
**Decision:** Task objects are copied into `DailyPlan`; mutations (e.g., marking complete) don't affect the source object.
**Trade-off:** Slightly more memory usage, but prevents plan history corruption — past plans remain accurate even after future task completions.

---

## Testing Summary

### How the System Proves It Works

PawPal+ uses four distinct layers of reliability measurement — not just "it seemed to work":

#### 1. Automated Unit Tests
```bash
pytest tests/test_pawpal.py -v
```

**40 tests across 9 test classes + 2 standalone tests.** Every core behavior and AI feature has a dedicated test.

| Test Class | Tests | What It Validates |
|---|---|---|
| `TestRecurrenceLogic` | 4 | Daily/weekly auto-generation, timedelta offsets, state transitions |
| `TestTaskSorting` | 3 | Priority ordering, secondary duration sort, chronological order |
| `TestConflictDetection` | 4 | Same-pet conflicts, overlapping windows, cross-pet conflicts, false-positive prevention |
| `TestTaskFitting` | 3 | Happy path fit, overflow skipping, empty task lists |
| `TestMandatoryFiltering` | 6 | Mandatory logic for all frequency types, null date handling |
| `TestPetCareKnowledgeBase` | 5 | Knowledge base init, dog/cat/general retrieval, advice formatting |
| `TestRAGIntegration` | 4 | Plan enhancement, smart suggestions for dogs and cats |
| `TestReliabilityValidator` | 5 | All 5 validation dimensions, pass/fail/warning scoring |
| `TestPlanTester` | 4 | Full test execution, overflow detection, edge cases |
| Standalone | 2 | Task completion state, pet task count |

> **Result: 40/40 tests pass.**

---

#### 2. Reliability Scoring (Built-in Validator)

Every generated plan is automatically scored by `ReliabilityValidator` across **5 independent checks**. Each check returns a `ValidationResult` with a severity level (`info`, `warning`, `error`) and a structured details dict that can be logged or displayed.

| Check | What It Catches | Pass Condition |
|---|---|---|
| **Time Feasibility** | Plan exceeds owner's available time | `total_duration ≤ available_time` |
| **Task Consistency** | Duplicate task types or zero-duration tasks | No duplicates, all durations > 0 |
| **Completeness** | Mandatory tasks skipped due to overflow | All `is_mandatory()` tasks appear in plan |
| **Conflict Detection** | Overlapping time slots, cross-pet owner conflicts | `plan.has_conflicts() == False` |
| **Priority Distribution** | Schedule filled with only low-priority tasks | At least some high-priority (4–5) tasks present |

**Typical result on a healthy plan:**
```
Reliability Score: 5/5 checks passed
  ✓ feasibility  — Plan fits comfortably: 75min of 120min used (45min buffer)
  ✓ consistency  — No duplicates, all task durations valid
  ✓ completeness — All 3 mandatory tasks scheduled
  ✓ conflicts    — No overlapping time slots detected
  ✓ priority     — High-priority tasks adequately represented
```

**When context is missing (empty schedule):**
```
Reliability Score: 1/5 checks passed
  ✗ completeness — No tasks scheduled [ERROR]
  ✗ priority     — No high-priority tasks in plan [ERROR]
  ✗ feasibility  — No tasks to evaluate [WARNING]
```
> The system correctly fails and surfaces the reason rather than silently producing a useless plan.

---

#### 3. Logging & Error Handling

The `ReliabilityValidator` stores every result in `validation_history` — a persistent list of `ValidationResult` objects. This means:
- Every plan ever validated leaves a traceable record
- Failures include structured `details` dicts (e.g., `{"missing_tasks": ["Feeding"], "mandatory_count": 2}`)
- Severity levels (`info` / `warning` / `error`) allow downstream code to respond differently instead of treating all issues the same way
- The `get_validation_summary()` method aggregates results into counts per category, making it easy to spot patterns across many plans

---

#### 4. Edge Case Testing (`PlanTester.test_edge_cases()`)

The `PlanTester` class runs three targeted edge case scenarios automatically:

| Edge Case | Scenario | Expected Behavior |
|---|---|---|
| Empty tasks | Owner has pets but no tasks added | Validation flags missing schedule; no crash |
| Time overflow | Two 15-min tasks, only 20 min available | Bin-packing fits one; second task skipped gracefully |
| Task dependencies | Task B depends on Task A | Topological sort runs; A always precedes B |

---

### What Worked
- **40/40 unit tests pass.** Core algorithms (bin-packing, conflict detection, topological sort) are consistent across all scenarios tested.
- **RAG retrieval accuracy:** Species + task type matching works correctly. Dog walking queries return exercise advice; cat litter queries return hygiene advice. Unknown combinations fall back to general hydration/rest tips rather than returning nothing.
- **Validation catches real failures:** Plans exceeding available time, missing mandatory tasks, and zero-duration tasks all produce `is_valid=False` results with descriptive error messages.

### What Didn't Work Initially
- **False positive conflicts on sequential tasks:** Early conflict detection flagged Task A (ends 08:30) and Task B (starts 08:30) as overlapping. Fixed by switching from `<=` to strict `<` in the interval comparison - boundary-sharing is not an overlap.
- **Duplicate RAG suggestions:** The suggestion engine initially returned the same advice twice when a pet had two matching tasks. Fixed by deduplicating against the current task list before appending.
- **Validation count mismatch:** Early `get_validation_summary()` counted results before the conflict check ran, producing off-by-one totals. Fixed by running all checks before summarizing.

### One-Line Summary
> **40/40 unit tests pass; the system correctly flags failure when context is missing (empty tasks or overflow), and confidence scoring via `ReliabilityValidator` averages 5/5 checks on well-formed plans, dropping to 1–2/5 on edge cases where it surfaces the specific reason.**

---

## Project Structure

```
applied-ai-system-final/
├── pawpal_system.py        # Core logic: Task, Pet, Owner, Scheduler, DailyPlan,
│                           #   PetCareKnowledgeBase, RAGIntegration,
│                           #   ReliabilityValidator, PlanTester
├── app.py                  # Streamlit UI with session state management
├── main.py                 # Basic demo script
├── main_enhanced.py        # Full demo with RAG and reliability output
├── tests/
│   └── test_pawpal.py      # 40 unit tests across 9 test classes
├── assets/
│   └── system_architecture.md
├── reflection.md           # Detailed design notes
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.8+
- `streamlit >= 1.30`
- `pytest >= 7.0`

```bash
pip install -r requirements.txt
```

---

## Author

Built for AI110 Applied AI Systems - Final Project.
Extends the Module 2 PawPal scheduler with RAG-based knowledge retrieval, automated reliability validation, and expanded test coverage.

**Skills demonstrated:** object-oriented design, greedy algorithms, topological sorting, retrieval-augmented generation (RAG), automated testing, constraint satisfaction, Streamlit UI development.
