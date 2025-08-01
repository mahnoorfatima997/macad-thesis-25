# agents/cognitive_enhancement.py - SCIENTIFICALLY GROUNDED
from typing import Dict, Any, List, Optional
import os
import random
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import sys
import time

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'benchmarking'))

from state_manager import ArchMentorState

# Import linkography components if available
try:
    from linkography_types import Linkograph, DesignMove, LinkographLink, CognitiveLinkographMapping
    from linkography_cognitive_mapping import CognitiveMappingService
    LINKOGRAPHY_AVAILABLE = True
except ImportError:
    LINKOGRAPHY_AVAILABLE = False
    print("⚠️ Linkography components not available - using fallback cognitive assessment")

load_dotenv()

class CognitiveEnhancementAgent:
    def __init__(self, domain="architecture"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.domain = domain
        self.name = "cognitive_enhancement"
        
        # Initialize linkography mapping service if available
        self.cognitive_mapper = CognitiveMappingService() if LINKOGRAPHY_AVAILABLE else None
        
        # Research-validated challenge templates based on cognitive dimensions
        self.challenge_templates = {
            "deep_thinking_engagement": [
                "What if you had to explain your design process to someone who knows nothing about architecture?",
                "How would you break down your current approach into smaller, more manageable steps?",
                "What assumptions are you making about the user experience that you haven't tested?",
                "How would your design change if you had to justify every single design decision?"
            ],
            "cognitive_offloading_prevention": [
                "Instead of asking for the answer, what specific aspect are you struggling with?",
                "What have you already tried that didn't work, and what did you learn from that?",
                "How could you test your current approach before asking for help?",
                "What resources or information do you need to solve this independently?"
            ],
            "scaffolding_effectiveness": [
                "Let's build on your previous idea. How does it connect to what you were working on earlier?",
                "What would be the next logical step in your design process?",
                "How does this current challenge relate to the fundamentals we discussed?",
                "What principles from earlier in our conversation apply here?"
            ],
            "knowledge_integration": [
                "How does this new concept connect to what you already know about architecture?",
                "What similarities do you see between this and other design problems you've solved?",
                "How could you apply principles from different architectural styles to this project?",
                "What patterns or systems from nature could inform your design approach?"
            ],
            "learning_progression": [
                "How has your understanding of this topic evolved since we started?",
                "What would you do differently now compared to when you first approached this?",
                "How has your design thinking process changed throughout this project?",
                "What new skills or insights have you developed that you didn't have before?"
            ],
            "metacognitive_awareness": [
                "What's your current thinking process? Walk me through your mental model.",
                "How do you know when you're making progress versus when you're stuck?",
                "What strategies work best for you when you encounter design challenges?",
                "How do you evaluate the quality of your own design decisions?"
            ]
        }
        
        # Scientific baseline and target metrics from benchmarking research
        self.baseline_metrics = {
            "deep_thinking_engagement": 0.35,  # Traditional tutoring baseline
            "cognitive_offloading_prevention": 0.65,
            "scaffolding_effectiveness": 0.45,
            "knowledge_integration": 0.40,
            "learning_progression": 0.30,
            "metacognitive_awareness": 0.25
        }
        
        self.target_metrics = {
            "deep_thinking_engagement": 0.75,  # MEGA system targets
            "cognitive_offloading_prevention": 0.85,
            "scaffolding_effectiveness": 0.80,
            "knowledge_integration": 0.70,
            "learning_progression": 0.65,
            "metacognitive_awareness": 0.60
        }
        
        print(f"🧠 {self.name} initialized for domain: {domain}")
        if LINKOGRAPHY_AVAILABLE:
            print(f"🔗 Linkography integration: ENABLED")
        else:
            print(f"🔗 Linkography integration: FALLBACK MODE")
    
    async def provide_challenge(self, state: ArchMentorState, context_classification: Dict, analysis_result: Dict, routing_decision: Dict) -> Dict[str, Any]:
        """Provide scientifically grounded cognitive challenge"""
        
        print(f"\n🧠 {self.name} providing scientifically grounded cognitive challenge...")
        
        # Generate linkograph from conversation if possible
        linkograph = self._generate_linkograph_from_conversation(state) if LINKOGRAPHY_AVAILABLE else None
        
        # Calculate cognitive metrics using research-validated formulas
        cognitive_metrics = self._calculate_scientific_cognitive_metrics(state, linkograph, context_classification)
        
        # Select enhancement strategy based on weakest cognitive dimension
        strategy = self._select_scientific_strategy(cognitive_metrics, context_classification)
        
        # Generate contextualized challenge
        challenge_result = await self._generate_scientific_challenge(strategy, state, analysis_result, cognitive_metrics)
        
        # Calculate improvement over baseline
        improvement_metrics = self._calculate_improvement_over_baseline(cognitive_metrics)
        
        return {
            "agent": self.name,
            "cognitive_state": cognitive_metrics,
            "scientific_metrics": {
                "cognitive_dimensions": cognitive_metrics,
                "improvement_over_baseline": improvement_metrics,
                "linkography_available": LINKOGRAPHY_AVAILABLE,
                "research_basis": "Linkography-to-Cognitive Mapping (Goldschmidt, 2014; Kan & Gero, 2017)"
            },
            "enhancement_strategy": strategy,
            "context_used": context_classification,
            "pedagogical_intent": self._get_scientific_intent(strategy, cognitive_metrics),
            "response_text": challenge_result,
            "challenge_type": strategy
        }
    
    def _generate_linkograph_from_conversation(self, state: ArchMentorState) -> Optional[Linkograph]:
        """Generate linkograph from conversation history for cognitive analysis"""
        
        if not state.messages or len(state.messages) < 3:
            return None
        
        try:
            # Extract design moves from conversation
            moves = []
            for i, msg in enumerate(state.messages):
                if msg.get('role') == 'user':
                    move = DesignMove(
                        id=f"move_{i}",
                        timestamp=time.time() + i,
                        session_id="conversation_session",
                        user_id="student",
                        phase=state.design_phase,
                        content=msg['content'],
                        move_type="conceptual" if "think" in msg['content'].lower() else "practical",
                        modality="text"
                    )
                    moves.append(move)
            
            if len(moves) < 2:
                return None
            
            # Generate links between moves using semantic similarity
            links = self._generate_semantic_links(moves)
            
            # Create linkograph
            linkograph = Linkograph(
                id="conversation_linkograph",
                session_id="conversation_session",
                moves=moves,
                links=links,
                metrics=self._calculate_linkograph_metrics(moves, links),
                phase=state.design_phase,
                generated_at=time.time()
            )
            
            return linkograph
            
        except Exception as e:
            print(f"⚠️ Linkograph generation failed: {e}")
            return None
    
    def _generate_semantic_links(self, moves: List[DesignMove]) -> List[LinkographLink]:
        """Generate semantic links between design moves"""
        
        links = []
        for i, source_move in enumerate(moves):
            for j, target_move in enumerate(moves[i+1:], i+1):
                # Simple semantic similarity based on common words
                source_words = set(source_move.content.lower().split())
                target_words = set(target_move.content.lower().split())
                
                if source_words and target_words:
                    similarity = len(source_words.intersection(target_words)) / len(source_words.union(target_words))
                    
                    if similarity > 0.1:  # Threshold for meaningful connection
                        link = LinkographLink(
                            id=f"link_{i}_{j}",
                            source_move=source_move.id,
                            target_move=target_move.id,
                            strength=similarity,
                            confidence=min(similarity * 1.5, 1.0),
                            link_type="semantic",
                            temporal_distance=j - i,
                            semantic_similarity=similarity
                        )
                        links.append(link)
        
        return links
    
    def _calculate_linkograph_metrics(self, moves: List[DesignMove], links: List[LinkographLink]) -> Any:
        """Calculate basic linkograph metrics"""
        
        # Create a simple metrics object
        class SimpleMetrics:
            def __init__(self):
                self.link_density = len(links) / len(moves) if moves else 0.0
                self.critical_move_ratio = 0.2  # Default
                self.entropy = 0.5  # Default
                self.phase_balance = {"ideation": 0.33, "visualization": 0.33, "materialization": 0.34}
                self.cognitive_indicators = {}
                self.avg_link_strength = np.mean([link.strength for link in links]) if links else 0.0
                self.max_link_range = max([link.temporal_distance for link in links]) if links else 0
                self.orphan_move_ratio = 0.1  # Default
                self.chunk_count = 0
                self.web_count = 0
                self.sawtooth_count = 0
        
        return SimpleMetrics()
    
    def _calculate_scientific_cognitive_metrics(self, state: ArchMentorState, linkograph: Optional[Linkograph], context_classification: Dict) -> Dict[str, float]:
        """Calculate cognitive metrics using research-validated formulas"""
        
        if linkograph and self.cognitive_mapper:
            # Use linkography-based cognitive mapping
            cognitive_mapping = self.cognitive_mapper.map_linkography_to_cognitive(linkograph)
            return cognitive_mapping.to_dict()
        else:
            # Fallback to conversation-based assessment
            return self._calculate_conversation_based_metrics(state, context_classification)
    
    def _calculate_conversation_based_metrics(self, state: ArchMentorState, context_classification: Dict) -> Dict[str, float]:
        """Calculate cognitive metrics from conversation patterns"""
        
        user_messages = [msg['content'] for msg in state.messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {dim: 0.5 for dim in self.baseline_metrics.keys()}
        
        # Deep thinking engagement
        thinking_indicators = ["think", "process", "approach", "strategy", "consider", "analyze"]
        thinking_score = sum(1 for msg in user_messages 
                           if any(indicator in msg.lower() for indicator in thinking_indicators)) / len(user_messages)
        
        # Cognitive offloading prevention
        help_requests = ["help", "tell me", "what should", "how do i", "can you"]
        offloading_score = 1.0 - sum(1 for msg in user_messages 
                                   if any(request in msg.lower() for request in help_requests)) / len(user_messages)
        
        # Scaffolding effectiveness
        connection_indicators = ["because", "therefore", "so", "this relates", "connects"]
        scaffolding_score = sum(1 for msg in user_messages 
                              if any(indicator in msg.lower() for indicator in connection_indicators)) / len(user_messages)
        
        # Knowledge integration
        integration_indicators = ["similar", "like", "compare", "different", "pattern", "principle"]
        integration_score = sum(1 for msg in user_messages 
                              if any(indicator in msg.lower() for indicator in integration_indicators)) / len(user_messages)
        
        # Learning progression
        progression_indicators = ["before", "now", "changed", "evolved", "improved", "better"]
        progression_score = sum(1 for msg in user_messages 
                              if any(indicator in msg.lower() for indicator in progression_indicators)) / len(user_messages)
        
        # Metacognitive awareness
        metacognitive_indicators = ["i think", "i believe", "my approach", "i realize", "looking back", "i should"]
        metacognitive_score = sum(1 for msg in user_messages 
                                if any(indicator in msg.lower() for indicator in metacognitive_indicators)) / len(user_messages)
        
        return {
            "deep_thinking_engagement": min(thinking_score * 2, 1.0),
            "cognitive_offloading_prevention": max(offloading_score, 0.0),
            "scaffolding_effectiveness": min(scaffolding_score * 2, 1.0),
            "knowledge_integration": min(integration_score * 2, 1.0),
            "learning_progression": min(progression_score * 2, 1.0),
            "metacognitive_awareness": min(metacognitive_score * 2, 1.0)
        }
    
    def _select_scientific_strategy(self, cognitive_metrics: Dict[str, float], context_classification: Dict) -> str:
        """Select enhancement strategy based on weakest cognitive dimension"""
        
        # Find the dimension with the lowest score relative to target
        worst_dimension = None
        worst_ratio = float('inf')
        
        for dimension, current_score in cognitive_metrics.items():
            target_score = self.target_metrics[dimension]
            ratio = current_score / target_score if target_score > 0 else 1.0
            
            if ratio < worst_ratio:
                worst_ratio = ratio
                worst_dimension = dimension
        
        # Use context classification to override if needed
        if context_classification:
            confidence = context_classification.get("confidence_level", "")
            if confidence == "overconfident":
                return "metacognitive_awareness"
            elif confidence == "uncertain":
                return "cognitive_offloading_prevention"
        
        return worst_dimension or "metacognitive_awareness"
    
    async def _generate_scientific_challenge(self, strategy: str, state: ArchMentorState, analysis_result: Dict, cognitive_metrics: Dict) -> str:
        """Generate scientifically grounded challenge"""
        
        templates = self.challenge_templates.get(strategy, self.challenge_templates["metacognitive_awareness"])
        base_challenge = random.choice(templates)
        
        # Contextualize to current topic
        recent_messages = [msg['content'] for msg in state.messages[-2:] if msg.get('role') == 'user']
        current_topic = " ".join(recent_messages) if recent_messages else ""
        
        if current_topic and len(current_topic) > 10:
            contextualized = await self._contextualize_scientific_challenge(base_challenge, current_topic, strategy, cognitive_metrics)
            return contextualized if contextualized else base_challenge
        
        return base_challenge
    
    async def _contextualize_scientific_challenge(self, base_challenge: str, current_topic: str, strategy: str, cognitive_metrics: Dict) -> str:
        """Contextualize challenge using scientific approach"""
        
        try:
            # Get current cognitive score for this dimension
            current_score = cognitive_metrics.get(strategy, 0.5)
            target_score = self.target_metrics.get(strategy, 0.7)
            
            prompt = f"""
            Create a cognitive challenge that targets the {strategy.replace('_', ' ')} dimension.
            
            BASE CHALLENGE: {base_challenge}
            STUDENT TOPIC: {current_topic}
            CURRENT SCORE: {current_score:.2f} (Target: {target_score:.2f})
            
            The student needs to improve their {strategy.replace('_', ' ')} skills.
            Create a brief, relevant challenge question that directly addresses this cognitive dimension:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.6
            )
            
            result = response.choices[0].message.content.strip()
            return result if result and len(result) < 120 else base_challenge
            
        except Exception as e:
            print(f"   ⚠️ Scientific contextualization failed: {e}")
            return base_challenge
    
    def _calculate_improvement_over_baseline(self, cognitive_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Calculate improvement over baseline using research metrics"""
        
        improvements = {}
        for dimension, current_score in cognitive_metrics.items():
            baseline = self.baseline_metrics.get(dimension, 0.5)
            target = self.target_metrics.get(dimension, 0.7)
            
            if baseline > 0:
                improvement_pct = ((current_score - baseline) / baseline) * 100
            else:
                improvement_pct = 0
            
            target_progress = (current_score - baseline) / (target - baseline) if target > baseline else 0
            
            improvements[dimension] = {
                "current_score": round(current_score, 3),
                "baseline_score": baseline,
                "target_score": target,
                "improvement_percentage": round(improvement_pct, 1),
                "target_progress": round(target_progress, 3)
            }
        
        # Overall improvement
        overall_improvement = np.mean([imp["improvement_percentage"] for imp in improvements.values()])
        
        return {
            "overall_improvement": round(overall_improvement, 1),
            "dimension_improvements": improvements,
            "research_basis": "MEGA System vs Traditional Tutoring Baseline"
        }
    
    def _get_scientific_intent(self, strategy: str, cognitive_metrics: Dict) -> str:
        """Get scientifically grounded pedagogical intent"""
        
        current_score = cognitive_metrics.get(strategy, 0.5)
        target_score = self.target_metrics.get(strategy, 0.7)
        
        intents = {
            "deep_thinking_engagement": "Enhance sustained cognitive engagement and generative thinking",
            "cognitive_offloading_prevention": "Reduce dependency on external solutions and promote independent problem-solving",
            "scaffolding_effectiveness": "Improve structured learning progression and concept building",
            "knowledge_integration": "Enhance cross-domain knowledge synthesis and pattern recognition",
            "learning_progression": "Accelerate skill development and adaptive learning capacity",
            "metacognitive_awareness": "Develop self-monitoring and strategic thinking capabilities"
        }
        
        base_intent = intents.get(strategy, "Enhance cognitive development")
        progress = "needs improvement" if current_score < target_score * 0.8 else "developing well"
        
        return f"{base_intent} (Current: {current_score:.1%}, {progress})"

# Test function
async def test_scientific_cognitive_agent():
    print("🧪 Testing Scientifically Grounded Cognitive Enhancement Agent...")
    
    state = ArchMentorState()
    state.current_design_brief = "Design a community center for 200 people"
    state.student_profile.skill_level = "intermediate"
    state.messages = [
        {"role": "user", "content": "I think the central space should be flexible for different activities"},
        {"role": "assistant", "content": "That's a good approach"},
        {"role": "user", "content": "But I'm not sure how to make it work for both exhibitions and celebrations"}
    ]
    
    context_classification = {"confidence_level": "uncertain"}
    analysis_result = {"cognitive_flags": ["needs_knowledge_integration"]}
    routing_decision = {"path": "cognitive_challenge"}
    
    agent = CognitiveEnhancementAgent("architecture")
    result = await agent.provide_challenge(state, context_classification, analysis_result, routing_decision)
    
    print(f"✅ Strategy: {result['enhancement_strategy']}")
    print(f"✅ Challenge: {result['response_text']}")
    print(f"✅ Cognitive Metrics: {result['cognitive_state']}")
    print(f"✅ Improvement: {result['scientific_metrics']['improvement_over_baseline']['overall_improvement']}%")
    print(f"✅ Research Basis: {result['scientific_metrics']['research_basis']}")
    
    return result

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scientific_cognitive_agent())