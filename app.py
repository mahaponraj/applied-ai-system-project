import streamlit as st
import pandas as pd
from pawpal_system import Owner, Pet, Task, Scheduler, RAGIntegration, ReliabilityValidator
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown("**Your AI Pet Care Planning Assistant**")

st.divider()

# ============================================================
# Helper Functions
# ============================================================

def build_task_dataframe(tasks, owner, scheduler):
    """Convert tasks to a Pandas DataFrame for professional display."""
    data = []
    for task in tasks:
        # Find pet name
        pet_name = None
        for pet in owner.get_pets():
            if task in pet.get_tasks():
                pet_name = pet.name
                break
        
        # Get time categorization from scheduler
        time_category = scheduler.categorize_task_time(task)
        
        # Determine mandatory status
        is_mandatory = task.is_mandatory()
        mandatory_label = "✓ Mandatory" if is_mandatory else "○ Optional"
        
        data.append({
            "Pet": pet_name or "Unknown",
            "Task": task.task_type,
            "Duration (min)": task.duration,
            "Priority ⭐": task.priority,
            "Frequency": task.frequency,
            "Time": time_category.capitalize(),
            "Status": mandatory_label
        })
    
    return pd.DataFrame(data)


def display_conflict_warnings(plan, scheduler):
    """Display conflict warnings in a user-friendly format."""
    if not plan.has_conflicts():
        st.success("✓ No scheduling conflicts detected!")
        return
    
    warnings = plan.get_warnings()
    
    st.warning("⚠️ **Scheduling Conflicts Detected!**")
    st.markdown("""
    The scheduler has identified potential conflicts in your schedule. 
    Review the suggestions below and consider rescheduling tasks.
    """)
    
    # Organize warnings by type
    same_pet_conflicts = [w for w in warnings if "CONFLICT" in w or "SAME-PET" in w]
    cross_pet_conflicts = [w for w in warnings if "CROSS-PET" in w]
    overlap_conflicts = [w for w in warnings if "OVERLAP" in w]
    
    if same_pet_conflicts:
        st.error("🔴 **Same-Pet Conflicts** (same pet, same time)")
        for warning in same_pet_conflicts:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"• {warning}")
            with col2:
                st.caption("⏰ Reschedule one task")
    
    if cross_pet_conflicts:
        st.error("🔴 **Cross-Pet Conflicts** (owner unavailable)")
        for warning in cross_pet_conflicts:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"• {warning}")
            with col2:
                st.caption("⏰ Stagger times")
    
    if overlap_conflicts:
        st.warning("🟡 **Task Overlaps** (partial time collision)")
        for warning in overlap_conflicts:
            st.write(f"• {warning}")


# ============================================================
# Initialize Session State - Persistent Storage
# ============================================================
# Check if Owner exists in session state; if not, create one
if "owner" not in st.session_state:
    st.session_state.owner = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

if "current_plan" not in st.session_state:
    st.session_state.current_plan = None

# ============================================================
# SECTION 1: Owner Setup
# ============================================================
st.subheader("👤 Owner Setup")
col1, col2 = st.columns(2)

with col1:
    owner_name = st.text_input("Owner name", value="Alice", key="owner_name_input")

with col2:
    available_time = st.number_input(
        "Available time today (minutes)",
        min_value=30,
        max_value=480,
        value=120,
        step=15,
        key="available_time_input"
    )

# Button to create/update Owner
if st.button("✅ Create/Update Owner", key="owner_button"):
    # Check if owner already exists
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, available_time=available_time)
        st.session_state.scheduler = Scheduler(st.session_state.owner)
        st.success(f"✓ Owner '{owner_name}' created!")
    else:
        # Update existing owner
        st.session_state.owner.name = owner_name
        st.session_state.owner.update_available_time(available_time)
        st.success(f"✓ Owner '{owner_name}' updated!")

if st.session_state.owner:
    st.info(f"**Current Owner:** {st.session_state.owner.name} | **Available Time:** {st.session_state.owner.available_time} min")

st.divider()

