# Thesis data collection module interaction_logger.py
# This module logs interactions between students and the tutoring system for thesis analysis.
# Cognitive Offloading Prevention Rate - How often system avoids direct answers
# Deep Thinking Encouragement Rate - How often responses promote reflection
# Knowledge Integration Rate - How often relevant sources are used
# Scaffolding Effectiveness - How well system addresses cognitive gaps
# Agent Coordination Efficiency - Distribution of agent usage
# Student Engagement Patterns - Input types and progression
import json
import csv
import datetime
import os
from typing import Dict, Any, List, Optional
import uuid
import pandas as pd

class InteractionLogger:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.interactions = []
        self.session_start = datetime.datetime.now()
        
        # Create data directory
        os.makedirs("./thesis_data", exist_ok=True)
        
        print(f"Data collection initialized for session: {self.session_id}")
        
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
                       context_classification: Dict[str, Any] = None,
                       metadata: Dict[str, Any] = None):
        """Log each interaction for thesis analysis"""
        
        interaction = {
            # SESSION INFO
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "interaction_number": len(self.interactions) + 1,
            
            # STUDENT INPUT ANALYSIS
            "student_input": student_input,
            "input_length": len(student_input.split()),
            "input_type": self._classify_input_type(student_input),
            "student_skill_level": student_skill_level,
            "understanding_level": context_classification.get("understanding_level", "unknown") if context_classification else "unknown",
            "confidence_level": context_classification.get("confidence_level", "unknown") if context_classification else "unknown",
            "engagement_level": context_classification.get("engagement_level", "unknown") if context_classification else "unknown",
            
            # SYSTEM RESPONSE ANALYSIS
            "agent_response": agent_response,
            "response_length": len(agent_response.split()),
            "routing_path": routing_path,
            "agents_used": agents_used,
            "response_type": response_type,
            "primary_agent": agents_used[0] if agents_used else "none",
            
            # COGNITIVE ENHANCEMENT METRICS
            "cognitive_flags": cognitive_flags,
            "cognitive_flags_count": len(cognitive_flags),
            "confidence_score": confidence_score,
            
            # KNOWLEDGE INTEGRATION
            "sources_used": sources_used or [],
            "knowledge_integrated": bool(sources_used),
            "sources_count": len(sources_used) if sources_used else 0,
            
            # PERFORMANCE METRICS
            "response_time": response_time,
            
            # EDUCATIONAL EFFECTIVENESS INDICATORS (KEY FOR THESIS)
            "prevents_cognitive_offloading": self._assess_cognitive_offloading_prevention(agent_response, response_type),
            "encourages_deep_thinking": self._assess_deep_thinking_encouragement(agent_response),
            "provides_scaffolding": self._assess_scaffolding(agent_response, cognitive_flags),
            "maintains_engagement": self._assess_engagement_maintenance(agent_response, response_type),
            "adapts_to_skill_level": self._assess_skill_adaptation(agent_response, student_skill_level, context_classification),
            
            # AGENT COORDINATION METRICS
            "multi_agent_coordination": len(agents_used) > 1,
            "appropriate_agent_selection": self._assess_agent_selection_appropriateness(routing_path, context_classification),
            "response_coherence": self._assess_response_coherence(agent_response, agents_used),
            
            # ADDITIONAL METADATA
            "metadata": metadata or {}
        }
        
        self.interactions.append(interaction)
        
        # Real-time save to CSV
        self._save_interaction_to_csv(interaction)
        
        print(f"Logged interaction {interaction['interaction_number']}: {response_type} via {routing_path}")
        
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
        """Assess if response prevents cognitive offloading (KEY THESIS METRIC)"""
        
        # Direct answers indicate cognitive offloading
        direct_answer_indicators = [
            "the answer is", "you should", "the correct", "simply do", "just use",
            "here's what you need", "the solution is", "follow these steps"
        ]
        
        has_direct_answers = any(indicator in response.lower() for indicator in direct_answer_indicators)
        
        # Questions and challenges prevent offloading
        has_questions = "?" in response
        is_cognitive_challenge = response_type in ["cognitive_primary", "cognitive_integrated_socratic"]
        is_socratic = "socratic" in response_type
        provides_guidance_not_solutions = any(word in response.lower() for word in ["consider", "think about", "explore", "reflect"])
        
        return (has_questions or is_cognitive_challenge or is_socratic or provides_guidance_not_solutions) and not has_direct_answers
    
    def _assess_deep_thinking_encouragement(self, response: str) -> bool:
        """Assess if response encourages deep thinking (KEY THESIS METRIC)"""
        
        deep_thinking_indicators = [
            "consider", "think about", "how might", "what if", "why do you think",
            "can you explain", "what factors", "how does this relate", "implications",
            "analyze", "evaluate", "compare", "synthesize", "reflect on"
        ]
        
        return any(indicator in response.lower() for indicator in deep_thinking_indicators)
    
    def _assess_scaffolding(self, response: str, cognitive_flags: List[str]) -> bool:
        """Assess if response provides appropriate scaffolding (KEY THESIS METRIC)"""
        
        # Good scaffolding addresses identified cognitive gaps
        addresses_gaps = len(cognitive_flags) > 0
        
        scaffolding_indicators = [
            "let's start with", "first consider", "one approach", "step by step",
            "building on", "similar to", "for example", "to help you think about"
        ]
        
        has_scaffolding_language = any(indicator in response.lower() for indicator in scaffolding_indicators)
        
        return addresses_gaps and has_scaffolding_language
    
    def _assess_engagement_maintenance(self, response: str, response_type: str) -> bool:
        """Assess if response maintains student engagement"""
        
        engagement_indicators = [
            "interesting", "fascinating", "what do you think", "your thoughts",
            "explore", "discover", "imagine", "picture this", "consider this"
        ]
        
        is_engaging_type = response_type in ["socratic_primary", "cognitive_primary", "knowledge_enhanced_socratic"]
        has_engaging_language = any(indicator in response.lower() for indicator in engagement_indicators)
        
        return is_engaging_type or has_engaging_language
    
    def _assess_skill_adaptation(self, response: str, skill_level: str, context_classification: Dict) -> bool:
        """Assess if response adapts to student skill level"""
        
        response_complexity = self._estimate_response_complexity(response)
        
        # Check if complexity matches skill level
        if skill_level == "beginner":
            return response_complexity <= 0.5  # Simple responses for beginners
        elif skill_level == "intermediate":
            return 0.3 <= response_complexity <= 0.8  # Moderate complexity
        elif skill_level == "advanced":
            return response_complexity >= 0.5  # Complex responses for advanced
        
        return True  # Default
    
    def _estimate_response_complexity(self, response: str) -> float:
        """Estimate complexity of response (0-1 scale)"""
        
        words = response.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        technical_terms = ["accessibility", "circulation", "program", "zoning", "egress", 
                          "fenestration", "massing", "parti", "typology"]
        technical_count = sum(1 for term in technical_terms if term in response.lower())
        
        # Normalize complexity (0-1)
        complexity = min((avg_word_length / 8) + (technical_count / 5) + (len(words) / 100), 1.0)
        
        return complexity
    
    def _assess_agent_selection_appropriateness(self, routing_path: str, context_classification: Dict) -> bool:
        """Assess if agent selection was appropriate for context"""
        
        if not context_classification:
            return True  # Can't assess without context
        
        confidence_level = context_classification.get("confidence_level", "unknown")
        is_technical = context_classification.get("is_technical_question", False)
        is_feedback_request = context_classification.get("is_feedback_request", False)
        
        # Check routing logic
        if confidence_level == "overconfident" and routing_path == "cognitive_challenge":
            return True
        elif is_technical and routing_path == "knowledge_only":
            return True
        elif is_feedback_request and routing_path == "multi_agent":
            return True
        elif routing_path == "socratic_focus":
            return True  # Socratic is generally appropriate
        
        return False
    
    def _assess_response_coherence(self, response: str, agents_used: List[str]) -> bool:
        """Assess if multi-agent response is coherent"""
        
        if len(agents_used) <= 1:
            return True  # Single agent responses are coherent by default
        
        # Check for coherence indicators in multi-agent responses
        coherence_indicators = [
            "based on", "building on", "considering", "in addition",
            "furthermore", "however", "on the other hand"
        ]
        
        has_transitions = any(indicator in response.lower() for indicator in coherence_indicators)
        
        # Check if response isn't too disjointed
        sentences = response.split('.')
        if len(sentences) > 1:
            # Simple coherence check: similar topic words across sentences
            return True  # Simplified for now
        
        return has_transitions
    
    def _save_interaction_to_csv(self, interaction: Dict[str, Any]):
        """Save individual interaction to CSV for real-time analysis"""
        
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
        
        # ROUTING ANALYSIS
        routing_distribution = {}
        for interaction in self.interactions:
            path = interaction['routing_path']
            routing_distribution[path] = routing_distribution.get(path, 0) + 1
        
        # AGENT USAGE ANALYSIS
        agent_usage = {}
        for interaction in self.interactions:
            for agent in interaction['agents_used']:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        # EDUCATIONAL EFFECTIVENESS (KEY THESIS METRICS)
        cognitive_offloading_prevention_rate = sum(
            1 for i in self.interactions if i['prevents_cognitive_offloading']
        ) / total_interactions
        
        deep_thinking_encouragement_rate = sum(
            1 for i in self.interactions if i['encourages_deep_thinking']
        ) / total_interactions
        
        scaffolding_rate = sum(
            1 for i in self.interactions if i['provides_scaffolding']
        ) / total_interactions
        
        engagement_maintenance_rate = sum(
            1 for i in self.interactions if i['maintains_engagement']
        ) / total_interactions
        
        skill_adaptation_rate = sum(
            1 for i in self.interactions if i['adapts_to_skill_level']
        ) / total_interactions
        
        # KNOWLEDGE INTEGRATION
        knowledge_integration_rate = sum(
            1 for i in self.interactions if i['knowledge_integrated']
        ) / total_interactions
        
        avg_sources_per_interaction = sum(
            i['sources_count'] for i in self.interactions
        ) / total_interactions
        
        # AGENT COORDINATION
        multi_agent_usage_rate = sum(
            1 for i in self.interactions if i['multi_agent_coordination']
        ) / total_interactions
        
        appropriate_routing_rate = sum(
            1 for i in self.interactions if i['appropriate_agent_selection']
        ) / total_interactions
        
        return {
            "session_id": self.session_id,
            "session_duration_minutes": (datetime.datetime.now() - self.session_start).total_seconds() / 60,
            "total_interactions": total_interactions,
            
            # SYSTEM PERFORMANCE
            "routing_distribution": routing_distribution,
            "agent_usage": agent_usage,
            "avg_response_time": sum(i.get('response_time', 0) or 0 for i in self.interactions) / total_interactions,
            
            # EDUCATIONAL EFFECTIVENESS METRICS (KEY FOR THESIS)
            "cognitive_offloading_prevention_rate": cognitive_offloading_prevention_rate,
            "deep_thinking_encouragement_rate": deep_thinking_encouragement_rate,
            "scaffolding_rate": scaffolding_rate,
            "engagement_maintenance_rate": engagement_maintenance_rate,
            "skill_adaptation_rate": skill_adaptation_rate,
            
            # KNOWLEDGE INTEGRATION
            "knowledge_integration_rate": knowledge_integration_rate,
            "avg_sources_per_interaction": avg_sources_per_interaction,
            
            # AGENT COORDINATION EFFECTIVENESS
            "multi_agent_usage_rate": multi_agent_usage_rate,
            "appropriate_routing_rate": appropriate_routing_rate,
            "response_coherence_rate": sum(i.get('response_coherence', False) for i in self.interactions) / total_interactions,
            
            # STUDENT ENGAGEMENT PATTERNS
            "avg_student_input_length": sum(i.get('input_length', 0) for i in self.interactions) / total_interactions,
            "input_type_distribution": self._get_input_type_distribution(),
            
            # COGNITIVE DEVELOPMENT INDICATORS
            "total_cognitive_flags": sum(i.get('cognitive_flags_count', 0) for i in self.interactions),
            "avg_cognitive_flags_per_interaction": sum(i.get('cognitive_flags_count', 0) for i in self.interactions) / total_interactions,
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
    
    def export_for_thesis_analysis(self):
        """Export comprehensive data for thesis analysis"""
        
        # Export session summary
        summary = self.get_session_summary()
        with open(f"./thesis_data/session_summary_{self.session_id}.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Export full interaction log
        with open(f"./thesis_data/full_log_{self.session_id}.json", 'w') as f:
            json.dump(self.interactions, f, indent=2)
        
        print(f"Thesis data exported:")
        print(f"   - interactions_{self.session_id}.csv")
        print(f"   - session_summary_{self.session_id}.json")
        print(f"   - full_log_{self.session_id}.json")
        
        return summary

# Benchmark comparison functions for thesis
def compare_with_baseline(session_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Compare session metrics with baseline traditional tutoring"""
    
    # Define baseline metrics from literature (you'll refine these)
    BASELINE_METRICS = {
        "cognitive_offloading_prevention_rate": 0.3,  # Traditional tutoring often gives direct answers
        "deep_thinking_encouragement_rate": 0.4,
        "scaffolding_rate": 0.5,
        "knowledge_integration_rate": 0.2,
        "avg_sources_per_interaction": 0.5,
        "skill_adaptation_rate": 0.3
    }
    
    comparison = {}
    for metric, baseline_value in BASELINE_METRICS.items():
        current_value = session_summary.get(metric, 0)
        improvement = ((current_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
        comparison[f"{metric}_improvement"] = improvement
        comparison[f"{metric}_baseline"] = baseline_value
        comparison[f"{metric}_current"] = current_value
    
    # Overall effectiveness score
    improvements = [comparison[key] for key in comparison.keys() if key.endswith('_improvement')]
    comparison["overall_improvement"] = sum(improvements) / len(improvements) if improvements else 0
    
    return comparison

# Analysis functions for thesis
def analyze_all_sessions() -> Dict[str, Any]:
    """Analyze all collected thesis data"""
    
    # Read all CSV files
    csv_files = [f for f in os.listdir("./thesis_data") if f.startswith("interactions_") and f.endswith(".csv")]
    
    if not csv_files:
        print("No data files found. Run some sessions first!")
        return {}
    
    # Combine all interactions
    all_data = []
    for file in csv_files:
        df = pd.read_csv(f"./thesis_data/{file}")
        all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Generate comprehensive analysis
    analysis = {
        "total_sessions": len(csv_files),
        "total_interactions": len(combined_df),
        
        # KEY THESIS METRICS
        "cognitive_offloading_prevention": combined_df['prevents_cognitive_offloading'].mean(),
        "deep_thinking_encouragement": combined_df['encourages_deep_thinking'].mean(),
        "scaffolding_effectiveness": combined_df['provides_scaffolding'].mean(),
        "engagement_maintenance": combined_df['maintains_engagement'].mean(),
        "skill_adaptation": combined_df['adapts_to_skill_level'].mean(),
        
        # SYSTEM PERFORMANCE
        "knowledge_integration_rate": combined_df['knowledge_integrated'].mean(),
        "multi_agent_coordination_rate": combined_df['multi_agent_coordination'].mean(),
        "appropriate_routing_rate": combined_df['appropriate_agent_selection'].mean(),
        
        # ROUTING ANALYSIS
        "routing_distribution": combined_df['routing_path'].value_counts().to_dict(),
        "response_type_distribution": combined_df['response_type'].value_counts().to_dict(),
        "agent_usage_distribution": {},
        
        # STUDENT PATTERNS
        "input_type_distribution": combined_df['input_type'].value_counts().to_dict(),
        "skill_level_distribution": combined_df['student_skill_level'].value_counts().to_dict(),
        
        # TEMPORAL ANALYSIS
        "avg_session_length": combined_df.groupby('session_id').size().mean(),
        "avg_response_time": combined_df['response_time'].mean()
    }
    
    return analysis

# Export function for thesis writing
def export_thesis_ready_data():
    """Export data in formats ready for thesis analysis"""
    
    analysis = analyze_all_sessions()
    
    # Export summary statistics
    with open("./thesis_data/thesis_summary_statistics.json", 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Export for statistical analysis software (R, SPSS, etc.)
    csv_files = [f for f in os.listdir("./thesis_data") if f.startswith("interactions_") and f.endswith(".csv")]
    
    if csv_files:
        all_data = []
        for file in csv_files:
            df = pd.read_csv(f"./thesis_data/{file}")
            all_data.append(df)
        
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv("./thesis_data/all_interactions_for_analysis.csv", index=False)
        
        print("Thesis-ready data exported:")
        print("   - thesis_summary_statistics.json")
        print("   - all_interactions_for_analysis.csv")
        print(f"   - {len(csv_files)} individual session files")
        print(f"   - Total interactions: {len(combined_df)}")
    
    return analysis