"""
PawPal+ Logic Layer
Contains the core classes for pet care scheduling system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta


@dataclass
class TimeSlot:
    """Represents a preferred time window for a task."""
    start_time: int  # minutes from midnight (e.g., 420 = 7:00 AM)
    end_time: int    # minutes from midnight (e.g., 720 = 12:00 PM)
    label: str = ""  # e.g., "morning", "afternoon", "evening"
    
    def contains(self, time_minutes: int) -> bool:
        """Check if a time falls within this slot."""
        return self.start_time <= time_minutes < self.end_time
    
    def duration_available(self, start: int, duration: int) -> bool:
        """Check if a task of given duration fits within this slot starting at time."""
        return start >= self.start_time and start + duration <= self.end_time


@dataclass
class Task:
    """Represents a single pet care activity."""
    task_type: str
    duration: int = 0  # in minutes (default for simple tasks)
    priority: int = 3  # 1-5 scale (default to medium)
    description: str = ""
    frequency: str = "daily"  # "daily", "weekly", "as-needed"
    last_completed: Optional[date] = None  # tracks when task was last done
    is_complete: bool = False  # Track completion status within a day
    preferred_times: List[TimeSlot] = field(default_factory=list)  # preferred scheduling windows
    actual_start_time: Optional[int] = None  # assigned during scheduling (minutes from midnight)
    depends_on: List[str] = field(default_factory=list)  # task IDs this depends on
    
    def get_duration(self) -> int:
        """Return time needed for this task in minutes."""
        return self.duration
    
    def get_priority(self) -> int:
        """Return priority level (1-5, where 5 is highest)."""
        return self.priority
    
    def mark_complete(self) -> None:
        """Mark this task as complete for today."""
        self.is_complete = True
    
    def is_mandatory(self) -> bool:
        """Check if task must be done today based on frequency and last completion."""
        today = date.today()
        
        if self.frequency == "daily":
            # Daily tasks are mandatory if not completed today
            return self.last_completed != today
        
        elif self.frequency == "weekly":
            # Weekly tasks are mandatory if not completed in the past 7 days
            if self.last_completed is None:
                return True  # Never completed, so mandatory
            days_since = (today - self.last_completed).days
            return days_since >= 7
        
        elif self.frequency == "as-needed":
            # As-needed tasks are never mandatory (owner decides)
            return False
        
        return False
    
    def set_actual_start_time(self, time_minutes: int) -> None:
        """Assign the actual scheduled start time for this task."""
        self.actual_start_time = time_minutes
    
    def get_end_time(self) -> Optional[int]:
        """Calculate when this task ends based on start time and duration."""
        if self.actual_start_time is None:
            return None
        return self.actual_start_time + self.duration


@dataclass
class Pet:
    """Represents a pet that needs care."""
    name: str
    species: str = "Unknown"  # Default value
    age: int = 0  # Default value
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    
    def get_info(self) -> dict:
        """Return pet details as a dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs,
            "task_count": len(self.tasks)
        }
    
    def add_special_need(self, need: str) -> None:
        """Record a medical or behavioral need."""
        if need not in self.special_needs:
            self.special_needs.append(need)
    
    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)
    
    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        return self.tasks


