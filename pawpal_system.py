"""
PawPal+ Logic Layer
Contains the core classes for pet care scheduling system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, timedelta


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
    
    def mark_task_completed(self, task: Task) -> None:
        """Mark a task as completed for this day's plan.
        Does NOT modify the original task object to preserve its state."""
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            self.completed_tasks.append(task)
            # FIXED: Don't modify the shared Task object
            # task.last_completed = date.today()  <-- REMOVED
    
    def mark_task_skipped(self, task: Task) -> None:
        """Mark a task as skipped for today."""
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            self.skipped_tasks.append(task)


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
        
        # Step 5: Generate reasoning
        reasoning = self._generate_reasoning(mandatory_tasks, fitted_tasks)
        plan.set_reasoning(reasoning)
        
        # Step 6: Store plan in owner's history
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
