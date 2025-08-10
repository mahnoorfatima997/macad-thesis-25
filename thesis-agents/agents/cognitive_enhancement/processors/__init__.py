"""
Processing modules for the Cognitive Enhancement Agent.
"""
from .cognitive_assessment import CognitiveAssessmentProcessor
from .intervention_generator import InterventionGeneratorProcessor
from .challenge_generator import ChallengeGeneratorProcessor
from .scientific_metrics import ScientificMetricsProcessor
from .phase_analyzer import PhaseAnalyzerProcessor

__all__ = [
    'CognitiveAssessmentProcessor',
    'InterventionGeneratorProcessor',
    'ChallengeGeneratorProcessor',
    'ScientificMetricsProcessor',
    'PhaseAnalyzerProcessor'
] 