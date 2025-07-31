"""
Verify that metrics are being updated properly during test sessions
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis_tests'))

from data_models import DesignMove, TestPhase, MoveType, MoveSource, Modality, DesignFocus
from linkography_logger import LinkographyLogger
from logging_system import TestSessionLogger, TestGroup
from datetime import datetime
import uuid

def test_metrics_update():
    """Test that metrics update properly when moves are logged"""
    print("Testing Metrics Updates...")
    print("=" * 60)
    
    # Create session logger
    session_id = str(uuid.uuid4())
    logger = TestSessionLogger(
        session_id=session_id,
        participant_id="TEST001",
        test_group=TestGroup.MENTOR
    )
    
    # Create linkography logger
    linkography_logger = LinkographyLogger(session_id)
    
    print(f"Session ID: {session_id}")
    print(f"Initial metrics: {linkography_logger.get_linkography_metrics()}")
    print()
    
    # Create and log some design moves
    moves = [
        DesignMove(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            sequence_number=1,
            content="I want to create an open community space",
            move_type=MoveType.SYNTHESIS,
            phase=TestPhase.IDEATION,
            modality=Modality.TEXT,
            cognitive_operation="proposal",
            design_focus=DesignFocus.FUNCTION,
            move_source=MoveSource.USER_GENERATED,
            complexity_score=0.6,
            cognitive_load="medium"
        ),
        DesignMove(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            sequence_number=2,
            content="What if we used circular forms to encourage gathering?",
            move_type=MoveType.TRANSFORMATION,
            phase=TestPhase.IDEATION,
            modality=Modality.TEXT,
            cognitive_operation="transformation",
            design_focus=DesignFocus.FORM,
            move_source=MoveSource.USER_GENERATED,
            complexity_score=0.7,
            cognitive_load="high"
        ),
        DesignMove(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            sequence_number=3,
            content="The circulation should connect all main functions",
            move_type=MoveType.ANALYSIS,
            phase=TestPhase.IDEATION,
            modality=Modality.TEXT,
            cognitive_operation="analysis",
            design_focus=DesignFocus.STRUCTURE,
            move_source=MoveSource.USER_GENERATED,
            complexity_score=0.5,
            cognitive_load="medium"
        )
    ]
    
    # Log moves
    for i, move in enumerate(moves):
        print(f"\nLogging move {i+1}: {move.content[:50]}...")
        
        # Log to both loggers
        logger.log_design_move(move)
        linkography_logger.log_design_move(move)
        
        # Check metrics after each move
        metrics = linkography_logger.get_linkography_metrics()
        print(f"Metrics after move {i+1}:")
        print(f"  - Total moves: {metrics.get('total_moves', 0)}")
        print(f"  - Total links: {metrics.get('total_links', 0)}")
        print(f"  - Link density: {metrics.get('link_density', 0):.3f}")
        print(f"  - Move diversity: {metrics.get('move_diversity', 0):.3f}")
    
    # Test cognitive metrics logging
    print("\n" + "=" * 60)
    print("Testing Cognitive Metrics...")
    
    cognitive_metrics = {
        'cop': 0.75,  # Cognitive Offloading Prevention
        'dte': 0.68,  # Deep Thinking Engagement
        'se': 0.82,   # Scaffolding Effectiveness
        'ki': 0.45,   # Knowledge Integration
        'lp': 0.55,   # Learning Progression
        'ma': 0.71,   # Metacognitive Awareness
        'composite': 0.66
    }
    
    logger.log_cognitive_metrics(cognitive_metrics)
    
    # Get session summary
    summary = logger.get_session_summary()
    print("\nSession Summary:")
    print(f"  - Total moves: {summary['total_moves']}")
    print(f"  - Total interactions: {summary['total_interactions']}")
    print(f"  - Cognitive metrics available: {'cognitive_metrics' in summary}")
    
    if 'cognitive_metrics' in summary:
        print("\nCognitive Metrics:")
        for metric, value in summary['cognitive_metrics'].items():
            print(f"  - {metric.upper()}: {value:.2%}")
    
    print("\n✅ Metrics test completed!")
    return True

if __name__ == "__main__":
    test_metrics_update()