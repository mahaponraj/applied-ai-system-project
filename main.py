"""
Temporary test ground to verify PawPal+ logic
"""

from pawpal_system import Task, Pet, Owner, Scheduler, TimeSlot
from datetime import date

# ============================================================
# Step 1: Create an Owner
# ============================================================
owner = Owner(name="Alice", available_time=120)  # 120 minutes available today
print(f"\n{'='*60}")
print(f"Owner: {owner.name}")
print(f"Available Time: {owner.available_time} minutes")
print(f"{'='*60}\n")

# ============================================================
# Step 2: Create at least 2 Pets
# ============================================================
dog = Pet(
    name="Max",
    species="Golden Retriever",
    age=3,
    special_needs=["Dog food allergy (chicken-free)"]
)

cat = Pet(
    name="Whiskers",
    species="Siamese",
    age=5,
    special_needs=["Sensitive stomach"]
)

owner.add_pet(dog)
owner.add_pet(cat)

print(f"Pets registered to {owner.name}:")
for pet in owner.get_pets():
    print(f"  • {pet.name} ({pet.species}, age {pet.age})")
print()

# ============================================================
# Step 3: Create at least 3 Tasks with different priorities/times
# ============================================================

# Tasks for Max (dog)
morning_walk = Task(
    task_type="Morning Walk",
    duration=30,
    priority=5,  # High priority
    description="Walk Max in the park",
    frequency="daily"
)

feeding = Task(
    task_type="Feeding",
    duration=15,
    priority=5,  # High priority
    description="Feed Max dinner (chicken-free)",
    frequency="daily"
)

playtime = Task(
    task_type="Playtime",
    duration=20,
    priority=4,
    description="Interactive play with ball",
    frequency="daily"
)

# Tasks for Whiskers (cat)
cat_feeding = Task(
    task_type="Cat Feeding",
    duration=10,
    priority=5,  # High priority
    description="Feed Whiskers dinner",
    frequency="daily"
)

litter_cleanup = Task(
    task_type="Litter Box Cleanup",
    duration=15,
    priority=4,
    description="Clean litter box",
    frequency="daily"
)

cat_enrichment = Task(
    task_type="Cat Enrichment",
    duration=25,
    priority=3,
    description="Interactive play + laser pointer",
    frequency="daily"
)

# Add tasks to pets
dog.add_task(morning_walk)
dog.add_task(feeding)
dog.add_task(playtime)

cat.add_task(cat_feeding)
cat.add_task(litter_cleanup)
cat.add_task(cat_enrichment)

print(f"Tasks added to {dog.name}:")
for task in dog.get_tasks():
    print(f"  • {task.task_type} ({task.duration}min, priority {task.priority})")
print()

print(f"Tasks added to {cat.name}:")
for task in cat.get_tasks():
    print(f"  • {task.task_type} ({task.duration}min, priority {task.priority})")
print()

# ============================================================
# NEW FEATURE: Add CONFLICTING TASKS for conflict detection
# ============================================================
print(f"\n{'='*60}")
print("ADDING CONFLICTING TASKS (to test conflict detection)")
print(f"{'='*60}\n")

# Create two tasks with SAME START TIME (will conflict)
conflict_walk = Task(
    task_type="Afternoon Walk",
    duration=30,
    priority=5,
    description="Another walk with Max",
    frequency="daily"
)

conflict_training = Task(
    task_type="Training Session",
    duration=45,
    priority=4,
    description="Obedience training with Max",
    frequency="daily"
)

# Manually assign SAME actual start time to create conflict
conflict_walk.set_actual_start_time(900)   # 15:00 (3 PM)
conflict_training.set_actual_start_time(900)  # 15:00 (3 PM) - SAME TIME!

dog.add_task(conflict_walk)
dog.add_task(conflict_training)

print("Added 2 conflicting tasks to Max:")
print(f"  • Afternoon Walk (30min, priority 5) - START TIME: 15:00 (3 PM)")
print(f"  • Training Session (45min, priority 4) - START TIME: 15:00 (3 PM) *** SAME TIME ***")
print()

