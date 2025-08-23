"""
Integration module for enhanced data collection in unified dashboard
This module patches the unified dashboard to use complete metric collection
"""

import time
from typing import Dict, Any, Optional
from thesis_tests.enhanced_data_collector import EnhancedDataCollector


class EnhancedDashboardIntegration:
    """Integration layer for enhanced data collection"""
    
    def __init__(self, dashboard_instance):
        self.dashboard = dashboard_instance
        self.enhanced_collectors = {}
        
    def create_enhanced_collector(self, session_id: str, participant_id: str, test_group: str) -> EnhancedDataCollector:
        """Create an enhanced data collector for a session"""
        
        collector = EnhancedDataCollector(session_id, participant_id, test_group)
        self.enhanced_collectors[session_id] = collector
        return collector
    
    async def process_interaction_with_metrics(self, 
                                              user_input: str,
                                              mode: str,
                                              session_id: str,
                                              participant_id: str = "unified_user") -> Dict[str, Any]:
        """Process interaction with complete metric collection"""
        
        # Get or create enhanced collector
        if session_id not in self.enhanced_collectors:
            test_group = "MENTOR" if mode == "mentor" else "GENERIC_AI"
            self.enhanced_collectors[session_id] = EnhancedDataCollector(
                session_id, participant_id, test_group
            )
        
        collector = self.enhanced_collectors[session_id]
        
        # Track response time
        start_time = time.time()
        
        # Process based on mode
        if mode == "mentor":
            # Use the orchestrator for MENTOR mode
            state = {
                "messages": [{"role": "user", "content": user_input}],
                "current_agent": "orchestrator",
                "user_context": {
                    "skill_level": collector.user_state.skill_level,
                    "understanding": collector.user_state.understanding_level,
                    "confidence": collector.user_state.confidence_level,
                    "engagement": collector.user_state.engagement_level
                }
            }
            
            result = await self.dashboard.orchestrator.process_student_input(state)
            response = result.get("response", "I couldn't generate a response.")
            
            # Extract agent information
            agent_info = {
                'routing_path': result.get('routing_path', 'orchestrator'),
                'agents_used': result.get('agents_used', 'orchestrator'),
                'primary_agent': result.get('primary_agent', 'orchestrator'),
                'agent_type': result.get('agent_type', 'mentor')
            }
            
        else:  # Generic AI mode
            response = self.dashboard.test_dashboard.generic_ai_env.process_input(user_input)
            agent_info = {
                'routing_path': 'direct',
                'agents_used': 'generic_ai',
                'primary_agent': 'generic_ai',
                'agent_type': 'direct'
            }
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record interaction with all metrics
        interaction_data = collector.record_interaction(
            user_input=user_input,
            system_response=response,
            response_time=response_time,
            agent_info=agent_info
        )
        
        # Return response and metrics
        return {
            'response': response,
            'metrics': interaction_data,
            'session_summary': collector.get_session_summary()
        }
    
    def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a session"""
        
        if session_id in self.enhanced_collectors:
            return self.enhanced_collectors[session_id].get_session_summary()
        return {}


def patch_unified_dashboard():
    """
    Patch the unified dashboard to use enhanced data collection
    
    Usage in unified_architectural_dashboard.py:
    
    1. Import this module:
       from unified_dashboard_enhanced import patch_unified_dashboard, EnhancedDashboardIntegration
    
    2. After initializing UnifiedDashboard:
       dashboard = UnifiedDashboard()
       enhanced_integration = EnhancedDashboardIntegration(dashboard)
    
    3. Replace process methods with:
       result = await enhanced_integration.process_interaction_with_metrics(
           user_input, mode, session_id
       )
       response = result['response']
       metrics = result['metrics']
    """
    
    import unified_architectural_dashboard as uad
    
    # Store original methods
    original_process_mentor = uad.UnifiedDashboard._process_mentor_mode
    original_process_generic = uad.UnifiedDashboard._process_generic_ai_mode
    
    # Create patched methods
    async def patched_process_mentor(self, user_input: str) -> str:
        """Enhanced mentor mode processing with complete metrics"""
        
        # Create enhanced integration if not exists
        if not hasattr(self, 'enhanced_integration'):
            self.enhanced_integration = EnhancedDashboardIntegration(self)
        
        # Get session ID
        import streamlit as st
        from datetime import datetime
        if not st.session_state.get('session_id'):
            st.session_state.session_id = f"mentor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process with metrics
        result = await self.enhanced_integration.process_interaction_with_metrics(
            user_input, 'mentor', st.session_state.session_id
        )
        
        # Display metrics in sidebar (optional)
        if st.session_state.get('show_metrics', False):
            with st.sidebar:
                st.subheader("Cognitive Metrics")
                metrics = result['metrics']
                st.metric("Offloading Prevention", f"{metrics['prevents_cognitive_offloading']:.1%}")
                st.metric("Deep Thinking", f"{metrics['encourages_deep_thinking']:.1%}")
                st.metric("Scaffolding", f"{metrics['provides_scaffolding']:.1%}")
                st.metric("Engagement", f"{metrics['maintains_engagement']:.1%}")
        
        return result['response']
    
    async def patched_process_generic(self, user_input: str) -> str:
        """Enhanced generic AI processing with complete metrics"""
        
        # Create enhanced integration if not exists
        if not hasattr(self, 'enhanced_integration'):
            self.enhanced_integration = EnhancedDashboardIntegration(self)
        
        # Get session ID
        import streamlit as st
        from datetime import datetime
        if not st.session_state.get('session_id'):
            st.session_state.session_id = f"generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process with metrics
        result = await self.enhanced_integration.process_interaction_with_metrics(
            user_input, 'generic', st.session_state.session_id
        )
        
        # Display metrics in sidebar (optional)
        if st.session_state.get('show_metrics', False):
            with st.sidebar:
                st.subheader("Cognitive Metrics")
                metrics = result['metrics']
                st.metric("Offloading Prevention", f"{metrics['prevents_cognitive_offloading']:.1%}")
                st.metric("Deep Thinking", f"{metrics['encourages_deep_thinking']:.1%}")
                st.metric("Scaffolding", f"{metrics['provides_scaffolding']:.1%}")
        
        return result['response']
    
    # Apply patches
    uad.UnifiedDashboard._process_mentor_mode = patched_process_mentor
    uad.UnifiedDashboard._process_generic_ai_mode = patched_process_generic
    
    print("✓ Unified dashboard patched with enhanced data collection")
    
    return True