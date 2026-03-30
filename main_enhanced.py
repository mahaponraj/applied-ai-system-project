"""
Temporary test ground to verify PawPal+ logic with new improvements
"""

from pawpal_system import Task, Pet, Owner, Scheduler, TimeSlot
from datetime import date

# ============================================================
# Step 1: Create an Owner
# ============================================================
owner = Owner(name="Alice", available_time=300)  # 300 minutes available today
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
# Step 3: Create Tasks with time-of-day preferences
# ============================================================

# Define time slots
morning_slot = TimeSlot(start_time=420, end_time=720, label="morning")
afternoon_slot = TimeSlot(start_time=720, end_time=1020, label="afternoon")
evening_slot = TimeSlot(start_time=1020, end_time=1320, label="evening")

# Tasks for Max (dog)
morning_walk = Task(
    task_type="Morning Walk",
    duration=30,
    priority=5,
    description="Walk Max in the park",
    frequency="daily",
    preferred_times=[morning_slot]
)

feeding = Task(
    task_type="Feeding",
    duration=15,
    priority=5,
    description="Feed Max dinner (chicken-free)",
    frequency="daily",
    preferred_times=[evening_slot]
)

playtime = Task(
    task_type="Playtime",
    duration=20,
    priority=4,
    description="Interactive play with ball",
    frequency="daily",
    preferred_times=[afternoon_slot]
)

# Tasks for Whiskers (cat)
cat_feeding = Task(
    task_type="Cat Feeding",
    duration=10,
    priority=5,
    description="Feed Whiskers dinner",
    frequency="daily",
    preferred_times=[evening_slot]
)

litter_cleanup = Task(
    task_type="Litter Box Cleanup",
    duration=15,
    priority=4,
    description="Clean litter box",
    frequency="daily",
    preferred_times=[afternoon_slot]
)