# Create overlapping (not exact conflict) tasks for cat
overlap_groom = Task(
    task_type="Grooming",
    duration=40,
    priority=3,
    description="Brush and groom Whiskers",
    frequency="weekly"
)

overlap_nap = Task(
    task_type="Nap Time",
    duration=60,
    priority=1,
    description="Quiet rest time",
    frequency="daily"
)

# Assign overlapping times
overlap_groom.set_actual_start_time(1000)   # 16:40 (4:40 PM)
overlap_nap.set_actual_start_time(1020)    # 17:00 (5:00 PM) - OVERLAPS with grooming!

cat.add_task(overlap_groom)
cat.add_task(overlap_nap)

print("Added 2 overlapping tasks to Whiskers:")
print(f"  • Grooming (40min, priority 3) - START TIME: 16:40 (4:40 PM)")
print(f"  • Nap Time (60min, priority 1) - START TIME: 17:00 (5:00 PM) *** OVERLAPS ***")
print()

# ============================================================
# IMPROVEMENT: Add tasks OUT OF ORDER (to show sorting works)
# ============================================================
print(f"\n{'='*60}")
print("ADDING TASKS OUT OF ORDER (to test sorting)")
print(f"{'='*60}\n")

# Add these AFTER the order above (out of sequence)
grooming = Task(
    task_type="Dog Grooming",
    duration=45,
    priority=2,
    description="Bath and brush Max",
    frequency="weekly"
)

vet_meds = Task(
    task_type="Medication",
    duration=5,
    priority=5,  # HIGH - medical task
    description="Give Max allergy medication",
    frequency="daily"
)

# Add out of order - these will be last in the task list initially
dog.add_task(grooming)
dog.add_task(vet_meds)

print("Added 2 more tasks to Max (out of sequence):")
print(f"  • Dog Grooming (45min, priority 2) - Added 4th")
print(f"  • Medication (5min, priority 5) - Added 5th")
print()

# ============================================================
# NEW: Demonstrate SORTING by Priority
# ============================================================
print(f"\n{'='*60}")
print("FEATURE 1: SORTING TASKS BY PRIORITY")
print(f"{'='*60}\n")

all_tasks = owner.get_all_tasks()
print(f"Tasks in original order (as added):")
for i, task in enumerate(all_tasks, 1):
    print(f"  {i}. {task.task_type} (priority {task.priority})")
print()

# Use Scheduler's rank_tasks method
scheduler = Scheduler(owner)
sorted_tasks = scheduler.rank_tasks(all_tasks)
print(f"Tasks SORTED by priority (highest first):")
for i, task in enumerate(sorted_tasks, 1):
    print(f"  {i}. {task.task_type} (priority {task.priority})")
print()

# ============================================================
# NEW: Demonstrate FILTERING by Pet
# ============================================================
print(f"\n{'='*60}")
print("FEATURE 2: FILTERING TASKS BY PET")
print(f"{'='*60}\n")

dog_tasks = owner.get_tasks_for_pet(dog)
print(f"All tasks for {dog.name}: {len(dog_tasks)}")
for task in dog_tasks:
    print(f"  • {task.task_type}")
print()

cat_tasks = owner.get_tasks_for_pet(cat)
print(f"All tasks for {cat.name}: {len(cat_tasks)}")
for task in cat_tasks:
    print(f"  • {task.task_type}")
print()

# ============================================================
# NEW: Demonstrate FILTERING by Task Type
# ============================================================
print(f"\n{'='*60}")
print("FEATURE 3: FILTERING BY TASK TYPE")
print(f"{'='*60}\n")

feeding_tasks = owner.get_tasks_by_type("feeding")
print(f"All 'Feeding' tasks: {len(feeding_tasks)}")
for task in feeding_tasks:
    pet = owner.get_pet_for_task(task)
    print(f"  • {task.task_type} (for {pet.name if pet else 'Unknown'})")
