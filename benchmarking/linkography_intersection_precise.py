"""
Mathematically precise intersection detection for linkography arcs
Priority: PRECISION over performance
"""

import numpy as np
from typing import List, Tuple, Optional
import math


def get_arc_point(start: float, end: float, t: float) -> Tuple[float, float]:
    """
    Get a point on a parabolic arc at parameter t (0 to 1).
    Arc goes from (start, 0) to (end, 0) with parabolic shape.
    """
    x = start + (end - start) * t
    # Parabolic equation: y = 4 * depth * t * (1 - t)
    # Depth is proportional to the span
    depth = -abs(end - start) * 0.5
    y = 4 * depth * t * (1 - t)
    return (x, y)


def find_arc_intersection(s1: float, t1: float, s2: float, t2: float, 
                         precision: int = 1000) -> Optional[Tuple[float, float]]:
    """
    Find the precise intersection point of two parabolic arcs.
    
    Args:
        s1, t1: Start and end of first arc
        s2, t2: Start and end of second arc
        precision: Number of points to sample on each arc
        
    Returns:
        (x, y) coordinates of intersection, or None if no intersection
    """
    # Ensure proper ordering
    if s1 > t1:
        s1, t1 = t1, s1
    if s2 > t2:
        s2, t2 = t2, s2
    
    # Generate points along both arcs
    arc1_points = []
    arc2_points = []
    
    for i in range(precision + 1):
        t = i / precision
        arc1_points.append(get_arc_point(s1, t1, t))
        arc2_points.append(get_arc_point(s2, t2, t))
    
    # Find the closest approach between any two points
    min_distance = float('inf')
    intersection = None
    
    # For each segment of arc1
    for i in range(len(arc1_points) - 1):
        p1_start = arc1_points[i]
        p1_end = arc1_points[i + 1]
        
        # Check against each segment of arc2
        for j in range(len(arc2_points) - 1):
            p2_start = arc2_points[j]
            p2_end = arc2_points[j + 1]
            
            # Find intersection of two line segments
            intersection_point = line_segment_intersection(
                p1_start, p1_end, p2_start, p2_end
            )
            
            if intersection_point:
                # We found an actual intersection!
                return intersection_point
    
    # If no exact intersection, find closest approach
    for p1 in arc1_points:
        for p2 in arc2_points:
            dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            if dist < min_distance:
                min_distance = dist
                # Only consider it an intersection if points are very close
                if dist < 0.1:  # Threshold for "touching"
                    intersection = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    
    return intersection


def line_segment_intersection(p1: Tuple[float, float], p2: Tuple[float, float],
                             p3: Tuple[float, float], p4: Tuple[float, float]) -> Optional[Tuple[float, float]]:
    """
    Find intersection point of two line segments.
    
    Args:
        p1, p2: Endpoints of first segment
        p3, p4: Endpoints of second segment
        
    Returns:
        Intersection point or None if segments don't intersect
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Calculate denominator
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    # Lines are parallel if denominator is 0
    if abs(denom) < 1e-10:
        return None
    
    # Calculate intersection parameters
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    # Check if intersection is within both segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate intersection point
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    
    return None


def check_arcs_actually_cross(s1: float, t1: float, s2: float, t2: float) -> bool:
    """
    Check if two arcs actually have a crossing pattern.
    This is more strict than just overlapping ranges.
    """
    # Ensure proper ordering
    if s1 > t1:
        s1, t1 = t1, s1
    if s2 > t2:
        s2, t2 = t2, s2
    
    # For arcs to truly cross, one must start outside the other and end inside it
    # or pass completely through it
    
    # Pattern 1: Arc1 starts before Arc2 and ends inside Arc2's range
    pattern1 = s1 < s2 and s2 < t1 < t2
    
    # Pattern 2: Arc2 starts before Arc1 and ends inside Arc1's range
    pattern2 = s2 < s1 and s1 < t2 < t1
    
    # Pattern 3: One arc completely contains the other (they must cross twice)
    # But for linkography, we typically don't want this case
    
    return pattern1 or pattern2


def calculate_precise_intersections(links: List[Tuple[int, int]], 
                                   precision: int = 500) -> List[Tuple[float, float]]:
    """
    Calculate all intersection points for a set of links.
    
    Args:
        links: List of (source, target) pairs
        precision: Sampling precision for arc intersection
        
    Returns:
        List of (x, y) intersection points
    """
    intersections = []
    
    # Check all pairs of links
    for i in range(len(links)):
        s1, t1 = links[i]
        
        for j in range(i + 1, len(links)):
            s2, t2 = links[j]
            
            # First check if arcs can possibly cross
            if check_arcs_actually_cross(s1, t1, s2, t2):
                # Find precise intersection
                intersection = find_arc_intersection(s1, t1, s2, t2, precision)
                
                if intersection:
                    intersections.append(intersection)
    
    return intersections