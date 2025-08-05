"""
Test script to debug concept extraction
"""

from session_knowledge_graphs import SessionKnowledgeGraphBuilder
from linkography_analyzer import LinkographySessionAnalyzer
import json

# Initialize
analyzer = LinkographySessionAnalyzer()
kg_builder = SessionKnowledgeGraphBuilder()

# Get sessions
sessions = analyzer.analyze_all_sessions()

if sessions:
    # Test on first session
    first_session_id = list(sessions.keys())[0]
    session = sessions[first_session_id]
    
    print(f"\n=== Testing Session {first_session_id[:8]} ===")
    print(f"Has linkographs: {len(session.linkographs)}")
    print(f"Has raw_data: {hasattr(session, 'raw_data') and session.raw_data is not None}")
    
    if hasattr(session, 'raw_data') and session.raw_data:
        print(f"Raw data keys: {session.raw_data.keys()}")
        if 'interactions' in session.raw_data:
            print(f"Number of interactions: {len(session.raw_data['interactions'])}")
            # Show first interaction
            if session.raw_data['interactions']:
                first = session.raw_data['interactions'][0]
                print(f"\nFirst interaction sample:")
                print(f"  User: {first.get('user_message', '')[:100]}...")
                print(f"  AI: {first.get('ai_response', '')[:100]}...")
    
    # Test concept extraction on sample text
    print("\n=== Testing concept extraction ===")
    test_text = "I want to design a sustainable building with natural light and open spaces for the community"
    concepts = kg_builder.extract_concepts_from_text(test_text)
    print(f"Test text: {test_text}")
    print(f"Extracted concepts: {concepts}")
    
    # Build graph
    print("\n=== Building knowledge graph ===")
    G = kg_builder.build_session_knowledge_graph(session)
    print(f"Graph nodes: {len(G.nodes())}")
    print(f"Graph edges: {len(G.edges())}")
    
    if G.nodes():
        print("\nSample nodes:")
        for i, (node, data) in enumerate(G.nodes(data=True)):
            if i < 5:
                print(f"  - {data['label']} ({data['category']}): {data['count']} mentions")
else:
    print("No sessions found!")