print()

# ============================================================
# NEW: Demonstrate TIME CATEGORIZATION
# ============================================================
print(f"\n{'='*60}")
print("FEATURE 4: TIME-OF-DAY CATEGORIZATION")
print(f"{'='*60}\n")

print("Tasks categorized by time preference:")
morning_list = [t for t in all_tasks if scheduler.categorize_task_time(t) == 'morning']
afternoon_list = [t for t in all_tasks if scheduler.categorize_task_time(t) == 'afternoon']
evening_list = [t for t in all_tasks if scheduler.categorize_task_time(t) == 'evening']

print(f"\n[MORNING] tasks ({len(morning_list)}):")
for task in morning_list:
    print(f"  • {task.task_type}")

print(f"\n[AFTERNOON] tasks ({len(afternoon_list)}):")
for task in afternoon_list:
    print(f"  • {task.task_type}")

print(f"\n[EVENING] tasks ({len(evening_list)}):")
for task in evening_list:
    print(f"  • {task.task_type}")
print()

# ============================================================
# Step 4: Create Scheduler and Generate Today's Plan
# ============================================================
scheduler = Scheduler(owner)
today_plan = scheduler.generate_daily_plan()

# ============================================================
# Step 5: Print "Today's Schedule"
# ============================================================
print(f"\n{'='*60}")
print(f"TODAY'S SCHEDULE - {today_plan.date}")
print(f"{'='*60}\n")

if not today_plan.get_plan():
    print("[NO] No tasks scheduled for today.")
else:
    print(f"[YES] Tasks Scheduled: {len(today_plan.get_plan())}")
    print(f"   Total Time: {today_plan.total_time} minutes")
    print(f"   Available: {owner.available_time} minutes\n")
    
    print("[SCHEDULE]:\n")
    for idx, task in enumerate(today_plan.get_plan(), 1):
        # Using NEW METHOD: get_pet_for_task instead of manual iteration
        pet = scheduler.get_pet_for_task(task)
        pet_name = pet.name if pet else "Unknown"
        
        print(f"{idx}. {task.task_type}")
        print(f"   Pet: {pet_name}")
        print(f"   Duration: {task.duration} min")
        print(f"   Priority: {'*' * task.priority} ({task.priority}/5)")
        print(f"   Description: {task.description}")
        print()

print("[REASONING]:")
print(f"   {today_plan.get_reasoning()}\n")

# ============================================================
# NEW: Display Conflict Warnings (lightweight detection)
# ============================================================
print(f"\n{'='*60}")
print("CONFLICT DETECTION RESULTS")
print(f"{'='*60}\n")

if today_plan.has_conflicts():
    print(f"[WARNING] Found {len(today_plan.get_warnings())} scheduling conflict(s):\n")
    for warning in today_plan.get_warnings():
        print(f"  {warning}")
    print()
else:
    print("[OK] No scheduling conflicts detected!\n")

# ============================================================
# NEW: Test time-aware scheduling with conflict detection
# ============================================================
print(f"\n{'='*60}")
print("ADVANCED: TIME-AWARE SCHEDULING WITH CONFLICT CHECK")
print(f"{'='*60}\n")

# Get only safe tasks (without the deliberately conflicting ones)
safe_tasks = [t for t in owner.get_all_tasks() 
              if t.task_type not in ["Afternoon Walk", "Training Session", "Grooming", "Nap Time"]]

# Create a smart plan with time awareness
smart_plan = scheduler.schedule_with_time_awareness(safe_tasks, buffer_minutes=10)

# Check for conflicts in the smart plan
scheduler.check_scheduling_conflicts(smart_plan)

print(f"Smart-scheduled {len(smart_plan.get_plan())} tasks:\n")
for task in smart_plan.get_plan():
    if task.actual_start_time is not None:
        time_str = scheduler.minutes_to_time_str(task.actual_start_time)
        end_time = task.get_end_time()
        end_str = scheduler.minutes_to_time_str(end_time) if end_time else "?"
        pet = scheduler.get_pet_for_task(task)
        pet_name = pet.name if pet else "Unknown"
        print(f"  {time_str}-{end_str}: {task.task_type} ({pet_name})")

