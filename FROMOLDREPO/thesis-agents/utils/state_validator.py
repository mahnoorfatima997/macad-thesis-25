# utils/state_validator.py - State Validation and Error Handling
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging
from datetime import datetime

from state_manager import ArchMentorState, StudentProfile, VisualArtifact

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of state validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

class StateValidator:
    """Validates and safely updates ArchMentorState"""
    
    def __init__(self):
        self.required_fields = [
            "messages", "current_design_brief", "design_phase",
            "student_profile", "session_metrics", "domain"
        ]
        
        self.optional_fields = [
            "visual_artifacts", "current_sketch", "last_agent", "next_agent",
            "agent_context", "domain_config", "show_response_summary",
            "show_scientific_metrics"
        ]
    
    def validate_state(self, state: ArchMentorState) -> ValidationResult:
        """Validate the current state"""
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        for field in self.required_fields:
            if not hasattr(state, field):
                result.is_valid = False
                result.errors.append(f"Missing required field: {field}")
        
        # Validate messages
        if hasattr(state, 'messages') and state.messages:
            if not isinstance(state.messages, list):
                result.is_valid = False
                result.errors.append("Messages must be a list")
            else:
                for i, msg in enumerate(state.messages):
                    if not isinstance(msg, dict):
                        result.errors.append(f"Message {i} must be a dictionary")
                    elif 'role' not in msg or 'content' not in msg:
                        result.errors.append(f"Message {i} missing required fields")
        
        # Validate student profile
        if hasattr(state, 'student_profile'):
            profile_result = self._validate_student_profile(state.student_profile)
            if not profile_result.is_valid:
                result.is_valid = False
                result.errors.extend(profile_result.errors)
            result.warnings.extend(profile_result.warnings)
        
        # Validate session metrics
        if hasattr(state, 'session_metrics'):
            metrics_result = self._validate_session_metrics(state.session_metrics)
            if not metrics_result.is_valid:
                result.is_valid = False
                result.errors.extend(metrics_result.errors)
        
        # Validate visual artifacts
        if hasattr(state, 'visual_artifacts') and state.visual_artifacts:
            artifacts_result = self._validate_visual_artifacts(state.visual_artifacts)
            if not artifacts_result.is_valid:
                result.is_valid = False
                result.errors.extend(artifacts_result.errors)
        
        return result
    
    def _validate_student_profile(self, profile: StudentProfile) -> ValidationResult:
        """Validate student profile"""
        result = ValidationResult(is_valid=True)
        
        # Validate skill level
        valid_skill_levels = ["beginner", "intermediate", "advanced"]
        if profile.skill_level not in valid_skill_levels:
            result.warnings.append(f"Invalid skill level: {profile.skill_level}")
        
        # Validate cognitive load (0-1)
        if not 0 <= profile.cognitive_load <= 1:
            result.is_valid = False
            result.errors.append(f"Cognitive load must be between 0 and 1, got: {profile.cognitive_load}")
        
        # Validate engagement level (0-1)
        if not 0 <= profile.engagement_level <= 1:
            result.is_valid = False
            result.errors.append(f"Engagement level must be between 0 and 1, got: {profile.engagement_level}")
        
        # Validate knowledge gaps and strengths are lists
        if not isinstance(profile.knowledge_gaps, list):
            result.errors.append("Knowledge gaps must be a list")
        if not isinstance(profile.strengths, list):
            result.errors.append("Strengths must be a list")
        
        return result
    
    def _validate_session_metrics(self, metrics: Dict[str, float]) -> ValidationResult:
        """Validate session metrics"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(metrics, dict):
            result.is_valid = False
            result.errors.append("Session metrics must be a dictionary")
            return result
        
        # Validate metric values are numeric
        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                result.errors.append(f"Metric {key} must be numeric, got: {type(value)}")
        
        return result
    
    def _validate_visual_artifacts(self, artifacts: List[VisualArtifact]) -> ValidationResult:
        """Validate visual artifacts"""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(artifacts, list):
            result.is_valid = False
            result.errors.append("Visual artifacts must be a list")
            return result
        
        for i, artifact in enumerate(artifacts):
            if not isinstance(artifact, VisualArtifact):
                result.errors.append(f"Artifact {i} must be a VisualArtifact instance")
                continue
            
            # Validate artifact fields
            if not artifact.id:
                result.errors.append(f"Artifact {i} missing ID")
            if not artifact.type:
                result.errors.append(f"Artifact {i} missing type")
            if not artifact.image_path:
                result.errors.append(f"Artifact {i} missing image path")
        
        return result
    
    def validate_state_update(self, state: ArchMentorState, update: Dict[str, Any]) -> ValidationResult:
        """Validate a state update before applying it"""
        result = ValidationResult(is_valid=True)
        
        # Check for invalid field names
        for field_name in update.keys():
            if field_name not in self.required_fields + self.optional_fields:
                result.warnings.append(f"Unknown field in update: {field_name}")
        
        # Validate specific update types
        if 'messages' in update:
            if not isinstance(update['messages'], list):
                result.is_valid = False
                result.errors.append("Messages update must be a list")
        
        if 'student_profile' in update:
            if not isinstance(update['student_profile'], StudentProfile):
                result.is_valid = False
                result.errors.append("Student profile update must be a StudentProfile instance")
        
        if 'session_metrics' in update:
            if not isinstance(update['session_metrics'], dict):
                result.is_valid = False
                result.errors.append("Session metrics update must be a dictionary")
        
        if 'visual_artifacts' in update:
            if not isinstance(update['visual_artifacts'], list):
                result.is_valid = False
                result.errors.append("Visual artifacts update must be a list")
        
        return result
    
    def safe_state_update(self, state: ArchMentorState, update: Dict[str, Any]) -> ValidationResult:
        """Safely update state with validation"""
        # Validate the update
        validation_result = self.validate_state_update(state, update)
        
        if not validation_result.is_valid:
            logger.error(f"State update validation failed: {validation_result.errors}")
            return validation_result
        
        try:
            # Apply the update
            for key, value in update.items():
                if hasattr(state, key):
                    setattr(state, key, value)
                else:
                    logger.warning(f"Attempted to set unknown field: {key}")
            
            # Validate the updated state
            final_validation = self.validate_state(state)
            if not final_validation.is_valid:
                logger.error(f"State validation failed after update: {final_validation.errors}")
                return final_validation
            
            logger.info("State updated successfully")
            return ValidationResult(is_valid=True)
            
        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Exception during state update: {str(e)}"]
            )
    
    def log_state_error(self, update: Dict[str, Any]):
        """Log state update errors"""
        logger.error(f"Invalid state update attempted: {update}")
    
    def create_state_backup(self, state: ArchMentorState) -> Dict[str, Any]:
        """Create a backup of the current state"""
        backup = {}
        
        # Backup all fields
        for field in self.required_fields + self.optional_fields:
            if hasattr(state, field):
                backup[field] = getattr(state, field)
        
        backup['backup_timestamp'] = datetime.now().isoformat()
        return backup
    
    def restore_state_from_backup(self, state: ArchMentorState, backup: Dict[str, Any]) -> ValidationResult:
        """Restore state from backup"""
        try:
            # Clear current state
            for field in self.required_fields + self.optional_fields:
                if hasattr(state, field):
                    setattr(state, field, None)
            
            # Restore from backup
            for key, value in backup.items():
                if key != 'backup_timestamp' and hasattr(state, key):
                    setattr(state, key, value)
            
            # Validate restored state
            return self.validate_state(state)
            
        except Exception as e:
            logger.error(f"Error restoring state from backup: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Exception during state restoration: {str(e)}"]
            )

class StateMonitor:
    """Monitor state changes and detect anomalies"""
    
    def __init__(self):
        self.state_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
    
    def record_state_change(self, state: ArchMentorState, change_type: str):
        """Record a state change"""
        state_snapshot = {
            'timestamp': datetime.now().isoformat(),
            'change_type': change_type,
            'messages_count': len(state.messages) if hasattr(state, 'messages') else 0,
            'skill_level': state.student_profile.skill_level if hasattr(state, 'student_profile') else None,
            'cognitive_load': state.student_profile.cognitive_load if hasattr(state, 'student_profile') else 0.0,
            'engagement_level': state.student_profile.engagement_level if hasattr(state, 'student_profile') else 0.0
        }
        
        self.state_history.append(state_snapshot)
        
        # Keep history size manageable
        if len(self.state_history) > self.max_history_size:
            self.state_history.pop(0)
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous state changes"""
        anomalies = []
        
        if len(self.state_history) < 2:
            return anomalies
        
        for i in range(1, len(self.state_history)):
            current = self.state_history[i]
            previous = self.state_history[i-1]
            
            # Detect rapid cognitive load changes
            if abs(current['cognitive_load'] - previous['cognitive_load']) > 0.5:
                anomalies.append({
                    'type': 'rapid_cognitive_load_change',
                    'timestamp': current['timestamp'],
                    'change': current['cognitive_load'] - previous['cognitive_load']
                })
            
            # Detect engagement drops
            if current['engagement_level'] < previous['engagement_level'] - 0.3:
                anomalies.append({
                    'type': 'engagement_drop',
                    'timestamp': current['timestamp'],
                    'drop': previous['engagement_level'] - current['engagement_level']
                })
            
            # Detect message count anomalies
            if current['messages_count'] - previous['messages_count'] > 10:
                anomalies.append({
                    'type': 'message_spam',
                    'timestamp': current['timestamp'],
                    'message_increase': current['messages_count'] - previous['messages_count']
                })
        
        return anomalies
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of state history"""
        if not self.state_history:
            return {}
        
        return {
            'total_changes': len(self.state_history),
            'first_change': self.state_history[0]['timestamp'],
            'last_change': self.state_history[-1]['timestamp'],
            'anomalies_detected': len(self.detect_anomalies()),
            'average_cognitive_load': sum(s['cognitive_load'] for s in self.state_history) / len(self.state_history),
            'average_engagement': sum(s['engagement_level'] for s in self.state_history) / len(self.state_history)
        }

# Global state validator instance
state_validator = StateValidator()
state_monitor = StateMonitor()

def validate_and_update_state(state: ArchMentorState, update: Dict[str, Any]) -> bool:
    """Convenience function to validate and update state"""
    result = state_validator.safe_state_update(state, update)
    
    if result.is_valid:
        state_monitor.record_state_change(state, "update")
        return True
    else:
        logger.error(f"State update failed: {result.errors}")
        return False 