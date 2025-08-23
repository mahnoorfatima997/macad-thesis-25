# Response Structure Mapping

This document maps each route type and interaction type combination to ensure coherent response generation.

## Route Types and Their Purpose

### Core Learning Routes
- **knowledge_only**: Direct information delivery without Socratic questioning
- **socratic_exploration**: Guided discovery through questions and reflection
- **cognitive_challenge**: Challenge assumptions and push deeper thinking
- **multi_agent_comprehensive**: Full multi-agent response with all perspectives

### Support Routes
- **socratic_clarification**: Clarifying questions when user is confused
- **supportive_scaffolding**: Gentle guidance for struggling users
- **foundational_building**: Building basic understanding step by step
- **knowledge_with_challenge**: Knowledge delivery with follow-up challenges
- **balanced_guidance**: Balanced mix of information and guidance

### Management Routes
- **progressive_opening**: First message handling with project spark
- **topic_transition**: Bridging between conversation topics
- **cognitive_intervention**: Addressing cognitive offloading attempts

## Interaction Types and Expected Responses

### example_request
**Intent**: User wants examples or case studies
**Expected Response Structure**:
- **knowledge_only**: Direct examples without questions
- **socratic_exploration**: Examples with "What do you notice about..." questions
- **balanced_guidance**: Examples + brief analysis + one follow-up question

**Current Issues**:
- Sometimes routes to socratic_exploration instead of knowledge_only
- Hardcoded examples instead of contextual ones
- Generic follow-up questions instead of example-specific ones

### feedback_request
**Intent**: User wants evaluation of their work/ideas
**Expected Response Structure**:
- **socratic_exploration**: Questions to help user self-evaluate
- **balanced_guidance**: Brief feedback + guiding questions
- **multi_agent_comprehensive**: Detailed feedback from multiple perspectives

**Current Issues**:
- Generic feedback responses
- Not building on user's specific context

### confusion_expression
**Intent**: User is confused or doesn't understand
**Expected Response Structure**:
- **socratic_clarification**: Clarifying questions to identify confusion source
- **supportive_scaffolding**: Step-by-step breakdown
- **foundational_building**: Basic concepts first, then build up

**Current Issues**:
- May provide too much information instead of clarification
- Not identifying specific confusion source

### knowledge_request
**Intent**: User wants information about a topic
**Expected Response Structure**:
- **knowledge_only**: Direct information delivery
- **knowledge_with_challenge**: Information + challenging questions
- **balanced_guidance**: Information + one guiding question

**Current Issues**:
- Sometimes adds unnecessary Socratic questions to knowledge_only
- May not provide sufficient depth

## Route-Interaction Compatibility Matrix

| Interaction Type | Primary Routes | Secondary Routes | Avoid |
|------------------|----------------|------------------|-------|
| example_request | knowledge_only | balanced_guidance | socratic_exploration |
| feedback_request | socratic_exploration, balanced_guidance | multi_agent_comprehensive | knowledge_only |
| confusion_expression | socratic_clarification, supportive_scaffolding | foundational_building | cognitive_challenge |
| knowledge_request | knowledge_only | knowledge_with_challenge | socratic_exploration |
| technical_question | knowledge_only | balanced_guidance | socratic_exploration |
| design_exploration | socratic_exploration | cognitive_challenge | knowledge_only |
| implementation_request | balanced_guidance | multi_agent_comprehensive | socratic_exploration |

## Response Quality Requirements

### All Routes Must Include:
1. **Context Awareness**: Reference user's project type, building type, phase
2. **Appropriate Tone**: Match user's confidence and understanding level
3. **Logical Flow**: Clear progression of ideas
4. **Actionable Content**: Something user can work with

### Route-Specific Requirements:

#### knowledge_only
- **No Socratic questions** in the main response
- **Direct information** relevant to user's query
- **Complete answers** that don't require follow-up
- **Sources/examples** when appropriate

#### socratic_exploration
- **Thought-provoking questions** that guide discovery
- **Minimal direct answers** - let user discover
- **Progressive questioning** that builds understanding
- **Encouragement** for user's thinking process

#### balanced_guidance
- **Brief information** followed by **one guiding question**
- **Balance** between giving answers and promoting thinking
- **Contextual relevance** to user's specific situation
- **Clear structure**: Info → Question

## Current Synthesis Issues Identified

### 1. Route Selection Conflicts
- `example_request` sometimes routes to `socratic_exploration` instead of `knowledge_only`
- Multiple routes can match the same conditions
- Intent classification inconsistencies

### 2. Response Generation Problems
- **balanced_guidance** often returns incomplete responses
- Generic fallbacks instead of contextual responses
- Hardcoded content instead of dynamic generation

### 3. Agent Coordination Issues
- Agents operate in isolation
- No context sharing between agents
- Inconsistent pedagogical approaches

### 4. Context Loss
- Building type and project context not maintained
- Previous conversation context ignored
- Generic responses instead of project-specific ones

## Recommended Fixes

### Priority 1: Route Selection
1. Fix intent classification patterns to reduce overlaps
2. Implement route priority rules
3. Add validation for route-interaction compatibility

### Priority 2: Response Synthesis
1. Fix balanced_guidance synthesis fallbacks
2. Implement contextual response generation
3. Remove hardcoded responses

### Priority 3: Context Integration
1. Ensure all synthesis methods access project context
2. Implement conversation continuity
3. Add context validation

### Priority 4: Quality Assurance
1. Add response validation for each route type
2. Implement minimum quality thresholds
3. Add route-specific quality metrics

## Testing Requirements

Each route-interaction combination should be tested with:
1. **Typical user inputs** for that interaction type
2. **Edge cases** and ambiguous inputs
3. **Context variations** (different building types, phases)
4. **Quality validation** against requirements above

## Implementation Notes

- Changes should be **incremental** and **tested individually**
- Preserve existing working functionality
- Add **logging** for route decisions and synthesis choices
- Implement **fallback mechanisms** for all synthesis methods
