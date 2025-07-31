"""
Test that linkography data is being loaded properly in the benchmarking dashboard
"""

import sys
import os
from pathlib import Path

# Add benchmarking to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'benchmarking'))

from linkography_analyzer import LinkographySessionAnalyzer

def test_linkography_loading():
    """Test loading linkography data from files"""
    print("Testing Linkography Data Loading")
    print("=" * 60)
    
    # Check if linkography directory exists
    linkography_dir = Path("./thesis_data/linkography")
    if not linkography_dir.exists():
        print(f"ERROR: Linkography directory not found at {linkography_dir}")
        return False
    
    # List available linkography files
    linkography_files = list(linkography_dir.glob("linkography_*.json"))
    print(f"\nFound {len(linkography_files)} linkography files:")
    for file in linkography_files[:5]:  # Show first 5
        print(f"  - {file.name}")
    
    # Initialize analyzer
    print("\nInitializing LinkographySessionAnalyzer...")
    analyzer = LinkographySessionAnalyzer()
    
    # Load sessions
    print("\nLoading sessions...")
    sessions = analyzer.analyze_all_sessions()
    
    print(f"\nLoaded {len(sessions)} sessions:")
    for session_id, session in list(sessions.items())[:3]:  # Show first 3
        print(f"\n  Session: {session_id[:8]}...")
        print(f"    - Total moves: {sum(len(lg.moves) for lg in session.linkographs)}")
        print(f"    - Total links: {sum(len(lg.links) for lg in session.linkographs)}")
        print(f"    - Link density: {session.overall_metrics.link_density:.2f}")
        print(f"    - Patterns detected: {len(session.patterns_detected)}")
        
        # Show first move if available
        if session.linkographs and session.linkographs[0].moves:
            first_move = session.linkographs[0].moves[0]
            print(f"    - First move: {first_move.content[:50]}...")
    
    if len(sessions) > 0:
        print(f"\n✅ SUCCESS: Linkography data is loading properly!")
        print(f"   - {len(sessions)} sessions available for analysis")
        print(f"   - Data should now appear in the benchmarking dashboard")
    else:
        print(f"\n❌ FAILURE: No sessions were loaded")
        print(f"   - Check if linkography files have correct format")
        print(f"   - Check console for error messages")
    
    return len(sessions) > 0

if __name__ == "__main__":
    test_linkography_loading()