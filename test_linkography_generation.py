"""
Test that linkography is generating links between moves
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'benchmarking'))

from data_models import DesignMove, TestPhase, MoveType, MoveSource, Modality, DesignFocus
from linkography_logger import LinkographyLogger
from datetime import datetime
import uuid
import time

def test_linkography_generation():
    """Test that linkography generates links between related moves"""
    print("Testing Linkography Link Generation...")
    print("=" * 60)
    
    # Create linkography logger
    session_id = str(uuid.uuid4())
    linkography_logger = LinkographyLogger(session_id)
    
    print(f"Session ID: {session_id}")
    print()
    
    # Create related design moves with slight time delays
    moves = [
        DesignMove(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            sequence_number=1,
            content="I want to create an open community space that encourages social interaction",
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
            content="The open space should have circular seating arrangements to facilitate conversation",
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
            content="Social interaction areas need good natural lighting and ventilation",
            move_type=MoveType.ANALYSIS,
            phase=TestPhase.IDEATION,
            modality=Modality.TEXT,
            cognitive_operation="analysis",
            design_focus=DesignFocus.STRUCTURE,
            move_source=MoveSource.USER_GENERATED,
            complexity_score=0.5,
            cognitive_load="medium"
        ),
        DesignMove(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            sequence_number=4,
            content="Let's use sustainable materials like bamboo for the seating structures",
            move_type=MoveType.SYNTHESIS,
            phase=TestPhase.MATERIALIZATION,
            modality=Modality.TEXT,
            cognitive_operation="proposal",
            design_focus=DesignFocus.MATERIAL,
            move_source=MoveSource.USER_GENERATED,
            complexity_score=0.6,
            cognitive_load="medium"
        )
    ]
    
    # Log moves with small delays to ensure different timestamps
    for i, move in enumerate(moves):
        print(f"\nLogging move {i+1}: {move.content[:50]}...")
        
        # Log the move
        linkography_logger.log_design_move(move)
        
        # Check metrics after each move
        metrics = linkography_logger.get_linkography_metrics()
        print(f"After move {i+1}:")
        print(f"  - Total moves: {metrics.get('total_moves', 0)}")
        print(f"  - Total links: {metrics.get('total_links', 0)}")
        print(f"  - Link density: {metrics.get('link_density', 0):.3f}")
        
        # Get current linkograph to see links
        linkograph = linkography_logger.get_current_linkograph()
        if linkograph and linkograph.links:
            print(f"  - Links found:")
            for link in linkograph.links[-3:]:  # Show last 3 links
                print(f"    - Link strength {link.strength:.2f} between moves")
        
        # Small delay between moves
        time.sleep(0.1)
    
    # Finalize and check final metrics
    print("\n" + "=" * 60)
    print("Finalizing linkography...")
    linkography_logger.finalize()
    
    final_metrics = linkography_logger.get_linkography_metrics()
    print("\nFinal Metrics:")
    print(f"  - Total moves: {final_metrics.get('total_moves', 0)}")
    print(f"  - Total links: {final_metrics.get('total_links', 0)}")
    print(f"  - Link density: {final_metrics.get('link_density', 0):.3f}")
    print(f"  - Critical move ratio: {final_metrics.get('critical_move_ratio', 0):.3f}")
    
    # Check if linkography file was created
    linkography_file = linkography_logger.linkography_file
    if os.path.exists(linkography_file):
        print(f"\nLinkography file created: {linkography_file}")
    
    print("\nTest completed!")
    return True

if __name__ == "__main__":
    test_linkography_generation()