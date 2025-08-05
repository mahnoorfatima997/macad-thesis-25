# Master Metrics Requirements Analysis

## 1. Key Metrics Section

### Required Data:
- **total_sessions**: Count of unique session IDs
- **avg_prevention_rate**: Average of prevents_cognitive_offloading across all interactions
- **avg_deep_thinking_rate**: Average of encourages_deep_thinking
- **overall_improvement**: Calculated as ((avg_prevention - 0.30) + (avg_deep_thinking - 0.35)) / 0.325 * 100
- **total_interactions**: Sum of all interactions across sessions
- **total_duration_minutes**: Sum of session durations

### Source:
- Direct from thesis_data CSVs

## 2. Proficiency Analysis Section

### Required Data Per Session:
- **proficiency_level**: Derived from prevention/deep thinking rates
  - expert: prevention > 0.8 AND deep_thinking > 0.8
  - advanced: prevention > 0.6 AND deep_thinking > 0.6
  - intermediate: prevention > 0.4 OR deep_thinking > 0.4
  - beginner: otherwise

### Required Aggregate Data Per Proficiency Level:
- **question_quality_score**: 
  - From: (cognitive_flags_count/5 + input_length/100) / 2
- **reflection_depth_score**: 
  - From: deep_thinking_rate
- **concept_integration_score**: 
  - From: knowledge_integrated rate OR sources_count/3
- **problem_solving_score**: 
  - From: prevention_rate
- **critical_thinking_score**: 
  - From: (prevention + deep_thinking + confidence_score) / 3

### Characteristics Per Proficiency:
- **cognitive_load**: Average engagement_level
- **learning_effectiveness**: (prevention + deep_thinking) / 2
- **scaffolding_need**: 1 - proficiency_numeric_value
- **knowledge_integration**: concept_integration_score
- **engagement**: maintains_engagement rate

## 3. Cognitive Patterns Section

### Required Per Session:
- **cognitive_offloading_prevention**: prevention_rate
- **deep_thinking**: deep_thinking_rate
- **scaffolding_effectiveness**: provides_scaffolding rate
- **knowledge_integration**: concept_integration_score
- **engagement**: maintains_engagement rate

### Correlation Matrix Needs:
- All above metrics plus duration and interaction count

## 4. Learning Progression Section

### Required Per Session (Time-Series):
- **timestamp**: First interaction timestamp
- **skill_level**: From student_skill_level or derived
- **improvement_score**: Improvement over baseline
- **cumulative_interactions**: Running total
- **session_duration**: Calculated from interactions

### Milestone Tracking:
- **first_expert_moment**: First interaction where both rates > 0.8
- **consistency_achieved**: 3+ consecutive high-performance interactions
- **breakthrough_moments**: Sudden jumps in performance

## 5. Agent Effectiveness Section

### Required Per Session:
- **agent_coordination_score**: multi_agent_coordination rate
- **agent_usage_counts**: Frequency count per agent from agent_response text
- **response_quality_avg**: response_coherence average
- **appropriate_selection_rate**: appropriate_agent_selection rate

### Per Agent Metrics:
- **socratic_effectiveness**: Count of socratic mentions / total
- **domain_expert_effectiveness**: Count of expert mentions / total
- **cognitive_enhancement_effectiveness**: Count of cognitive mentions / total

## 6. Comparative Analysis Section

### Required Improvement Metrics:
- **cognitive_offloading_improvement**: (rate - 0.30) / 0.30 * 100
- **deep_thinking_improvement**: (rate - 0.35) / 0.35 * 100
- **knowledge_retention_improvement**: Estimated from integration
- **metacognitive_improvement**: Estimated from deep thinking
- **creative_solving_improvement**: Estimated from pattern diversity
- **critical_thinking_improvement**: From critical_thinking_score

## 7. Anthropomorphism Analysis (PRESERVE EXISTING)

### Critical Requirements:
- **MUST NOT MODIFY**: Uses _load_thesis_data() directly
- **Reads**: Raw thesis_data CSVs with specific column structure
- **Calculates**: Complex anthropomorphism metrics internally
- **Special Needs**: 
  - session JSON files for test_group classification
  - Full interaction text for language analysis
  - Temporal data for attachment patterns

### Master CSV Should Include:
- **anthropomorphism_risk_level**: low/medium/high
- **dependency_score**: 0-1 scale
- **language_pattern_score**: Formality measure
- **session_test_group**: From JSON files

## 8. Linkography Analysis (PRESERVE EXISTING)

### Critical Requirements:
- **MUST NOT MODIFY**: Uses linkography/*.json files directly
- **Reads**: linkography_moves_*.jsonl files
- **Complex Structure**: Design moves, links, patterns
- **Special Needs**:
  - Move sequences with timestamps
  - Link strength calculations
  - Pattern detection (chunks, webs, tracks)

### Master CSV Should Include:
- **linkography_density**: Links per move
- **critical_move_ratio**: Critical moves / total moves
- **max_link_span**: Longest link distance
- **dominant_pattern**: chunk/web/track/sawtooth

## 9. Graph ML Analysis (PRESERVE EXISTING)

### Critical Requirements:
- **MUST NOT MODIFY**: Uses PyVis HTML files and graph structures
- **Reads**: results/visualizations/pyvis/*.html
- **Complex Structure**: Node-edge relationships
- **Special Needs**:
  - Graph topology metrics
  - Clustering coefficients
  - Path lengths

### Master CSV Should Include:
- **graph_density**: Edges / possible edges
- **avg_clustering_coefficient**: Network measure
- **centrality_score**: Key node importance
- **community_count**: Detected communities

## 10. Recommendations Section

### Derived From All Above:
- **primary_weakness**: Lowest scoring metric
- **recommended_intervention**: Based on weakness
- **progress_indicator**: Positive/neutral/negative
- **next_milestone**: Based on current level

## 11. Technical Details Section

### Static Information:
- No dynamic data needed

## 12. Export Options Section

### Aggregates All Above:
- Full master CSV export
- Filtered views by session/proficiency

---

## Master CSV Structure

### Per-Session Metrics:
```csv
session_id, timestamp, proficiency_level, 
prevention_rate, deep_thinking_rate, improvement_score,
question_quality, reflection_depth, concept_integration, 
problem_solving, critical_thinking, total_interactions,
duration_minutes, skill_progression, 
agent_coordination, response_quality, 
anthropomorphism_risk, dependency_score,
linkography_density, critical_moves, graph_density,
data_quality_score, calculation_method
```

### Aggregate Metrics:
```csv
metric_name, beginner_avg, intermediate_avg, advanced_avg, expert_avg,
overall_avg, overall_std, trend_direction, confidence_level
```

### Data Quality Indicators:
- **direct**: Value taken directly from CSV
- **calculated**: Derived from multiple columns
- **inferred**: Estimated using patterns
- **default**: No data, using baseline