# User Proficiency Classification System
# This module implements a comprehensive proficiency classification system
# for categorizing users based on their cognitive patterns and learning behaviors

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import warnings
warnings.filterwarnings('ignore')


class UserProficiencyClassifier:
    """Classifies users into proficiency levels based on interaction patterns"""
    
    def __init__(self):
        self.feature_extractor = CognitiveFeatureExtractor()
        self.classifier = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.proficiency_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        self.trained = False
        
    def extract_user_features(self, session_data: pd.DataFrame) -> np.ndarray:
        """Extract comprehensive features from user session data"""
        
        features = []
        
        # 1. Cognitive Performance Features
        cognitive_features = self.feature_extractor.extract_cognitive_features(session_data)
        features.extend(cognitive_features)
        
        # 2. Behavioral Pattern Features
        behavioral_features = self.feature_extractor.extract_behavioral_features(session_data)
        features.extend(behavioral_features)
        
        # 3. Learning Progression Features
        progression_features = self.feature_extractor.extract_progression_features(session_data)
        features.extend(progression_features)
        
        # 4. Interaction Quality Features
        quality_features = self.feature_extractor.extract_quality_features(session_data)
        features.extend(quality_features)
        
        # 5. Temporal Pattern Features
        temporal_features = self.feature_extractor.extract_temporal_features(session_data)
        features.extend(temporal_features)
        
        return np.array(features)
    
    def train_classifier(self, 
                        training_data: List[Tuple[pd.DataFrame, str]],
                        model_type: str = 'ensemble'):
        """Train proficiency classifier on labeled data"""
        
        print("Training user proficiency classifier...")
        
        # Extract features and labels
        X = []
        y = []
        
        for session_data, proficiency_label in training_data:
            features = self.extract_user_features(session_data)
            X.append(features)
            y.append(proficiency_label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train classifier based on model type
        if model_type == 'random_forest':
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
        elif model_type == 'gradient_boosting':
            self.classifier = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif model_type == 'ensemble':
            # Ensemble of multiple classifiers
            self.classifier = VotingClassifierCustom([
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
                ('gb', GradientBoostingClassifier(n_estimators=100, random_state=42))
            ])
        
        # Train the model
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_
        ))
        
        # Cross-validation
        cv_scores = cross_val_score(self.classifier, X_scaled, y_encoded, cv=5)
        print(f"\nCross-validation scores: {cv_scores}")
        print(f"Average CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        self.trained = True
        
        # Feature importance analysis
        if hasattr(self.classifier, 'feature_importances_'):
            self._analyze_feature_importance()
    
    def classify_user(self, session_data: pd.DataFrame) -> Dict[str, Any]:
        """Classify a user's proficiency level"""
        
        if not self.trained:
            raise ValueError("Classifier not trained. Call train_classifier() first.")
        
        # Extract features
        features = self.extract_user_features(session_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Predict proficiency
        prediction = self.classifier.predict(features_scaled)[0]
        proficiency_label = self.label_encoder.inverse_transform([prediction])[0]
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        prob_dict = {
            self.label_encoder.inverse_transform([i])[0]: prob 
            for i, prob in enumerate(probabilities)
        }
        
        # Generate detailed classification report
        classification_result = {
            'proficiency_level': proficiency_label,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict,
            'feature_analysis': self._analyze_user_features(features, proficiency_label),
            'recommendations': self._generate_recommendations(features, proficiency_label),
            'progression_potential': self._assess_progression_potential(features, proficiency_label)
        }
        
        return classification_result
    
    def _analyze_feature_importance(self):
        """Analyze and display feature importance"""
        
        if hasattr(self.classifier, 'feature_importances_'):
            importances = self.classifier.feature_importances_
            feature_names = self.feature_extractor.get_feature_names()
            
            # Sort features by importance
            indices = np.argsort(importances)[::-1]
            
            print("\nTop 10 Most Important Features:")
            for i in range(min(10, len(indices))):
                print(f"{i+1}. {feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
    
    def _analyze_user_features(self, features: np.ndarray, proficiency: str) -> Dict[str, Any]:
        """Analyze user's features relative to proficiency level"""
        
        feature_names = self.feature_extractor.get_feature_names()
        feature_dict = {name: float(value) for name, value in zip(feature_names, features)}
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        # Define expected ranges for each proficiency level
        proficiency_benchmarks = self._get_proficiency_benchmarks()
        benchmarks = proficiency_benchmarks.get(proficiency, {})
        
        for feature_name, value in feature_dict.items():
            if feature_name in benchmarks:
                expected_range = benchmarks[feature_name]
                if value > expected_range[1]:
                    strengths.append({
                        'feature': feature_name,
                        'value': value,
                        'expected': expected_range,
                        'deviation': value - expected_range[1]
                    })
                elif value < expected_range[0]:
                    weaknesses.append({
                        'feature': feature_name,
                        'value': value,
                        'expected': expected_range,
                        'deviation': expected_range[0] - value
                    })
        
        return {
            'strengths': sorted(strengths, key=lambda x: x['deviation'], reverse=True)[:5],
            'weaknesses': sorted(weaknesses, key=lambda x: x['deviation'], reverse=True)[:5],
            'overall_profile': self._generate_profile_summary(feature_dict, proficiency)
        }
    
    def _generate_recommendations(self, features: np.ndarray, proficiency: str) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on classification"""
        
        recommendations = []
        feature_names = self.feature_extractor.get_feature_names()
        feature_dict = {name: value for name, value in zip(feature_names, features)}
        
        # Analyze specific areas for improvement
        if feature_dict.get('cognitive_offload_prevention_rate', 0) < 0.6:
            recommendations.append({
                'area': 'Cognitive Independence',
                'recommendation': 'Focus on developing independent problem-solving skills by resisting the urge to seek immediate answers',
                'priority': 'high'
            })
        
        if feature_dict.get('deep_thinking_rate', 0) < 0.5:
            recommendations.append({
                'area': 'Critical Thinking',
                'recommendation': 'Engage more deeply with design challenges by asking "why" and "how" questions',
                'priority': 'high'
            })
        
        if feature_dict.get('reflection_depth', 0) < 0.4:
            recommendations.append({
                'area': 'Reflective Practice',
                'recommendation': 'Spend more time reflecting on your design decisions and their implications',
                'priority': 'medium'
            })
        
        if proficiency == 'beginner':
            recommendations.append({
                'area': 'Foundation Building',
                'recommendation': 'Focus on understanding basic spatial relationships and design principles',
                'priority': 'high'
            })
        elif proficiency == 'intermediate':
            recommendations.append({
                'area': 'Skill Integration',
                'recommendation': 'Work on connecting different design concepts and applying them holistically',
                'priority': 'medium'
            })
        elif proficiency == 'advanced':
            recommendations.append({
                'area': 'Mastery Development',
                'recommendation': 'Challenge yourself with complex, multi-faceted design problems',
                'priority': 'low'
            })
        
        return recommendations
    
    def _assess_progression_potential(self, features: np.ndarray, current_proficiency: str) -> Dict[str, Any]:
        """Assess potential for progression to next proficiency level"""
        
        feature_names = self.feature_extractor.get_feature_names()
        feature_dict = {name: value for name, value in zip(feature_names, features)}
        
        # Define progression criteria
        progression_criteria = {
            'beginner': {
                'next_level': 'intermediate',
                'requirements': {
                    'cognitive_offload_prevention_rate': 0.6,
                    'deep_thinking_rate': 0.5,
                    'scaffolding_utilization': 0.7,
                    'engagement_consistency': 0.6
                }
            },
            'intermediate': {
                'next_level': 'advanced',
                'requirements': {
                    'cognitive_offload_prevention_rate': 0.8,
                    'deep_thinking_rate': 0.7,
                    'conceptual_integration': 0.6,
                    'independent_exploration': 0.7
                }
            },
            'advanced': {
                'next_level': 'expert',
                'requirements': {
                    'cognitive_offload_prevention_rate': 0.95,
                    'deep_thinking_rate': 0.85,
                    'creative_problem_solving': 0.8,
                    'knowledge_synthesis': 0.8
                }
            }
        }
        
        if current_proficiency not in progression_criteria:
            return {'ready_for_progression': False, 'progress': 0}
        
        criteria = progression_criteria[current_proficiency]
        requirements = criteria['requirements']
        
        # Calculate progress towards next level
        progress_scores = []
        unmet_requirements = []
        
        for req_name, req_value in requirements.items():
            current_value = feature_dict.get(req_name, 0)
            progress = min(current_value / req_value, 1.0)
            progress_scores.append(progress)
            
            if progress < 1.0:
                unmet_requirements.append({
                    'requirement': req_name,
                    'current': current_value,
                    'needed': req_value,
                    'gap': req_value - current_value
                })
        
        overall_progress = np.mean(progress_scores)
        ready_for_progression = overall_progress >= 0.8
        
        return {
            'ready_for_progression': ready_for_progression,
            'next_level': criteria['next_level'],
            'overall_progress': float(overall_progress),
            'progress_breakdown': dict(zip(requirements.keys(), progress_scores)),
            'unmet_requirements': sorted(unmet_requirements, key=lambda x: x['gap'], reverse=True),
            'estimated_sessions_to_progress': self._estimate_sessions_to_progress(overall_progress)
        }
    
    def _estimate_sessions_to_progress(self, current_progress: float) -> int:
        """Estimate number of sessions needed to progress"""
        
        if current_progress >= 0.8:
            return 0
        elif current_progress >= 0.6:
            return 3
        elif current_progress >= 0.4:
            return 7
        else:
            return 12
    
    def _get_proficiency_benchmarks(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Get expected feature ranges for each proficiency level"""
        
        return {
            'beginner': {
                'cognitive_offload_prevention_rate': (0.2, 0.5),
                'deep_thinking_rate': (0.2, 0.4),
                'engagement_consistency': (0.4, 0.6),
                'question_complexity': (0.2, 0.4),
                'reflection_depth': (0.1, 0.3)
            },
            'intermediate': {
                'cognitive_offload_prevention_rate': (0.5, 0.7),
                'deep_thinking_rate': (0.4, 0.6),
                'engagement_consistency': (0.6, 0.8),
                'question_complexity': (0.4, 0.6),
                'reflection_depth': (0.3, 0.5)
            },
            'advanced': {
                'cognitive_offload_prevention_rate': (0.7, 0.9),
                'deep_thinking_rate': (0.6, 0.8),
                'engagement_consistency': (0.8, 0.95),
                'question_complexity': (0.6, 0.8),
                'reflection_depth': (0.5, 0.7)
            },
            'expert': {
                'cognitive_offload_prevention_rate': (0.9, 1.0),
                'deep_thinking_rate': (0.8, 1.0),
                'engagement_consistency': (0.95, 1.0),
                'question_complexity': (0.8, 1.0),
                'reflection_depth': (0.7, 1.0)
            }
        }
    
    def _generate_profile_summary(self, features: Dict[str, float], proficiency: str) -> str:
        """Generate a narrative summary of the user's profile"""
        
        summaries = {
            'beginner': "Shows foundational understanding with room for growth in critical thinking and independent problem-solving.",
            'intermediate': "Demonstrates solid grasp of concepts with developing ability to integrate knowledge and think critically.",
            'advanced': "Exhibits strong analytical skills and consistent engagement with complex design challenges.",
            'expert': "Displays mastery-level thinking with exceptional ability to synthesize knowledge and solve novel problems."
        }
        
        base_summary = summaries.get(proficiency, "Profile under development.")
        
        # Add specific observations
        if features.get('cognitive_offload_prevention_rate', 0) > 0.8:
            base_summary += " Excellent at independent thinking."
        
        if features.get('engagement_consistency', 0) > 0.9:
            base_summary += " Maintains exceptional focus throughout sessions."
        
        return base_summary
    
    def save_model(self, path: str):
        """Save trained classifier and associated components"""
        
        if not self.trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'feature_extractor': self.feature_extractor,
            'proficiency_levels': self.proficiency_levels
        }
        
        joblib.dump(model_data, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained classifier and components"""
        
        model_data = joblib.load(path)
        
        self.classifier = model_data['classifier']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.feature_extractor = model_data['feature_extractor']
        self.proficiency_levels = model_data['proficiency_levels']
        self.trained = True
        
        print(f"Model loaded from {path}")


class CognitiveFeatureExtractor:
    """Extracts cognitive features from user interaction data"""
    
    def __init__(self):
        self.feature_names = []
        
    def extract_cognitive_features(self, data: pd.DataFrame) -> List[float]:
        """Extract cognitive performance features"""
        
        features = []
        
        # Cognitive offloading prevention
        features.append(data['prevents_cognitive_offloading'].mean())
        features.append(data['prevents_cognitive_offloading'].std())
        
        # Deep thinking engagement
        features.append(data['encourages_deep_thinking'].mean())
        features.append(data['encourages_deep_thinking'].std())
        
        # Scaffolding utilization
        features.append(data['provides_scaffolding'].mean())
        features.append(data['adapts_to_skill_level'].mean())
        
        # Knowledge integration
        features.append(data['knowledge_integrated'].mean())
        features.append(data['sources_count'].mean())
        
        # Update feature names
        self._update_feature_names([
            'cognitive_offload_prevention_rate', 'cognitive_offload_consistency',
            'deep_thinking_rate', 'deep_thinking_consistency',
            'scaffolding_utilization', 'skill_adaptation_rate',
            'knowledge_integration_rate', 'avg_sources_used'
        ])
        
        return features
    
    def extract_behavioral_features(self, data: pd.DataFrame) -> List[float]:
        """Extract behavioral pattern features"""
        
        features = []
        
        # Engagement patterns
        features.append(data['maintains_engagement'].mean())
        engagement_streaks = self._calculate_engagement_streaks(data['maintains_engagement'])
        features.append(np.mean(engagement_streaks) if engagement_streaks else 0)
        
        # Input patterns
        input_type_dist = data['input_type'].value_counts(normalize=True)
        features.append(input_type_dist.get('direct_question', 0))
        features.append(input_type_dist.get('feedback_request', 0))
        features.append(input_type_dist.get('knowledge_seeking', 0))
        
        # Response patterns
        features.append(data['response_coherence'].mean())
        features.append(data['multi_agent_coordination'].mean())
        
        self._update_feature_names([
            'engagement_consistency', 'avg_engagement_streak',
            'direct_question_ratio', 'feedback_request_ratio', 'knowledge_seeking_ratio',
            'response_coherence_rate', 'multi_agent_usage_rate'
        ])
        
        return features
    
    def extract_progression_features(self, data: pd.DataFrame) -> List[float]:
        """Extract learning progression features"""
        
        features = []
        
        # Skill level progression
        skill_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        skill_values = [skill_map.get(s, 1) for s in data['student_skill_level']]
        
        features.append(self._calculate_progression_score(skill_values))
        features.append(np.std(skill_values))
        
        # Confidence progression
        if 'confidence_score' in data.columns:
            conf_progression = self._calculate_trend(data['confidence_score'])
            features.append(conf_progression)
        else:
            features.append(0)
        
        # Cognitive flag reduction (fewer flags = better)
        flag_progression = self._calculate_trend(data['cognitive_flags_count'], inverse=True)
        features.append(flag_progression)
        
        self._update_feature_names([
            'skill_progression_score', 'skill_stability',
            'confidence_progression', 'cognitive_gap_reduction'
        ])
        
        return features
    
    def extract_quality_features(self, data: pd.DataFrame) -> List[float]:
        """Extract interaction quality features"""
        
        features = []
        
        # Question quality
        questions = data[data['input_type'].str.contains('question', na=False)]
        if len(questions) > 0:
            features.append(questions['input_length'].mean() / 20)  # Normalized
            features.append(len(questions) / len(data))
        else:
            features.extend([0, 0])
        
        # Input elaboration
        features.append(data['input_length'].mean() / 20)  # Normalized
        features.append(data['input_length'].std() / 20)
        
        # Reflection depth
        reflections = data[data['input_type'].isin(['feedback_request', 'improvement_seeking'])]
        if len(reflections) > 0:
            features.append(reflections['input_length'].mean() / 30)  # Normalized
        else:
            features.append(0)
        
        self._update_feature_names([
            'question_complexity', 'question_frequency',
            'input_elaboration', 'input_variability',
            'reflection_depth'
        ])
        
        return features
    
    def extract_temporal_features(self, data: pd.DataFrame) -> List[float]:
        """Extract temporal pattern features"""
        
        features = []
        
        # Response time patterns
        if 'response_time' in data.columns:
            features.append(data['response_time'].mean())
            features.append(data['response_time'].std())
        else:
            features.extend([0, 0])
        
        # Interaction pacing
        features.append(len(data))  # Total interactions
        
        # Routing diversity over time
        routing_diversity = len(data['routing_path'].unique()) / len(data)
        features.append(routing_diversity)
        
        # Agent usage diversity
        agent_diversity = self._calculate_agent_diversity(data)
        features.append(agent_diversity)
        
        self._update_feature_names([
            'avg_response_time', 'response_time_consistency',
            'session_length', 'routing_diversity',
            'agent_diversity'
        ])
        
        return features
    
    def _calculate_engagement_streaks(self, engagement_series: pd.Series) -> List[int]:
        """Calculate engagement streak lengths"""
        
        streaks = []
        current_streak = 0
        
        for engaged in engagement_series:
            if engaged:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        return streaks
    
    def _calculate_progression_score(self, values: List[float]) -> float:
        """Calculate progression score from a series of values"""
        
        if len(values) < 2:
            return 0
        
        progression = 0
        for i in range(1, len(values)):
            if values[i] > values[i-1]:
                progression += 1
            elif values[i] < values[i-1]:
                progression -= 0.5
        
        return progression / (len(values) - 1)
    
    def _calculate_trend(self, series: pd.Series, inverse: bool = False) -> float:
        """Calculate trend in a series"""
        
        if len(series) < 2:
            return 0
        
        x = np.arange(len(series))
        y = series.values
        
        # Calculate linear regression slope
        slope, _ = np.polyfit(x, y, 1)
        
        # Normalize to -1 to 1 range
        normalized_slope = np.tanh(slope * 10)
        
        return -normalized_slope if inverse else normalized_slope
    
    def _calculate_agent_diversity(self, data: pd.DataFrame) -> float:
        """Calculate diversity of agent usage"""
        
        agent_counts = {}
        
        for agents in data['agents_used']:
            if isinstance(agents, str):
                try:
                    agent_list = eval(agents)
                    for agent in agent_list:
                        agent_counts[agent] = agent_counts.get(agent, 0) + 1
                except:
                    pass
        
        if not agent_counts:
            return 0
        
        # Calculate Shannon entropy for diversity
        total = sum(agent_counts.values())
        entropy = -sum((count/total) * np.log(count/total) 
                      for count in agent_counts.values())
        
        # Normalize by maximum possible entropy
        max_entropy = np.log(len(agent_counts))
        
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def _update_feature_names(self, names: List[str]):
        """Update feature names list"""
        self.feature_names.extend(names)
    
    def get_feature_names(self) -> List[str]:
        """Get all feature names"""
        return self.feature_names


class VotingClassifierCustom:
    """Custom voting classifier for ensemble methods"""
    
    def __init__(self, estimators):
        self.estimators = estimators
        self.fitted_estimators = []
        
    def fit(self, X, y):
        """Fit all estimators"""
        self.fitted_estimators = []
        
        for name, estimator in self.estimators:
            fitted_est = estimator.fit(X, y)
            self.fitted_estimators.append((name, fitted_est))
        
        return self
    
    def predict(self, X):
        """Predict using majority voting"""
        predictions = []
        
        for name, estimator in self.fitted_estimators:
            pred = estimator.predict(X)
            predictions.append(pred)
        
        # Majority voting
        predictions = np.array(predictions)
        final_predictions = []
        
        for i in range(predictions.shape[1]):
            votes = predictions[:, i]
            final_predictions.append(np.bincount(votes).argmax())
        
        return np.array(final_predictions)
    
    def predict_proba(self, X):
        """Predict probabilities by averaging"""
        probabilities = []
        
        for name, estimator in self.fitted_estimators:
            proba = estimator.predict_proba(X)
            probabilities.append(proba)
        
        # Average probabilities
        return np.mean(probabilities, axis=0)
    
    @property
    def feature_importances_(self):
        """Get averaged feature importances"""
        importances = []
        
        for name, estimator in self.fitted_estimators:
            if hasattr(estimator, 'feature_importances_'):
                importances.append(estimator.feature_importances_)
        
        if importances:
            return np.mean(importances, axis=0)
        return None


def generate_training_data_from_sessions(session_files: List[str]) -> List[Tuple[pd.DataFrame, str]]:
    """Generate training data from session files with pseudo-labels"""
    
    training_data = []
    
    for session_file in session_files:
        session_data = pd.read_csv(session_file)
        
        # Generate pseudo-label based on metrics
        proficiency_label = assign_proficiency_label(session_data)
        
        training_data.append((session_data, proficiency_label))
    
    return training_data


def assign_proficiency_label(session_data: pd.DataFrame) -> str:
    """Assign proficiency label based on session metrics"""
    
    # Calculate key metrics
    offload_prevention = session_data['prevents_cognitive_offloading'].mean()
    deep_thinking = session_data['encourages_deep_thinking'].mean()
    scaffolding = session_data['provides_scaffolding'].mean()
    
    # Simple rule-based assignment (would be replaced with actual labels)
    composite_score = (offload_prevention + deep_thinking + scaffolding) / 3
    
    if composite_score >= 0.8:
        return 'expert'
    elif composite_score >= 0.6:
        return 'advanced'
    elif composite_score >= 0.4:
        return 'intermediate'
    else:
        return 'beginner'


def main():
    """Example usage of proficiency classifier"""
    
    # Initialize classifier
    classifier = UserProficiencyClassifier()
    
    # Load session data
    data_dir = Path("./thesis_data")
    session_files = list(data_dir.glob("interactions_*.csv"))
    
    if not session_files:
        print("No session data found.")
        return
    
    print(f"Found {len(session_files)} session files")
    
    # Generate training data
    training_data = generate_training_data_from_sessions(
        [str(f) for f in session_files]
    )
    
    if len(training_data) < 10:
        print("Insufficient data for training. Need at least 10 sessions.")
        return
    
    # Train classifier
    classifier.train_classifier(training_data, model_type='ensemble')
    
    # Save model
    classifier.save_model("./benchmarking/proficiency_classifier.pkl")
    
    # Example classification
    test_session = pd.read_csv(session_files[0])
    result = classifier.classify_user(test_session)
    
    print("\n" + "="*50)
    print("Example Classification Result:")
    print(f"Proficiency Level: {result['proficiency_level']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print("\nProbabilities:")
    for level, prob in result['probabilities'].items():
        print(f"  {level}: {prob:.2%}")
    
    print("\nStrengths:")
    for strength in result['feature_analysis']['strengths'][:3]:
        print(f"  - {strength['feature']}: {strength['value']:.2f}")
    
    print("\nRecommendations:")
    for rec in result['recommendations'][:3]:
        print(f"  - {rec['area']}: {rec['recommendation']}")
    
    print("\nProgression Potential:")
    prog = result['progression_potential']
    print(f"  Ready for next level: {prog['ready_for_progression']}")
    print(f"  Progress: {prog['overall_progress']:.0%}")
    print(f"  Estimated sessions to progress: {prog['estimated_sessions_to_progress']}")


if __name__ == "__main__":
    main()