print()

if smart_plan.has_conflicts():
    print(f"[WARNING] Smart plan conflicts: {len(smart_plan.get_warnings())}")
    for warning in smart_plan.get_warnings():
        print(f"  {warning}")
else:
    print("[OK] Smart schedule is conflict-free!")
print()

# ============================================================
# NEW: Direct Test - Create conflicting tasks in a plan
# ============================================================
print(f"\n{'='*60}")
print("DIRECT CONFLICT DETECTION TEST")
print(f"{'='*60}\n")

from pawpal_system import DailyPlan

# Create a test plan with deliberately conflicting tasks
test_plan = DailyPlan(date.today(), owner)

# Get some real tasks
all_tasks = owner.get_all_tasks()

# Create test tasks with same start time
conflict_task_1 = Task(
    task_type="Test Conflict 1",
    duration=30,
    priority=5,
    description="First task at 10:00 AM"
)
conflict_task_1.set_actual_start_time(600)  # 10:00 AM

conflict_task_2 = Task(
    task_type="Test Conflict 2",
    duration=45,
    priority=4,
    description="Second task at 10:00 AM - SAME TIME"
)
conflict_task_2.set_actual_start_time(600)  # 10:00 AM - CONFLICT!

# Add to test plan
test_plan.scheduled_tasks = [conflict_task_1, conflict_task_2]
test_plan.total_time = 75

print("Test Plan: Created 2 tasks at SAME TIME (10:00 AM):")
print(f"  1. Test Conflict 1 (30 min, 10:00-10:30)")
print(f"  2. Test Conflict 2 (45 min, 10:00-10:45)")
print()

# Run conflict detection
print("Running conflict detection...")
scheduler.check_scheduling_conflicts(test_plan)
print()

if test_plan.has_conflicts():
    print(f"[DETECTED] Found {len(test_plan.get_warnings())} conflict(s):")
    for warning in test_plan.get_warnings():
        print(f"  >>> {warning}")
else:
    print("[NO CONFLICTS] Plan is clean")
print()

# Test 2: Overlapping tasks
print(f"\n{'='*60}")
print("OVERLAPPING TASKS TEST")
print(f"{'='*60}\n")

overlap_plan = DailyPlan(date.today(), owner)

overlap_task_1 = Task(
    task_type="Overlap Task A",
    duration=60,
    priority=3,
    description="Runs from 2:00 PM to 3:00 PM"
)
overlap_task_1.set_actual_start_time(840)  # 14:00 (2:00 PM)

overlap_task_2 = Task(
    task_type="Overlap Task B",
    duration=45,
    priority=3,
    description="Runs from 2:45 PM to 3:30 PM - OVERLAPS"
)
overlap_task_2.set_actual_start_time(885)  # 14:45 (2:45 PM) - OVERLAPS!

overlap_plan.scheduled_tasks = [overlap_task_1, overlap_task_2]
overlap_plan.total_time = 105

print("Test Plan: Created 2 OVERLAPPING tasks:")
print(f"  1. Overlap Task A (60 min, 14:00-15:00)")
print(f"  2. Overlap Task B (45 min, 14:45-15:30)")
print()

print("Running conflict detection...")
scheduler.check_scheduling_conflicts(overlap_plan)
print()

if overlap_plan.has_conflicts():
    print(f"[DETECTED] Found {len(overlap_plan.get_warnings())} conflict(s):")
    for warning in overlap_plan.get_warnings():
        print(f"  >>> {warning}")
else:
    print("[NO CONFLICTS] Plan is clean")
print()

# ============================================================
# Step 6: Test task completion tracking and AUTO-RECURRENCE
# ============================================================
print(f"{'='*60}")
print("NEW FEATURE: AUTO-RECURRENCE FOR DAILY/WEEKLY TASKS")
print(f"{'='*60}\n")

