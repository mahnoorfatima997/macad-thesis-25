"""
Centralized telemetry system for consistent logging across agents.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime


class AgentTelemetry:
    """
    Centralized telemetry and logging system for all agents.
    
    Provides consistent logging, timing, and metrics collection
    across the entire agent system.
    """
    
    def __init__(self, agent_name: Optional[str] = None):
        self.agent_name = agent_name or "unknown_agent"
        self.logger = self._setup_logger()
        self.start_times = {}
        self.counters = {}
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging for the agent."""
        logger = logging.getLogger(f"thesis_agents.{self.agent_name}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def log_agent_start(self, method: str, **kwargs):
        """Log the start of an agent method."""
        self.logger.info(f"🚀 {self.agent_name}.{method} started", extra=kwargs)
        self.start_times[method] = time.time()
    
    def log_agent_end(self, method: str, **kwargs):
        """Log the end of an agent method with timing."""
        if method in self.start_times:
            duration = time.time() - self.start_times[method]
            self.logger.info(f"✅ {self.agent_name}.{method} completed in {duration:.2f}s", extra=kwargs)
            del self.start_times[method]
        else:
            self.logger.info(f"✅ {self.agent_name}.{method} completed", extra=kwargs)
    
    def log_llm_call(self, model: str, message_count: int):
        """Log LLM API call."""
        self.logger.debug(f"🤖 LLM call: model={model}, messages={message_count}")
        self.increment_counter("llm_calls")
    
    def log_llm_response(self, response: Dict[str, Any]):
        """Log LLM response details."""
        usage = response.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        self.logger.debug(f"🤖 LLM response: tokens={tokens}, finish_reason={response.get('finish_reason')}")
    
    def log_phase_detection(self, detected_phase: str, confidence: float):
        """Log phase detection results."""
        self.logger.info(f"🎯 Phase detected: {detected_phase} (confidence: {confidence:.2f})")
    
    def log_skill_assessment(self, skill_level: str, confidence: float):
        """Log skill level assessment results."""
        self.logger.info(f"📊 Skill assessed: {skill_level} (confidence: {confidence:.2f})")
    
    def log_cognitive_flags(self, flags: list):
        """Log cognitive flags generated."""
        if flags:
            self.logger.info(f"🧠 Cognitive flags: {', '.join(flags)}")
    
    def log_error(self, error_message: str, **kwargs):
        """Log error with context."""
        self.logger.error(f"❌ {error_message}", extra=kwargs)
        self.increment_counter("errors")
    
    def log_warning(self, warning_message: str, **kwargs):
        """Log warning with context."""
        self.logger.warning(f"⚠️ {warning_message}", extra=kwargs)
        self.increment_counter("warnings")
    
    def log_debug(self, debug_message: str, **kwargs):
        """Log debug information."""
        self.logger.debug(f"🔍 {debug_message}", extra=kwargs)
    
    def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment a named counter."""
        self.counters[counter_name] = self.counters.get(counter_name, 0) + amount
    
    def get_counters(self) -> Dict[str, int]:
        """Get all counter values."""
        return self.counters.copy()
    
    def reset_counters(self):
        """Reset all counters."""
        self.counters.clear()
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log structured metrics."""
        metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
        self.logger.info(f"📈 Metrics: {metrics_str}")
    
    def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        return TimedOperation(self, operation_name)


class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, telemetry: AgentTelemetry, operation_name: str):
        self.telemetry = telemetry
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.telemetry.log_debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.telemetry.log_debug(f"Completed {self.operation_name} in {duration:.2f}s")
        else:
            self.telemetry.log_error(f"Failed {self.operation_name} after {duration:.2f}s: {exc_val}") 