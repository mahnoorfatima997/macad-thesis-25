"""
Cached intersection calculation for performance optimization
"""

from typing import Dict, Tuple, Optional, List
import hashlib
import json
from linkography_intersection_precise import find_arc_intersection, check_arcs_actually_cross

# Global cache for intersection calculations
_intersection_cache: Dict[str, Optional[Tuple[float, float]]] = {}
_crossing_cache: Dict[str, bool] = {}

def _get_arc_key(s1: float, t1: float, s2: float, t2: float) -> str:
    """Generate a unique key for an arc pair"""
    # Normalize order to ensure consistent keys
    if (s1, t1) > (s2, t2):
        s1, t1, s2, t2 = s2, t2, s1, t1
    return f"{s1:.2f},{t1:.2f},{s2:.2f},{t2:.2f}"

def check_arcs_cross_cached(s1: float, t1: float, s2: float, t2: float) -> bool:
    """Cached version of arc crossing check"""
    key = _get_arc_key(s1, t1, s2, t2)
    
    if key not in _crossing_cache:
        _crossing_cache[key] = check_arcs_actually_cross(s1, t1, s2, t2)
    
    return _crossing_cache[key]

def find_arc_intersection_cached(s1: float, t1: float, s2: float, t2: float, 
                                precision: int = 200) -> Optional[Tuple[float, float]]:
    """
    Cached version of arc intersection with reduced default precision.
    Uses 200 points by default (good enough for visual accuracy).
    """
    key = f"{_get_arc_key(s1, t1, s2, t2)}_{precision}"
    
    if key not in _intersection_cache:
        # Use lower precision for faster calculation
        _intersection_cache[key] = find_arc_intersection(s1, t1, s2, t2, precision)
    
    return _intersection_cache[key]

def clear_intersection_cache():
    """Clear the cache when needed"""
    global _intersection_cache, _crossing_cache
    _intersection_cache.clear()
    _crossing_cache.clear()

def get_cache_size() -> int:
    """Get the current cache size"""
    return len(_intersection_cache) + len(_crossing_cache)