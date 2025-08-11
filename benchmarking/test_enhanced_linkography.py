"""
Test script to verify enhanced linkography is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarking.linkography_enhanced import EnhancedLinkographVisualizer
from benchmarking.linkography_types import Linkograph, DesignMove, LinkographLink, LinkographMetrics
import uuid

# Create a simple test linkograph
moves = [
    DesignMove(
        id=str(uuid.uuid4()),
        timestamp=i * 1000,
        session_id="test_session",
        user_id="test_user",
        phase="ideation" if i < 3 else "visualization" if i < 6 else "materialization",
        content=f"Move {i}",
        move_type="analysis",
        modality="text",
        embedding=None
    )
    for i in range(8)
]

# Create some links to test intersection detection
links = [
    LinkographLink(
        id=str(uuid.uuid4()),
        source_move=moves[0].id,
        target_move=moves[3].id,
        strength=0.8,
        confidence=0.9,
        link_type="forward",
        temporal_distance=3,
        semantic_similarity=0.8,
        automated=True
    ),
    LinkographLink(
        id=str(uuid.uuid4()),
        source_move=moves[1].id,
        target_move=moves[5].id,
        strength=0.6,
        confidence=0.7,
        link_type="forward",
        temporal_distance=4,
        semantic_similarity=0.6,
        automated=True
    ),
    LinkographLink(
        id=str(uuid.uuid4()),
        source_move=moves[2].id,
        target_move=moves[4].id,
        strength=0.9,
        confidence=0.95,
        link_type="forward",
        temporal_distance=2,
        semantic_similarity=0.9,
        automated=True
    ),
    LinkographLink(
        id=str(uuid.uuid4()),
        source_move=moves[3].id,
        target_move=moves[6].id,
        strength=0.7,
        confidence=0.8,
        link_type="forward",
        temporal_distance=3,
        semantic_similarity=0.7,
        automated=True
    ),
]

# Create metrics
metrics = LinkographMetrics(
    link_density=len(links) / len(moves),
    critical_move_ratio=0.3,
    entropy=0.8,
    phase_balance={"ideation": 0.375, "visualization": 0.375, "materialization": 0.25},
    cognitive_indicators={}
)

# Create linkograph
test_linkograph = Linkograph(
    id=str(uuid.uuid4()),
    session_id="test_session",
    moves=moves,
    links=links,
    metrics=metrics,
    phase="overall",
    generated_at=0
)

# Test the enhanced visualizer
visualizer = EnhancedLinkographVisualizer()
try:
    fig = visualizer.create_enhanced_linkograph(
        test_linkograph,
        show_intersections=True,
        show_critical_moves=True,
        show_patterns=False,
        patterns=None,
        interactive=True
    )
    print("[OK] Enhanced linkograph created successfully!")
    print(f"  - Moves: {len(moves)}")
    print(f"  - Links: {len(links)}")
    
    # Save to HTML for inspection
    fig.write_html("test_enhanced_linkograph.html")
    print("[OK] Saved to test_enhanced_linkograph.html")
    
except Exception as e:
    print(f"[ERROR] Error creating enhanced linkograph: {e}")
    import traceback
    traceback.print_exc()