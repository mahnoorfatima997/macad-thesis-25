# Enhanced Pattern System Proposal

## Current Issues Identified

### 1. Pattern Conflicts
- `"I want to see case studies"` → `question_response` (should be `example_request`)
- `"what is"` → `technical_question` (should be `knowledge_request`)
- `"show me exactly"` → `example_request` (should be `direct_answer_request`)

### 2. Inconsistent Classification
- Same intent, different expressions get different classifications
- Manual override sometimes catches variations it shouldn't

### 3. Limited Flexibility
- Rigid pattern matching misses nuanced expressions
- AI classification handles variations better but is slower

## Test Results Analysis

### ✅ **Successes (38/53 tests - 71.7%)**
- **High-Confidence Patterns**: Working well for clear, unambiguous patterns
- **Direct Answer Requests**: All cognitive offloading patterns correctly identified
- **Example Requests**: Most example request patterns working correctly
- **Knowledge Requests**: Basic knowledge request patterns working
- **Other Interaction Types**: Feedback, confusion, improvement, technical questions working

### ❌ **Remaining Issues (15/53 tests - 28.3%)**

#### 1. **Context-Dependent Pattern Issues**
- `"I want to see case studies"` → `question_response` (should be `example_request`)
- `"I need you to create"` → `general_statement` (should be `direct_answer_request`)
- `"Could you build"` → `general_statement` (should be `direct_answer_request`)
- `"I'd like to see some"` → `general_statement` (should be `example_request`)
- `"Can I get references"` → `general_statement` (should be `example_request`)
- `"I want you to make"` → `general_statement` (should be `direct_answer_request`)
- `"Please design"` → `question_response` (should be `direct_answer_request`)
- `"Show me how to"` → `example_request` (should be `direct_answer_request`)

#### 2. **Knowledge Request Issues**
- `"I need to understand"` → `general_statement` (should be `knowledge_request`)
- `"I want to learn about"` → `general_statement` (should be `knowledge_request`)
- `"I need some references"` → `general_statement` (should be `example_request`)

#### 3. **Implementation Request Issues**
- `"how do I"` → `knowledge_request` (should be `implementation_request`)
- `"how to implement"` → `technical_question` (should be `implementation_request`)

#### 4. **Technical Question Issues**
- `"what is the requirement"` → `knowledge_request` (should be `technical_question`)

## Root Cause Analysis

### **Primary Issue: Pattern Priority and Specificity**
The main problem is that some patterns are being caught by more general patterns before reaching the specific ones:

1. **General Statement Patterns**: Too broad, catching specific requests
2. **Question Response Patterns**: Too broad, catching example requests
3. **Pattern Order**: General patterns are checked before specific ones

### **Secondary Issue: Pattern Completeness**
Some patterns are missing variations or are too specific:

1. **Missing Variations**: `"I need you to create"` not in direct answer patterns
2. **Incomplete Patterns**: `"Could you build"` not covered
3. **Context Insensitivity**: `"what is the requirement"` not recognized as technical

## Proposed Enhanced System

### 1. **Multi-Level Pattern Matching**

```python
# Level 1: High-Confidence Patterns (Manual Override)
HIGH_CONFIDENCE_PATTERNS = {
    "direct_answer_request": [
        "can you design", "design this for me", "do it for me",
        "make it for me", "complete design", "full design", "finished design"
    ],
    "example_request": [
        "show me examples", "can you give me examples", "provide me with examples",
        "can you show me precedents", "I need some references"
    ],
    "knowledge_request": [
        "tell me about", "what are", "explain", "describe",
        "I want to learn about", "can you explain"
    ]
}

# Level 2: Medium-Confidence Patterns (AI with Pattern Hint)
MEDIUM_CONFIDENCE_PATTERNS = {
    "direct_answer_request": [
        "I need you to create", "Could you build", "I want you to make",
        "Please design", "Show me how to"
    ],
    "example_request": [
        "I'd like to see some", "Can I get references", "I want to see case studies"
    ],
    "knowledge_request": [
        "I need to understand", "what is", "how do"
    ]
}

# Level 3: Context-Dependent Patterns (AI Classification)
CONTEXT_DEPENDENT_PATTERNS = {
    "show me": ["example_request", "direct_answer_request"],
    "tell me": ["knowledge_request", "direct_answer_request"],
    "help me": ["confusion_expression", "knowledge_request", "direct_answer_request"]
}
```

### 2. **Enhanced Classification Logic**

