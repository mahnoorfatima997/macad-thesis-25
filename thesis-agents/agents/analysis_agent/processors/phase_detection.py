"""
Phase detection processing module for analyzing design phases.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..schemas import DesignPhase, PhaseAnalysis
from ..config import PHASE_INDICATORS, PHASE_WEIGHTS
from ...common import TextProcessor, MetricsCalculator, AgentTelemetry
from state_manager import ArchMentorState


class PhaseDetectionProcessor:
    """
    Processes design phase detection from conversation and visual analysis.
    """
    
    def __init__(self):
        self.telemetry = AgentTelemetry("phase_detection")
        self.text_processor = TextProcessor()
        self.metrics_calculator = MetricsCalculator()
        
    def detect_design_phase(self, state: ArchMentorState, analysis_result: Dict = None) -> Dict[str, Any]:
        """
        Detect current design phase based on conversation and visual indicators.
        """
        self.telemetry.log_agent_start("detect_design_phase")
        
        try:
            # Step 1: Analyze conversation phase indicators
            conversation_analysis = self._analyze_conversation_phase_indicators(state)
            
            # Step 2: Analyze visual phase indicators
            visual_analysis = self._analyze_visual_phase_indicators(state, analysis_result)
            
            # Step 3: Analyze design progression indicators
            progression_analysis = self._analyze_design_progression_indicators(state)
            
            # Step 4: Analyze temporal phase indicators
            temporal_analysis = self._analyze_temporal_phase_indicators(state)
            
            # Step 5: Calculate phase scores
            phase_scores = self._calculate_phase_scores(
                conversation_analysis, visual_analysis, progression_analysis, temporal_analysis
            )
            
            # Step 6: Calculate phase confidence
            phase_confidence = self._calculate_phase_confidence(
                phase_scores, conversation_analysis, visual_analysis
            )
            
            # Step 7: Determine primary phase
            primary_phase = max(phase_scores, key=phase_scores.get)
            
            # Step 8: Analyze phase progression
            phase_progression = self._analyze_phase_progression(state, primary_phase)
            
            # Step 9: Get phase characteristics
            phase_characteristics = self._get_phase_characteristics(primary_phase)
            
            # Step 10: Generate phase recommendations
            phase_recommendations = self._generate_phase_recommendations(
                primary_phase, phase_confidence.get(primary_phase, 0.0)
            )
            
            return {
                "primary_phase": primary_phase,
                "phase_scores": phase_scores,
                "phase_confidence": phase_confidence,
                "conversation_analysis": conversation_analysis,
                "visual_analysis": visual_analysis,
                "progression_analysis": progression_analysis,
                "temporal_analysis": temporal_analysis,
                "phase_progression": phase_progression,
                "phase_characteristics": phase_characteristics,
                "phase_recommendations": phase_recommendations,
                "detection_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.telemetry.log_error("detect_design_phase", str(e))
            return self._fallback_phase_detection(state)
    
    def _analyze_conversation_phase_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze conversation content for phase indicators."""
        try:
            messages = []
            if hasattr(state, 'conversation_history') and state.conversation_history:
                messages = [msg.get('content', '') for msg in state.conversation_history[-10:]]
            
            phase_scores = {}
            for phase, indicators in PHASE_INDICATORS.items():
                conversation_indicators = indicators.get('conversation_indicators', [])
                score = self._calculate_indicator_score(messages, conversation_indicators)
                phase_scores[phase] = score
            
            return {
                "phase_scores": phase_scores,
                "message_count": len(messages),
                "analysis_method": "conversation_indicators"
            }
            
        except Exception as e:
            self.telemetry.log_error("_analyze_conversation_phase_indicators", str(e))
            return {"phase_scores": {}, "message_count": 0, "analysis_method": "fallback"}
    
    def _analyze_visual_phase_indicators(self, state: ArchMentorState, analysis_result: Dict = None) -> Dict[str, Any]:
        """Analyze visual artifacts for phase indicators."""
        try:
            visual_artifacts = []
            if hasattr(state, 'visual_artifacts') and state.visual_artifacts:
                visual_artifacts = [artifact.description for artifact in state.visual_artifacts if hasattr(artifact, 'description')]
            
            # Include analysis results if available
            if analysis_result and 'visual_analysis' in analysis_result:
                visual_content = analysis_result['visual_analysis'].get('description', '')
                if visual_content:
                    visual_artifacts.append(visual_content)
            
            phase_scores = {}
            for phase, indicators in PHASE_INDICATORS.items():
                visual_indicators = indicators.get('visual_indicators', [])
                score = self._calculate_indicator_score(visual_artifacts, visual_indicators)
                phase_scores[phase] = score
            
            return {
                "phase_scores": phase_scores,
                "artifact_count": len(visual_artifacts),
                "analysis_method": "visual_indicators"
            }
            
        except Exception as e:
            self.telemetry.log_error("_analyze_visual_phase_indicators", str(e))
            return {"phase_scores": {}, "artifact_count": 0, "analysis_method": "fallback"}
    
    def _analyze_design_progression_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze design progression patterns."""
        try:
            # Get recent conversation history
            messages = []
            if hasattr(state, 'conversation_history') and state.conversation_history:
                messages = [msg.get('content', '') for msg in state.conversation_history[-5:]]
            
            phase_scores = {}
            for phase, indicators in PHASE_INDICATORS.items():
                design_indicators = indicators.get('design_indicators', [])
                score = self._calculate_indicator_score(messages, design_indicators)
                phase_scores[phase] = score
            
            return {
                "phase_scores": phase_scores,
                "progression_depth": len(messages),
                "analysis_method": "design_progression"
            }
            
        except Exception as e:
            self.telemetry.log_error("_analyze_design_progression_indicators", str(e))
            return {"phase_scores": {}, "progression_depth": 0, "analysis_method": "fallback"}
    
    def _analyze_temporal_phase_indicators(self, state: ArchMentorState) -> Dict[str, Any]:
        """Analyze temporal patterns in conversation."""
        try:
            # Simple temporal analysis based on conversation length and recency
            conversation_length = 0
            if hasattr(state, 'conversation_history') and state.conversation_history:
                conversation_length = len(state.conversation_history)
            
            # Basic temporal scoring (could be enhanced with actual timestamps)
            if conversation_length < 5:
                temporal_phase = "ideation"
                confidence = 0.7
            elif conversation_length < 15:
                temporal_phase = "visualization"
                confidence = 0.6
            else:
                temporal_phase = "materialization"
                confidence = 0.5
            
            phase_scores = {
                "ideation": 0.1,
                "visualization": 0.1,
                "materialization": 0.1
            }
            phase_scores[temporal_phase] = confidence
            
            return {
                "phase_scores": phase_scores,
                "conversation_length": conversation_length,
                "temporal_phase": temporal_phase,
                "analysis_method": "temporal_patterns"
            }
            
        except Exception as e:
            self.telemetry.log_error("_analyze_temporal_phase_indicators", str(e))
            return {"phase_scores": {"ideation": 0.5, "visualization": 0.3, "materialization": 0.2}, "analysis_method": "fallback"}
    
    def _calculate_phase_scores(self, conversation_analysis: Dict, visual_analysis: Dict, 
                               progression_analysis: Dict, temporal_analysis: Dict) -> Dict[str, float]:
        """Calculate weighted phase scores from all analyses."""
        try:
            phase_scores = {"ideation": 0.0, "visualization": 0.0, "materialization": 0.0}
            
            # Get weights from config
            conv_weight = PHASE_WEIGHTS.get("conversation_weight", 0.4)
            visual_weight = PHASE_WEIGHTS.get("visual_weight", 0.3)
            design_weight = PHASE_WEIGHTS.get("design_weight", 0.2)
            temporal_weight = PHASE_WEIGHTS.get("temporal_weight", 0.1)
            
            # Combine scores with weights
            for phase in phase_scores.keys():
                conv_score = conversation_analysis.get("phase_scores", {}).get(phase, 0.0)
                visual_score = visual_analysis.get("phase_scores", {}).get(phase, 0.0)
                design_score = progression_analysis.get("phase_scores", {}).get(phase, 0.0)
                temporal_score = temporal_analysis.get("phase_scores", {}).get(phase, 0.0)
                
                weighted_score = (
                    conv_score * conv_weight +
                    visual_score * visual_weight +
                    design_score * design_weight +
                    temporal_score * temporal_weight
                )
                
                phase_scores[phase] = min(weighted_score, 1.0)  # Cap at 1.0
            
            return phase_scores
            
        except Exception as e:
            self.telemetry.log_error("_calculate_phase_scores", str(e))
            return {"ideation": 0.5, "visualization": 0.3, "materialization": 0.2}
    
    def _calculate_phase_confidence(self, phase_scores: Dict[str, float], 
                                   conversation_analysis: Dict, visual_analysis: Dict) -> Dict[str, float]:
        """Calculate confidence levels for phase detection."""
        try:
            confidence_scores = {}
            threshold = PHASE_WEIGHTS.get("confidence_threshold", 0.6)
            
            for phase, score in phase_scores.items():
                # Base confidence on score relative to threshold
                base_confidence = min(score / threshold, 1.0) if threshold > 0 else 0.5
                
                # Adjust based on data availability
                data_factor = 1.0
                if conversation_analysis.get("message_count", 0) < 3:
                    data_factor *= 0.8
                if visual_analysis.get("artifact_count", 0) == 0:
                    data_factor *= 0.7
                
                confidence_scores[phase] = base_confidence * data_factor
            
            return confidence_scores
            
        except Exception as e:
            self.telemetry.log_error("_calculate_phase_confidence", str(e))
            return {"ideation": 0.5, "visualization": 0.4, "materialization": 0.3}
    
    def _analyze_phase_progression(self, state: ArchMentorState, current_phase: str) -> Dict[str, Any]:
        """Analyze phase progression patterns."""
        try:
            # Simple progression analysis
            progression_data = {
                "current_phase": current_phase,
                "suggested_next_phase": self._get_next_phase(current_phase),
                "progression_readiness": self._assess_progression_readiness(state, current_phase),
                "phase_transitions": self._analyze_phase_transitions(state)
            }
            
            return progression_data
            
        except Exception as e:
            self.telemetry.log_error("_analyze_phase_progression", str(e))
            return self._fallback_phase_progression(state, current_phase)
    
    def _fallback_phase_progression(self, state: ArchMentorState, current_phase: str) -> Dict[str, Any]:
        """Fallback phase progression analysis."""
        return {
            "current_phase": current_phase,
            "suggested_next_phase": "visualization",
            "progression_readiness": 0.5,
            "phase_transitions": [],
            "analysis_method": "fallback"
        }
    
    def _get_phase_characteristics(self, phase: str) -> Dict[str, Any]:
        """Get characteristics of a specific design phase."""
        characteristics = {
            "ideation": {
                "focus": "Concept development and exploration",
                "activities": ["Research", "Brainstorming", "Program analysis", "Site study"],
                "deliverables": ["Concept sketches", "Program diagrams", "Research findings"],
                "mindset": "Exploratory and open-ended"
            },
            "visualization": {
                "focus": "Spatial and formal development",
                "activities": ["Design development", "Spatial planning", "Form exploration"],
                "deliverables": ["Floor plans", "Sections", "3D models", "Renderings"],
                "mindset": "Creative and iterative"
            },
            "materialization": {
                "focus": "Technical resolution and implementation",
                "activities": ["Detail design", "Material specification", "Technical coordination"],
                "deliverables": ["Construction documents", "Details", "Specifications"],
                "mindset": "Analytical and precise"
            }
        }
        
        return characteristics.get(phase, characteristics["visualization"])
    
    def _generate_phase_recommendations(self, phase: str, confidence: float) -> List[str]:
        """Generate recommendations based on current phase and confidence."""
        recommendations = []
        
        if confidence < 0.5:
            recommendations.append("Consider clarifying your design intent and goals")
        
        if phase == "ideation":
            recommendations.extend([
                "Explore multiple conceptual approaches",
                "Research relevant precedents and case studies",
                "Analyze site conditions and user requirements",
                "Develop a clear design philosophy"
            ])
        elif phase == "visualization":
            recommendations.extend([
                "Develop spatial relationships and circulation",
                "Explore form, massing, and proportions",
                "Create diagrams and sketches to test ideas",
                "Consider lighting and material qualities"
            ])
        elif phase == "materialization":
            recommendations.extend([
                "Develop technical details and connections",
                "Specify materials and systems",
                "Address building codes and regulations",
                "Consider construction feasibility and costs"
            ])
        
        return recommendations
    
    def _calculate_indicator_score(self, messages: List[str], indicators: List[str]) -> float:
        """Calculate score based on indicator presence in messages."""
        if not messages or not indicators:
            return 0.0
        
        total_matches = 0
        total_possible = len(messages) * len(indicators)
        
        for message in messages:
            message_lower = message.lower()
            for indicator in indicators:
                if indicator.lower() in message_lower:
                    total_matches += 1
        
        return total_matches / total_possible if total_possible > 0 else 0.0
    
    def _get_next_phase(self, current_phase: str) -> str:
        """Get suggested next phase."""
        phase_order = ["ideation", "visualization", "materialization"]
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
            else:
                return current_phase  # Already at final phase
        except ValueError:
            return "visualization"  # Default fallback
    
    def _assess_progression_readiness(self, state: ArchMentorState, current_phase: str) -> float:
        """Assess readiness to progress to next phase."""
        # Simple heuristic based on conversation depth
        conversation_length = 0
        if hasattr(state, 'conversation_history') and state.conversation_history:
            conversation_length = len(state.conversation_history)
        
        # More conversation indicates more development
        readiness = min(conversation_length / 10.0, 1.0)
        return readiness
    
    def _analyze_phase_transitions(self, state: ArchMentorState) -> List[Dict[str, Any]]:
        """Analyze phase transitions in conversation history."""
        # Simplified implementation - could be enhanced with actual transition detection
        transitions = []
        
        if hasattr(state, 'conversation_history') and state.conversation_history:
            history_length = len(state.conversation_history)
            if history_length > 5:
                transitions.append({
                    "from_phase": "ideation",
                    "to_phase": "visualization",
                    "transition_point": history_length // 2,
                    "confidence": 0.6
                })
        
        return transitions
    
    def _fallback_phase_detection(self, state: ArchMentorState) -> Dict[str, Any]:
        """Fallback phase detection when main analysis fails."""
        return {
            "primary_phase": "visualization",
            "phase_scores": {"ideation": 0.3, "visualization": 0.5, "materialization": 0.2},
            "phase_confidence": {"ideation": 0.4, "visualization": 0.6, "materialization": 0.3},
            "analysis_method": "fallback",
            "detection_timestamp": datetime.now().isoformat()
        } 