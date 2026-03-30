import pytest
from datetime import date, timedelta
from pawpal_system import Pet, Task, Owner, Scheduler, DailyPlan, TimeSlot


# ============================================================
# CORE BEHAVIOR 1: Task Completion & Recurrence Logic
# ============================================================

class TestRecurrenceLogic:
    """Test automatic task recurrence when daily/weekly tasks are completed."""
    
    def test_daily_task_creates_next_occurrence(self):
        """Verify that marking a daily task complete creates next day's occurrence."""
        pet = Pet("Buddy", "dog", 5)
        daily_task = Task("Feed breakfast", duration=15, frequency="daily")
        daily_task.last_completed = date.today() - timedelta(days=1)
        pet.add_task(daily_task)
        
        owner = Owner("Alice", 240)
        owner.add_pet(pet)
        
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(daily_task, 480)
        
        # Mark task as completed
        plan.mark_task_completed(daily_task)
        
        # Should have created a next occurrence
        assert len(plan.next_occurrences) == 1
        assert plan.next_occurrences[0].frequency == "daily"
        assert plan.next_occurrences[0].task_type == "Feed breakfast"
    
    def test_weekly_task_creates_next_occurrence_7_days_later(self):
        """Verify weekly task creates occurrence 7 days later."""
        pet = Pet("Max", "cat", 3)
        weekly_task = Task("Grooming", duration=30, frequency="weekly")
        weekly_task.last_completed = date.today() - timedelta(days=7)
        pet.add_task(weekly_task)
        
        owner = Owner("Bob", 240)
        owner.add_pet(pet)
        
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(weekly_task, 480)
        plan.mark_task_completed(weekly_task)
        
        # Weekly should have 7-day offset in last_completed
        assert len(plan.next_occurrences) == 1
        assert plan.next_occurrences[0].last_completed == date.today() + timedelta(weeks=1)
    
    def test_as_needed_task_does_not_recur(self):
        """Verify as-needed tasks don't auto-generate recurrences."""
        pet = Pet("Charlie", "dog", 2)
        as_needed = Task("Vet visit", duration=60, frequency="as-needed")
        pet.add_task(as_needed)
        
        owner = Owner("Carol", 240)
        owner.add_pet(pet)
        
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(as_needed, 480)
        plan.mark_task_completed(as_needed)
        
        # As-needed should not create next occurrence
        assert len(plan.next_occurrences) == 0
        assert as_needed in plan.completed_tasks
    
    def test_task_moved_to_completed_list_after_marking(self):
        """Verify task moves from scheduled to completed after mark_task_completed()."""
        pet = Pet("Buddy")
        task = Task("Morning walk", duration=20, frequency="daily")
        pet.add_task(task)
        
        owner = Owner("Alice", 240)
        owner.add_pet(pet)
        
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(task, 480)
        
        assert task in plan.scheduled_tasks
        plan.mark_task_completed(task)
        
        assert task not in plan.scheduled_tasks
        assert task in plan.completed_tasks


# ============================================================
# CORE BEHAVIOR 2: Task Sorting/Ranking
# ============================================================

class TestTaskSorting:
    """Test that tasks are ranked and sorted correctly by priority and duration."""
    
    def test_rank_tasks_by_priority_descending(self):
        """Verify tasks are sorted by priority (5=highest first)."""
        scheduler = Scheduler(Owner("Test", 300))
        
        low_task = Task("Low priority", priority=1, duration=10)
        high_task = Task("High priority", priority=5, duration=10)
        mid_task = Task("Mid priority", priority=3, duration=10)
        
        tasks = [low_task, high_task, mid_task]
        ranked = scheduler.rank_tasks(tasks)
        
        assert ranked[0] == high_task
        assert ranked[1] == mid_task
        assert ranked[2] == low_task
    
    def test_rank_tasks_secondary_sort_by_duration(self):
        """When priorities are equal, shorter tasks should be first."""
        scheduler = Scheduler(Owner("Test", 300))
        
        long_task = Task("Long task", priority=3, duration=60)
        short_task = Task("Short task", priority=3, duration=15)
        medium_task = Task("Medium task", priority=3, duration=30)
        
        tasks = [long_task, short_task, medium_task]
        ranked = scheduler.rank_tasks(tasks)
        
        # All have same priority, so sorted by duration ascending
        assert ranked[0] == short_task
        assert ranked[1] == medium_task
        assert ranked[2] == long_task
    
    def test_chronological_order_in_plan(self):
        """Verify scheduled tasks maintain insertion order (chrono)."""
        owner = Owner("Alice", 300)
        pet = Pet("Buddy")
        owner.add_pet(pet)
        
        plan = DailyPlan(date.today(), owner)
        
        task1 = Task("Morning feed", duration=15)
        task1.set_actual_start_time(480)  # 8:00 AM
        
        task2 = Task("Afternoon walk", duration=20)
        task2.set_actual_start_time(720)  # 12:00 PM
        
        task3 = Task("Evening feed", duration=15)
        task3.set_actual_start_time(1020)  # 5:00 PM
        
        plan.add_task_to_schedule(task1, 480)
        plan.add_task_to_schedule(task2, 720)
        plan.add_task_to_schedule(task3, 1020)
        
        scheduled = plan.get_plan()
        assert scheduled[0].actual_start_time < scheduled[1].actual_start_time
        assert scheduled[1].actual_start_time < scheduled[2].actual_start_time


