"""
Dynamic Task Manager for Three-Condition Testing
Implements task detection and progression based on test logic documents
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import streamlit as st


class TaskType(Enum):
    """Types of dynamic tasks from test documents"""
    # Test 1.x series - Concept Development
    ARCHITECTURAL_CONCEPT = "architectural_concept"  # Test 1.1
    SPATIAL_PROGRAM = "spatial_program"  # Test 1.2

    # Test 2.x series - Visual Development
    VISUAL_ANALYSIS_2D = "visual_analysis_2d"  # Test 2.1 - Visual analysis (no image required)
    ENVIRONMENTAL_CONTEXTUAL = "environmental_contextual"  # Test 2.2

    # Test 3.x series - 3D and Material Systems
    SPATIAL_ANALYSIS_3D = "spatial_analysis_3d"  # Test 3.1
    REALIZATION_IMPLEMENTATION = "realization_implementation"  # Test 3.2

    # Test 4.x series - Reflection and Evolution
    DESIGN_EVOLUTION = "design_evolution"  # Test 4.1
    KNOWLEDGE_TRANSFER = "knowledge_transfer"  # Test 4.2


@dataclass
class ActiveTask:
    """Represents an active dynamic task - PHASE COMPLETION BASED"""
    task_type: TaskType
    start_time: datetime
    test_group: str  # MENTOR, GENERIC_AI, CONTROL
    current_phase: str  # ideation, visualization, materialization
    trigger_reason: str
    completion_criteria: List[str] = field(default_factory=list)
    progress_indicators: Dict[str, Any] = field(default_factory=dict)
    task_specific_data: Dict[str, Any] = field(default_factory=dict)
    trigger_phase_completion: float = 0.0  # Phase completion % when task was triggered

    @property
    def is_expired(self) -> bool:
        """Tasks don't expire by time - they complete based on phase progression"""
        return False  # Tasks are manually completed or completed by phase progression

    @property
    def phase_completion_range(self) -> str:
        """Get the phase completion range for this task"""
        return self.progress_indicators.get("phase_completion_range", "Unknown")

    @property
    def triggered_at_completion(self) -> str:
        """Get the phase completion percentage when this task was triggered"""
        return self.progress_indicators.get("triggered_at_completion", "Unknown")


