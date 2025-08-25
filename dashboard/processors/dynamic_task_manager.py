"""
Dynamic Task Manager for Three-Condition Testing
Implements task detection and progression based on test logic documents
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import streamlit as st


class TaskType(Enum):
    """Types of dynamic tasks from test documents"""
    # Test 1.x series - Concept Development
    ARCHITECTURAL_CONCEPT = "architectural_concept"  # Test 1.1
    SPATIAL_PROGRAM = "spatial_program"  # Test 1.2

    # Test 2.x series - Visual Development
    VISUAL_ANALYSIS_2D = "visual_analysis_2d"  # Test 2.1
    ENVIRONMENTAL_CONTEXTUAL = "environmental_contextual"  # Test 2.2

    # Test 3.x series - 3D and Material Systems
    SPATIAL_ANALYSIS_3D = "spatial_analysis_3d"  # Test 3.1
    REALIZATION_IMPLEMENTATION = "realization_implementation"  # Test 3.2

    # Test 4.x series - Reflection and Evolution
    DESIGN_EVOLUTION = "design_evolution"  # Test 4.1
    KNOWLEDGE_TRANSFER = "knowledge_transfer"  # Test 4.2


@dataclass
class ActiveTask:
    """Represents an active dynamic task"""
    task_type: TaskType
    start_time: datetime
    duration_minutes: int  # Keep for reference but don't use for expiration
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
    def time_remaining(self) -> int:
        """Deprecated - tasks are not time-based"""
        return 0  # Always return 0 since we don't use time-based expiration

    @property
    def phase_completion_range(self) -> str:
        """Get the phase completion range for this task"""
        # This will be set by the task manager based on trigger conditions
        return self.progress_indicators.get("phase_completion_range", "Unknown")


class DynamicTaskManager:
    """Manages dynamic task detection and progression for three-condition testing"""
    
    def __init__(self):
        self.active_tasks: Dict[str, ActiveTask] = {}
        self.task_history: List[ActiveTask] = []
        self.task_triggers = self._initialize_task_triggers()
        self.task_durations = self._initialize_task_durations()
        
    def _initialize_task_triggers(self) -> Dict[TaskType, Dict[str, Any]]:
        """Initialize task trigger conditions based on phase completion percentages"""
        return {
            # Test 1.1: Architectural Concept Development - START OF IDEATION
            TaskType.ARCHITECTURAL_CONCEPT: {
                "conversation_length": 1,  # Trigger after first exchange
                "keywords": ["concept", "idea", "approach", "design", "community", "center", "warehouse"],
                "phase_requirement": "ideation",
                "trigger_once": True,
                "phase_completion_min": 0.0,   # Trigger at start of ideation
                "phase_completion_max": 15.0   # Don't trigger if ideation is already 15% complete
            },

            # Test 1.2: Spatial Program Development - MID IDEATION (20-35% completion)
            TaskType.SPATIAL_PROGRAM: {
                "conversation_length": 2,
                "keywords": ["space", "program", "function", "room", "area", "circulation", "spatial"],
                "phase_requirement": "ideation",
                "requires_previous": [TaskType.ARCHITECTURAL_CONCEPT],
                "trigger_once": True,
                "phase_completion_min": 20.0,  # Trigger when ideation is 20% complete
                "phase_completion_max": 35.0   # Don't trigger if ideation is already 35% complete
            },

            # Test 2.1: 2D Design Development & Analysis - START OF VISUALIZATION
            TaskType.VISUAL_ANALYSIS_2D: {
                "image_upload": True,
                "image_types": ["floor_plan", "elevation", "section", "sketch"],
                "phase_requirement": "visualization",
                "trigger_once": False,  # Can trigger multiple times
                "conversation_length": 0,  # No conversation length requirement for image uploads
                "phase_completion_min": 0.0,   # Trigger immediately when visualization starts
                "phase_completion_max": 50.0   # Trigger in first half of visualization
            },

            # Test 2.2: Environmental & Contextual Integration - MID VISUALIZATION
            TaskType.ENVIRONMENTAL_CONTEXTUAL: {
                "conversation_length": 3,
                "keywords": ["environment", "context", "site", "climate", "surroundings", "integration"],
                "phase_requirement": "visualization",
                "trigger_once": True,
                "phase_completion_min": 30.0,  # Trigger when visualization is 30% complete
                "phase_completion_max": 70.0   # Don't trigger if visualization is already 70% complete
            },

            # Test 3.1: 3D Spatial Analysis & Material Systems - START OF MATERIALIZATION
            TaskType.SPATIAL_ANALYSIS_3D: {
                "conversation_length": 1,
                "keywords": ["material", "structure", "construction", "3d", "volume", "technical", "building"],
                "phase_requirement": "materialization",
                "trigger_once": True,
                "phase_completion_min": 0.0,   # Trigger at start of materialization
                "phase_completion_max": 40.0   # Don't trigger if materialization is already 40% complete
            },

            # Test 3.2: Realization & Implementation Strategy - MID MATERIALIZATION
            TaskType.REALIZATION_IMPLEMENTATION: {
                "conversation_length": 2,
                "keywords": ["implementation", "realization", "construction", "strategy", "execution", "build"],
                "phase_requirement": "materialization",
                "requires_previous": [TaskType.SPATIAL_ANALYSIS_3D],
                "trigger_once": True,
                "phase_completion_min": 40.0,  # Trigger when materialization is 40% complete
                "phase_completion_max": 80.0   # Don't trigger if materialization is already 80% complete
            },

            # Test 4.1: Design Evolution Analysis - LATE IN ANY PHASE (75%+ completion)
            TaskType.DESIGN_EVOLUTION: {
                "conversation_length": 4,
                "keywords": ["evolution", "change", "development", "progress", "journey", "reflection"],
                "phase_requirement": None,  # Can trigger in any phase
                "trigger_once": True,
                "phase_completion_min": 75.0,  # Trigger when any phase is 75% complete
                "phase_completion_max": 90.0   # Don't trigger if phase is already 90% complete
            },

            # Test 4.2: Knowledge Transfer Challenge - VERY LATE IN ANY PHASE (85%+ completion)
            TaskType.KNOWLEDGE_TRANSFER: {
                "conversation_length": 5,
                "keywords": ["knowledge", "transfer", "learning", "teach", "explain", "share"],
                "phase_requirement": None,  # Can trigger in any phase
                "requires_previous": [TaskType.DESIGN_EVOLUTION],
                "trigger_once": True,
                "phase_completion_min": 85.0,  # Trigger when any phase is 85% complete
                "phase_completion_max": 100.0  # Can trigger up to completion
            }
        }
    
    def _initialize_task_durations(self) -> Dict[TaskType, int]:
        """Initialize task durations based on test documents - FROM ACTUAL TEST DURATIONS"""
        return {
            TaskType.ARCHITECTURAL_CONCEPT: 15,         # Test 1.1: 15 minutes (from document)
            TaskType.SPATIAL_PROGRAM: 10,              # Test 1.2: 10 minutes (from document)
            TaskType.VISUAL_ANALYSIS_2D: 20,           # Test 2.1: 20 minutes (from document)
            TaskType.ENVIRONMENTAL_CONTEXTUAL: 10,     # Test 2.2: 10 minutes (from document)
            TaskType.SPATIAL_ANALYSIS_3D: 20,          # Test 3.1: 20 minutes (from document)
            TaskType.REALIZATION_IMPLEMENTATION: 15,   # Test 3.2: 15 minutes (from document)
            TaskType.DESIGN_EVOLUTION: 10,             # Test 4.1: 10 minutes (from document)
            TaskType.KNOWLEDGE_TRANSFER: 15            # Test 4.2: 15 minutes (from document)
        }
    
    def check_task_triggers(self, user_input: str, conversation_history: List[Dict],
                          current_phase: str, test_group: str,
                          image_uploaded: bool = False, image_analysis: Optional[Dict] = None,
                          phase_completion_percent: float = 0.0) -> Optional[TaskType]:
        """Check if any subtasks should be triggered based on conversation state"""
        
        # Clean up expired tasks first
        self._cleanup_expired_tasks()
        
        # Check each task type for trigger conditions
        for task_type, conditions in self.task_triggers.items():
            if self._should_trigger_task(task_type, conditions, user_input, conversation_history,
                                       current_phase, test_group, image_uploaded, image_analysis, phase_completion_percent):
                return task_type

        return None

    def _should_trigger_task(self, task_type: TaskType, conditions: Dict[str, Any],
                           user_input: str, conversation_history: List[Dict],
                           current_phase: str, test_group: str,
                           image_uploaded: bool = False, image_analysis: Optional[Dict] = None,
                           phase_completion_percent: float = 0.0) -> bool:
        """Check if specific task should be triggered"""
        
        # Check if task is already active or completed
        if task_type.value in self.active_tasks:
            return False
        
        if conditions.get("trigger_once", False):
            if any(task.task_type == task_type for task in self.task_history):
                return False
        
        # Check phase requirement
        phase_req = conditions.get("phase_requirement")
        if phase_req and current_phase != phase_req:
            return False

        # Check phase completion requirement (ENHANCED WITH RANGES)
        min_completion = conditions.get("phase_completion_min", 0.0)
        max_completion = conditions.get("phase_completion_max", 100.0)

        if phase_completion_percent < min_completion:
            return False

        if phase_completion_percent > max_completion:
            return False

        # Check conversation length requirement
        min_length = conditions.get("conversation_length", 0)
        if len(conversation_history) < min_length:
            return False
        
        # Check image upload requirement
        if conditions.get("image_upload", False) and not image_uploaded:
            return False
        
        # Check image type requirement
        if image_uploaded and image_analysis:
            required_types = conditions.get("image_types", [])
            if required_types:
                image_type = image_analysis.get("image_type", "unknown")
                if image_type not in required_types:
                    return False
        
        # Check keyword requirements
        keywords = conditions.get("keywords", [])
        if keywords:
            text_to_check = f"{user_input} {' '.join([msg.get('content', '') for msg in conversation_history[-3:]])}"
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_to_check.lower())
            if keyword_matches < 2:  # Require at least 2 keyword matches
                return False
        
        # Check prerequisite tasks
        required_previous = conditions.get("requires_previous", [])
        if required_previous:
            completed_tasks = [task.task_type for task in self.task_history]
            if not all(req_task in completed_tasks for req_task in required_previous):
                return False
        
        return True
    
    def activate_task(self, task_type: TaskType, test_group: str, current_phase: str,
                     trigger_reason: str, task_data: Optional[Dict[str, Any]] = None,
                     phase_completion_percent: float = 0.0) -> ActiveTask:
        """Activate a new dynamic task"""
        
        duration = self.task_durations.get(task_type, 15)
        
        # Get phase completion range for this task
        task_conditions = self.task_triggers.get(task_type, {})
        min_completion = task_conditions.get("phase_completion_min", 0.0)
        max_completion = task_conditions.get("phase_completion_max", 100.0)
        phase_range = f"{min_completion:.0f}-{max_completion:.0f}%"

        task = ActiveTask(
            task_type=task_type,
            start_time=datetime.now(),
            duration_minutes=duration,  # Keep for reference
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
        
        print(f"🎯 TASK_MANAGER: Activated {task_type.value} for {test_group} ({duration} min)")
        
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
        
        if task_type.value in self.active_tasks:
            task = self.active_tasks[task_type.value]
            task.progress_indicators["completion_reason"] = completion_reason
            task.progress_indicators["completion_time"] = datetime.now().isoformat()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_type.value]
            
            print(f"✅ TASK_MANAGER: Completed {task_type.value} - {completion_reason}")
    
    def _cleanup_expired_tasks(self):
        """Remove expired tasks and move them to history"""
        expired_tasks = []
        
        for task_id, task in self.active_tasks.items():
            if task.is_expired:
                expired_tasks.append(task_id)
        
        for task_id in expired_tasks:
            task = self.active_tasks[task_id]
            task.progress_indicators["completion_reason"] = "Time expired"
            task.progress_indicators["completion_time"] = datetime.now().isoformat()
            
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            print(f"⏰ TASK_MANAGER: Expired task {task_id}")
    
    def get_active_tasks(self) -> List[ActiveTask]:
        """Get list of currently active tasks"""
        self._cleanup_expired_tasks()
        return list(self.active_tasks.values())
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get comprehensive task status for debugging/monitoring"""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.task_history),
            "active_task_details": {
                task_id: {
                    "type": task.task_type.value,
                    "time_remaining": task.time_remaining,
                    "test_group": task.test_group,
                    "phase": task.current_phase
                }
                for task_id, task in self.active_tasks.items()
            }
        }
