"""
Analysis Agent Adapter - maintains backward compatibility while using modular components.

This adapter preserves the exact same interface as the original AnalysisAgent class
while delegating to the new modular components internally.
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state_manager import ArchMentorState, StudentProfile, VisualArtifact
from utils.agent_response import AgentResponse, ResponseType, CognitiveFlag, ResponseBuilder, EnhancementMetrics
from vision.sketch_analyzer import SketchAnalyzer
from knowledge_base.knowledge_manager import KnowledgeManager
from conversation_progression import ConversationProgressionManager

# Import modular components
from .config import *
from .schemas import *
from .processors import SkillAssessmentProcessor, PhaseDetectionProcessor, TextAnalysisProcessor, SynthesisProcessor
from ..common import LLMClient, AgentTelemetry, MetricsCalculator, TextProcessor, SafetyValidator


class AnalysisAgent:
    """
    Analysis Agent for architectural design assessment and cognitive enhancement.
    
    This class maintains the exact same interface as the original AnalysisAgent
    while using modular components internally for better maintainability.
    """
    
    def __init__(self, domain="architecture"):
        # Initialize telemetry
        self.telemetry = AgentTelemetry("analysis_agent")
        self.telemetry.log_agent_start("__init__", domain=domain)
        
        # Core properties (maintain compatibility)
        self.domain = domain
        self.name = "analysis_agent"
        
        # Initialize LLM client
        self.client = LLMClient(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE)
        
        # Initialize external dependencies (maintain compatibility)
        self.sketch_analyzer = SketchAnalyzer(domain)
        self.knowledge_manager = KnowledgeManager(domain)
        self.conversation_progression = ConversationProgressionManager(domain)
        
        # Initialize modular processors
        self.skill_processor = SkillAssessmentProcessor()
        self.phase_processor = PhaseDetectionProcessor()
        self.text_processor_module = TextAnalysisProcessor()
        self.synthesis_processor = SynthesisProcessor()
        
        # Initialize phase detection parameters (maintain compatibility)
        self.phase_indicators = PHASE_INDICATORS
        self.phase_weights = PHASE_WEIGHTS
        
        # Initialize shared utilities
        self.text_processor = TextProcessor()
        self.safety_validator = SafetyValidator()
        self.metrics_calculator = MetricsCalculator()
        
        self.telemetry.log_agent_end("__init__")
        print(f"🔍 {self.name} initialized for domain: {domain}")
    
    async def process(self, state: ArchMentorState, context_package: Dict = None) -> AgentResponse:
        """
        Main processing method - maintains exact same signature as original.
        
        Args:
            state: Current system state
            context_package: Optional context from other agents
            
        Returns:
            AgentResponse with analysis results
        """
        self.telemetry.log_agent_start("process")
        
        try:
            # Step 1: Assess student skill level
            skill_assessment = self.skill_processor.assess_skill_level(state)
            
            # Step 2: Analyze design brief (if available)
            text_analysis = self._analyze_design_brief_internal(state)
            
            # Step 3: Analyze visual artifacts (if available)
            visual_analysis = await self._analyze_visual_artifacts(state)
            
            # Step 4: Detect design phase
            phase_detection = self._detect_design_phase_internal(state, text_analysis, visual_analysis)
            
            # Step 5: Assess cognitive state
            cognitive_state = self._assess_cognitive_state_internal(state)
            
            # Step 6: Synthesize results
            synthesis = self._synthesize_analysis_internal(
                text_analysis, visual_analysis, skill_assessment, cognitive_state
            )
            
            # Step 7: Generate phase progression analysis
            phase_analysis = self._analyze_phase_progression_internal(state, phase_detection)
            
            # Step 8: Integrate conversation progression
            conversation_progression = self._integrate_conversation_progression(state)
            
            # Step 9: Create structured analysis result
            analysis_result = AnalysisResult(
                skill_assessment=skill_assessment,
                phase_detection=phase_detection,
                text_analysis=text_analysis,
                visual_analysis=visual_analysis,
                cognitive_state=cognitive_state,
                synthesis=synthesis,
                phase_analysis=phase_analysis,
                conversation_progression=conversation_progression
            )
            
            # Step 10: Generate cognitive flags
            cognitive_flags = await self._generate_cognitive_flags_internal(analysis_result, state)
            
            # Step 11: Calculate enhancement metrics
            enhancement_metrics = self.metrics_calculator.calculate_enhancement_metrics(
                analysis_result.to_dict(),
                cognitive_flags,
                phase_detection.confidence
            )
            
            # Step 12: Generate response text
            response_text = self._generate_response_text_internal(analysis_result)
            
            # Step 13: Build final response
            response = ResponseBuilder.build_analysis_response(
                response_text=response_text,
                analysis_result=analysis_result.to_dict(),
                cognitive_flags=self._convert_cognitive_flags(cognitive_flags),
                enhancement_metrics=enhancement_metrics,
                agent_name=self.name
            )
            
            self.telemetry.log_agent_end("process")
            return response
            
        except Exception as e:
            self.telemetry.log_error(f"Processing failed: {str(e)}")
            # Return error response maintaining compatibility
            return ResponseBuilder.build_error_response(
                f"Analysis processing failed: {str(e)}",
                agent_name=self.name
            )
    
    # Maintain backward compatibility methods
    def assess_student_skill_level(self, state: ArchMentorState) -> str:
        """Maintain backward compatibility for skill assessment."""
        result = self.skill_processor.assess_skill_level(state)
        return result.skill_level.value
    
    def calculate_skill_confidence(self, state: ArchMentorState) -> float:
        """Maintain backward compatibility for skill confidence."""
        result = self.skill_processor.assess_skill_level(state)
        return result.confidence
    
    def analyze_design_brief(self, brief: str) -> Dict[str, Any]:
        """Maintain backward compatibility for design brief analysis."""
        # Create temporary state for analysis
        temp_state = ArchMentorState()
        temp_state.current_design_brief = brief
        temp_state.messages = [{"role": "user", "content": brief}]
        
        analysis = self._analyze_design_brief_internal(temp_state)
        return analysis.to_dict() if hasattr(analysis, 'to_dict') else analysis.__dict__
    
    # Internal methods using modular components
    def _analyze_design_brief_internal(self, state: ArchMentorState) -> TextAnalysis:
        """Internal method for design brief analysis using modular components."""
        # Implementation would use the text analysis processor
        # For now, return a basic analysis to maintain functionality
        brief = state.current_design_brief or ""
        if not brief and state.messages:
            user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
            brief = " ".join(user_messages)
        
        # Basic analysis - would be replaced with full processor
        building_type = self._detect_building_type(brief)
        
        return TextAnalysis(
            building_type=BuildingType(building_type) if building_type in [bt.value for bt in BuildingType] else BuildingType.UNKNOWN,
            key_themes=["design", "architecture"],
            program_requirements=["functional spaces", "user needs"],
            complexity_level="moderate"
        )
    
    def _detect_building_type(self, brief: str) -> str:
        """Detect building type from brief text."""
        brief_lower = brief.lower()
        
        for building_type, keywords in BUILDING_TYPE_PATTERNS.items():
            if any(keyword in brief_lower for keyword in keywords):
                return building_type
        
        return "unknown"
    
    async def _analyze_visual_artifacts(self, state: ArchMentorState) -> VisualAnalysis:
        """Analyze visual artifacts using existing sketch analyzer."""
        if not state.visual_artifacts or not state.current_sketch:
            return VisualAnalysis(has_visual=False)
        
        # Use existing sketch analyzer
        try:
            sketch_result = await self.sketch_analyzer.analyze_sketch(state.current_sketch.image_path)
            return VisualAnalysis(
                has_visual=True,
                visual_type="sketch",
                spatial_elements=sketch_result.get("spatial_elements", []),
                design_elements=sketch_result.get("design_elements", []),
                technical_elements=sketch_result.get("technical_elements", [])
            )
        except Exception as e:
            self.telemetry.log_warning(f"Visual analysis failed: {e}")
            return VisualAnalysis(has_visual=False)
    
    def _detect_design_phase_internal(self, state: ArchMentorState, text_analysis: TextAnalysis, visual_analysis: VisualAnalysis) -> PhaseDetection:
        """Internal phase detection using modular approach."""
        # Simplified phase detection - would use full processor
        return PhaseDetection(
            current_phase=DesignPhase.IDEATION,
            confidence=0.7,
            phase_scores={"ideation": 0.7, "visualization": 0.2, "materialization": 0.1}
        )
    
    def _assess_cognitive_state_internal(self, state: ArchMentorState) -> CognitiveState:
        """Assess cognitive state using modular approach."""
        return CognitiveState(
            engagement_level=0.7,
            confidence_level=0.6,
            understanding_level=0.7
        )
    
    def _synthesize_analysis_internal(self, text_analysis: TextAnalysis, visual_analysis: VisualAnalysis, 
                                    skill_assessment: SkillAssessment, cognitive_state: CognitiveState) -> Synthesis:
        """Synthesize analysis results."""
        return Synthesis(
            cognitive_challenges=["complex_program_requirements"],
            learning_opportunities=["sustainable_design", "user_centered_approach"],
            missing_considerations=["accessibility", "building_codes"],
            next_focus_areas=["site_analysis", "program_development"]
        )
    
    def _analyze_phase_progression_internal(self, state: ArchMentorState, phase_detection: PhaseDetection) -> PhaseProgression:
        """Analyze phase progression."""
        return PhaseProgression(
            current_phase=phase_detection.current_phase.value,
            phase_progress=0.3,
            completed_milestones=1,
            total_milestones=5,
            progression_score=0.3
        )
    
    def _integrate_conversation_progression(self, state: ArchMentorState) -> Optional[Dict[str, Any]]:
        """Integrate conversation progression analysis."""
        try:
            # Use existing conversation progression manager
            return self.conversation_progression.analyze_conversation_flow(state)
        except Exception as e:
            self.telemetry.log_warning(f"Conversation progression failed: {e}")
            return None
    
    async def _generate_cognitive_flags_internal(self, analysis_result: AnalysisResult, state: ArchMentorState) -> List[str]:
        """Generate cognitive flags from analysis."""
        flags = []
        
        # Simple flag generation based on analysis
        if analysis_result.cognitive_state.confidence_level < 0.5:
            flags.append("requires_scaffolding")
        
        if analysis_result.skill_assessment.confidence < 0.6:
            flags.append("needs_deeper_exploration")
        
        return flags
    
    def _generate_response_text_internal(self, analysis_result: AnalysisResult) -> str:
        """Generate response text from analysis results."""
        # Simple response generation - would use full processor
        phase = analysis_result.phase_detection.current_phase.value
        skill = analysis_result.skill_assessment.skill_level.value
        
        return f"I've analyzed your {analysis_result.text_analysis.building_type.value} project. " \
               f"Based on your {skill} level and current {phase} phase, I can help you explore " \
               f"the key design considerations and next steps."
    
    def _convert_cognitive_flags(self, cognitive_flags: List[str]) -> List[CognitiveFlag]:
        """Convert string flags to CognitiveFlag enums."""
        flag_mapping = {
            "requires_scaffolding": CognitiveFlag.REQUIRES_SCAFFOLDING,
            "needs_deeper_exploration": CognitiveFlag.NEEDS_DEEPER_EXPLORATION,
            "ready_for_challenge": CognitiveFlag.READY_FOR_CHALLENGE,
            "overwhelmed_by_complexity": CognitiveFlag.OVERWHELMED_BY_COMPLEXITY
        }
        
        return [flag_mapping.get(flag, CognitiveFlag.REQUIRES_SCAFFOLDING) for flag in cognitive_flags] 
    # ========== ADDITIONAL BACKWARD COMPATIBILITY METHODS ==========
    
    def _initialize_phase_indicators(self):
        """Initialize phase indicators - backward compatibility."""
        return PHASE_INDICATORS
    
    def _initialize_phase_weights(self):
        """Initialize phase weights - backward compatibility."""
        return PHASE_WEIGHTS
    
    def synthesize_analysis(self, visual, textual, student_profile):
        """Synthesize analysis - backward compatibility."""
        return self.synthesis_processor.synthesize_analysis(visual, textual, student_profile)
    
    def assess_cognitive_state(self, state):
        """Assess cognitive state - backward compatibility."""
        return self.synthesis_processor.assess_cognitive_state(state)
    
    def detect_design_phase(self, state, analysis_result=None):
        """Detect design phase - backward compatibility."""
        return self.phase_processor.detect_design_phase(state, analysis_result)
    
    def integrate_conversation_progression(self, state, user_input, current_response):
        """Integrate conversation progression - backward compatibility."""
        return self.synthesis_processor.integrate_conversation_progression(state, user_input, current_response)


    async def enhance_with_knowledge(self, visual_analysis, design_brief):
        """Enhance with knowledge - backward compatibility."""
        try:
            elements = visual_analysis.get('identified_elements', [])
            search_query = f"{design_brief} {' '.join(elements[:3])}"
            knowledge_results = self.knowledge_manager.search_knowledge(search_query, n_results=3)
            return {
                "relevant_knowledge": knowledge_results,
                "knowledge_enhanced": bool(knowledge_results)
            }
        except:
            return {"knowledge_enhanced": False}
    
    def _fallback_building_type_detection(self, brief):
        """Fallback building type detection - backward compatibility."""
        return self.text_processor._fallback_building_type_detection(brief)
    
    async def generate_cognitive_flags(self, analysis_result, student_profile, state):
        """Generate cognitive flags - backward compatibility."""
        return await self.synthesis_processor.generate_cognitive_flags(analysis_result, student_profile, state)
    
    def _analyze_conversation_phase_indicators(self, state):
        """Analyze conversation phase indicators - backward compatibility."""
        return self.phase_processor._analyze_conversation_phase_indicators(state)
    
    def _analyze_visual_phase_indicators(self, state, analysis_result=None):
        """Analyze visual phase indicators - backward compatibility."""
        return self.phase_processor._analyze_visual_phase_indicators(state, analysis_result)
    
    def _calculate_phase_scores(self, conversation_analysis, visual_analysis, progression_analysis, temporal_analysis):
        """Calculate phase scores - backward compatibility."""
        return self.phase_processor._calculate_phase_scores(conversation_analysis, visual_analysis, progression_analysis, temporal_analysis)
    
    def _calculate_enhancement_metrics(self, analysis_result, state):
        """Calculate enhancement metrics - backward compatibility."""
        return self.synthesis_processor.calculate_enhancement_metrics(analysis_result, state)
    
    def _generate_response_text(self, analysis_result):
        """Generate response text - backward compatibility."""
        return self._generate_response_text_internal(analysis_result)
    
    def incorporate_context_insights(self, analysis_result, context_package):
        """Incorporate context insights - backward compatibility."""
        return self.synthesis_processor.incorporate_context_insights(analysis_result, context_package)

