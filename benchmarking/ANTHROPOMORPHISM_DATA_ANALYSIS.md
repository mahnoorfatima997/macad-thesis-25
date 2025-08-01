# Anthropomorphism Metrics - Data Source Analysis

## Current Data Available in thesis_data

### 1. Interaction CSV Files Structure
Based on analysis of `interactions_*.csv` files, we have these columns:

#### Basic Session Data
- `session_id`, `timestamp`, `interaction_number`
- `student_input`, `input_length`, `input_type`
- `agent_response`, `response_length`, `response_type`

#### Cognitive Metrics (EXISTING)
- `prevents_cognitive_offloading` (0-1 score)
- `encourages_deep_thinking` (0-1 score)
- `provides_scaffolding` (0-1 score)
- `maintains_engagement` (0-1 score)
- `adapts_to_skill_level` (0-1 score)

#### Agent & Routing Data
- `routing_path`, `agents_used`, `primary_agent`
- `multi_agent_coordination`, `appropriate_agent_selection`

#### Student State
- `student_skill_level` (beginner/intermediate/advanced)
- `understanding_level`, `confidence_level`, `engagement_level`
- `cognitive_flags`, `confidence_score`

#### Metadata
- Contains phase information, cognitive metrics (cop, dte, se, ki, lp, ma)

### 2. Enhanced Data from InteractionLogger
The `interaction_logger.py` shows additional data being collected:

#### Phase Tracking
- `current_phase` (ideation/visualization/materialization)
- `phase_confidence`, `phase_characteristics`
- `phase_progression_score`, `phase_duration`

#### Design Move Tracking
- `design_moves`, `move_types`, `move_modalities`
- `design_moves_count`

#### Scientific Metrics
- `engagement_metrics`, `complexity_metrics`
- `reflection_metrics`, `progression_metrics`
- `overall_cognitive_score`

#### Cognitive State
- `engagement_level`, `cognitive_load`
- `metacognitive_awareness`, `passivity_level`
- `overconfidence_level`, `conversation_depth`

## Anthropomorphism Metrics Data Requirements

### 1. Cognitive Autonomy Index (CAI) - ✅ Can Use Existing Data
**Data Available:**
- `student_input` - for autonomous vs dependent statements
- `input_type` - already classifies questions vs statements
- `prevents_cognitive_offloading` - direct metric
- `confidence_level`, `understanding_level`

**Calculation:**
```python
CAI = (1 - dependency_ratio) * cop_score * (statement_ratio / question_ratio)
```

### 2. Anthropomorphism Detection Score (ADS) - ⚠️ Partial Data Available
**Data Available:**
- `student_input` - can analyze for anthropomorphic language
- `agent_response` - can analyze AI's language patterns

**Data Needed:**
- Need to analyze text for personal pronouns, emotional language, relationship terms
- Can be computed from existing text columns

**Implementation:**
```python
# Can be calculated by text analysis of existing columns
anthropomorphic_patterns = analyze_text_patterns(student_input + agent_response)
ADS = anthropomorphic_patterns / total_words
```

### 3. Neural Engagement Score (NES) - ✅ Can Use Existing Data
**Data Available:**
- `encourages_deep_thinking` - direct metric
- `cognitive_load` (in metadata)
- `response_complexity` (in performance_metrics)
- `conversation_depth` (in cognitive_state)

**Calculation:**
```python
NES = (deep_thinking * 0.3 + cognitive_load * 0.3 + 
       complexity * 0.2 + conversation_depth * 0.2)
```

### 4. Professional Boundary Index (PBI) - ⚠️ Partial Data Available
**Data Available:**
- `student_input`, `agent_response` - for topic analysis
- `routing_path` - shows if staying on educational path

**Data Needed:**
- Topic classification (architectural vs personal)
- Can be computed from text analysis

### 5. Bias Resistance Score (BRS) - ❌ New Data Required
**Data Needed:**
- Tracking of user acceptance/rejection of AI suggestions
- Follow-up actions after AI recommendations
- Time spent on independent work vs AI interaction

**Proposed Collection:**
```python
# Add to interaction logger:
- suggestion_accepted: bool
- independent_work_time: float
- ai_interaction_time: float
- post_interaction_action: str
```

## Implementation Strategy

### Phase 1: Metrics Using Existing Data (CAI, NES)
These can be implemented immediately by analyzing existing CSV columns.

### Phase 2: Text Analysis Metrics (ADS, PBI)
These require text analysis of existing `student_input` and `agent_response` columns:
```python
def analyze_anthropomorphism(text):
    patterns = {
        'personal_pronouns': ['you', 'your', 'i', 'me', 'we', 'us'],
        'emotional_language': ['feel', 'think', 'believe', 'hope'],
        'relationship_terms': ['friend', 'partner', 'help me', 'together']
    }
    # Count occurrences and calculate score
```

### Phase 3: New Data Collection (BRS)
Requires modifications to data collection:
1. Add fields to track suggestion acceptance
2. Add timing for independent vs AI-assisted work
3. Track post-interaction behaviors

## Recommended Approach

1. **Immediate Implementation** (No data changes needed):
   - CAI using existing cognitive metrics
   - NES using existing engagement metrics
   
2. **Text Analysis Implementation** (Using existing text data):
   - ADS by analyzing language patterns
   - PBI by topic classification
   
3. **Future Enhancement** (Requires thesis_tests updates):
   - BRS with new tracking fields
   - Enhanced interaction outcome tracking

## Data Validation Notes

- Most interaction CSV files have data, but some are empty (only headers)
- Metadata field contains rich cognitive metrics (cop, dte, se, ki, lp, ma)
- Phase information is tracked in newer sessions
- Design move tracking provides additional context for analysis