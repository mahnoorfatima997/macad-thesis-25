"""
Wrapper for MENTOR environment that handles initialization issues gracefully
"""

import streamlit as st
import sys
import os

# Add paths
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
if thesis_agents_dir not in sys.path:
    sys.path.insert(0, thesis_agents_dir)

class MentorOrchestratorWrapper:
    """Wrapper that handles ChromaDB initialization issues"""
    
    def __init__(self):
        self._orchestrator = None
        self._init_error = None
        
        try:
            from orchestration.langgraph_orchestrator import LangGraphOrchestrator
            self._orchestrator = LangGraphOrchestrator(domain="architecture")
        except Exception as e:
            self._init_error = str(e)
            # If it's just the ChromaDB collection exists error, try to use existing
            if "already exists" in str(e):
                try:
                    # Try a different approach - modify the knowledge manager temporarily
                    self._setup_with_existing_collection()
                except:
                    pass
    
    def _setup_with_existing_collection(self):
        """Setup orchestrator with existing ChromaDB collection"""
        # Temporarily patch the KnowledgeManager to use get_or_create
        import chromadb
        from orchestration.langgraph_orchestrator import LangGraphOrchestrator
        from agents.analysis_agent import AnalysisAgent
        from knowledge_base.knowledge_manager import KnowledgeManager
        
        # Monkey patch the __init__ method
        original_init = KnowledgeManager.__init__
        
        def patched_init(self, domain="architecture", collection_name=None):
            self.domain = domain
            self.collection_name = collection_name or f"{domain}_knowledge"
            self.client = chromadb.PersistentClient(path="./knowledge_base/vectorstore")
            
            try:
                # Try to get existing collection first
                self.collection = self.client.get_collection(name=self.collection_name)
                print(f"Using existing collection: {self.collection_name}")
            except:
                # If it doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"Created new collection: {self.collection_name}")
        
        # Apply patch
        KnowledgeManager.__init__ = patched_init
        
        try:
            # Now try to create orchestrator again
            self._orchestrator = LangGraphOrchestrator(domain="architecture")
        finally:
            # Restore original method
            KnowledgeManager.__init__ = original_init
    
    async def process_student_input(self, state):
        """Process input through orchestrator or return fallback"""
        if self._orchestrator:
            return await self._orchestrator.process_student_input(state)
        else:
            # Fallback response if orchestrator failed to initialize
            return {
                'response': "I'm experiencing some technical difficulties, but I'm here to help guide your architectural thinking. What aspects of the community center design are you exploring?",
                'metadata': {'error': self._init_error},
                'routing_path': 'fallback',
                'classification': {}
            }
    
    @property
    def is_available(self):
        """Check if orchestrator is available"""
        return self._orchestrator is not None