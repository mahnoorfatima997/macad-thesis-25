# Agent Cleanup Plan

## Overview
This plan identifies unused code, redundancies, and cleanup actions for each agent file in the thesis-agents/agents directory.

## 1. Context Agent (`context_agent.py`)

### Issues Found
1. **Redundant OpenAI Client**
   - Each agent creates its own client instance
   - Memory leak potential

2. **Incomplete Methods**
   ```python
   # Line 154: Incomplete implementation
   context_package
   ```

3. **Unused Analysis Patterns**
   ```python
   # Many patterns defined but not used in core logic
   self.analysis_patterns = self._initialize_analysis_patterns()
   ```

### Cleanup Actions
```python
# 1. Replace individual client with shared instance
from utils.client_manager import get_shared_client

class ContextAgent:
    def __init__(self, domain="architecture"):
        self.client = get_shared_client()
        self.domain = domain
        self.name = "context_agent"

# 2. Complete context package implementation
def _compile_context_package(self, 
                           core_classification: Dict,
                           content_analysis: Dict,
                           routing_suggestions: Dict) -> Dict:
    return {
        "classification": core_classification,
        "content": content_analysis,
        "routing": routing_suggestions
    }

# 3. Remove unused patterns, keep only what's used in core logic
```

## 2. Analysis Agent (`analysis_agent.py`)

### Issues Found
1. **Redundant Imports**
   ```python
   import re  # Unused
   from datetime import datetime, timedelta  # Partially used
   ```

2. **Memory Leak**
   ```python
   self.client = OpenAI()  # Comment notes memory issue
   ```

3. **Incomplete Initialization**
   ```python
   # Line 33: Incomplete initialization
   # 0708-Initialize conversation progression manager
   ```

### Cleanup Actions
```python
# 1. Clean up imports
from typing import Dict, Any, List, Optional
import sys
import os
from openai import OpenAI
from datetime import datetime
import numpy as np

# 2. Fix client initialization
from utils.client_manager import get_shared_client

class AnalysisAgent:
    def __init__(self, domain="architecture"):
        self.client = get_shared_client()
        # ... rest of init

# 3. Complete or remove incomplete initialization
```

## 3. Socratic Tutor (`socratic_tutor.py`)

### Issues Found
1. **Redundant Client Setup**
   ```python
   self.client = OpenAI()
   self.llm = self.client.chat.completions  # Redundant
   ```

2. **Incomplete Implementation**
   ```python
   # Line 47: Incomplete
   student_analysis
   ```

3. **Unnecessary Print Statements**
   ```python
   print(f"🤔 {self.name} initialized for domain: {domain}")
   ```

### Cleanup Actions
```python
class SocraticTutorAgent:
    def __init__(self, domain="architecture"):
        self.client = get_shared_client()
        self.domain = domain
        self.name = "socratic_tutor"

    async def generate_response(self, 
                              state: ArchMentorState,
                              analysis_result: Dict[str, Any],
                              context_classification: Optional[Dict] = None,
                              domain_expert_result: Optional[Dict] = None) -> AgentResponse:
        # Remove print statements, use logger
        logger.info(f"{self.name}: Generating response")
```

## 4. Cognitive Enhancement (`cognitive_enhancement.py`)

### Issues Found
1. **Redundant Print Statements**
   ```python
   print(f"\n🧠 {self.name} providing enhanced cognitive challenge...")
   print(f"🧠 Cognitive state assessment: {cognitive_state}")
   ```

2. **Duplicate Metric Calculations**
   ```python
   scientific_metrics = self.calculate_scientific_metrics()
   validation_result = self.validate_thesis_metrics()
   # Metrics calculated multiple times
   ```

3. **Unused Challenge Templates**
   ```python
   def _initialize_challenge_templates(self):
       # Many templates defined but not all used
   ```

### Cleanup Actions
```python
class CognitiveEnhancementAgent:
    def __init__(self, domain="architecture"):
        self.client = get_shared_client()
        self.domain = domain
        self.name = "cognitive_enhancement"
        self.metrics_calculator = MetricsCalculator()

    async def provide_challenge(self,
                              state: ArchMentorState,
                              context: Dict) -> AgentResponse:
        metrics = await self.metrics_calculator.calculate_once(state)
        return await self._generate_challenge(state, metrics)
```

## 5. Domain Expert (`domain_expert.py`)

### Issues Found
1. **Unused Helper Functions**
   ```python
   def is_building_request(text: str) -> bool:
   def is_landscape_request(text: str) -> bool:
   def get_search_query_modifiers(text: str) -> Dict[str, str]:
   ```

2. **Redundant Client Setup**
   ```python
   self.client = OpenAI()
   ```

### Cleanup Actions
```python
# 1. Remove unused helpers or integrate them
class DomainExpertAgent:
    def __init__(self, domain="architecture"):
        self.client = get_shared_client()
        self.domain = domain
        self.name = "domain_expert"
```

## Implementation Steps

### 1. Create Shared Client Manager
```python
# utils/client_manager.py
class ClientManager:
    _instance = None
    
    @classmethod
    def get_client(cls):
        if not cls._instance:
            cls._instance = OpenAI()
        return cls._instance
```

### 2. Update Agent Base Class
```python
# agents/base_agent.py
class BaseAgent:
    def __init__(self, domain: str):
        self.client = get_shared_client()
        self.domain = domain
        self.logger = setup_logger(self.__class__.__name__)
    
    def _log(self, message: str):
        self.logger.info(f"{self.name}: {message}")
```

### 3. Clean Each Agent
1. Remove unused imports
2. Replace client initialization
3. Complete incomplete methods
4. Remove redundant code
5. Add proper logging

### 4. Add Tests
```python
# tests/test_agents.py
async def test_agent_initialization():
    # Ensure single client instance
    agent1 = ContextAgent()
    agent2 = AnalysisAgent()
    assert id(agent1.client) == id(agent2.client)
```

## Success Criteria
- Reduced file sizes
- No redundant client instances
- Complete implementations
- Proper logging
- Passing tests

Would you like me to start implementing these cleanup changes? I recommend starting with:
1. Creating the shared client manager
2. Implementing the base agent class
3. Cleaning up the context agent
4. Adding initial tests
