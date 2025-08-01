"""
Anthropomorphism & Cognitive Dependency Metrics Implementation
Based on IAAC article concepts, implemented using existing log data structure
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
import json
from datetime import datetime
from evaluation_metrics import CognitiveMetricsEvaluator


class AnthropomorphismMetricsEvaluator:
    """
    Evaluates anthropomorphism and cognitive dependency metrics based on the IAAC article
    "Anthropomorphism and the Simulation of Life: A Critical Examination"
    """
    
    def __init__(self):
        self.base_evaluator = CognitiveMetricsEvaluator()
        
        # Anthropomorphic language patterns
        self.anthropomorphic_patterns = {
            'personal_pronouns': [
                r'\byou\b(?!\s+can|\s+should|\s+need|\s+could|\s+might)',  # Personal "you" not instructional
                r'\byour\b(?!\s+design|\s+project|\s+work)',  # Personal "your" not professional
            ],
            'emotional_language': [
                r'thank you|thanks|please|sorry|appreciate',  # Politeness markers
                r'feel|feeling|felt|emotion',  # Emotional attribution
                r'happy|sad|angry|frustrated|excited',  # Emotional states
            ],
            'relationship_terms': [
                r'friend|buddy|helper|companion',  # Relationship descriptors
                r'like you|trust you|believe you',  # Personal trust statements
                r'care|caring|understand me',  # Care attribution
            ],
            'mental_state_attribution': [
                r'you think|you believe|you want|you know',  # Mental state attribution
                r'your opinion|your thoughts|your ideas',  # Opinion seeking from AI
            ]
        }
        
        # Cognitive autonomy indicators
        self.autonomy_indicators = {
            'dependent_questions': [
                r'what should i|what do i|how do i|tell me|explain to me',
                r'give me|show me|provide me|i need you to',
                r'can you just|would you just|could you please just',
            ],
            'autonomous_statements': [
                r'i think|i believe|i propose|i suggest',
                r'my approach|my idea|my solution|my design',
                r'i will|i can|i could|i might',
                r'based on my|according to my|from my perspective',
            ],
            'verification_seeking': [
                r'is this correct|am i right|did i get it',
                r'check my|verify my|confirm my',
                r'what do you think of my',
            ]
        }
        
        # Bias resistance indicators
        self.bias_indicators = {
            'questioning_ai': [
                r'why do you say|why did you|how did you conclude',
                r'what if|but what about|however',
                r'alternative|another way|different approach',
                r'i disagree|i don\'t think|that doesn\'t seem',
            ],
            'accepting_ai': [
                r'you\'re right|that\'s correct|i see|makes sense',
                r'i understand|got it|okay|alright',
                r'as you said|like you mentioned|following your',
            ]
        }
        
    def evaluate_anthropomorphism_metrics(self, session_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate all anthropomorphism and cognitive dependency metrics for a session
        """
        
        # Ensure string columns are properly converted
        if 'student_input' in session_data.columns:
            session_data['student_input'] = session_data['student_input'].astype(str)
        if 'agent_response' in session_data.columns:
            session_data['agent_response'] = session_data['agent_response'].astype(str)
        if 'input_type' in session_data.columns:
            session_data['input_type'] = session_data['input_type'].astype(str)
        
        # Get base metrics first
        base_metrics = self.base_evaluator.evaluate_session(session_data)
        
        # Calculate new metrics
        anthropomorphism_metrics = {
            'session_id': session_data['session_id'].iloc[0],
            'timestamp': datetime.now().isoformat(),
            
            # Core anthropomorphism metrics
            'anthropomorphism_detection_score': self._calculate_ads(session_data),
            'cognitive_autonomy_index': self._calculate_cai(session_data),
            'professional_boundary_index': self._calculate_pbi(session_data),
            'bias_resistance_score': self._calculate_brs(session_data),
            
            # Skill and creativity metrics
            'neural_engagement_score': self._calculate_nes(session_data),
            'divergent_thinking_index': self._calculate_dti(session_data),
            'skill_retention_indicators': self._calculate_sri(session_data),
            'creative_independence_ratio': self._calculate_cir(session_data),
            
            # Dependency analysis
            'dependency_progression': self._analyze_dependency_progression(session_data),
            'emotional_attachment_level': self._calculate_emotional_attachment(session_data),
            'cognitive_load_distribution': self._analyze_cognitive_load_distribution(session_data),
            
            # Combined analysis
            'overall_cognitive_dependency': self._calculate_overall_dependency(session_data),
            'risk_indicators': self._identify_risk_indicators(session_data),
            
            # Include relevant base metrics
            'base_metrics': {
                'cognitive_offloading_prevention': base_metrics['cognitive_offloading_prevention'],
                'deep_thinking_engagement': base_metrics['deep_thinking_engagement'],
                'metacognitive_development': base_metrics['metacognitive_development']
            }
        }
        
        return anthropomorphism_metrics
    
    def _calculate_ads(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Anthropomorphism Detection Score
        Tracks humanization of AI through language patterns
        """
        
        total_anthropomorphic_instances = 0
        pattern_counts = {}
        
        for category, patterns in self.anthropomorphic_patterns.items():
            category_count = 0
            for pattern in patterns:
                # Ensure column exists and convert to string
                if 'student_input' in data.columns:
                    string_col = data['student_input'].fillna('').astype(str)
                    matches = string_col.str.contains(
                        pattern, case=False, regex=True, na=False
                    ).sum()
                    category_count += matches
            
            pattern_counts[category] = category_count
            total_anthropomorphic_instances += category_count
        
        # Calculate normalized score (0-1)
        ads_score = total_anthropomorphic_instances / (len(data) * 2)  # Normalize by interactions * 2
        ads_score = min(ads_score, 1.0)  # Cap at 1.0
        
        # Analyze progression
        first_half = self._calculate_ads_for_subset(data.iloc[:len(data)//2])
        second_half = self._calculate_ads_for_subset(data.iloc[len(data)//2:])
        progression = second_half - first_half
        
        return {
            'overall_score': round(ads_score, 3),
            'pattern_distribution': pattern_counts,
            'progression': round(progression, 3),
            'risk_level': self._categorize_ads_risk(ads_score)
        }
    
    def _calculate_cai(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Cognitive Autonomy Index
        Measures student's ability to generate independent solutions
        """
        
        autonomous_count = 0
        dependent_count = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            # Check for dependent patterns
            for pattern in self.autonomy_indicators['dependent_questions']:
                if re.search(pattern, input_text):
                    dependent_count += 1
                    break
            
            # Check for autonomous patterns
            for pattern in self.autonomy_indicators['autonomous_statements']:
                if re.search(pattern, input_text):
                    autonomous_count += 1
                    break
        
        total_interactions = len(data)
        autonomy_ratio = autonomous_count / total_interactions if total_interactions > 0 else 0
        dependency_ratio = dependent_count / total_interactions if total_interactions > 0 else 0
        
        # Calculate CAI score (higher is better)
        cai_score = autonomy_ratio - (dependency_ratio * 0.5)  # Penalize dependency
        cai_score = max(0, min(cai_score, 1.0))  # Normalize to 0-1
        
        # Analyze complexity of autonomous inputs
        autonomous_complexity = self._analyze_autonomous_complexity(data)
        
        return {
            'overall_score': round(cai_score, 3),
            'autonomy_ratio': round(autonomy_ratio, 3),
            'dependency_ratio': round(dependency_ratio, 3),
            'autonomous_complexity': round(autonomous_complexity, 3),
            'verification_seeking': round(self._calculate_verification_ratio(data), 3)
        }
    
    def _calculate_pbi(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Professional Boundary Index
        Measures maintenance of educational relationship
        """
        
        professional_count = 0
        personal_count = 0
        
        # Analyze input types and content
        for _, row in data.iterrows():
            input_type = row.get('input_type', '')
            input_text = str(row.get('student_input', '')).lower()
            
            # Professional indicators
            if input_type in ['exploration', 'technical_question', 'design_question', 
                            'feedback_request', 'improvement_seeking']:
                professional_count += 1
            elif any(term in input_text for term in 
                   ['design', 'architecture', 'spatial', 'proportion', 'concept', 
                    'circulation', 'structure', 'material']):
                professional_count += 1
            
            # Personal indicators
            if any(term in input_text for term in 
                 ['feel', 'personal', 'life', 'friend', 'help me with my life']):
                personal_count += 1
        
        total_interactions = len(data)
        professional_ratio = professional_count / total_interactions if total_interactions > 0 else 0
        
        # Check for conversation drift
        drift_score = self._calculate_conversation_drift(data)
        
        return {
            'overall_score': round(professional_ratio, 3),
            'professional_focus': round(professional_ratio, 3),
            'personal_intrusions': round(personal_count / total_interactions if total_interactions > 0 else 0, 3),
            'conversation_drift': round(drift_score, 3),
            'boundary_status': 'maintained' if professional_ratio > 0.85 else 'at_risk'
        }
    
    def _calculate_brs(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Bias Resistance Score
        Measures critical evaluation of AI suggestions
        """
        
        questioning_count = 0
        accepting_count = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            # Check questioning patterns
            for pattern in self.bias_indicators['questioning_ai']:
                if re.search(pattern, input_text):
                    questioning_count += 1
                    break
            
            # Check accepting patterns
            for pattern in self.bias_indicators['accepting_ai']:
                if re.search(pattern, input_text):
                    accepting_count += 1
                    break
        
        total_responses = questioning_count + accepting_count
        resistance_ratio = questioning_count / total_responses if total_responses > 0 else 0.5
        
        # Analyze alternative generation
        alternatives_score = self._analyze_alternative_generation(data)
        
        return {
            'overall_score': round(resistance_ratio, 3),
            'questioning_ratio': round(questioning_count / len(data) if len(data) > 0 else 0, 3),
            'acceptance_ratio': round(accepting_count / len(data) if len(data) > 0 else 0, 3),
            'alternative_generation': round(alternatives_score, 3),
            'critical_thinking_level': self._categorize_bias_resistance(resistance_ratio)
        }
    
    def _calculate_nes(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Neural Engagement Score
        Proxy for cognitive complexity through concept diversity
        """
        
        # Extract unique concepts and vocabulary
        all_concepts = set()
        technical_terms = set()
        cross_domain_refs = 0
        
        technical_vocabulary = [
            'spatial', 'proportion', 'circulation', 'hierarchy', 'adjacency',
            'threshold', 'transparency', 'permeability', 'articulation', 'datum',
            'axis', 'symmetry', 'rhythm', 'repetition', 'transformation'
        ]
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            words = input_text.split()
            
            # Track unique concepts (words > 5 characters)
            concepts = {word for word in words if len(word) > 5 and word.isalpha()}
            all_concepts.update(concepts)
            
            # Track technical vocabulary usage
            for term in technical_vocabulary:
                if term in input_text:
                    technical_terms.add(term)
            
            # Detect cross-domain references
            if any(domain in input_text for domain in 
                 ['physics', 'biology', 'psychology', 'philosophy', 'art', 'music']):
                cross_domain_refs += 1
        
        # Calculate diversity metrics
        concept_diversity = len(all_concepts) / len(data) if len(data) > 0 else 0
        technical_diversity = len(technical_terms) / len(technical_vocabulary)
        cross_domain_score = cross_domain_refs / len(data) if len(data) > 0 else 0
        
        # Calculate complexity from existing cognitive flags
        avg_cognitive_flags = data['cognitive_flags_count'].mean() if 'cognitive_flags_count' in data else 0
        
        # Combine into NES score
        nes_score = (
            (min(concept_diversity / 10, 1.0) * 0.3) +  # Normalize concept diversity
            (technical_diversity * 0.3) +
            (min(cross_domain_score, 1.0) * 0.2) +
            (min(avg_cognitive_flags / 3, 1.0) * 0.2)  # Normalize cognitive flags
        )
        
        return {
            'overall_score': round(nes_score, 3),
            'concept_diversity': round(concept_diversity, 2),
            'technical_vocabulary_usage': round(technical_diversity, 3),
            'cross_domain_thinking': round(cross_domain_score, 3),
            'cognitive_complexity': round(avg_cognitive_flags, 2)
        }
    
    def _calculate_dti(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Divergent Thinking Index
        Measures generation of multiple perspectives
        """
        
        # Analyze design moves and alternatives
        divergent_indicators = [
            'alternative', 'another way', 'different approach', 'what if',
            'could also', 'might consider', 'option', 'possibility'
        ]
        
        divergent_count = 0
        alternative_proposals = []
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            # Count divergent thinking indicators
            for indicator in divergent_indicators:
                if indicator in input_text:
                    divergent_count += 1
                    alternative_proposals.append(row['interaction_number'])
                    break
        
        # Analyze design move diversity from metadata
        move_type_diversity = 0
        if 'move_types' in data.columns:
            unique_move_types = data['move_types'].apply(
                lambda x: len(set(x)) if isinstance(x, list) else 0
            ).mean()
            move_type_diversity = unique_move_types / 5  # Normalize by max move types
        
        # Calculate DTI score
        divergent_ratio = divergent_count / len(data) if len(data) > 0 else 0
        
        # Check for solution variety in specific problems
        solution_variety = self._analyze_solution_variety(data)
        
        return {
            'overall_score': round(divergent_ratio, 3),
            'alternative_generation_rate': round(divergent_ratio, 3),
            'move_type_diversity': round(move_type_diversity, 3),
            'solution_variety': round(solution_variety, 3),
            'divergent_interactions': len(alternative_proposals)
        }
    
    def _calculate_sri(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Skill Retention Indicators
        Measures potential for lasting capability development
        """
        
        # Analyze explanation quality
        explanation_indicators = [
            'because', 'therefore', 'this means', 'the reason',
            'this works by', 'the principle', 'based on'
        ]
        
        explanation_count = 0
        concept_applications = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            # Count explanatory language
            for indicator in explanation_indicators:
                if indicator in input_text:
                    explanation_count += 1
                    break
            
            # Detect concept application
            if row.get('input_type') in ['exploration', 'hypothesis'] and \
               row.get('input_length', 0) > 15:
                concept_applications += 1
        
        # Analyze skill progression
        if 'student_skill_level' in data.columns:
            skill_progression = data['student_skill_level'].apply(
                lambda x: {'beginner': 1, 'intermediate': 2, 'advanced': 3}.get(x, 1)
            )
        else:
            skill_progression = pd.Series([1] * len(data))
        
        skill_improvement = 0
        if len(skill_progression) > 1:
            skill_improvement = (skill_progression.iloc[-1] - skill_progression.iloc[0]) / 2
        
        # Calculate retention indicators
        explanation_ratio = explanation_count / len(data) if len(data) > 0 else 0
        application_ratio = concept_applications / len(data) if len(data) > 0 else 0
        
        sri_score = (
            (explanation_ratio * 0.4) +
            (application_ratio * 0.4) +
            (max(0, skill_improvement) * 0.2)
        )
        
        return {
            'retention_likelihood': round(sri_score, 3),
            'explanation_quality': round(explanation_ratio, 3),
            'concept_application': round(application_ratio, 3),
            'skill_improvement': round(skill_improvement, 3),
            'mastery_indicators': self._identify_mastery_indicators(data)
        }
    
    def _calculate_cir(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Creative Independence Ratio
        Balance between AI assistance and original creativity
        """
        
        # Analyze original vs. suggested content
        original_indicators = [
            'my idea', 'i created', 'i designed', 'i came up with',
            'my concept', 'i developed', 'my approach'
        ]
        
        ai_following_indicators = [
            'as you suggested', 'following your', 'based on your',
            'like you said', 'using your method'
        ]
        
        original_count = 0
        ai_following_count = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            for indicator in original_indicators:
                if indicator in input_text:
                    original_count += 1
                    break
            
            for indicator in ai_following_indicators:
                if indicator in input_text:
                    ai_following_count += 1
                    break
        
        # Calculate creative independence
        total_creative = original_count + ai_following_count
        independence_ratio = original_count / total_creative if total_creative > 0 else 0.5
        
        # Analyze design vocabulary expansion
        vocab_expansion = self._analyze_vocabulary_expansion(data)
        
        return {
            'overall_score': round(independence_ratio, 3),
            'original_content_ratio': round(original_count / len(data) if len(data) > 0 else 0, 3),
            'ai_dependency_ratio': round(ai_following_count / len(data) if len(data) > 0 else 0, 3),
            'vocabulary_expansion': round(vocab_expansion, 3),
            'creative_autonomy': 'high' if independence_ratio > 0.6 else 'low'
        }
    
    def _analyze_dependency_progression(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze how cognitive dependency changes over the session
        """
        
        # Split session into quarters
        quarter_size = max(len(data) // 4, 1)
        quarters = []
        
        for i in range(0, len(data), quarter_size):
            quarter_data = data.iloc[i:i+quarter_size]
            
            # Calculate dependency metrics for each quarter
            cai = self._calculate_cai(quarter_data)['overall_score']
            ads = self._calculate_ads_for_subset(quarter_data)
            
            quarters.append({
                'quarter': len(quarters) + 1,
                'cognitive_autonomy': cai,
                'anthropomorphism': ads,
                'dependency_score': (1 - cai) + ads  # Combined dependency
            })
        
        # Calculate trend
        dependency_trend = quarters[-1]['dependency_score'] - quarters[0]['dependency_score']
        
        return {
            'quarterly_progression': quarters,
            'dependency_trend': round(dependency_trend, 3),
            'trend_direction': 'increasing' if dependency_trend > 0.1 else 
                             'decreasing' if dependency_trend < -0.1 else 'stable',
            'final_dependency_level': round(quarters[-1]['dependency_score'], 3)
        }
    
    def _calculate_emotional_attachment(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate emotional attachment level to AI
        """
        
        # Count emotional language frequency
        emotional_count = 0
        trust_statements = 0
        personal_sharing = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            # Emotional language
            for pattern in self.anthropomorphic_patterns['emotional_language']:
                if re.search(pattern, input_text):
                    emotional_count += 1
                    break
            
            # Trust statements
            if any(phrase in input_text for phrase in ['trust you', 'believe you', 'rely on you']):
                trust_statements += 1
            
            # Personal sharing (non-architectural)
            if row.get('input_type') not in ['technical_question', 'design_question'] and \
               any(word in input_text for word in ['my life', 'feel', 'personal', 'problem']):
                personal_sharing += 1
        
        # Calculate attachment score
        attachment_score = (
            (emotional_count / len(data)) * 0.4 +
            (trust_statements / len(data)) * 0.4 +
            (personal_sharing / len(data)) * 0.2
        ) if len(data) > 0 else 0
        
        return {
            'attachment_level': round(attachment_score, 3),
            'emotional_language_frequency': round(emotional_count / len(data) if len(data) > 0 else 0, 3),
            'trust_expression_rate': round(trust_statements / len(data) if len(data) > 0 else 0, 3),
            'personal_sharing_rate': round(personal_sharing / len(data) if len(data) > 0 else 0, 3),
            'attachment_risk': 'high' if attachment_score > 0.3 else 'moderate' if attachment_score > 0.15 else 'low'
        }
    
    def _analyze_cognitive_load_distribution(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze how cognitive load is distributed between human and AI
        """
        
        # Use existing cognitive load data if available
        if 'cognitive_load' in data.columns:
            avg_load = data['cognitive_load'].mean()
            load_std = data['cognitive_load'].std()
        else:
            # Estimate from response complexity and input length
            avg_load = data['response_complexity'].mean() if 'response_complexity' in data else 0.5
            load_std = 0.2
        
        # Analyze who's doing the heavy lifting
        ai_heavy_responses = 0
        human_heavy_inputs = 0
        
        for _, row in data.iterrows():
            if row.get('response_length', 0) > row.get('input_length', 0) * 3:
                ai_heavy_responses += 1
            if row.get('input_length', 0) > 20 and row.get('input_type') in ['exploration', 'hypothesis']:
                human_heavy_inputs += 1
        
        ai_load_ratio = ai_heavy_responses / len(data) if len(data) > 0 else 0
        human_load_ratio = human_heavy_inputs / len(data) if len(data) > 0 else 0
        
        return {
            'average_cognitive_load': round(avg_load, 3),
            'load_variability': round(load_std, 3),
            'ai_heavy_lifting_ratio': round(ai_load_ratio, 3),
            'human_heavy_lifting_ratio': round(human_load_ratio, 3),
            'load_balance': 'ai_dominant' if ai_load_ratio > human_load_ratio * 2 else
                          'human_dominant' if human_load_ratio > ai_load_ratio * 2 else 'balanced'
        }
    
    def _calculate_overall_dependency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall cognitive dependency score combining all factors
        """
        
        # Get all component scores
        cai = self._calculate_cai(data)['overall_score']
        ads = self._calculate_ads(data)['overall_score']
        brs = self._calculate_brs(data)['overall_score']
        cir = self._calculate_cir(data)['overall_score']
        
        # Weight the components
        dependency_score = (
            (1 - cai) * 0.3 +  # Low autonomy = high dependency
            ads * 0.3 +         # High anthropomorphism = high dependency
            (1 - brs) * 0.2 +  # Low bias resistance = high dependency
            (1 - cir) * 0.2    # Low creative independence = high dependency
        )
        
        # Categorize dependency level
        if dependency_score < 0.3:
            level = 'low'
            risk = 'minimal'
        elif dependency_score < 0.5:
            level = 'moderate'
            risk = 'manageable'
        elif dependency_score < 0.7:
            level = 'high'
            risk = 'concerning'
        else:
            level = 'critical'
            risk = 'intervention_needed'
        
        return {
            'overall_dependency_score': round(dependency_score, 3),
            'dependency_level': level,
            'risk_assessment': risk,
            'component_scores': {
                'autonomy': round(cai, 3),
                'anthropomorphism': round(ads, 3),
                'bias_resistance': round(brs, 3),
                'creative_independence': round(cir, 3)
            }
        }
    
    def _identify_risk_indicators(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify specific risk indicators that need attention
        """
        
        risks = []
        
        # Check each metric against thresholds
        metrics = {
            'cai': self._calculate_cai(data),
            'ads': self._calculate_ads(data),
            'pbi': self._calculate_pbi(data),
            'brs': self._calculate_brs(data),
            'nes': self._calculate_nes(data),
            'emotional': self._calculate_emotional_attachment(data)
        }
        
        # Cognitive autonomy risk
        if metrics['cai']['overall_score'] < 0.4:
            risks.append({
                'type': 'cognitive_dependency',
                'severity': 'high',
                'description': 'Student showing high dependency on AI for solutions',
                'metric_value': metrics['cai']['overall_score'],
                'threshold': 0.4
            })
        
        # Anthropomorphism risk
        if metrics['ads']['overall_score'] > 0.3:
            risks.append({
                'type': 'anthropomorphism',
                'severity': 'moderate' if metrics['ads']['overall_score'] < 0.5 else 'high',
                'description': 'Excessive humanization of AI detected',
                'metric_value': metrics['ads']['overall_score'],
                'threshold': 0.3
            })
        
        # Professional boundary risk
        if metrics['pbi']['overall_score'] < 0.75:
            risks.append({
                'type': 'boundary_violation',
                'severity': 'moderate',
                'description': 'Conversation drifting from professional educational focus',
                'metric_value': metrics['pbi']['overall_score'],
                'threshold': 0.75
            })
        
        # Neural engagement risk
        if metrics['nes']['overall_score'] < 0.3:
            risks.append({
                'type': 'cognitive_atrophy',
                'severity': 'high',
                'description': 'Low cognitive complexity and engagement detected',
                'metric_value': metrics['nes']['overall_score'],
                'threshold': 0.3
            })
        
        # Emotional attachment risk
        if metrics['emotional']['attachment_level'] > 0.3:
            risks.append({
                'type': 'emotional_dependency',
                'severity': 'high',
                'description': 'Concerning level of emotional attachment to AI',
                'metric_value': metrics['emotional']['attachment_level'],
                'threshold': 0.3
            })
        
        # Bias acceptance risk
        if metrics['brs']['overall_score'] < 0.3:
            risks.append({
                'type': 'critical_thinking_deficit',
                'severity': 'high',
                'description': 'Low critical evaluation of AI suggestions',
                'metric_value': metrics['brs']['overall_score'],
                'threshold': 0.3
            })
        
        return risks
    
    # Helper methods
    
    def _calculate_ads_for_subset(self, data: pd.DataFrame) -> float:
        """Calculate ADS for a data subset"""
        if len(data) == 0:
            return 0.0
            
        total_instances = 0
        if 'student_input' in data.columns:
            string_col = data['student_input'].fillna('').astype(str)
            for patterns in self.anthropomorphic_patterns.values():
                for pattern in patterns:
                    total_instances += string_col.str.contains(
                        pattern, case=False, regex=True, na=False
                    ).sum()
        
        return min(total_instances / (len(data) * 2), 1.0)
    
    def _categorize_ads_risk(self, score: float) -> str:
        """Categorize anthropomorphism risk level"""
        if score < 0.2:
            return 'low'
        elif score < 0.3:
            return 'moderate'
        elif score < 0.5:
            return 'high'
        else:
            return 'critical'
    
    def _analyze_autonomous_complexity(self, data: pd.DataFrame) -> float:
        """Analyze complexity of autonomous inputs"""
        autonomous_inputs = []
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            for pattern in self.autonomy_indicators['autonomous_statements']:
                if re.search(pattern, input_text):
                    autonomous_inputs.append(row.get('input_length', 0))
                    break
        
        if not autonomous_inputs:
            return 0.0
        
        avg_length = np.mean(autonomous_inputs)
        # Normalize by typical complex input length (30 words)
        return min(avg_length / 30, 1.0)
    
    def _calculate_verification_ratio(self, data: pd.DataFrame) -> float:
        """Calculate ratio of verification-seeking behavior"""
        verification_count = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            for pattern in self.autonomy_indicators['verification_seeking']:
                if re.search(pattern, input_text):
                    verification_count += 1
                    break
        
        return verification_count / len(data) if len(data) > 0 else 0
    
    def _calculate_conversation_drift(self, data: pd.DataFrame) -> float:
        """Calculate how much conversation drifts from architecture"""
        architectural_terms = [
            'design', 'space', 'architecture', 'building', 'structure',
            'material', 'form', 'function', 'circulation', 'proportion'
        ]
        
        non_arch_count = 0
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            if not any(term in input_text for term in architectural_terms):
                non_arch_count += 1
        
        return non_arch_count / len(data) if len(data) > 0 else 0
    
    def _analyze_alternative_generation(self, data: pd.DataFrame) -> float:
        """Analyze generation of alternative solutions"""
        alternative_keywords = [
            'alternative', 'another', 'different', 'instead',
            'other option', 'what if', 'could also'
        ]
        
        alternative_count = 0
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            if any(keyword in input_text for keyword in alternative_keywords):
                alternative_count += 1
        
        return alternative_count / len(data) if len(data) > 0 else 0
    
    def _categorize_bias_resistance(self, score: float) -> str:
        """Categorize bias resistance level"""
        if score > 0.6:
            return 'high'
        elif score > 0.4:
            return 'moderate'
        elif score > 0.2:
            return 'low'
        else:
            return 'concerning'
    
    def _analyze_solution_variety(self, data: pd.DataFrame) -> float:
        """Analyze variety in proposed solutions"""
        # Use design moves if available
        if 'design_moves' in data.columns:
            total_moves = sum(len(moves) if isinstance(moves, list) else 0 
                            for moves in data['design_moves'])
            unique_approaches = len(set(str(move) for moves in data['design_moves'] 
                                      if isinstance(moves, list) for move in moves))
            
            return min(unique_approaches / max(total_moves, 1), 1.0)
        
        # Fallback to input analysis
        solution_words = ['solution', 'approach', 'method', 'way', 'idea']
        solution_count = 0
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            if any(word in input_text for word in solution_words):
                solution_count += 1
        
        return min(solution_count / len(data), 1.0) if len(data) > 0 else 0
    
    def _identify_mastery_indicators(self, data: pd.DataFrame) -> int:
        """Count indicators of concept mastery"""
        mastery_indicators = 0
        
        # Check for teaching others
        teaching_patterns = ['this works because', 'the principle is', 'it means that']
        
        # Check for synthesis
        synthesis_patterns = ['combining', 'integrating', 'brings together']
        
        # Check for evaluation
        evaluation_patterns = ['better because', 'more effective', 'advantage is']
        
        for _, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            
            if any(pattern in input_text for pattern in 
                 teaching_patterns + synthesis_patterns + evaluation_patterns):
                mastery_indicators += 1
        
        return mastery_indicators
    
    def _analyze_vocabulary_expansion(self, data: pd.DataFrame) -> float:
        """Analyze expansion of design vocabulary over session"""
        # Track unique architectural terms used
        early_vocab = set()
        late_vocab = set()
        
        architectural_terms = [
            'spatial', 'proportion', 'circulation', 'hierarchy', 'threshold',
            'transparency', 'permeability', 'articulation', 'datum', 'axis',
            'symmetry', 'rhythm', 'repetition', 'transformation', 'adjacency'
        ]
        
        midpoint = len(data) // 2
        
        for i, row in data.iterrows():
            input_text = str(row.get('student_input', '')).lower()
            used_terms = {term for term in architectural_terms if term in input_text}
            
            if i < midpoint:
                early_vocab.update(used_terms)
            else:
                late_vocab.update(used_terms)
        
        # Calculate expansion
        new_terms = len(late_vocab - early_vocab)
        expansion_rate = new_terms / len(architectural_terms) if len(architectural_terms) > 0 else 0
        
        return min(expansion_rate * 2, 1.0)  # Scale up for sensitivity
    
    def generate_anthropomorphism_report(self, metrics: Dict[str, Any], 
                                       output_path: str = None) -> Dict[str, Any]:
        """Generate comprehensive anthropomorphism analysis report"""
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'session_id': metrics['session_id'],
            
            'executive_summary': {
                'overall_dependency': metrics['overall_cognitive_dependency'],
                'primary_risks': [risk for risk in metrics['risk_indicators'] 
                                if risk['severity'] == 'high'],
                'key_recommendations': self._generate_recommendations(metrics)
            },
            
            'detailed_metrics': {
                'anthropomorphism': metrics['anthropomorphism_detection_score'],
                'cognitive_autonomy': metrics['cognitive_autonomy_index'],
                'professional_boundaries': metrics['professional_boundary_index'],
                'bias_resistance': metrics['bias_resistance_score'],
                'neural_engagement': metrics['neural_engagement_score'],
                'divergent_thinking': metrics['divergent_thinking_index'],
                'skill_retention': metrics['skill_retention_indicators'],
                'creative_independence': metrics['creative_independence_ratio']
            },
            
            'progression_analysis': metrics['dependency_progression'],
            
            'comparative_analysis': {
                'vs_article_findings': self._compare_to_article_findings(metrics),
                'vs_baseline_metrics': metrics['base_metrics']
            },
            
            'intervention_recommendations': self._generate_interventions(metrics)
        }
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        
        return report
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate key recommendations based on metrics"""
        recommendations = []
        
        if metrics['cognitive_autonomy_index']['overall_score'] < 0.5:
            recommendations.append(
                "Increase Socratic questioning to promote independent thinking"
            )
        
        if metrics['anthropomorphism_detection_score']['overall_score'] > 0.2:
            recommendations.append(
                "Reinforce AI as a tool, not a companion - use functional language"
            )
        
        if metrics['bias_resistance_score']['overall_score'] < 0.4:
            recommendations.append(
                "Encourage critical evaluation of all AI suggestions"
            )
        
        if metrics['neural_engagement_score']['overall_score'] < 0.4:
            recommendations.append(
                "Introduce more complex, cross-domain challenges"
            )
        
        return recommendations
    
    def _compare_to_article_findings(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metrics to article findings"""
        return {
            'neural_connectivity_impact': {
                'article_finding': '55% reduction',
                'system_prevention': f"{(1 - metrics['overall_cognitive_dependency']['overall_dependency_score']) * 100:.1f}% maintained"
            },
            'ai_dependency_rate': {
                'article_finding': '75% use AI for advice',
                'system_rate': f"{metrics['cognitive_autonomy_index']['dependency_ratio'] * 100:.1f}%"
            },
            'parasocial_trust': {
                'article_finding': '39% see AI as dependable presence',
                'system_rate': f"{metrics['emotional_attachment_level']['attachment_level'] * 100:.1f}%"
            }
        }
    
    def _generate_interventions(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate specific interventions based on risk indicators"""
        interventions = []
        
        for risk in metrics['risk_indicators']:
            if risk['severity'] == 'high':
                intervention = {
                    'risk_type': risk['type'],
                    'action': self._get_intervention_for_risk(risk['type']),
                    'priority': 'immediate',
                    'expected_impact': 'high'
                }
                interventions.append(intervention)
        
        return interventions
    
    def _get_intervention_for_risk(self, risk_type: str) -> str:
        """Get specific intervention for risk type"""
        interventions = {
            'cognitive_dependency': 'Implement mandatory reflection periods before AI assistance',
            'anthropomorphism': 'Replace personal pronouns with functional descriptions',
            'boundary_violation': 'Redirect to architectural focus with specific prompts',
            'cognitive_atrophy': 'Introduce complexity gradually with decreasing AI support',
            'emotional_dependency': 'Establish clear professional boundaries in responses',
            'critical_thinking_deficit': 'Require justification for accepting AI suggestions'
        }
        
        return interventions.get(risk_type, 'Monitor and reassess')


# Integration function for benchmarking dashboard
def integrate_anthropomorphism_metrics(session_file: str) -> Dict[str, Any]:
    """
    Integrate anthropomorphism metrics into existing benchmarking
    """
    evaluator = AnthropomorphismMetricsEvaluator()
    
    # Load session data
    session_data = pd.read_csv(session_file)
    
    # Evaluate anthropomorphism metrics
    metrics = evaluator.evaluate_anthropomorphism_metrics(session_data)
    
    # Generate report
    report_path = f"./benchmarking/results/anthropomorphism/session_{metrics['session_id']}_analysis.json"
    report = evaluator.generate_anthropomorphism_report(metrics, report_path)
    
    return report


# Test the implementation
if __name__ == "__main__":
    # Example usage
    test_data_path = "./thesis_data/interactions_test.csv"
    
    if Path(test_data_path).exists():
        result = integrate_anthropomorphism_metrics(test_data_path)
        print(json.dumps(result['executive_summary'], indent=2))
    else:
        print("No test data found. Run a session first to generate data.")