class DynamicTaskManager:
    """Manages dynamic task detection and progression for three-condition testing"""
    
    def __init__(self):
        print(f"🚨 TASK_MANAGER_INIT: Creating new task manager instance {id(self)}")

        self.active_tasks: Dict[str, ActiveTask] = {}
        self.task_history: List[ActiveTask] = []
        self.task_triggers = self._initialize_task_triggers()
        # CRITICAL FIX: Track user's phase completion progression to detect threshold crossings
        self.user_progression_history: Dict[str, float] = {}  # phase -> last_completion_percent
        self.triggered_tasks_by_user: Set[TaskType] = set()  # Tasks user has actually seen
        # REMOVED: self.task_durations - no longer using time-based durations

        print(f"🚨 TASK_MANAGER_INIT: Initialized with empty active_tasks: {list(self.active_tasks.keys())}")
        
    def _initialize_task_triggers(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize task trigger conditions - PHASE COMPLETION BASED ONLY"""
        return {
            # Test 1.1: Architectural Concept Development - START OF IDEATION
            TaskType.ARCHITECTURAL_CONCEPT: {
                "phase_requirement": "ideation",
                "trigger_once": True,
                "phase_completion_min": 0.0,   # Trigger at start of ideation
                "phase_completion_max": 15.0   # Don't trigger if ideation is already 15% complete
            },

            # Test 1.2: Spatial Program Development - MID IDEATION (20-80% completion)
            TaskType.SPATIAL_PROGRAM: {
                "phase_requirement": "ideation",
                "requires_previous": [TaskType.ARCHITECTURAL_CONCEPT],
                "trigger_once": True,
                "phase_completion_min": 20.0,  # Trigger when ideation is 30% complete
                "phase_completion_max": 70.0   # EXTENDED WINDOW - allow retroactive triggering up to 80%
            },

            # Test 2.1: 2D Design Development & Analysis - NO IMAGE REQUIRED
            TaskType.VISUAL_ANALYSIS_2D: {
                "image_upload": False,  # FIXED: No image required
                "image_types": ["floor_plan", "elevation", "section", "sketch"],
                "phase_requirement": "visualization",
                "trigger_once": False,  # Can trigger multiple times
                "phase_completion_min": 0.0,   # Trigger immediately when visualization starts
                "phase_completion_max": 50.0   # Trigger in first half of visualization
            },

            # Test 2.2: Environmental & Contextual Integration - MID VISUALIZATION
            TaskType.ENVIRONMENTAL_CONTEXTUAL: {
                "phase_requirement": "visualization",
                "trigger_once": True,
                "phase_completion_min": 30.0,  # Trigger when visualization is 30% complete
                "phase_completion_max": 70.0   # Don't trigger if visualization is already 70% complete
            },

            # Test 3.1: 3D Spatial Analysis & Material Systems - START OF MATERIALIZATION
            TaskType.SPATIAL_ANALYSIS_3D: {
                "phase_requirement": "materialization",
                "trigger_once": True,
                "phase_completion_min": 0.0,   # Trigger at start of materialization
                "phase_completion_max": 40.0   # Don't trigger if materialization is already 40% complete
            },

            # Test 3.2: Realization & Implementation Strategy - MID MATERIALIZATION
            TaskType.REALIZATION_IMPLEMENTATION: {
                "phase_requirement": "materialization",
                "requires_previous": [TaskType.SPATIAL_ANALYSIS_3D],
                "trigger_once": True,
                "phase_completion_min": 40.0,  # Trigger when materialization is 40% complete
                "phase_completion_max": 80.0   # Don't trigger if materialization is already 80% complete
            },

            # Test 4.1: Design Evolution Analysis - LATE IN ANY PHASE (75%+ completion)
            TaskType.DESIGN_EVOLUTION: {
                "phase_requirement": None,  # Can trigger in any phase
                "trigger_once": True,
                "phase_completion_min": 75.0,  # Trigger when any phase is 75% complete
                "phase_completion_max": 90.0   # Don't trigger if phase is already 90% complete
            },

            # Test 4.2: Knowledge Transfer Challenge - VERY LATE IN ANY PHASE (85%+ completion)
            TaskType.KNOWLEDGE_TRANSFER: {
                "phase_requirement": None,  # Can trigger in any phase
                "requires_previous": [TaskType.DESIGN_EVOLUTION],
                "trigger_once": True,
                "phase_completion_min": 85.0,  # Trigger when any phase is 85% complete
                "phase_completion_max": 100.0  # Can trigger up to completion
            }
        }
    
    # REMOVED: _initialize_task_durations - no longer using time-based durations
    # Tasks complete based on phase progression, not time limits
    
    def check_task_triggers(self, user_input: str, conversation_history: List[Dict],
                          current_phase: str, test_group: str,
                          image_uploaded: bool = False, image_analysis: Optional[Dict] = None,
                          phase_completion_percent: float = 0.0) -> Optional[TaskType]:
        """Check if any subtasks should be triggered based on conversation state and threshold crossing"""

        # Clean up expired tasks first
        self._cleanup_expired_tasks()

        # CRITICAL FIX: Update progression history and detect threshold crossings
        last_completion = self.user_progression_history.get(current_phase, 0.0)
        self.user_progression_history[current_phase] = phase_completion_percent

        print(f"🎯 THRESHOLD_CHECK: {current_phase} phase: {last_completion:.1f}% → {phase_completion_percent:.1f}%")

        # Check for threshold crossings and missed tasks
        triggered_tasks = self._detect_threshold_crossings(
            current_phase, last_completion, phase_completion_percent,
            user_input, conversation_history, test_group, image_uploaded, image_analysis
        )

        if triggered_tasks:
            # CRITICAL FIX: Return the most relevant task, not just the first one
            # Priority: Current threshold tasks > Retroactive tasks
            current_threshold_tasks = []
            retroactive_tasks = []

            for task in triggered_tasks:
                conditions = self.task_triggers.get(task, {})
                min_completion = conditions.get("phase_completion_min", 0.0)
                max_completion = conditions.get("phase_completion_max", 100.0)

                # Check if this is a current threshold task (within range)
                if min_completion <= phase_completion_percent <= max_completion:
                    current_threshold_tasks.append(task)
                else:
                    retroactive_tasks.append(task)

            # Return current threshold task first, then retroactive
            if current_threshold_tasks:
                selected_task = current_threshold_tasks[0]
                print(f"🎯 SELECTED: {selected_task.value} (current threshold task)")
                return selected_task
            elif retroactive_tasks:
                selected_task = retroactive_tasks[0]
                print(f"🎯 SELECTED: {selected_task.value} (retroactive task)")
                return selected_task

        return None

    def _is_task_allowed_for_group(self, task_type: TaskType, test_group: str) -> bool:
        """Check if a task is allowed for the specified test group"""

        # MENTOR mode: All 8 tasks allowed
        mentor_tasks = {
            TaskType.ARCHITECTURAL_CONCEPT,      # 1.1
            TaskType.SPATIAL_PROGRAM,           # 1.2
            TaskType.VISUAL_ANALYSIS_2D,        # 2.1
            TaskType.ENVIRONMENTAL_CONTEXTUAL,   # 2.2
            TaskType.SPATIAL_ANALYSIS_3D,       # 3.1
            TaskType.REALIZATION_IMPLEMENTATION, # 3.2
            TaskType.DESIGN_EVOLUTION,          # 4.1
            TaskType.KNOWLEDGE_TRANSFER         # 4.2
        }

        # GENERIC_AI mode: Only 5 tasks allowed
        generic_ai_tasks = {
            TaskType.ARCHITECTURAL_CONCEPT,      # 1.1
            TaskType.VISUAL_ANALYSIS_2D,        # 2.1
            TaskType.SPATIAL_ANALYSIS_3D,       # 3.1
            TaskType.DESIGN_EVOLUTION,          # 4.1
            TaskType.KNOWLEDGE_TRANSFER         # 4.2
        }

        # CONTROL mode: Only 5 tasks allowed
        control_tasks = {
            TaskType.ARCHITECTURAL_CONCEPT,      # 1.1
            TaskType.VISUAL_ANALYSIS_2D,        # 2.1
            TaskType.SPATIAL_ANALYSIS_3D,       # 3.1
            TaskType.DESIGN_EVOLUTION,          # 4.1
            TaskType.KNOWLEDGE_TRANSFER         # 4.2
        }

        if test_group == "MENTOR":
            return task_type in mentor_tasks
        elif test_group == "GENERIC_AI":
            return task_type in generic_ai_tasks
        elif test_group == "CONTROL":
            return task_type in control_tasks
        else:
            # Default to MENTOR tasks for unknown groups
            return task_type in mentor_tasks

    def _detect_threshold_crossings(self, current_phase: str, last_completion: float,
                                   current_completion: float, user_input: str,
                                   conversation_history: List[Dict], test_group: str,
                                   image_uploaded: bool, image_analysis: Optional[Dict]) -> List[TaskType]:
        """Detect tasks that should trigger based on threshold crossings"""

        triggered_tasks = []

        # Get all tasks for the current phase, sorted by trigger threshold
        phase_tasks = []
        for task_type, conditions in self.task_triggers.items():
            if conditions.get("phase_requirement") == current_phase:
                min_completion = conditions.get("phase_completion_min", 0.0)
                phase_tasks.append((task_type, conditions, min_completion))

        # Sort by trigger threshold (earliest tasks first)
        phase_tasks.sort(key=lambda x: x[2])

        print(f"🎯 CHECKING_CROSSINGS: Found {len(phase_tasks)} tasks for {current_phase} phase")

        for task_type, conditions, min_completion in phase_tasks:
            max_completion = conditions.get("phase_completion_max", 100.0)

            # CRITICAL FIX: Check if threshold was crossed OR if we're in the trigger window
            threshold_crossed = (
                last_completion < min_completion <= current_completion or  # Crossed minimum threshold
                (min_completion <= current_completion <= max_completion)   # Currently within trigger range
            )

            # Check if user has already seen this task
            already_triggered = task_type in self.triggered_tasks_by_user
            # CRITICAL FIX: Compare by value to avoid enum identity issues
            already_completed = any(task.task_type.value == task_type.value for task in self.task_history)
            already_active = task_type.value in self.active_tasks

            print(f"   🎯 {task_type.value}: {min_completion:.0f}-{max_completion:.0f}% | "
                  f"Crossed: {threshold_crossed} | Seen: {already_triggered} | "
                  f"Completed: {already_completed} | Active: {already_active}")

            # CRITICAL TEST: Force complete architectural_concept if it's been active too long
            if task_type.value == "architectural_concept" and already_active and already_triggered:
                print(f"🚨 FORCE_COMPLETE_TEST: architectural_concept has been active and seen, forcing completion")
                self.complete_task(task_type, "FORCE COMPLETED - was stuck in active state")
                already_completed = True
                already_active = False

            if threshold_crossed and not already_triggered and not already_completed and not already_active:
                # CRITICAL FIX: Before triggering new task, complete any previously displayed tasks
                self._complete_previously_displayed_tasks()

                # Verify other conditions (prerequisites, image requirements, etc.)
                if self._verify_task_conditions(task_type, conditions, user_input, conversation_history,
                                              current_phase, test_group, image_uploaded, image_analysis):
                    triggered_tasks.append(task_type)
                    self.triggered_tasks_by_user.add(task_type)  # Mark as seen

                    # CRITICAL FIX: Activate the task immediately so it can be displayed
                    activated_task = self.activate_task(
                        task_type=task_type,
                        test_group=test_group,
                        current_phase=current_phase,
                        trigger_reason=f"Triggered at {current_completion:.1f}% completion",
                        phase_completion_percent=current_completion
                    )
                    print(f"   ✅ THRESHOLD_CROSSED: {task_type.value} triggered and activated at {current_completion:.1f}%")
                else:
                    print(f"   ❌ THRESHOLD_CROSSED but conditions not met: {task_type.value}")
            elif current_completion >= min_completion and not already_triggered and not already_completed and not already_active:
                # RETROACTIVE TRIGGERING: User exceeded threshold but never saw the task
                if self._verify_task_conditions(task_type, conditions, user_input, conversation_history,
                                              current_phase, test_group, image_uploaded, image_analysis):
                    triggered_tasks.append(task_type)
                    self.triggered_tasks_by_user.add(task_type)  # Mark as seen

                    # CRITICAL FIX: Activate the task immediately so it can be displayed
                    activated_task = self.activate_task(
                        task_type=task_type,
                        test_group=test_group,
                        current_phase=current_phase,
                        trigger_reason=f"Retroactive trigger at {current_completion:.1f}% completion",
                        phase_completion_percent=current_completion
                    )
                    print(f"   ✅ RETROACTIVE_TRIGGER: {task_type.value} triggered and activated at {current_completion:.1f}% (missed threshold)")

        return triggered_tasks

    def _complete_previously_displayed_tasks(self):
        """Complete any tasks that have been displayed to the user"""
        import streamlit as st

        # Check if there's a displayed task in session state
        active_task_data = st.session_state.get('active_task')
        if active_task_data and (active_task_data.get('displayed', False) or active_task_data.get('display_time')):
            task = active_task_data.get('task')
            if task:
                print(f"🔍 AUTO_COMPLETE: Completing previously displayed task: {task.task_type.value}")

                # Check if already completed to avoid double completion
                already_completed = any(t.task_type.value == task.task_type.value for t in self.task_history)
                if not already_completed:
                    self.complete_task(task.task_type, "Auto-completed before triggering next task")
                    # Clear the session state
                    st.session_state['active_task'] = None
                    print(f"🔍 AUTO_COMPLETE: Task {task.task_type.value} completed and session cleared")
                else:
                    print(f"🔍 AUTO_COMPLETE: Task {task.task_type.value} already completed")

    def _verify_task_conditions(self, task_type: TaskType, conditions: Dict[str, Any],
                               user_input: str, conversation_history: List[Dict],
                               current_phase: str, test_group: str,
                               image_uploaded: bool, image_analysis: Optional[Dict]) -> bool:
        """Verify that task conditions (prerequisites, image requirements, etc.) are met"""

        # Check prerequisite tasks (MANDATORY - must be completed first)
        required_previous = conditions.get("requires_previous", [])
        if required_previous:
            completed_tasks = [task.task_type for task in self.task_history]
            completed_task_values = [task.value for task in completed_tasks]
            required_task_values = [req.value for req in required_previous]

            # CRITICAL FIX: Compare by value to avoid enum identity issues
            if not all(req_value in completed_task_values for req_value in required_task_values):
                print(f"      ❌ Prerequisites not met: {required_task_values}")
                print(f"      ❌ Completed tasks: {completed_task_values}")
                return False

        # Check image upload requirement (MANDATORY for image-based tasks)
        if conditions.get("image_upload", False) and not image_uploaded:
            print(f"      ❌ Image upload required but not provided")
            return False

        # Check image type requirement (MANDATORY for image-based tasks)
        if image_uploaded and image_analysis:
            required_types = conditions.get("image_types", [])
            if required_types:
                image_type = image_analysis.get("image_type", "unknown")
                if image_type not in required_types:
                    print(f"      ❌ Image type {image_type} not in required types: {required_types}")
                    return False

        return True

    def check_phase_transition_tasks(self, from_phase: str, to_phase: str,
                                   user_input: str, conversation_history: List[Dict],
                                   test_group: str, image_uploaded: bool = False,
                                   image_analysis: Optional[Dict] = None) -> List[TaskType]:
        """Check for missed tasks during phase transitions and trigger new phase tasks"""

        triggered_tasks = []

        print(f"🔄 PHASE_TRANSITION: {from_phase} → {to_phase}")

        # 1. Check for missed tasks in the previous phase (retroactive triggering)
        if from_phase in self.user_progression_history:
            final_completion = self.user_progression_history[from_phase]
            print(f"   📊 Final {from_phase} completion: {final_completion:.1f}%")

            # Find all tasks that should have triggered in the previous phase
            for task_type, conditions in self.task_triggers.items():
                if conditions.get("phase_requirement") == from_phase:
                    min_completion = conditions.get("phase_completion_min", 0.0)
                    max_completion = conditions.get("phase_completion_max", 100.0)

                    # Check if user exceeded the trigger range but never saw the task
                    already_triggered = task_type in self.triggered_tasks_by_user
                    # CRITICAL FIX: Compare by value to avoid enum identity issues
                    already_completed = any(task.task_type.value == task_type.value for task in self.task_history)

                    if (final_completion >= min_completion and not already_triggered and not already_completed):
                        if self._verify_task_conditions(task_type, conditions, user_input, conversation_history,
                                                      from_phase, test_group, image_uploaded, image_analysis):
                            triggered_tasks.append(task_type)
                            self.triggered_tasks_by_user.add(task_type)
                            print(f"   ✅ MISSED_TASK_RECOVERY: {task_type.value} from {from_phase} phase")

        # 2. Check for tasks that should trigger at the start of the new phase
        self.user_progression_history[to_phase] = 0.0  # Initialize new phase

        for task_type, conditions in self.task_triggers.items():
            if conditions.get("phase_requirement") == to_phase:
                min_completion = conditions.get("phase_completion_min", 0.0)

                # Trigger tasks that start at 0% of the new phase
                if min_completion == 0.0:
                    already_triggered = task_type in self.triggered_tasks_by_user
                    # CRITICAL FIX: Compare by value to avoid enum identity issues
                    already_completed = any(task.task_type.value == task_type.value for task in self.task_history)
                    already_active = task_type.value in self.active_tasks

                    if not already_triggered and not already_completed and not already_active:
                        if self._verify_task_conditions(task_type, conditions, user_input, conversation_history,
                                                      to_phase, test_group, image_uploaded, image_analysis):
                            triggered_tasks.append(task_type)
                            self.triggered_tasks_by_user.add(task_type)
                            print(f"   ✅ NEW_PHASE_TASK: {task_type.value} for {to_phase} phase start")

        return triggered_tasks

    def _should_trigger_task(self, task_type: TaskType, conditions: Dict[str, Any],
                           user_input: str, conversation_history: List[Dict],
                           current_phase: str, test_group: str,
                           image_uploaded: bool = False, image_analysis: Optional[Dict] = None,
                           phase_completion_percent: float = 0.0) -> bool:
        """Check if specific task should be triggered - MODE-SPECIFIC TASK FILTERING"""

        # CRITICAL: Check if task is allowed for this test group
        if not self._is_task_allowed_for_group(task_type, test_group):
            return False

        # Check if task is already active or completed
        if task_type.value in self.active_tasks:
            return False

        if conditions.get("trigger_once", False):
            # CRITICAL FIX: Compare by value to avoid enum identity issues
            if any(task.task_type.value == task_type.value for task in self.task_history):
                return False

        # Check phase requirement (MANDATORY)
        phase_req = conditions.get("phase_requirement")
        if phase_req and current_phase != phase_req:
            return False

        # Check phase completion requirement (PRIMARY TRIGGER CONDITION)
        min_completion = conditions.get("phase_completion_min", 0.0)
        max_completion = conditions.get("phase_completion_max", 100.0)

        if phase_completion_percent < min_completion:
            return False

        if phase_completion_percent > max_completion:
            # Special case: If phase completion is very high (>80%) and this is a missed task,
            # allow triggering to ensure users don't miss important tasks
            if (phase_completion_percent > 80.0 and
                task_type in [TaskType.SPATIAL_PROGRAM] and
                # CRITICAL FIX: Compare by value to avoid enum identity issues
                not any(task.task_type.value == task_type.value for task in self.task_history)):
                print(f"🎯 LATE_TRIGGER: Allowing {task_type.value} at {phase_completion_percent:.1f}% (missed task recovery)")
            else:
                return False

        # CRITICAL CHANGE: Phase completion in range is sufficient for most tasks
        # Only check additional conditions for special cases

        # Check prerequisite tasks (MANDATORY - must be completed first)
        required_previous = conditions.get("requires_previous", [])
        if required_previous:
            completed_tasks = [task.task_type for task in self.task_history]
            completed_task_values = [task.value for task in completed_tasks]
            required_task_values = [req.value for req in required_previous]

            # CRITICAL FIX: Compare by value to avoid enum identity issues
            if not all(req_value in completed_task_values for req_value in required_task_values):
                return False

        # Check image upload requirement (MANDATORY for image-based tasks)
        if conditions.get("image_upload", False) and not image_uploaded:
            return False

        # Check image type requirement (MANDATORY for image-based tasks)
        if image_uploaded and image_analysis:
            required_types = conditions.get("image_types", [])
            if required_types:
                image_type = image_analysis.get("image_type", "unknown")
                if image_type not in required_types:
                    return False

        # PHASE COMPLETION OVERRIDE: If we reach here and phase completion is in range,
        # trigger the task regardless of keywords or conversation length
        print(f"🎯 TASK TRIGGER: {task_type.value} at {phase_completion_percent:.1f}% completion (range: {min_completion:.0f}-{max_completion:.0f}%)")
        return True
    
    def activate_task(self, task_type: TaskType, test_group: str, current_phase: str,
                     trigger_reason: str, task_data: Optional[Dict[str, Any]] = None,
                     phase_completion_percent: float = 0.0) -> ActiveTask:
        """Activate a new dynamic task - PHASE COMPLETION BASED"""

        # Get phase completion range for this task
        task_conditions = self.task_triggers.get(task_type, {})
        min_completion = task_conditions.get("phase_completion_min", 0.0)
        max_completion = task_conditions.get("phase_completion_max", 100.0)
        phase_range = f"{min_completion:.0f}-{max_completion:.0f}%"

        task = ActiveTask(
            task_type=task_type,
            start_time=datetime.now(),
            test_group=test_group,
            current_phase=current_phase,
            trigger_reason=trigger_reason,
            completion_criteria=self._get_completion_criteria(task_type),
            task_specific_data=task_data or {},
            trigger_phase_completion=phase_completion_percent
        )

        # Store phase completion range in progress indicators
        task.progress_indicators["phase_completion_range"] = phase_range
        task.progress_indicators["triggered_at_completion"] = f"{phase_completion_percent:.1f}%"
        
        self.active_tasks[task_type.value] = task

        print(f"🚨 ACTIVATE_TASK_DEBUG: Added {task_type.value} to active_tasks")
        print(f"🚨 ACTIVATE_TASK_DEBUG: Active tasks after addition: {list(self.active_tasks.keys())}")
        print(f"🚨 ACTIVATE_TASK_DEBUG: Task manager instance ID: {id(self)}")
        print(f"🎯 TASK_MANAGER: Activated {task_type.value} for {test_group} (phase completion: {phase_completion_percent:.1f}%)")

        # CRITICAL FIX: Immediately complete the task to prevent it from getting lost
        # This ensures task progression works and prerequisites are met for subsequent tasks
        print(f"🚨 AUTO_COMPLETE_ON_ACTIVATE: Immediately completing {task_type.value} to ensure progression")
        completion_success = self.complete_task(task_type, f"Auto-completed immediately after activation - {trigger_reason}")
        print(f"🚨 AUTO_COMPLETE_RESULT: {task_type.value} completion = {completion_success}")

        return task
    
    def _get_completion_criteria(self, task_type: TaskType) -> List[str]:
        """Get completion criteria for specific task types"""
        criteria_map = {
            TaskType.ARCHITECTURAL_CONCEPT: [
                "User has articulated initial design concept",
                "Key design principles identified",
                "Community needs addressed"
            ],
            TaskType.SPATIAL_PROGRAM: [
                "Spatial relationships defined",
                "Program elements identified",
                "Circulation patterns considered"
            ],
            TaskType.VISUAL_ANALYSIS_2D: [
                "Visual elements analyzed",
                "Design critique provided",
                "Improvement suggestions offered"
            ],
            TaskType.SPATIAL_ANALYSIS_3D: [
                "3D spatial relationships analyzed",
                "Material systems considered",
                "Construction methodology addressed"
            ],
            TaskType.DESIGN_EVOLUTION: [
                "Design journey reflected upon",
                "Key decisions identified",
                "Learning outcomes articulated"
            ]
        }
        return criteria_map.get(task_type, ["Task completion criteria not defined"])
    
    def complete_task(self, task_type: TaskType, completion_reason: str = "Natural completion"):
        """Mark a task as completed and move to history"""
        print(f"🚨 COMPLETE_TASK_CALLED: Attempting to complete {task_type.value}")
        print(f"🚨 COMPLETE_TASK_CALLED: Task manager instance ID: {id(self)}")
        print(f"🚨 COMPLETE_TASK_CALLED: Active tasks: {list(self.active_tasks.keys())}")
        print(f"🚨 COMPLETE_TASK_CALLED: Task exists in active tasks: {task_type.value in self.active_tasks}")

        if task_type.value in self.active_tasks:
            task = self.active_tasks[task_type.value]
            task.progress_indicators["completion_reason"] = completion_reason
            task.progress_indicators["completion_time"] = datetime.now().isoformat()

            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_type.value]

            print(f"🚨 TASK_COMPLETED_SUCCESS: {task_type.value} - {completion_reason}")
            print(f"🚨 TASK_COMPLETED_SUCCESS: History count: {len(self.task_history)}")
            print(f"🚨 TASK_COMPLETED_SUCCESS: Active tasks now: {list(self.active_tasks.keys())}")
            return True
        else:
            print(f"🚨 COMPLETE_TASK_FAILED: Task {task_type.value} not found in active tasks")
            print(f"🚨 COMPLETE_TASK_FAILED: Available active tasks: {list(self.active_tasks.keys())}")
            return False

    def _auto_complete_task(self, task_type: TaskType, completion_reason: str = "Auto-completed after trigger"):
        """Automatically mark a task as completed to allow subsequent tasks to trigger"""
        from datetime import datetime

        # Create a mock completed task for the task history
        # This allows subsequent tasks with prerequisites to trigger
        mock_task = ActiveTask(
            task_type=task_type,
            start_time=datetime.now(),
            test_group="AUTO",
            current_phase="auto",
            trigger_reason=completion_reason
        )

        mock_task.progress_indicators["completion_reason"] = completion_reason
        mock_task.progress_indicators["completion_time"] = datetime.now().isoformat()
        mock_task.progress_indicators["phase_completion_range"] = "auto"

        # Add to history to satisfy prerequisite checks
        self.task_history.append(mock_task)

        print(f"🔄 TASK_MANAGER: Auto-completed {task_type.value} - {completion_reason}")
    
    def _cleanup_expired_tasks(self):
        """Remove expired tasks and move them to history"""
        print(f"🚨 CLEANUP_DEBUG: Starting cleanup on instance {id(self)}")
        print(f"🚨 CLEANUP_DEBUG: Active tasks before cleanup: {list(self.active_tasks.keys())}")

        expired_tasks = []

        for task_id, task in self.active_tasks.items():
            is_expired = task.is_expired
            print(f"🚨 CLEANUP_DEBUG: Task {task_id} is_expired: {is_expired}")
            if is_expired:
                expired_tasks.append(task_id)

        print(f"🚨 CLEANUP_DEBUG: Found {len(expired_tasks)} expired tasks: {expired_tasks}")

        for task_id in expired_tasks:
            task = self.active_tasks[task_id]
            task.progress_indicators["completion_reason"] = "Time expired"
            task.progress_indicators["completion_time"] = datetime.now().isoformat()

            self.task_history.append(task)
            del self.active_tasks[task_id]

            print(f"🚨 CLEANUP_EXPIRED: Removed expired task {task_id}")

        print(f"🚨 CLEANUP_DEBUG: Active tasks after cleanup: {list(self.active_tasks.keys())}")
    
    def get_active_tasks(self) -> List[ActiveTask]:
        """Get list of currently active tasks"""
        print(f"🚨 GET_ACTIVE_TASKS: Instance {id(self)} has active tasks: {list(self.active_tasks.keys())}")
        self._cleanup_expired_tasks()
        print(f"🚨 GET_ACTIVE_TASKS: After cleanup: {list(self.active_tasks.keys())}")
        return list(self.active_tasks.values())
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get comprehensive task status for debugging/monitoring"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.task_history),
            "active_task_details": {
                task_id: {
                    "type": task.task_type.value,
                    "phase_completion_range": task.phase_completion_range,
                    "triggered_at_completion": task.triggered_at_completion,
                    "test_group": task.test_group,
                    "phase": task.current_phase
                }
                for task_id, task in self.active_tasks.items()
            }
        }
