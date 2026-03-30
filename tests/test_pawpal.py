import pytest
from pawpal_system import Pet, Task

def test_mark_complete_changes_task_status():
    """Verify that calling mark_complete() changes the task's status."""
    task = Task("Feed the dog", False)
    assert task.is_complete == False
    task.mark_complete()
    assert task.is_complete == True


def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Buddy")
    initial_count = len(pet.tasks)
    pet.add_task(Task("Walk", False))
    assert len(pet.tasks) == initial_count + 1