"""
PawPal+ Logic Layer
Contains the core classes for pet care scheduling system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date


@dataclass
class Pet:
    """Represents a pet that needs care."""
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    
    def get_info(self) -> dict:
        """Return pet details as a dictionary."""
        pass
    
    def add_special_need(self, need: str) -> None:
        """Record a medical or behavioral need."""
        pass


@dataclass
class Task:
    """Represents a single pet care activity."""
    task_type: str
    duration: int  # in minutes
    priority: int  # 1-5 scale
    description: str
    frequency: str = "daily"
    last_completed: Optional[date] = None  # tracks when task was last done
    
    def get_duration(self) -> int:
        """Return time needed for this task in minutes."""
        pass
    
    def get_priority(self) -> int:
        """Return priority level."""
        pass
    
    def is_mandatory(self) -> bool:
        """Check if task must be done today."""
        pass


class Owner:
    """Represents a pet owner using the app."""
    
    def __init__(self, name: str, available_time: int):
        self.name = name
        self.available_time = available_time  # in minutes
        self.preferences: Dict[str, any] = {}
        self.current_plan: Optional['DailyPlan'] = None
        self.plan_history: List['DailyPlan'] = []
    
    def update_available_time(self, time: int) -> None:
        """Adjust how much time the owner has available today."""
        pass
    
    def set_preferences(self, preferences: Dict) -> None:
        """Record owner priorities and preferences."""
        pass


class DailyPlan:
    """Represents the schedule for one day."""
    
    def __init__(self, plan_date: date, owner: 'Owner', pet: 'Pet'):
        self.date = plan_date
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_time = 0  # in minutes
        self.reasoning = ""
    
    def add_task_to_schedule(self, task: Task, start_time_minutes: int) -> None:
        """Insert a task at a specific time (minutes from midnight, e.g., 480 = 8am)."""
        pass
    
    def get_plan(self) -> List[Task]:
        """Return the full ordered schedule."""
        pass
    
    def get_reasoning(self) -> str:
        """Explain the scheduling decisions."""
        pass
    
    def is_feasible(self) -> bool:
        """Check if schedule fits in available time."""
        pass


class Scheduler:
    """Handles scheduling logic to arrange tasks into a daily plan."""
    
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.available_tasks: List[Task] = []
    
    def add_task(self, task: Task) -> None:
        """Register a new task."""
        pass
    
    def generate_daily_plan(self) -> DailyPlan:
        """Create today's schedule based on constraints and priorities."""
        pass
    
    def rank_tasks(self) -> List[Task]:
        """Order tasks by priority and constraints."""
        pass
    
    def fit_tasks_in_time(self, tasks: List[Task], available_time: int) -> List[Task]:
        """Determine which tasks fit within available time."""
        pass
    
    def generate_ranked_and_fitted_tasks(self) -> List[Task]:
        """Rank tasks by priority, then fit as many as possible into available time.
        Call this once instead of separately calling rank_tasks() and fit_tasks_in_time().
        """
        pass