cat_enrichment = Task(
    task_type="Cat Enrichment",
    duration=25,
    priority=3,
    description="Interactive play + laser pointer",
    frequency="daily",
    preferred_times=[evening_slot]
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
# Step 4: Demonstrate NEW FEATURE: Task Filtering
# ============================================================
print(f"\n{'='*60}")
print("NEW FEATURE: Task Filtering by Pet")
print(f"{'='*60}\n")

print(f"Mandatory tasks for {dog.name}:")
dog_mandatory = owner.get_tasks_for_pet(dog, status="mandatory")
for task in dog_mandatory:
    print(f"  • {task.task_type}")
print()

print(f"Mandatory tasks for {cat.name}:")
cat_mandatory = owner.get_tasks_for_pet(cat, status="mandatory")
for task in cat_mandatory:
    print(f"  • {task.task_type}")
print()

# ============================================================
# Step 5: Demonstrate NEW FEATURE: Task Type Filtering
# ============================================================
print(f"\n{'='*60}")
print("NEW FEATURE: Task Type Filtering")
print(f"{'='*60}\n")

feeding_tasks = owner.get_tasks_by_type("feeding")
print(f"All 'Feeding' type tasks: {len(feeding_tasks)}")
for task in feeding_tasks:
    pet = owner.get_pet_for_task(task)
    print(f"  • {task.task_type} (for {pet.name if pet else 'Unknown'})")
print()

# ============================================================
# Step 6: Create Scheduler and Generate Today's Plan
# ============================================================
scheduler = Scheduler(owner)

# Demonstrate recurring task expansion
print(f"\n{'='*60}")
print("NEW FEATURE: Recurring Task Expansion (7 days)")
print(f"{'='*60}\n")

all_tasks = owner.get_all_tasks()
expanded = scheduler.expand_recurring_tasks(all_tasks, days_ahead=3)
print(f"Original tasks: {len(all_tasks)}")
print(f"Expanded across 3 days: {len(expanded)}")
print(f"Sample expanded tasks:")
for task in expanded[:4]:
    print(f"  • {task.task_type}")
print()

# Generate standard daily plan
today_plan = scheduler.generate_daily_plan()

# ============================================================
# Step 7: Print "Today's Schedule" with improved display
# ============================================================
print(f"\n{'='*60}")
print(f"TODAY'S SCHEDULE - {today_plan.date}")
print(f"{'='*60}\n")

if not today_plan.get_plan():
    print("❌ No tasks scheduled for today.")
else:
    print(f"✅ Tasks Scheduled: {len(today_plan.get_plan())}")
    print(f"   Total Time: {today_plan.total_time} minutes")
    print(f"   Available: {owner.available_time} minutes\n")
    
    print("📋 SCHEDULE:\n")
    for idx, task in enumerate(today_plan.get_plan(), 1):
        # Use NEW METHOD: get_pet_for_task instead of manual iteration
        pet = scheduler.get_pet_for_task(task)
        pet_name = pet.name if pet else "Unknown"
        
        # Show time categorization
        time_category = scheduler.categorize_task_time(task)
        
        print(f"{idx}. {task.task_type}")
        print(f"   Pet: {pet_name}")
        print(f"   Duration: {task.duration} min")
        print(f"   Priority: {'⭐' * task.priority} ({task.priority}/5)")
        print(f"   Time Preference: {time_category}")
        print(f"   Description: {task.description}")
        print()

print("📝 REASONING:")
print(f"   {today_plan.get_reasoning()}\n")

# ============================================================
# Step 8: NEW FEATURE: Time-Aware Scheduling
# ============================================================
print(f"\n{'='*60}")
print("NEW FEATURE: Smart Time-Slot Assignment")
print(f"{'='*60}\n")

# Get mandatory tasks and schedule with time awareness
mandatory = [t for t in owner.get_all_tasks() if t.is_mandatory()]
smart_plan = scheduler.schedule_with_time_awareness(mandatory, buffer_minutes=10)

print(f"Smart-scheduled {len(smart_plan.get_plan())} tasks with time awareness:\n")
for task in smart_plan.get_plan():
    if task.actual_start_time is not None:
        time_str = scheduler.minutes_to_time_str(task.actual_start_time)
        end_time = task.get_end_time()
        end_str = scheduler.minutes_to_time_str(end_time) if end_time else "?"
        print(f"  {time_str}-{end_str}: {task.task_type} ({task.duration} min)")
print()

# ============================================================
# Step 9: NEW FEATURE: Conflict Detection
# ============================================================
print(f"\n{'='*60}")
print("NEW FEATURE: Time Conflict Detection")
print(f"{'='*60}\n")

conflicts = scheduler.detect_time_conflicts(smart_plan.get_plan())
if conflicts:
    print(f"⚠️  Found {len(conflicts)} conflict(s):")
    for task1, task2 in conflicts:
        print(f"   ✗ {task1.task_type} vs {task2.task_type}")
else:
    print("✅ No time conflicts detected!")
print()

# ============================================================
# Step 10: Test task completion tracking
# ============================================================
print(f"\n{'='*60}")
print("TESTING TASK COMPLETION & ANALYTICS")
print(f"{'='*60}\n")

if today_plan.get_plan():
    first_task = today_plan.get_plan()[0]
    second_task = today_plan.get_plan()[1] if len(today_plan.get_plan()) > 1 else None
    
    print(f"Marking '{first_task.task_type}' as completed...")
    today_plan.mark_task_completed(first_task)
    
    if second_task:
        print(f"Marking '{second_task.task_type}' as completed...")
        today_plan.mark_task_completed(second_task)
    
    print(f"\n✅ Completion Percentage: {today_plan.get_completion_percentage():.1f}%")
    print(f"   Remaining: {len(today_plan.get_plan())} tasks")
    print(f"   Completed: {len(today_plan.completed_tasks)} tasks\n")

# ============================================================
# Step 11: NEW FEATURE: Status Filtering & Analytics
# ============================================================
print(f"\n{'='*60}")
print("NEW FEATURE: Task Status Filtering & Analytics")
print(f"{'='*60}\n")

print(f"Scheduled tasks: {len(today_plan.get_tasks_by_status('scheduled'))}")
print(f"Completed tasks: {len(today_plan.get_tasks_by_status('completed'))}")
print(f"Skipped tasks: {len(today_plan.get_tasks_by_status('skipped'))}")
print()

# Calculate with buffers
total_with_buffers = today_plan.calculate_schedule_with_buffers(buffer_minutes=10)
print(f"Total time (with 10-min buffers): {total_with_buffers} minutes\n")

# ============================================================
# Step 12: Verify Owner can access all tasks
# ============================================================
print(f"\n{'='*60}")
print("TESTING OWNER.GET_ALL_TASKS()")
print(f"{'='*60}\n")

all_tasks = owner.get_all_tasks()
print(f"Total tasks across all pets: {len(all_tasks)}\n")
print("All tasks:")
for task in all_tasks:
    mandatory = "✓ MANDATORY" if task.is_mandatory() else "○ optional"
    time_category = scheduler.categorize_task_time(task)
    print(f"  • {task.task_type} - {mandatory} ({time_category})")

print(f"\n{'='*60}")
print("✨ Enhanced test with all improvements completed successfully!")
print(f"{'='*60}\n")