class Owner:
    """Represents a pet owner using the app."""
    
    def __init__(self, name: str, available_time: int):
        self.name = name
        self.available_time = available_time  # in minutes
        self.preferences: Dict[str, any] = {}
        self.pets: List[Pet] = []
        self.current_plan: Optional['DailyPlan'] = None
        self.plan_history: List['DailyPlan'] = []
    
    def update_available_time(self, time: int) -> None:
        """Adjust how much time the owner has available today."""
        self.available_time = time
    
    def set_preferences(self, preferences: Dict) -> None:
        """Record owner priorities and preferences."""
        self.preferences.update(preferences)
    
    def add_pet(self, pet: Pet) -> None:
        """Register a new pet for this owner."""
        self.pets.append(pet)
    
    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from all pets owned by this owner.
        This is the method Scheduler calls to get tasks across all pets.
        """
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks
    
    def get_pets(self) -> List[Pet]:
        """Return list of all pets."""
        return self.pets
    
    def get_tasks_for_pet(self, pet: Pet, status: str = None) -> List[Task]:
        """Filter tasks by pet and optionally by completion status.
        
        Status can be: "mandatory", "optional", or None (all).
        """
        pet_tasks = pet.get_tasks()
        if status == "mandatory":
            return [t for t in pet_tasks if t.is_mandatory()]
        elif status == "optional":
            return [t for t in pet_tasks if not t.is_mandatory()]
        return pet_tasks
    
    def get_tasks_by_type(self, task_type: str) -> List[Task]:
        """Find all tasks matching a type pattern (e.g., 'Feeding', 'Walk')."""
        return [t for t in self.get_all_tasks() 
                if task_type.lower() in t.task_type.lower()]
    
    def get_pet_for_task(self, task: Task) -> Optional[Pet]:
        """Return the pet that owns this task, or None if not found."""
        for pet in self.pets:
            if task in pet.get_tasks():
                return pet
        return None


class DailyPlan:
    """Represents the schedule for one day."""
    
    def __init__(self, plan_date: date, owner: 'Owner'):
        self.date = plan_date
        self.owner = owner
        self.scheduled_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_time = 0  # in minutes
        self.reasoning = ""
        self.next_occurrences: List[Task] = []  # Auto-generated next occurrences of recurring tasks
        self.warnings: List[str] = []  # Lightweight conflict warnings (non-blocking)
    
    def add_task_to_schedule(self, task: Task, start_time_minutes: int) -> None:
        """Insert a task at a specific time (minutes from midnight, e.g., 480 = 8am)."""
        self.scheduled_tasks.append(task)
        self.total_time += task.get_duration()
    
    def get_plan(self) -> List[Task]:
        """Return the full ordered schedule."""
        return self.scheduled_tasks
    
    def get_reasoning(self) -> str:
        """Explain the scheduling decisions."""
        return self.reasoning
    
    def set_reasoning(self, reasoning: str) -> None:
        """Set the explanation for scheduling decisions."""
        self.reasoning = reasoning
    
    def is_feasible(self) -> bool:
        """Check if schedule fits in available time."""
        return self.total_time <= self.owner.available_time
    
    def _create_next_occurrence(self, task: Task) -> Task:
        """Create the next occurrence of a recurring task.
        
        Uses timedelta to calculate next due date based on frequency.
        """
        today = date.today()
        
        # Create new task with next occurrence date
        next_task = Task(
            task_type=task.task_type,
            duration=task.duration,
            priority=task.priority,
            description=task.description,
            frequency=task.frequency,
            last_completed=today,  # Mark as completed today
            is_complete=False,
            preferred_times=task.preferred_times.copy() if task.preferred_times else [],
            depends_on=task.depends_on.copy() if task.depends_on else []
        )
        
        # Calculate next due date using timedelta
        if task.frequency == "daily":
            # Next task due tomorrow: today + 1 day
            next_task.last_completed = today + timedelta(days=1)
        elif task.frequency == "weekly":
            # Next task due 7 days from now: today + 7 days
            next_task.last_completed = today + timedelta(weeks=1)
        # "as-needed" and "once" don't get auto-recurred
        
        return next_task
    
    def mark_task_completed(self, task: Task) -> None:
        """Mark a task as completed for this day's plan.
        
        Automatically creates next occurrence for daily/weekly recurring tasks.
        Does NOT modify the original task object directly.
        """
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            self.completed_tasks.append(task)
            
            # AUTO-RECURRENCE LOGIC: Create next occurrence for recurring tasks
            if task.frequency in ["daily", "weekly"]:
                next_occurrence = self._create_next_occurrence(task)
                self.next_occurrences.append(next_occurrence)
                
                # Add the next occurrence back to the pet's task list
                pet = self.owner.get_pet_for_task(task)
                if pet:
                    pet.add_task(next_occurrence)
                    print(f"   [*] Next occurrence of '{task.task_type}' scheduled for {next_occurrence.last_completed}")
    
    def mark_task_skipped(self, task: Task) -> None:
        """Mark a task as skipped for today."""
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            self.skipped_tasks.append(task)
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Retrieve tasks by status: 'scheduled', 'completed', or 'skipped'."""
        if status == "scheduled":
            return self.scheduled_tasks
        elif status == "completed":
            return self.completed_tasks
        elif status == "skipped":
            return self.skipped_tasks
        return []
    
    def get_completion_percentage(self) -> float:
        """Return percentage of initially scheduled tasks that were completed."""
        total = len(self.scheduled_tasks) + len(self.completed_tasks)
        if total == 0:
            return 0.0
        return (len(self.completed_tasks) / total) * 100
    
    def calculate_schedule_with_buffers(self, buffer_minutes: int = 10) -> int:
        """Calculate total time including transition buffers between tasks."""
        total = sum(t.get_duration() for t in self.scheduled_tasks)
        # Add buffer between each task (except the last one)
        buffers = max(0, len(self.scheduled_tasks) - 1) * buffer_minutes
        return total + buffers
    
    def add_warning(self, warning_message: str) -> None:
        """Add a non-blocking warning to the plan (e.g., scheduling conflict detected)."""
        if warning_message not in self.warnings:  # Avoid duplicates
            self.warnings.append(warning_message)
    
    def get_warnings(self) -> List[str]:
        """Return all warnings for this plan."""
        return self.warnings
    
    def has_conflicts(self) -> bool:
        """Check if any scheduling conflicts were detected."""
        return len(self.warnings) > 0