# ============================================================
# CORE BEHAVIOR 3: Time Conflict Detection
# ============================================================

class TestConflictDetection:
    """Test that scheduling conflicts are properly detected and flagged."""
    
    def test_detect_exact_time_conflict_same_pet(self):
        """Verify same pet with multiple tasks at exact same time is flagged."""
        owner = Owner("Alice", 300)
        pet = Pet("Buddy")
        owner.add_pet(pet)
        
        task1 = Task("Feed", duration=15, priority=5)
        task1.set_actual_start_time(480)
        
        task2 = Task("Walk", duration=20, priority=4)
        task2.set_actual_start_time(480)  # SAME TIME
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        scheduler = Scheduler(owner)
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(task1, 480)
        plan.add_task_to_schedule(task2, 480)
        
        scheduler.check_scheduling_conflicts(plan)
        
        assert len(plan.get_warnings()) > 0
        warnings = plan.get_warnings()
        assert any("CONFLICT" in w for w in warnings)
    
    def test_detect_overlapping_time_slots(self):
        """Verify overlapping task times are detected (e.g., 8:00-8:30 and 8:15-8:45)."""
        owner = Owner("Alice", 300)
        pet = Pet("Buddy")
        owner.add_pet(pet)
        
        task1 = Task("Feed", duration=30)  # 8:00 - 8:30
        task1.set_actual_start_time(480)
        
        task2 = Task("Walk", duration=30)  # 8:15 - 8:45 (overlaps with task1)
        task2.set_actual_start_time(495)
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        scheduler = Scheduler(owner)
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(task1, 480)
        plan.add_task_to_schedule(task2, 495)
        
        scheduler.check_scheduling_conflicts(plan)
        
        warnings = plan.get_warnings()
        assert len(warnings) > 0
        assert any("OVERLAP" in w for w in warnings)
    
    def test_detect_cross_pet_conflict(self):
        """Verify owner cannot do multiple pets' tasks at same time."""
        owner = Owner("Alice", 300)
        
        pet1 = Pet("Buddy", "dog")
        pet2 = Pet("Whiskers", "cat")
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        task1 = Task("Feed dog", duration=15)
        task1.set_actual_start_time(480)
        
        task2 = Task("Feed cat", duration=15)
        task2.set_actual_start_time(480)  # SAME TIME, different pets
        
        pet1.add_task(task1)
        pet2.add_task(task2)
        
        scheduler = Scheduler(owner)
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(task1, 480)
        plan.add_task_to_schedule(task2, 480)
        
        scheduler.check_scheduling_conflicts(plan)
        
        warnings = plan.get_warnings()
        assert len(warnings) > 0
        assert any("CROSS-PET" in w for w in warnings)
    
    def test_no_conflict_when_tasks_sequential(self):
        """Verify no conflict when tasks don't overlap (e.g., 8:00-8:15, then 8:15-8:30)."""
        owner = Owner("Alice", 300)
        pet = Pet("Buddy")
        owner.add_pet(pet)
        
        task1 = Task("Feed", duration=15)
        task1.set_actual_start_time(480)  # 8:00 - 8:15
        
        task2 = Task("Walk", duration=15)
        task2.set_actual_start_time(495)  # 8:15 - 8:30 (starts when task1 ends)
        
        pet.add_task(task1)
        pet.add_task(task2)
        
        scheduler = Scheduler(owner)
        plan = DailyPlan(date.today(), owner)
        plan.add_task_to_schedule(task1, 480)
        plan.add_task_to_schedule(task2, 495)
        
        scheduler.check_scheduling_conflicts(plan)
        
        # Should have no conflicts or only benign warnings
        conflicts = [w for w in plan.get_warnings() if "CONFLICT" in w or "OVERLAP" in w]
        assert len(conflicts) == 0


# ============================================================
# CORE BEHAVIOR 4: Bin-Packing/Task Fitting
# ============================================================