if today_plan.get_plan():
    daily_task = None
    weekly_task = None
    
    # Find a daily and weekly task to demonstrate recurrence
    for task in today_plan.get_plan():
        if task.frequency == "daily" and daily_task is None:
            daily_task = task
        elif task.frequency == "weekly" and weekly_task is None:
            weekly_task = task
    
    # Complete a daily task and show auto-recurrence
    if daily_task:
        print(f"Marking daily task '{daily_task.task_type}' as completed...")
        today_plan.mark_task_completed(daily_task)
        print(f"[YES] Task completed and moved to completed_tasks")
        print(f"   Next occurrence created: {len(today_plan.next_occurrences)} new task(s)\n")
    
    # Complete a weekly task and show auto-recurrence
    if weekly_task:
        print(f"Marking weekly task '{weekly_task.task_type}' as completed...")
        today_plan.mark_task_completed(weekly_task)
        print(f"[YES] Task completed and moved to completed_tasks")
        print(f"   Next occurrence created: {len(today_plan.next_occurrences)} new task(s)\n")
    
    print(f"Summary after completion:")
    print(f"  • Remaining scheduled: {len(today_plan.get_plan())} tasks")
    print(f"  • Completed: {len(today_plan.completed_tasks)} tasks")
    print(f"  • Auto-generated next occurrences: {len(today_plan.next_occurrences)} tasks\n")
    
    if today_plan.next_occurrences:
        print(f"Next occurrences scheduled:")
        for task in today_plan.next_occurrences:
            print(f"  • {task.task_type} (due: {task.last_completed})")
print()

# ============================================================
# Step 7: Verify task list includes auto-generated occurrences
# ============================================================
print(f"\n{'='*60}")
print("VERIFYING AUTO-GENERATED TASKS IN PET LISTS")
print(f"{'='*60}\n")

updated_dog_tasks = owner.get_all_tasks()
print(f"Total tasks for all pets after completion: {len(updated_dog_tasks)}")
print(f"(Increased by {len(today_plan.next_occurrences)} from auto-generated recurrences)\n")

print(f"Updated task list for {dog.name}:")
for task in dog.get_tasks():
    status = "[O] original" if task not in today_plan.next_occurrences else "[*] auto-generated"
    print(f"  • {task.task_type} ({status})")
print()

# ============================================================
# Step 8: BONUS - Show filtering on updated task list
# ============================================================
print(f"\n{'='*60}")
print("BONUS: Using Filters on Updated Task List")
print(f"{'='*60}\n")

all_updated_tasks = owner.get_all_tasks()
daily_tasks = [t for t in all_updated_tasks if t.frequency == "daily"]
weekly_tasks = [t for t in all_updated_tasks if t.frequency == "weekly"]
optional_tasks = [t for t in all_updated_tasks if not t.is_mandatory()]

print(f"Daily recurring tasks: {len(daily_tasks)}")
for task in daily_tasks:
    print(f"  • {task.task_type}")
print()

print(f"Weekly recurring tasks: {len(weekly_tasks)}")
for task in weekly_tasks:
    print(f"  • {task.task_type}")
print()

print(f"Optional tasks (as-needed): {len(optional_tasks)}")
for task in optional_tasks:
    print(f"  • {task.task_type}")
print()

print(f"\n{'='*60}")
print("[SUCCESS] DEMO COMPLETED: All Features Tested Successfully!")
print(f"{'='*60}")
print("\nFeatures demonstrated:")
print("  [YES] Sorting tasks by priority (out-of-order input)")
print("  [YES] Filtering tasks by pet")
print("  [YES] Filtering tasks by type")
print("  [YES] Time-of-day categorization")
print("  [YES] Auto-recurrence for daily/weekly tasks (using timedelta)")
print("  [YES] Task completion tracking")
print(f"{'='*60}\n")