# ============================================================
# SECTION 2: Manage Pets
# ============================================================
if st.session_state.owner:
    st.subheader("🐕 Manage Pets")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Max", key="pet_name_input")
    with col2:
        pet_species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"], key="pet_species_input")
    with col3:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3, key="pet_age_input")
    
    if st.button("➕ Add Pet", key="add_pet_button"):
        # Create new pet and add to owner
        new_pet = Pet(name=pet_name, species=pet_species, age=pet_age)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"✓ Pet '{pet_name}' added!")
    
    # Display current pets in a table
    if st.session_state.owner.get_pets():
        st.write("**📌 Registered Pets:**")
        pets_data = []
        for pet in st.session_state.owner.get_pets():
            pet_info = pet.get_info()
            pets_data.append({
                "Pet Name": pet_info['name'],
                "Species": pet_info['species'],
                "Age": pet_info['age'],
                "Tasks": pet_info['task_count']
            })
        st.dataframe(pd.DataFrame(pets_data), use_container_width=True, hide_index=True)
    else:
        st.info("No pets registered yet. Add one above.")
    
    st.divider()
    
    # ============================================================
    # SECTION 3: Add Tasks to Pets
    # ============================================================
    st.subheader("📋 Add Tasks")
    
    # Select which pet to add task to
    pet_options = [p.name for p in st.session_state.owner.get_pets()]
    
    if pet_options:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_pet_name = st.selectbox("Select pet for task", pet_options, key="select_pet_for_task")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            task_type = st.text_input("Task type", value="Walk", key="task_type_input")
        
        with col2:
            task_duration = st.number_input(
                "Duration (minutes)",
                min_value=5,
                max_value=240,
                value=30,
                step=5,
                key="task_duration_input"
            )
        
        with col3:
            task_priority = st.select_slider(
                "Priority",
                options=[1, 2, 3, 4, 5],
                value=4,
                key="task_priority_input"
            )
        
        with col4:
            task_frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly", "as-needed"],
                key="task_frequency_input"
            )
        
        task_description = st.text_area(
            "Task description",
            value="",
            height=60,
            key="task_description_input"
        )
        
        # Button to add task
        if st.button("➕ Add Task", key="add_task_button"):
            # Find the selected pet
            selected_pet = next(
                (p for p in st.session_state.owner.get_pets() if p.name == selected_pet_name),
                None
            )
            
            if selected_pet:
                # Create new task
                new_task = Task(
                    task_type=task_type,
                    duration=task_duration,
                    priority=task_priority,
                    description=task_description,
                    frequency=task_frequency
                )
                
                # Add task to pet
                if selected_pet.add_task(new_task):
                    st.success(f"✓ Task '{task_type}' added to {selected_pet_name}!")
                else:
                    st.warning(f"⚠️ '{task_type}' already exists for {selected_pet_name}. Each pet can only have one task of the same type.")
        
        # Display tasks for each pet in ranked order using Scheduler.rank_tasks()
        st.write("**📌 Current Tasks (sorted by priority):**")
        
        for pet in st.session_state.owner.get_pets():
            if pet.get_tasks():
                st.write(f"**{pet.name}:**")
                
                # Rank tasks using Scheduler method
                ranked_tasks = st.session_state.scheduler.rank_tasks(pet.get_tasks())
                
                # Build dataframe for this pet
                pet_tasks_df = build_task_dataframe(ranked_tasks, st.session_state.owner, st.session_state.scheduler)
                st.dataframe(pet_tasks_df, use_container_width=True, hide_index=True)
            else:
                st.write(f"**{pet.name}:** _(no tasks yet)_")
    else:
        st.warning("⚠️ Add at least one pet before creating tasks.")
    
    st.divider()
    
    # ============================================================
    # SECTION 4: Generate Daily Schedule
    # ============================================================
    st.subheader("📅 Generate Today's Schedule")
    
    if st.button("🔄 Generate Schedule", key="generate_schedule_button"):
        # Generate the daily plan using the scheduler
        st.session_state.current_plan = st.session_state.scheduler.generate_daily_plan()
        st.success("✓ Schedule generated!")
    
    # Display the generated plan
    if st.session_state.current_plan:
        plan = st.session_state.current_plan
        
        st.write(f"**📅 Schedule for {plan.date}**")
        
        # Display schedule stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tasks Scheduled", len(plan.get_plan()))
        with col2:
            st.metric("Total Time", f"{plan.total_time} min")
        with col3:
            st.metric("Available", f"{st.session_state.owner.available_time} min")
        with col4:
            feasible_status = "✓ Feasible" if plan.is_feasible() else "✗ Exceeds Time"
            st.metric("Status", feasible_status)
        
        st.divider()
        
        # ============================================================
        # Display Conflict Warnings (PROMINENT)
        # ============================================================
        display_conflict_warnings(plan, st.session_state.scheduler)
        
        st.divider()
        
        # Display scheduled tasks in ranked order
        if plan.get_plan():
            st.write("**📋 Scheduled Tasks:**")
            
            # Build dataframe for all scheduled tasks (already in order from generate_daily_plan)
            schedule_df = build_task_dataframe(plan.get_plan(), st.session_state.owner, st.session_state.scheduler)
            st.dataframe(schedule_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Display individual task details with completion option
            st.write("**✏️ Task Details & Actions:**")
            for idx, task in enumerate(plan.get_plan(), 1):
                # Find which pet this task belongs to
                pet_name = None
                for pet in st.session_state.owner.get_pets():
                    if task in pet.get_tasks():
                        pet_name = pet.name
                        break
                
                with st.expander(f"{idx}. {task.task_type} ({task.duration}min) - {pet_name}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Pet:** {pet_name}")
                        st.write(f"**Duration:** {task.duration} minutes")
                        st.write(f"**Priority:** {'⭐' * task.priority}")
                    with col2:
                        st.write(f"**Frequency:** {task.frequency}")
                        st.write(f"**Status:** {'✓ Mandatory' if task.is_mandatory() else '○ Optional'}")
                    
                    if task.description:
                        st.write(f"**Description:** {task.description}")
                    
                    # Button to mark as complete
                    if st.button(f"✅ Mark Complete", key=f"complete_{idx}"):
                        plan.mark_task_completed(task)
                        st.success(f"✓ {task.task_type} marked as complete!")
                        if plan.next_occurrences:
                            st.info(f"📅 Next occurrence created for {plan.next_occurrences[-1].task_type}")
        else:
            st.warning("🚨 No tasks fit in the available time!")
            st.info("💡 Try increasing available time or reducing task duration/priority.")
        
        st.divider()
        
        # ============================================================
        # SECTION 5: AI-Powered RAG Insights & Reliability
        # ============================================================
        st.subheader("🤖 AI Insights & Reliability Check")
        
        # Display RAG-powered pet care insights
        if plan.get_reasoning():
            with st.expander("📚 View AI Pet Care Insights", expanded=True):
                st.markdown(plan.get_reasoning())
        
        # Run and display reliability validation
        if st.session_state.scheduler and st.session_state.scheduler.validator:
            validation_results = st.session_state.scheduler.validator.validate_plan(plan)
            summary = st.session_state.scheduler.validator.get_validation_summary(validation_results)
            
            # Display validation summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Checks", summary['total_checks'])
            with col2:
                st.metric("✅ Passed", summary['passed'])
            with col3:
                st.metric("⚠️ Warnings", summary['warnings'])
            with col4:
                st.metric("❌ Errors", summary['errors'])
            
            # Show detailed validation results
            if validation_results:
                st.write("**🔍 Validation Details:**")
                for result in validation_results:
                    if result.severity == "error":
                        st.error(f"❌ **{result.category.upper()}:** {result.message}")
                    elif result.severity == "warning":
                        st.warning(f"⚠️ **{result.category.upper()}:** {result.message}")
                    else:
                        st.info(f"ℹ️ **{result.category.upper()}:** {result.message}")
            
            # Overall status
            if summary['errors'] == 0 and summary['failed'] == 0:
                st.success("✅ **Overall: All reliability checks passed!**")
            else:
                st.error("❌ **Overall: Some reliability checks failed. Review the details above.**")
        
        st.divider()

        # Display completion summary
        if plan.completed_tasks or plan.skipped_tasks:
            col1, col2 = st.columns(2)
            with col1:
                if plan.completed_tasks:
                    st.write("**✓ Completed:**")
                    for task in plan.completed_tasks:
                        st.write(f"  ✓ {task.task_type}")
            with col2:
                if plan.skipped_tasks:
                    st.write("**○ Skipped:**")
                    for task in plan.skipped_tasks:
                        st.write(f"  ○ {task.task_type}")


else:
    st.warning("👆 Please create an owner to get started!")