class TestTaskFitting:
    """Test that tasks are greedily fit into available time."""
    
    def test_all_tasks_fit_in_available_time(self):
        """Happy path: all mandatory tasks fit within available owner time."""
        owner = Owner("Alice", 120)  # 120 minutes available
        pet = Pet("Buddy")
        
        task1 = Task("Feed", duration=20, priority=5, frequency="daily")
        task1.last_completed = date.today() - timedelta(days=1)
        
        task2 = Task("Walk", duration=30, priority=4, frequency="daily")
        task2.last_completed = date.today() - timedelta(days=1)
        
        task3 = Task("Play", duration=25, priority=3, frequency="daily")
        task3.last_completed = date.today() - timedelta(days=1)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        all_tasks = owner.get_all_tasks()
        mandatory = [t for t in all_tasks if t.is_mandatory()]
        
        fitted = scheduler.fit_tasks_in_time(mandatory, owner.available_time)
        
        # All should fit: 20 + 30 + 25 = 75 minutes < 120
        assert len(fitted) == 3
        total = sum(t.duration for t in fitted)
        assert total <= owner.available_time
    
    def test_not_all_tasks_fit_lower_priority_skipped(self):
        """When tasks don't fit, lower-priority tasks are skipped."""
        owner = Owner("Alice", 60)  # Only 60 minutes
        pet = Pet("Buddy")
        
        high_task = Task("Feed", duration=40, priority=5, frequency="daily")
        high_task.last_completed = date.today() - timedelta(days=1)
        
        low_task = Task("Play", duration=50, priority=1, frequency="daily")
        low_task.last_completed = date.today() - timedelta(days=1)
        
        pet.add_task(high_task)
        pet.add_task(low_task)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        tasks = [high_task, low_task]
        ranked = scheduler.rank_tasks(tasks)
        fitted = scheduler.fit_tasks_in_time(ranked, owner.available_time)
        
        # Only high-priority should fit
        assert len(fitted) == 1
        assert high_task in fitted
    
    def test_empty_pet_task_list(self):
        """Edge case: pet with no tasks returns empty schedule."""
        owner = Owner("Alice", 100)
        pet = Pet("Buddy")  # No tasks added
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        all_tasks = owner.get_all_tasks()
        
        assert len(all_tasks) == 0


# ============================================================
# CORE BEHAVIOR 5: Mandatory vs Optional Task Filtering
# ============================================================

class TestMandatoryFiltering:
    """Test that is_mandatory() correctly identifies which tasks must be done today."""
    
    def test_daily_task_mandatory_if_not_completed_today(self):
        """Daily task is mandatory if last_completed != today."""
        task = Task("Feed", frequency="daily")
        task.last_completed = date.today() - timedelta(days=1)
        
        assert task.is_mandatory() is True
    
    def test_daily_task_not_mandatory_if_completed_today(self):
        """Daily task is NOT mandatory if last_completed == today."""
        today = date.today()
        task = Task("Feed", frequency="daily")
        task.last_completed = today
        
        assert task.is_mandatory() is False
    
    def test_weekly_task_mandatory_if_not_completed_past_7_days(self):
        """Weekly task is mandatory if not completed in past 7 days."""
        task = Task("Grooming", frequency="weekly")
        task.last_completed = date.today() - timedelta(days=8)
        
        assert task.is_mandatory() is True
    
    def test_weekly_task_not_mandatory_if_completed_within_7_days(self):
        """Weekly task is NOT mandatory if completed within past 7 days."""
        task = Task("Grooming", frequency="weekly")
        task.last_completed = date.today() - timedelta(days=3)
        
        assert task.is_mandatory() is False
    
    def test_weekly_task_never_completed_is_mandatory(self):
        """Weekly task never completed is mandatory (last_completed = None)."""
        task = Task("Grooming", frequency="weekly")
        task.last_completed = None
        
        assert task.is_mandatory() is True
    
    def test_as_needed_task_never_mandatory(self):
        """As-needed tasks are never mandatory."""
        task = Task("Vet visit", frequency="as-needed")
        task.last_completed = date.today() - timedelta(days=100)
        
        assert task.is_mandatory() is False


# ============================================================
# ORIGINAL TESTS (Preserved)
# ============================================================

def test_mark_complete_changes_task_status():
    """Verify that calling mark_complete() changes the task's status."""
    task = Task("Feed the dog", frequency="daily")
    assert task.is_complete == False
    task.mark_complete()
    assert task.is_complete == True


def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Buddy")
    initial_count = len(pet.tasks)
    pet.add_task(Task("Walk", frequency="daily"))
    assert len(pet.tasks) == initial_count + 1