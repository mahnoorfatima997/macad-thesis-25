# data_collection/interaction_logger.py - NEW FILE for thesis data
# ✅ Cognitive Offloading Prevention Rate - How often system avoids direct answers
# ✅ Deep Thinking Encouragement Rate - How often responses promote reflection
# ✅ Knowledge Integration Rate - How often relevant sources are used
# ✅ Scaffolding Effectiveness - How well system addresses cognitive gaps
# ✅ Agent Coordination Efficiency - Distribution of agent usage
# ✅ Student Engagement Patterns - Input types and progression
import json
import csv
import datetime
import os
from typing import Dict, Any, List
import uuid

class InteractionLogger:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.interactions = []
        self.session_start = datetime.datetime.now()
        
        # Create data directory
        os.makedirs("./thesis_data", exist_ok=True)
        
    def log_interaction(self, 
                       student_input: str,
                       agent_response: str,
                       routing_path: str,
                       agents_used: List[str],
                       response_type: str,
                       cognitive_flags: List[str],
                       student_skill_level: str,
                       confidence_score: float,
                       sources_used: List[str] = None,
                       response_time: float = None,
                       metadata: Dict[str, Any] = None):
        """Log each interaction for thesis analysis"""
        
        interaction = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "interaction_number": len(self.interactions) + 1,
            
            # Student Input Analysis
            "student_input": student_input,
            "input_length": len(student_input.split()),
            "input_type": self._classify_input_type(student_input),
            "student_skill_level": student_skill_level,
            
            # System Response Analysis
            "agent_response": agent_response,
            "response_length": len(agent_response.split()),
            "routing_path": routing_path,
            "agents_used": agents_used,
            "response_type": response_type,
            "primary_agent": agents_used[0] if agents_used else "none",
            
            # Cognitive Enhancement Metrics
            "cognitive_flags": cognitive_flags,
            "cognitive_flags_count": len(cognitive_flags),
            "confidence_score": confidence_score,
            
            # Knowledge Integration
            "sources_used": sources_used or [],
            "knowledge_integrated": bool(sources_used),
            "sources_count": len(sources_used) if sources_used else 0,
            
            # Performance Metrics
            "response_time": response_time,
            
            # Educational Effectiveness Indicators
            "prevents_cognitive_offloading": self._assess_cognitive_offloading_prevention(agent_response, response_type),
            "encourages_deep_thinking": self._assess_deep_thinking_encouragement(agent_response),
            "provides_scaffolding": self._assess_scaffolding(agent_response, cognitive_flags),
            
            # Additional metadata
            "metadata": metadata or {}
        }
        
        self.interactions.append(interaction)
        
        # Real-time save to file
        self._save_interaction(interaction)
        
    def _classify_input_type(self, input_text: str) -> str:
        """Classify student input for analysis"""
        input_lower = input_text.lower()
        
        if any(word in input_lower for word in ["review", "feedback", "thoughts", "evaluate"]):
            return "feedback_request"
        elif any(word in input_lower for word in ["improve", "better", "enhance", "fix"]):
            return "improvement_seeking"
        elif any(word in input_lower for word in ["precedents", "examples", "standards", "requirements"]):
            return "knowledge_seeking"
        elif any(word in input_lower for word in ["perfect", "optimal", "best", "obviously"]):
            return "overconfident_statement"
        elif any(word in input_lower for word in ["confused", "unclear", "don't understand"]):
            return "confusion_expression"
        elif "?" in input_text:
            return "direct_question"
        else:
            return "general_statement"
    
    def _assess_cognitive_offloading_prevention(self, response: str, response_type: str) -> bool:
        """Assess if response prevents cognitive offloading"""
        
        # Direct answers indicate cognitive offloading
        direct_answer_indicators = [
            "the answer is", "you should", "the correct", "simply", "just"
        ]
        
        has_direct_answers = any(indicator in response.lower() for indicator in direct_answer_indicators)
        
        # Questions and challenges prevent offloading
        has_questions = "?" in response
        is_cognitive_challenge = response_type == "cognitive_primary"
        is_socratic = response_type in ["socratic_primary", "knowledge_enhanced_socratic"]
        
        return (has_questions or is_cognitive_challenge or is_socratic) and not has_direct_answers
    
    def _assess_deep_thinking_encouragement(self, response: str) -> bool:
        """Assess if response encourages deep thinking"""
        
        deep_thinking_indicators = [
            "consider", "think about", "how might", "what if", "why do you think",
            "can you explain", "what factors", "how does this relate", "implications"
        ]
        
        return any(indicator in response.lower() for indicator in deep_thinking_indicators)
    
    def _assess_scaffolding(self, response: str, cognitive_flags: List[str]) -> bool:
        """Assess if response provides appropriate scaffolding"""
        
        # Good scaffolding addresses identified cognitive gaps
        addresses_gaps = len(cognitive_flags) > 0  # Response was generated based on identified gaps
        
        scaffolding_indicators = [
            "let's start with", "first consider", "one approach", "step by step",
            "building on", "similar to", "for example"
        ]
        
        has_scaffolding_language = any(indicator in response.lower() for indicator in scaffolding_indicators)
        
        return addresses_gaps and has_scaffolding_language
    
    def _save_interaction(self, interaction: Dict[str, Any]):
        """Save individual interaction to CSV"""
        
        filename = f"./thesis_data/interactions_{self.session_id}.csv"
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=interaction.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(interaction)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate session summary for thesis analysis"""
        
        if not self.interactions:
            return {}
        
        total_interactions = len(self.interactions)
        
        # Routing Analysis
        routing_distribution = {}
        for interaction in self.interactions:
            path = interaction['routing_path']
            routing_distribution[path] = routing_distribution.get(path, 0) + 1
        
        # Agent Usage Analysis
        agent_usage = {}
        for interaction in self.interactions:
            for agent in interaction['agents_used']:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        # Educational Effectiveness
        cognitive_offloading_prevention_rate = sum(
            1 for i in self.interactions if i['prevents_cognitive_offloading']
        ) / total_interactions
        
        deep_thinking_encouragement_rate = sum(
            1 for i in self.interactions if i['encourages_deep_thinking']
        ) / total_interactions
        
        scaffolding_rate = sum(
            1 for i in self.interactions if i['provides_scaffolding']
        ) / total_interactions
        
        # Knowledge Integration
        knowledge_integration_rate = sum(
            1 for i in self.interactions if i['knowledge_integrated']
        ) / total_interactions
        
        avg_sources_per_interaction = sum(
            i['sources_count'] for i in self.interactions
        ) / total_interactions
        
        return {
            "session_id": self.session_id,
            "session_duration_minutes": (datetime.datetime.now() - self.session_start).total_seconds() / 60,
            "total_interactions": total_interactions,
            
            # System Performance
            "routing_distribution": routing_distribution,
            "agent_usage": agent_usage,
            "avg_response_time": sum(i.get('response_time', 0) for i in self.interactions) / total_interactions,
            
            # Educational Effectiveness Metrics (KEY FOR THESIS)
            "cognitive_offloading_prevention_rate": cognitive_offloading_prevention_rate,
            "deep_thinking_encouragement_rate": deep_thinking_encouragement_rate,
            "scaffolding_rate": scaffolding_rate,
            "knowledge_integration_rate": knowledge_integration_rate,
            "avg_sources_per_interaction": avg_sources_per_interaction,
            
            # Student Engagement Patterns
            "avg_student_input_length": sum(i['input_length'] for i in self.interactions) / total_interactions,
            "input_type_distribution": self._get_input_type_distribution(),
            
            # Cognitive Development Indicators
            "total_cognitive_flags": sum(i['cognitive_flags_count'] for i in self.interactions),
            "avg_cognitive_flags_per_interaction": sum(i['cognitive_flags_count'] for i in self.interactions) / total_interactions,
            "skill_progression": self._analyze_skill_progression()
        }
    
    def _get_input_type_distribution(self) -> Dict[str, int]:
        """Analyze distribution of input types"""
        distribution = {}
        for interaction in self.interactions:
            input_type = interaction['input_type']
            distribution[input_type] = distribution.get(input_type, 0) + 1
        return distribution
    
    def _analyze_skill_progression(self) -> Dict[str, Any]:
        """Analyze student skill level changes throughout session"""
        skill_levels = [i['student_skill_level'] for i in self.interactions]
        
        return {
            "initial_skill": skill_levels[0] if skill_levels else "unknown",
            "final_skill": skill_levels[-1] if skill_levels else "unknown",
            "skill_changes": len(set(skill_levels)),
            "progression_detected": len(set(skill_levels)) > 1
        }
    
    def export_for_analysis(self):
        """Export comprehensive data for thesis analysis"""
        
        # Export session summary
        summary = self.get_session_summary()
        with open(f"./thesis_data/session_summary_{self.session_id}.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Export full interaction log
        with open(f"./thesis_data/full_log_{self.session_id}.json", 'w') as f:
            json.dump(self.interactions, f, indent=2)
        
        return summary

# Benchmark comparison functions for thesis
def compare_with_baseline(session_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Compare session metrics with baseline traditional tutoring"""
    
    # Define baseline metrics (you'll need to establish these through research)
    BASELINE_METRICS = {
        "cognitive_offloading_prevention_rate": 0.3,  # Traditional tutoring often gives direct answers
        "deep_thinking_encouragement_rate": 0.4,
        "knowledge_integration_rate": 0.2,
        "avg_sources_per_interaction": 0.5
    }
    
    comparison = {}
    for metric, baseline_value in BASELINE_METRICS.items():
        current_value = session_summary.get(metric, 0)
        improvement = ((current_value - baseline_value) / baseline_value) * 100
        comparison[f"{metric}_improvement"] = improvement
    
    return comparison