```python
async def _perform_enhanced_classification(self, input_text: str, state: ArchMentorState) -> Dict[str, Any]:
    """Enhanced classification with multi-level pattern matching"""
    
    input_lower = input_text.lower()
    
    # Level 1: High-Confidence Manual Override
    for intent, patterns in HIGH_CONFIDENCE_PATTERNS.items():
        if any(pattern in input_lower for pattern in patterns):
            return self._create_manual_override_result(intent, input_text, state)
    
    # Level 2: Medium-Confidence with AI Enhancement
    for intent, patterns in MEDIUM_CONFIDENCE_PATTERNS.items():
        if any(pattern in input_lower for pattern in patterns):
            return await self._create_ai_enhanced_result(intent, input_text, state)
    
    # Level 3: Context-Dependent with AI Classification
    for pattern, possible_intents in CONTEXT_DEPENDENT_PATTERNS.items():
        if pattern in input_lower:
            return await self._create_context_aware_result(possible_intents, input_text, state)
    
    # Level 4: Pure AI Classification
    return await self._get_ai_classification_for_other_metrics(input_text, state)
```

### 3. **Context-Aware Pattern Matching**

```python
def _analyze_context_for_pattern(self, input_text: str, state: ArchMentorState) -> str:
    """Analyze context to disambiguate patterns"""
    
    # Check conversation history
    recent_messages = state.messages[-3:] if state.messages else []
    
    # Check for question-response patterns
    if self._is_response_to_previous_question(input_text, state):
        return "question_response"
    
    # Check for cognitive offloading indicators
    if self._has_cognitive_offloading_indicators(input_text, recent_messages):
        return "direct_answer_request"
    
    # Check for knowledge seeking in context
    if self._is_knowledge_seeking_in_context(input_text, recent_messages):
        return "knowledge_request"
    
    return "unknown"
```

### 4. **Improved Pattern Definitions**

```python
# More specific and context-aware patterns
ENHANCED_PATTERNS = {
    "direct_answer_request": {
        "high_confidence": [
            "can you design", "design this for me", "do it for me",
            "make it for me", "complete design", "full design"
        ],
        "context_indicators": [
            "for me", "instead of me", "rather than me"
        ],
        "cognitive_offloading_phrases": [
            "just tell me", "give me the answer", "what's the solution"
        ]
    },
    "example_request": {
        "high_confidence": [
            "show me examples", "can you give me examples",
            "provide me with examples", "I need some references"
        ],
        "learning_indicators": [
            "I want to see", "I'd like to see", "Can I get"
        ],
        "specific_types": [
            "case studies", "precedents", "references", "examples"
        ]
    },
    "knowledge_request": {
        "high_confidence": [
            "tell me about", "what are", "explain", "describe"
        ],
        "learning_indicators": [
            "I want to learn", "I need to understand", "can you explain"
        ],
        "information_seeking": [
            "what is", "how do", "why is", "when should"
        ]
    }
}
```

## Benefits of Enhanced System

### 1. **Better Accuracy**
- Reduces false positives in manual override
- Handles context-dependent patterns better
- More consistent classification across variations

### 2. **Improved Flexibility**
- AI handles ambiguous cases
- Pattern hints guide AI classification
- Context awareness improves accuracy

### 3. **Maintainable Code**
- Clear separation of pattern types
- Easy to add new patterns
- Better debugging and testing

## Implementation Plan

### Phase 1: Pattern Refinement
1. Analyze test results to identify problematic patterns
2. Refine pattern definitions with better specificity
3. Add context-aware pattern matching

### Phase 2: Enhanced Classification
1. Implement multi-level classification system
2. Add context analysis for ambiguous patterns
3. Improve AI classification prompts

### Phase 3: Testing & Validation
1. Comprehensive testing with varied expressions
2. Performance optimization
3. User feedback integration

## Expected Outcomes

- **Reduced Pattern Conflicts**: Better handling of ambiguous expressions
- **Improved Consistency**: Same intent gets same classification regardless of expression
- **Enhanced Flexibility**: AI handles variations that manual patterns miss
- **Better User Experience**: More accurate routing and responses

This enhanced system addresses your concern about manual override being problematic when users express intent in different ways, while maintaining the benefits of fast pattern matching for clear cases.

## Next Steps

1. **Fix Remaining Pattern Issues**: Address the 15 failing test cases
2. **Improve Pattern Specificity**: Make patterns more precise to avoid conflicts
3. **Add Missing Patterns**: Include variations that are currently missed
4. **Test in Real App**: Verify the enhanced routing works in the actual application 