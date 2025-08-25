"""
Linkography Session Insights Extractor
Translates linkography metrics into actionable design process conclusions
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from linkography_types import Linkograph, LinkographSession

@dataclass
class SessionInsights:
    """Structured insights from linkography analysis"""
    session_id: str
    cognitive_profile: str
    design_strategy: str
    breakthrough_moments: List[int]
    bottlenecks: List[str]
    recommendations: List[str]
    overall_effectiveness: float

class LinkographyInsightExtractor:
    """Extract meaningful conclusions from linkography metrics"""
    
    def analyze_session(self, session: LinkographSession) -> SessionInsights:
        """Generate comprehensive insights for a design session"""
        
        insights = SessionInsights(
            session_id=session.session_id,
            cognitive_profile="",
            design_strategy="",
            breakthrough_moments=[],
            bottlenecks=[],
            recommendations=[],
            overall_effectiveness=0.0
        )
        
        # Analyze cognitive profile based on patterns
        insights.cognitive_profile = self._determine_cognitive_profile(session)
        
        # Identify design strategy from link patterns
        insights.design_strategy = self._identify_design_strategy(session)
        
        # Find breakthrough moments
        insights.breakthrough_moments = self._find_breakthroughs(session)
        
        # Detect bottlenecks
        insights.bottlenecks = self._detect_bottlenecks(session)
        
        # Generate recommendations
        insights.recommendations = self._generate_recommendations(session, insights)
        
        # Calculate overall effectiveness
        insights.overall_effectiveness = self._calculate_effectiveness(session)
        
        return insights
    
    def _determine_cognitive_profile(self, session: LinkographSession) -> str:
        """Determine designer's cognitive profile from linkography"""
        
        patterns = session.patterns_detected
        metrics = session.overall_metrics
        
        # Count pattern types
        chunks = sum(1 for p in patterns if p.pattern_type == 'chunk')
        webs = sum(1 for p in patterns if p.pattern_type == 'web')
        sawteeth = sum(1 for p in patterns if p.pattern_type == 'sawtooth')
        
        # Determine profile
        if webs > chunks * 2:
            return "DIVERGENT THINKER - Explores multiple ideas simultaneously"
        elif chunks > webs * 2:
            return "CONVERGENT THINKER - Deep focused exploration"
        elif sawteeth > (chunks + webs) / 2:
            return "ITERATIVE REFINER - Systematic improvement approach"
        elif metrics.get('critical_move_ratio', 0) > 0.3:
            return "INTEGRATIVE SYNTHESIZER - Strong concept connection"
        else:
            return "BALANCED EXPLORER - Mixed strategies"
    
    def _identify_design_strategy(self, session: LinkographSession) -> str:
        """Identify the predominant design strategy"""
        
        if not session.linkographs:
            return "UNDETERMINED - Insufficient data"
        
        # Analyze move phases
        linkograph = session.linkographs[0]
        moves = linkograph.moves
        
        ideation_count = sum(1 for m in moves if m.phase == 'ideation')
        visualization_count = sum(1 for m in moves if m.phase == 'visualization')
        materialization_count = sum(1 for m in moves if m.phase == 'materialization')
        
        total = len(moves)
        if total == 0:
            return "EMPTY SESSION"
        
        ideation_ratio = ideation_count / total
        visualization_ratio = visualization_count / total
        materialization_ratio = materialization_count / total
        
        # Determine strategy based on phase distribution
        if ideation_ratio > 0.6:
            return "EXPLORATORY - Problem space exploration"
        elif materialization_ratio > 0.5:
            return "IMPLEMENTATION-FOCUSED - Solution execution"
        elif visualization_ratio > 0.4:
            return "SOLUTION-ORIENTED - Concept development"
        else:
            return "FULL-CYCLE - Complete design process"
    
    def _find_breakthroughs(self, session: LinkographSession) -> List[int]:
        """Identify breakthrough moments from sudden link density increases"""
        
        breakthroughs = []
        if not session.linkographs:
            return breakthroughs
        
        linkograph = session.linkographs[0]
        moves = linkograph.moves
        links = linkograph.links
        
        # Calculate link density per move
        for i, move in enumerate(moves):
            # Count links connected to this move
            move_links = [l for l in links 
                         if l.source_move == move.id or l.target_move == move.id]
            
            # Breakthrough if this move has >5 connections
            if len(move_links) > 5:
                breakthroughs.append(i)
        
        return breakthroughs
    
    def _detect_bottlenecks(self, session: LinkographSession) -> List[str]:
        """Detect cognitive bottlenecks and issues"""
        
        bottlenecks = []
        metrics = session.overall_metrics
        cognitive = session.cognitive_mapping
        
        # Check for various bottleneck conditions
        if metrics.get('link_density', 0) < 2:
            bottlenecks.append("LOW CONNECTIVITY - Ideas not being linked")
        
        if metrics.get('entropy', 1) < 0.3:
            bottlenecks.append("FIXATION - Stuck on single concept")
        
        if cognitive.get('cognitive_offloading_prevention', 0) > 0.7:
            bottlenecks.append("OVER-RELIANCE - Too dependent on AI")
        
        if cognitive.get('deep_thinking_engagement', 0) < 0.3:
            bottlenecks.append("SURFACE THINKING - Lacking depth")
        
        if metrics.get('critical_move_ratio', 0) < 0.1:
            bottlenecks.append("LINEAR PROCESS - Missing integration")
        
        # Check for orphan patterns
        patterns = session.patterns_detected
        orphans = sum(1 for p in patterns if p.pattern_type == 'orphan')
        if orphans > len(patterns) * 0.3:
            bottlenecks.append("FRAGMENTATION - Too many isolated ideas")
        
        return bottlenecks
    
    def _generate_recommendations(self, session: LinkographSession, 
                                 insights: SessionInsights) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        # Based on bottlenecks
        if "LOW CONNECTIVITY" in str(insights.bottlenecks):
            recommendations.append("Try concept mapping to find connections between ideas")
        
        if "FIXATION" in str(insights.bottlenecks):
            recommendations.append("Use SCAMPER or other ideation techniques to break fixation")
        
        if "SURFACE THINKING" in str(insights.bottlenecks):
            recommendations.append("Apply '5 Whys' technique to deepen analysis")
        
        if "FRAGMENTATION" in str(insights.bottlenecks):
            recommendations.append("Create affinity diagrams to cluster related concepts")
        
        # Based on cognitive profile
        if "DIVERGENT" in insights.cognitive_profile:
            recommendations.append("Schedule convergence sessions to synthesize ideas")
        elif "CONVERGENT" in insights.cognitive_profile:
            recommendations.append("Use brainstorming to expand solution space")
        
        # Based on breakthrough moments
        if len(insights.breakthrough_moments) == 0:
            recommendations.append("Try cross-domain analogies to spark breakthroughs")
        elif len(insights.breakthrough_moments) > 5:
            recommendations.append("Document breakthrough patterns for future sessions")
        
        return recommendations
    
    def _calculate_effectiveness(self, session: LinkographSession) -> float:
        """Calculate overall session effectiveness score (0-1)"""
        
        score = 0.0
        weights = {
            'connectivity': 0.2,
            'critical_moves': 0.2,
            'cognitive_engagement': 0.2,
            'pattern_quality': 0.2,
            'phase_balance': 0.2
        }
        
        metrics = session.overall_metrics
        cognitive = session.cognitive_mapping
        
        # Connectivity score
        link_density = min(metrics.get('link_density', 0) / 10, 1.0)
        score += link_density * weights['connectivity']
        
        # Critical moves score
        critical_ratio = metrics.get('critical_move_ratio', 0)
        score += critical_ratio * weights['critical_moves']
        
        # Cognitive engagement score
        engagement = cognitive.get('deep_thinking_engagement', 0)
        score += engagement * weights['cognitive_engagement']
        
        # Pattern quality score
        patterns = session.patterns_detected
        if patterns:
            web_chunk_ratio = len([p for p in patterns 
                                  if p.pattern_type in ['web', 'chunk']]) / len(patterns)
            score += web_chunk_ratio * weights['pattern_quality']
        
        # Phase balance score
        if session.linkographs:
            moves = session.linkographs[0].moves
            phases = [m.phase for m in moves]
            unique_phases = len(set(phases))
            phase_score = unique_phases / 3.0  # Max 3 phases
            score += phase_score * weights['phase_balance']
        
        return min(score, 1.0)
    
    def generate_session_report(self, insights: SessionInsights) -> str:
        """Generate human-readable report from insights"""
        
        report = f"""
SESSION INSIGHTS REPORT
=======================
Session ID: {insights.session_id}

COGNITIVE PROFILE:
{insights.cognitive_profile}

DESIGN STRATEGY:
{insights.design_strategy}

EFFECTIVENESS SCORE: {insights.overall_effectiveness:.1%}

BREAKTHROUGH MOMENTS:
{f"Moves {insights.breakthrough_moments}" if insights.breakthrough_moments else "None detected"}

IDENTIFIED BOTTLENECKS:
{chr(10).join(f"• {b}" for b in insights.bottlenecks) if insights.bottlenecks else "• None - Healthy process"}

RECOMMENDATIONS:
{chr(10).join(f"→ {r}" for r in insights.recommendations)}

INTERPRETATION:
This session shows {"strong" if insights.overall_effectiveness > 0.7 else "moderate" if insights.overall_effectiveness > 0.4 else "weak"} 
design thinking with {"excellent" if len(insights.bottlenecks) == 0 else "some"} areas for improvement.
The designer demonstrates {insights.cognitive_profile.split('-')[0].lower()} cognitive patterns 
with {insights.design_strategy.split('-')[0].lower()} strategic approach.
"""
        return report


# Example usage for extracting insights
def analyze_all_sessions(sessions: List[LinkographSession]) -> Dict[str, SessionInsights]:
    """Analyze all sessions and extract insights"""
    
    extractor = LinkographyInsightExtractor()
    all_insights = {}
    
    for session in sessions:
        insights = extractor.analyze_session(session)
        all_insights[session.session_id] = insights
        
        # Print report
        print(extractor.generate_session_report(insights))
        print("-" * 80)
    
    return all_insights