class Scheduler:
    """Handles scheduling logic to arrange tasks into a daily plan.
    
    The Scheduler is the "Brain" that retrieves all tasks from the Owner's pets,
    organizes them by priority and constraints, and creates a feasible daily plan.
    """
    
    def __init__(self, owner: Owner):
        self.owner = owner
        self.available_tasks: List[Task] = []
    
    def add_task(self, task: Task, pet: Pet) -> None:
        """Register a new task to a pet."""
        pet.add_task(task)
        self.available_tasks.append(task)
    
    def generate_daily_plan(self) -> DailyPlan:
        """Create today's schedule based on constraints and priorities.
        
        This is the main entry point: retrieves all tasks from Owner's pets,
        ranks them, fits them into available time, and returns a DailyPlan.
        """
        plan = DailyPlan(date.today(), self.owner)
        
        # Step 1: Retrieve all tasks from all pets
        all_tasks = self.owner.get_all_tasks()
        
        # Step 2: Filter for mandatory tasks only (ones that MUST be done today)
        mandatory_tasks = [t for t in all_tasks if t.is_mandatory()]
        
        # Step 3: Rank and fit tasks
        fitted_tasks = self.generate_ranked_and_fitted_tasks(mandatory_tasks)
        
        # Step 4: Add tasks to plan
        for task in fitted_tasks:
            plan.add_task_to_schedule(task, 0)  # Time slot simplified for now
        
        # Step 5: Check for scheduling conflicts (lightweight, doesn't crash)
        self.check_scheduling_conflicts(plan)
        
        # Step 6: Generate reasoning
        reasoning = self._generate_reasoning(mandatory_tasks, fitted_tasks)
        plan.set_reasoning(reasoning)
        
        # Step 7: Store plan in owner's history
        self.owner.current_plan = plan
        self.owner.plan_history.append(plan)
        
        return plan
    
    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks by priority (highest first) and other constraints.
        
        Priority is 1-5, where 5 is highest.
        Secondary sort: by duration (shorter tasks first, for flexibility).
        """
        return sorted(tasks, key=lambda t: (-t.get_priority(), t.get_duration()))
    
    def fit_tasks_in_time(self, tasks: List[Task], available_time: int) -> List[Task]:
        """Determine which tasks fit within available time using a greedy approach.
        
        Takes tasks in order (already ranked by priority) and adds them until
        we run out of time. High-priority tasks are preferred.
        """
        fitted = []
        total_time = 0
        
        for task in tasks:
            if total_time + task.get_duration() <= available_time:
                fitted.append(task)
                total_time += task.get_duration()
        
        return fitted
    
    def generate_ranked_and_fitted_tasks(self, tasks: List[Task]) -> List[Task]:
        """Rank tasks by priority, then fit as many as possible into available time.
        
        Call this once instead of separately calling rank_tasks() and fit_tasks_in_time().
        """
        ranked = self.rank_tasks(tasks)
        fitted = self.fit_tasks_in_time(ranked, self.owner.available_time)
        return fitted
    
    def _generate_reasoning(self, all_mandatory: List[Task], scheduled: List[Task]) -> str:
        """Generate a human-readable explanation of the scheduling decisions."""
        total_duration = sum(t.get_duration() for t in scheduled)
        skipped_count = len(all_mandatory) - len(scheduled)
        
        reasoning = f"Scheduled {len(scheduled)} tasks in {total_duration} minutes. "
        if skipped_count > 0:
            remaining_time = self.owner.available_time - total_duration
            reasoning += f"Could not fit {skipped_count} task(s) (only {remaining_time} min left). "
            skipped = [t for t in all_mandatory if t not in scheduled]
            reasoning += f"Skipped lower-priority: {', '.join([t.task_type for t in skipped])}."
        else:
            reasoning += "All mandatory tasks fit!"
        
        return reasoning
    
    # ============================================================
    # IMPROVEMENT 1: Time-of-Day Categorization
    # ============================================================
    
    def categorize_task_time(self, task: Task) -> str:
        """Categorize task as 'morning', 'afternoon', or 'evening' based on task type."""
        morning_keywords = ['walk', 'breakfast', 'feed', 'exercise', 'morning']
        evening_keywords = ['dinner', 'cleanup', 'night', 'bedtime', 'evening']
        
        task_lower = task.task_type.lower()
        desc_lower = task.description.lower()
        text = f"{task_lower} {desc_lower}"
        
        for keyword in morning_keywords:
            if keyword in text:
                return 'morning'
        for keyword in evening_keywords:
            if keyword in text:
                return 'evening'
        return 'afternoon'
    
    # ============================================================
    # IMPROVEMENT 2: Recurring Task Expansion
    # ============================================================
    
    def expand_recurring_tasks(self, tasks: List[Task], days_ahead: int = 7) -> List[Task]:
        """Convert frequency patterns into actual task instances for upcoming days.
        
        Creates separate Task instances for each occurrence while preserving original.
        """
        expanded = []
        today = date.today()
        
        for task in tasks:
            if task.frequency == "daily":
                for day in range(days_ahead):
                    task_date = today + timedelta(days=day)
                    new_task = Task(
                        task_type=f"{task.task_type} ({task_date.strftime('%m/%d')})",
                        duration=task.duration,
                        priority=task.priority,
                        description=task.description,
                        frequency="once",
                        last_completed=task.last_completed,
                        depends_on=task.depends_on.copy()
                    )
                    expanded.append(new_task)
            elif task.frequency == "weekly":
                for week in range(days_ahead // 7 + 1):
                    task_date = today + timedelta(weeks=week)
                    new_task = Task(
                        task_type=f"{task.task_type} ({task_date.strftime('%m/%d')})",
                        duration=task.duration,
                        priority=task.priority,
                        description=task.description,
                        frequency="once",
                        last_completed=task.last_completed,
                        depends_on=task.depends_on.copy()
                    )
                    expanded.append(new_task)
            else:
                expanded.append(task)  # as-needed or once
        
        return expanded
    
    # ============================================================
    # IMPROVEMENT 3: Time-Based Conflict Detection
    # ============================================================
    
    def detect_time_conflicts(self, scheduled_tasks: List[Task]) -> List[Tuple[Task, Task]]:
        """Find overlapping time slots in the schedule.
        
        Returns list of (task1, task2) tuples that overlap.
        """
        conflicts = []
        for i, task1 in enumerate(scheduled_tasks):
            if task1.actual_start_time is None:
                continue
            for task2 in scheduled_tasks[i+1:]:
                if task2.actual_start_time is None:
                    continue
                # Check if task2 starts before task1 ends
                if (task1.actual_start_time < task2.actual_start_time + task2.duration and
                    task1.actual_start_time + task1.duration > task2.actual_start_time):
                    conflicts.append((task1, task2))
        return conflicts
    
    def check_scheduling_conflicts(self, plan: 'DailyPlan') -> None:
        """Lightweight conflict detection that adds warnings to the plan without crashing.
        
        Checks for:
        1. Same pet with multiple tasks at same time
        2. Cross-pet conflicts (e.g., owner can't do two tasks simultaneously)
        3. Returns warnings instead of blocking
        """
        scheduled_tasks = plan.get_plan()
        
        # Build a time map: time -> list of tasks
        time_map = {}
        for task in scheduled_tasks:
            if task.actual_start_time is not None:
                time_key = task.actual_start_time
                if time_key not in time_map:
                    time_map[time_key] = []
                time_map[time_key].append(task)
        
        # Check for conflicts at each time slot
        for time_slot, tasks_at_slot in time_map.items():
            if len(tasks_at_slot) > 1:
                # Multiple tasks at same time - check for conflicts
                
                # Group by pet
                pet_groups = {}
                for task in tasks_at_slot:
                    pet = self.owner.get_pet_for_task(task)
                    pet_name = pet.name if pet else "Unknown"
                    if pet_name not in pet_groups:
                        pet_groups[pet_name] = []
                    pet_groups[pet_name].append(task)
                
                # Check same-pet conflicts
                for pet_name, pet_tasks in pet_groups.items():
                    if len(pet_tasks) > 1:
                        task_names = ", ".join([t.task_type for t in pet_tasks])
                        time_str = self.minutes_to_time_str(time_slot)
                        warning = f"[CONFLICT] {pet_name} has multiple tasks at {time_str}: {task_names}"
                        plan.add_warning(warning)
                
                # Cross-pet conflicts (owner can't physically do two things at once)
                if len(pet_groups) > 1:
                    task_list = ", ".join([
                        f"{self.owner.get_pet_for_task(t).name if self.owner.get_pet_for_task(t) else 'Unknown'}: {t.task_type}"
                        for t in tasks_at_slot
                    ])
                    time_str = self.minutes_to_time_str(time_slot)
                    warning = f"[CROSS-PET CONFLICT] Owner cannot do multiple pets' tasks at {time_str}: {task_list}"
                    plan.add_warning(warning)
        
        # Check for overlapping tasks (not just exact same time)
        for i, task1 in enumerate(scheduled_tasks):
            if task1.actual_start_time is None:
                continue
            for task2 in scheduled_tasks[i+1:]:
                if task2.actual_start_time is None:
                    continue
                
                # Check for time overlap
                task1_end = task1.actual_start_time + task1.duration
                task2_end = task2.actual_start_time + task2.duration
                
                # Overlap detection: task1 starts before task2 ends AND task1 ends after task2 starts
                if task1.actual_start_time < task2_end and task1_end > task2.actual_start_time:
                    # Check if they're for the same pet
                    pet1 = self.owner.get_pet_for_task(task1)
                    pet2 = self.owner.get_pet_for_task(task2)
                    pet1_name = pet1.name if pet1 else "Unknown"
                    pet2_name = pet2.name if pet2 else "Unknown"
                    
                    task1_time = self.minutes_to_time_str(task1.actual_start_time)
                    task2_time = self.minutes_to_time_str(task2.actual_start_time)
                    
                    if pet1_name == pet2_name:
                        warning = f"[SAME-PET OVERLAP] {pet1_name}: '{task1.task_type}' ({task1_time}) overlaps with '{task2.task_type}' ({task2_time})"
                    else:
                        warning = f"[TIME OVERLAP] '{task1.task_type}' ({pet1_name}, {task1_time}) overlaps with '{task2.task_type}' ({pet2_name}, {task2_time})"
                    
                    plan.add_warning(warning)
    
    # ============================================================
    # IMPROVEMENT 4: Pet-Specific Filtering (already in Owner, but helper here too)
    # ============================================================
    
    def get_pet_for_task(self, task: Task) -> Optional[Pet]:
        """Return the pet that owns this task."""
        return self.owner.get_pet_for_task(task)
    
    def get_tasks_for_pet(self, pet: Pet) -> List[Task]:
        """Get all mandatory tasks for a specific pet."""
        return [t for t in pet.get_tasks() if t.is_mandatory()]
    
    # ============================================================
    # IMPROVEMENT 5: Task Dependency Resolution
    # ============================================================
    
    def order_tasks_by_dependencies(self, tasks: List[Task]) -> List[Task]:
        """Order tasks so dependencies are satisfied before dependents.
        
        Uses topological sorting to handle task dependencies.
        """
        ordered = []
        remaining_ids = {t.task_type for t in tasks}
        visited = set()
        
        while remaining_ids:
            # Find tasks with no unsatisfied dependencies
            ready = [t for t in tasks if t.task_type in remaining_ids
                    and all(dep not in remaining_ids for dep in t.depends_on)]
            
            if not ready:
                # Circular dependency detected, add remaining as-is
                ordered.extend([t for t in tasks if t.task_type in remaining_ids])
                break
            
            ordered.extend(ready)
            remaining_ids -= {t.task_type for t in ready}
        
        return ordered
    
    # ============================================================
    # IMPROVEMENT 6: Optimized Bin-Packing Algorithm
    # ============================================================
    
    def fit_tasks_optimized(self, tasks: List[Task], available_time: int) -> List[Task]:
        """Use improved bin-packing to fit more tasks in available time.
        
        First sorts by priority, then by duration (descending) for better packing.
        """
        # Primary: sort by priority (descending), secondary: by duration (descending)
        sorted_tasks = sorted(tasks, key=lambda t: (-t.get_priority(), -t.get_duration()))
        
        fitted = []
        total_time = 0
        
        for task in sorted_tasks:
            if total_time + task.get_duration() <= available_time:
                fitted.append(task)
                total_time += task.get_duration()
        
        return fitted
    
    # ============================================================
    # IMPROVEMENT 7: Smart Time-Slot Assignment
    # ============================================================
    
    def schedule_with_time_awareness(self, tasks: List[Task], 
                                      buffer_minutes: int = 10) -> DailyPlan:
        """Assign tasks to specific time slots, respecting time-of-day preferences.
        
        Organizes tasks into morning (7am-12pm), afternoon (12pm-5pm), 
        and evening (5pm-10pm) blocks.
        """
        plan = DailyPlan(date.today(), self.owner)
        
        # Categorize tasks by time preference
        morning_tasks = [t for t in tasks if self.categorize_task_time(t) == 'morning']
        afternoon_tasks = [t for t in tasks if self.categorize_task_time(t) == 'afternoon']
        evening_tasks = [t for t in tasks if self.categorize_task_time(t) == 'evening']
        
        # Time boundaries (in minutes from midnight)
        morning_start, morning_end = 420, 720      # 7am - 12pm
        afternoon_start, afternoon_end = 720, 1020 # 12pm - 5pm
        evening_start, evening_end = 1020, 1320    # 5pm - 10pm
        
        # Schedule morning tasks
        current_time = morning_start
        for task in sorted(morning_tasks, key=lambda t: -t.get_priority()):
            if current_time + task.duration <= morning_end:
                task.set_actual_start_time(current_time)
                plan.add_task_to_schedule(task, current_time)
                current_time += task.duration + buffer_minutes
        
        # Schedule afternoon tasks
        current_time = afternoon_start
        for task in sorted(afternoon_tasks, key=lambda t: -t.get_priority()):
            if current_time + task.duration <= afternoon_end:
                task.set_actual_start_time(current_time)
                plan.add_task_to_schedule(task, current_time)
                current_time += task.duration + buffer_minutes
        
        # Schedule evening tasks
        current_time = evening_start
        for task in sorted(evening_tasks, key=lambda t: -t.get_priority()):
            if current_time + task.duration <= evening_end:
                task.set_actual_start_time(current_time)
                plan.add_task_to_schedule(task, current_time)
                current_time += task.duration + buffer_minutes
        
        return plan
    
    # ============================================================
    # IMPROVEMENT 8: Convert minutes to time string (utility)
    # ============================================================
    
    def minutes_to_time_str(self, minutes: int) -> str:
        """Convert minutes from midnight to human-readable time string."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
