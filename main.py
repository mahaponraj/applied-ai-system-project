"""
Temporary test ground to verify PawPal+ logic
"""

from pawpal_system import Task, Pet, Owner, Scheduler
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
    print("❌ No tasks scheduled for today.")
else:
    print(f"✅ Tasks Scheduled: {len(today_plan.get_plan())}")
    print(f"   Total Time: {today_plan.total_time} minutes")
    print(f"   Available: {owner.available_time} minutes\n")
    
    print("📋 SCHEDULE:\n")
    for idx, task in enumerate(today_plan.get_plan(), 1):
        pet_name = None
        for pet in owner.get_pets():
            if task in pet.get_tasks():
                pet_name = pet.name
                break
        
        print(f"{idx}. {task.task_type}")
        print(f"   Pet: {pet_name}")
        print(f"   Duration: {task.duration} min")
        print(f"   Priority: {'⭐' * task.priority} ({task.priority}/5)")
        print(f"   Description: {task.description}")
        print()

print("📝 REASONING:")
print(f"   {today_plan.get_reasoning()}\n")

# ============================================================
# Step 6: Test task completion tracking
# ============================================================
print(f"{'='*60}")
print("TESTING TASK COMPLETION")
print(f"{'='*60}\n")

if today_plan.get_plan():
    first_task = today_plan.get_plan()[0]
    print(f"Marking '{first_task.task_type}' as completed in today's plan...")
    today_plan.mark_task_completed(first_task)
    print(f"✅ Task moved to completed_tasks\n")
    
    print(f"Remaining scheduled tasks: {len(today_plan.get_plan())}")
    print(f"Completed tasks: {len(today_plan.completed_tasks)}\n")
    print(f"NOTE: Original Task object is NOT modified (still marked as mandatory for future checks)\n")

# ============================================================
# Step 7: Verify Owner can access all tasks
# ============================================================
print(f"{'='*60}")
print("TESTING OWNER.GET_ALL_TASKS()")
print(f"{'='*60}\n")

all_tasks = owner.get_all_tasks()
print(f"Total tasks across all pets: {len(all_tasks)}\n")
print("All tasks:")
for task in all_tasks:
    mandatory = "✓ MANDATORY" if task.is_mandatory() else "○ optional"
    print(f"  • {task.task_type} - {mandatory}")

print(f"\n{'='*60}")
print("✨ Test completed successfully!")
print(f"{'='*60}\n")
