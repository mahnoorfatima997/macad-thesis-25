"""Orchestration package.

This package contains the LangGraph-based workflow orchestrator and its
modularized components (nodes, routing, synthesis, graph builder, and types).

Public API:
    - LangGraphOrchestrator
"""

from .orchestrator import LangGraphOrchestrator  # re-export for convenience

__all__ = ["LangGraphOrchestrator"]


