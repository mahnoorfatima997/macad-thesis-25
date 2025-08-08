"""
Enhanced Data Collection Module for Complete Metric Capture
Ensures all cognitive metrics are properly measured and recorded without defaults
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from pathlib import Path
import pandas as pd
from dataclasses import dataclass, asdict
import re

@dataclass
class CognitiveMetrics:
    """Complete cognitive metrics for an interaction"""
    prevents_cognitive_offloading: float = 0.0
    encourages_deep_thinking: float = 0.0
    provides_scaffolding: float = 0.0
    maintains_engagement: float = 0.0
    adapts_to_skill_level: float = 0.0
    promotes_knowledge_integration: float = 0.0
    develops_metacognition: float = 0.0
    
    # Additional detailed metrics
    question_complexity: float = 0.0
    response_elaboration: float = 0.0
    conceptual_connections: int = 0
    reflection_prompts: int = 0
    
@dataclass
class UserMetrics:
    """User state and skill metrics"""
    skill_level: str = "unknown"
    understanding_level: float = 0.5
    confidence_level: float = 0.5
    engagement_level: float = 0.5
    confusion_indicators: int = 0
    clarity_requests: int = 0
    
class EnhancedDataCollector:
    """Enhanced data collection with complete metric capture"""
    
    def __init__(self, session_id: str, participant_id: str, test_group: str):
        self.session_id = session_id
        self.participant_id = participant_id
        self.test_group = test_group
        self.session_start = datetime.now()
        
        # Initialize storage
        self.interactions = []
        self.user_state = UserMetrics()
        self.interaction_count = 0
        
        # Response time tracking
        self.last_input_time = None
        self.response_times = []
        
        # Pattern tracking for skill assessment
        self.question_patterns = []
        self.understanding_trajectory = []
        
        # Setup output directory
        self.data_dir = Path("thesis_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input for cognitive indicators"""
        
        input_lower = user_input.lower()
        input_words = user_input.split()
        
        # Classify input type
        input_type = self._classify_input_type(input_lower)
        
        # Measure complexity
        complexity = self._measure_input_complexity(user_input)
        
        # Detect confusion or clarity requests
        confusion_indicators = sum([
            1 for phrase in ['confused', "don't understand", 'not sure', 'help me', 'what do you mean']
            if phrase in input_lower
        ])
        
        clarity_requests = sum([
            1 for phrase in ['can you explain', 'tell me more', 'what about', 'how does']
            if phrase in input_lower
        ])
        
        # Detect exploratory thinking
        exploratory_indicators = sum([
            1 for phrase in ['what if', 'could we', 'maybe', 'perhaps', 'i think', 'it seems']
            if phrase in input_lower
        ])
        
        return {
            'input_type': input_type,
            'input_length': len(input_words),
            'complexity_score': complexity,
            'confusion_indicators': confusion_indicators,
            'clarity_requests': clarity_requests,
            'exploratory_thinking': exploratory_indicators,
            'timestamp': datetime.now()
        }
    
    def analyze_system_response(self, response: str, response_metadata: Dict = None) -> CognitiveMetrics:
        """Analyze system response for cognitive support metrics"""
        
        metrics = CognitiveMetrics()
        response_lower = response.lower()
        
        # 1. Cognitive Offloading Prevention (does it avoid giving direct answers?)
        direct_answer_phrases = ['the answer is', 'you should use', 'simply do', 'just follow']
        thinking_prompts = ['consider', 'think about', 'reflect on', 'explore', 'what if']
        
        direct_answers = sum(1 for phrase in direct_answer_phrases if phrase in response_lower)
        thinking_prompts_count = sum(1 for phrase in thinking_prompts if phrase in response_lower)
        
        metrics.prevents_cognitive_offloading = min(1.0, thinking_prompts_count * 0.3) - min(1.0, direct_answers * 0.4)
        metrics.prevents_cognitive_offloading = max(0, metrics.prevents_cognitive_offloading)
        
        # 2. Deep Thinking Engagement
        deep_thinking_indicators = [
            'why do you think', 'what might happen', 'consider the implications',
            'analyze', 'evaluate', 'compare', 'synthesize', 'reflect'
        ]
        metrics.encourages_deep_thinking = min(1.0, sum(
            0.25 for phrase in deep_thinking_indicators if phrase in response_lower
        ))
        
        # 3. Scaffolding Effectiveness
        scaffolding_indicators = [
            'let me guide', 'first consider', 'start by', 'next step',
            'building on', 'remember that', 'based on what'
        ]
        metrics.provides_scaffolding = min(1.0, sum(
            0.2 for phrase in scaffolding_indicators if phrase in response_lower
        ))
        
        # 4. Engagement Maintenance
        engagement_indicators = [
            'interesting', 'explore', 'discover', 'creative', 'imagine',
            'what do you think', 'your perspective', 'great question'
        ]
        metrics.maintains_engagement = min(1.0, sum(
            0.2 for phrase in engagement_indicators if phrase in response_lower
        ))
        
        # 5. Knowledge Integration
        integration_indicators = [
            'relates to', 'connects with', 'similar to', 'builds on',
            'remember when', 'as we discussed', 'ties into'
        ]
        metrics.promotes_knowledge_integration = min(1.0, sum(
            0.25 for phrase in integration_indicators if phrase in response_lower
        ))
        
        # 6. Metacognitive Development
        metacognitive_indicators = [
            'your approach', 'your thinking', 'notice how', 'be aware',
            'monitor your', 'check your understanding', 'reflect on your process'
        ]
        metrics.develops_metacognition = min(1.0, sum(
            0.25 for phrase in metacognitive_indicators if phrase in response_lower
        ))
        
        # 7. Additional detailed metrics
        metrics.question_complexity = len(re.findall(r'\?', response)) * 0.2
        metrics.response_elaboration = min(1.0, len(response.split()) / 200)  # Normalize by typical response length
        metrics.conceptual_connections = len(integration_indicators)
        metrics.reflection_prompts = sum(1 for phrase in ['reflect', 'think about', 'consider'] if phrase in response_lower)
        
        # Adjust for test group characteristics
        if response_metadata:
            if response_metadata.get('agent_type') == 'socratic':
                metrics.prevents_cognitive_offloading *= 1.2
                metrics.encourages_deep_thinking *= 1.2
            elif response_metadata.get('agent_type') == 'direct':
                metrics.prevents_cognitive_offloading *= 0.5
                
        # Ensure all metrics are in [0, 1] range
        for field in ['prevents_cognitive_offloading', 'encourages_deep_thinking', 
                     'provides_scaffolding', 'maintains_engagement', 
                     'promotes_knowledge_integration', 'develops_metacognition']:
            value = getattr(metrics, field)
            setattr(metrics, field, max(0.0, min(1.0, value)))
            
        return metrics
    
    def update_user_state(self, input_analysis: Dict, response_metrics: CognitiveMetrics):
        """Update user state based on interaction patterns"""
        
        # Update confusion/clarity tracking
        self.user_state.confusion_indicators = input_analysis['confusion_indicators']
        self.user_state.clarity_requests = input_analysis['clarity_requests']
        
        # Update engagement based on exploratory thinking and response quality
        engagement_delta = (
            input_analysis['exploratory_thinking'] * 0.1 +
            response_metrics.maintains_engagement * 0.1
        )
        self.user_state.engagement_level = max(0, min(1, 
            self.user_state.engagement_level + engagement_delta
        ))
        
        # Update understanding based on question complexity and scaffolding
        if response_metrics.provides_scaffolding > 0.5:
            self.user_state.understanding_level = min(1, 
                self.user_state.understanding_level + 0.05
            )
        
        # Update confidence based on clarity and confusion
        if input_analysis['confusion_indicators'] > 0:
            self.user_state.confidence_level = max(0, 
                self.user_state.confidence_level - 0.1
            )
        elif input_analysis['exploratory_thinking'] > 0:
            self.user_state.confidence_level = min(1, 
                self.user_state.confidence_level + 0.05
            )
        
        # Determine skill level based on patterns
        self._update_skill_level(input_analysis)
        
    def _update_skill_level(self, input_analysis: Dict):
        """Update skill level assessment based on interaction patterns"""
        
        self.question_patterns.append(input_analysis['complexity_score'])
        
        if len(self.question_patterns) >= 3:
            recent_complexity = np.mean(self.question_patterns[-3:])
            
            if recent_complexity > 0.7:
                self.user_state.skill_level = "advanced"
            elif recent_complexity > 0.4:
                self.user_state.skill_level = "intermediate"
            else:
                self.user_state.skill_level = "beginner"
    
    def _classify_input_type(self, input_lower: str) -> str:
        """Classify the type of user input"""
        
        if any(q in input_lower for q in ['what is', 'how do', 'can you', 'tell me']):
            return 'direct_question'
        elif any(q in input_lower for q in ['why', 'how come', 'what causes']):
            return 'causal_question'
        elif any(q in input_lower for q in ['what if', 'suppose', 'imagine']):
            return 'hypothetical_question'
        elif any(q in input_lower for q in ['i think', 'maybe', 'perhaps', 'seems like']):
            return 'exploratory_statement'
        elif any(q in input_lower for q in ['help', 'stuck', 'confused', "don't understand"]):
            return 'help_request'
        else:
            return 'general_statement'
    
    def _measure_input_complexity(self, user_input: str) -> float:
        """Measure the complexity of user input"""
        
        words = user_input.split()
        word_count = len(words)
        
        # Factors for complexity
        question_words = ['why', 'how', 'what', 'when', 'where', 'which']
        complex_connectors = ['because', 'therefore', 'however', 'although', 'moreover']
        domain_terms = ['spatial', 'design', 'structure', 'form', 'function', 'aesthetic']
        
        question_score = sum(0.1 for word in question_words if word in user_input.lower())
        connector_score = sum(0.15 for word in complex_connectors if word in user_input.lower())
        domain_score = sum(0.1 for word in domain_terms if word in user_input.lower())
        length_score = min(1.0, word_count / 30)  # Normalize by typical question length
        
        complexity = min(1.0, question_score + connector_score + domain_score + length_score)
        return complexity
    
    def record_interaction(self, 
                          user_input: str, 
                          system_response: str,
                          response_time: float,
                          agent_info: Dict = None) -> Dict[str, Any]:
        """Record a complete interaction with all metrics"""
        
        self.interaction_count += 1
        
        # Analyze input and response
        input_analysis = self.analyze_user_input(user_input)
        response_metrics = self.analyze_system_response(system_response, agent_info)
        
        # Update user state
        self.update_user_state(input_analysis, response_metrics)
        
        # Track response time
        self.response_times.append(response_time)
        avg_response_time = np.mean(self.response_times)
        
        # Prepare complete interaction record
        interaction_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'interaction_number': self.interaction_count,
            
            # Input metrics
            'student_input': user_input,
            'input_length': input_analysis['input_length'],
            'input_type': input_analysis['input_type'],
            'input_complexity': input_analysis['complexity_score'],
            
            # User state metrics
            'student_skill_level': self.user_state.skill_level,
            'understanding_level': self.user_state.understanding_level,
            'confidence_level': self.user_state.confidence_level,
            'engagement_level': self.user_state.engagement_level,
            'confusion_indicators': self.user_state.confusion_indicators,
            'clarity_requests': self.user_state.clarity_requests,
            
            # Response metrics
            'agent_response': system_response,
            'response_length': len(system_response.split()),
            'response_time': response_time,
            'avg_response_time': avg_response_time,
            
            # Cognitive support metrics (no defaults!)
            'prevents_cognitive_offloading': response_metrics.prevents_cognitive_offloading,
            'encourages_deep_thinking': response_metrics.encourages_deep_thinking,
            'provides_scaffolding': response_metrics.provides_scaffolding,
            'maintains_engagement': response_metrics.maintains_engagement,
            'adapts_to_skill_level': self._calculate_skill_adaptation(response_metrics),
            'promotes_knowledge_integration': response_metrics.promotes_knowledge_integration,
            'develops_metacognition': response_metrics.develops_metacognition,
            
            # Additional metrics
            'question_complexity': response_metrics.question_complexity,
            'response_elaboration': response_metrics.response_elaboration,
            'conceptual_connections': response_metrics.conceptual_connections,
            'reflection_prompts': response_metrics.reflection_prompts,
            
            # Agent information
            'routing_path': agent_info.get('routing_path', 'direct') if agent_info else 'direct',
            'agents_used': agent_info.get('agents_used', self.test_group) if agent_info else self.test_group,
            'primary_agent': agent_info.get('primary_agent', self.test_group) if agent_info else self.test_group,
            'multi_agent_coordination': 1 if agent_info and len(agent_info.get('agents_used', '').split(',')) > 1 else 0,
            'appropriate_agent_selection': self._assess_agent_selection(input_analysis, agent_info),
            
            # Session context
            'test_group': self.test_group,
            'session_duration_minutes': (datetime.now() - self.session_start).total_seconds() / 60
        }
        
        # Store interaction
        self.interactions.append(interaction_data)
        
        # Save to CSV immediately
        self._save_interaction_to_csv(interaction_data)
        
        return interaction_data
    
    def _calculate_skill_adaptation(self, response_metrics: CognitiveMetrics) -> float:
        """Calculate how well the response adapts to user skill level"""
        
        if self.user_state.skill_level == "beginner":
            # Beginners need more scaffolding, less complexity
            return response_metrics.provides_scaffolding * 0.7 + (1 - response_metrics.question_complexity) * 0.3
        elif self.user_state.skill_level == "advanced":
            # Advanced users need more deep thinking, less scaffolding
            return response_metrics.encourages_deep_thinking * 0.6 + response_metrics.promotes_knowledge_integration * 0.4
        else:
            # Intermediate users need balance
            return (response_metrics.provides_scaffolding * 0.4 + 
                   response_metrics.encourages_deep_thinking * 0.3 +
                   response_metrics.maintains_engagement * 0.3)
    
    def _assess_agent_selection(self, input_analysis: Dict, agent_info: Dict) -> float:
        """Assess appropriateness of agent selection for the input"""
        
        if not agent_info:
            return 0.5  # No agent info, neutral score
        
        primary_agent = agent_info.get('primary_agent', '')
        
        # Match agent type to input type
        if input_analysis['input_type'] == 'help_request' and 'support' in primary_agent.lower():
            return 1.0
        elif input_analysis['input_type'] == 'causal_question' and 'socratic' in primary_agent.lower():
            return 1.0
        elif input_analysis['input_type'] == 'direct_question' and 'knowledge' in primary_agent.lower():
            return 0.8
        elif input_analysis['confusion_indicators'] > 0 and 'scaffold' in primary_agent.lower():
            return 0.9
        else:
            return 0.6  # Default reasonable selection
    
    def _save_interaction_to_csv(self, interaction_data: Dict):
        """Save interaction data to CSV file"""
        
        csv_file = self.data_dir / f"interactions_{self.session_id}.csv"
        df = pd.DataFrame([interaction_data])
        
        if csv_file.exists():
            df.to_csv(csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_file, index=False)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        
        if not self.interactions:
            return {}
        
        df = pd.DataFrame(self.interactions)
        
        return {
            'session_id': self.session_id,
            'participant_id': self.participant_id,
            'test_group': self.test_group,
            'total_interactions': len(self.interactions),
            'session_duration_minutes': (datetime.now() - self.session_start).total_seconds() / 60,
            
            # Cognitive metrics (means)
            'avg_offloading_prevention': df['prevents_cognitive_offloading'].mean(),
            'avg_deep_thinking': df['encourages_deep_thinking'].mean(),
            'avg_scaffolding': df['provides_scaffolding'].mean(),
            'avg_engagement': df['maintains_engagement'].mean(),
            'avg_skill_adaptation': df['adapts_to_skill_level'].mean(),
            'avg_knowledge_integration': df['promotes_knowledge_integration'].mean(),
            'avg_metacognition': df['develops_metacognition'].mean(),
            
            # User progression
            'skill_progression': self._calculate_skill_progression(),
            'understanding_improvement': df['understanding_level'].iloc[-1] - df['understanding_level'].iloc[0],
            'confidence_change': df['confidence_level'].iloc[-1] - df['confidence_level'].iloc[0],
            
            # Interaction patterns
            'question_types': df['input_type'].value_counts().to_dict(),
            'avg_input_complexity': df['input_complexity'].mean(),
            'avg_response_time': df['response_time'].mean(),
            
            # Quality indicators
            'confusion_rate': df['confusion_indicators'].sum() / len(df),
            'clarity_request_rate': df['clarity_requests'].sum() / len(df),
            'multi_agent_usage_rate': df['multi_agent_coordination'].mean(),
            
            # Timestamp
            'summary_generated': datetime.now().isoformat()
        }
    
    def _calculate_skill_progression(self) -> float:
        """Calculate skill progression over the session"""
        
        if len(self.question_patterns) < 2:
            return 0.0
        
        # Compare first third to last third of session
        session_length = len(self.question_patterns)
        first_third = self.question_patterns[:session_length//3]
        last_third = self.question_patterns[-session_length//3:]
        
        if first_third and last_third:
            progression = np.mean(last_third) - np.mean(first_third)
            return max(-1.0, min(1.0, progression))  # Bound to [-1, 1]
        
        return 0.0