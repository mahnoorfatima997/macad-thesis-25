# MEGA Architectural Mentor - Benchmarking Dashboard Features Documentation

## Table of Contents
1. [Overview Section](#overview-section)
2. [Cognitive Patterns Section](#cognitive-patterns-section)
3. [Learning Progression Section](#learning-progression-section)
4. [Agent Performance Section](#agent-performance-section)
5. [Comparative Analysis Section](#comparative-analysis-section)
6. [Anthropomorphism Analysis Section](#anthropomorphism-analysis-section)
7. [Linkography Analysis Section](#linkography-analysis-section)
8. [Proficiency Analysis Section](#proficiency-analysis-section)
9. [Graph ML Analysis Section](#graph-ml-analysis-section)

---

## Overview Section

### Key Metrics Panel
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Total Sessions** | Count of evaluation reports | `evaluation_reports/*.json` | Basic statistical measure | `benchmark_dashboard.py:335` |
| **Average Cognitive Offloading Prevention** | Mean of all session prevention rates | `session_metrics.cognitive_offloading_prevention.overall_rate` | Bloom's Taxonomy (1956) - avoiding lower-order thinking | `benchmark_dashboard.py:428-429` |
| **Average Deep Thinking Engagement** | Mean of all session engagement rates | `session_metrics.deep_thinking_engagement.overall_rate` | Kahneman's System 2 thinking (2011) | `benchmark_dashboard.py:430-431` |
| **Overall Improvement** | Weighted average of prevention and deep thinking improvements over baseline | Calculated vs. 30% and 35% literature baselines | Educational psychology research on traditional tutoring | `benchmark_dashboard.py:443-448` |

### Learning Metrics Over Time Chart
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Time Series Plot** | Session metrics plotted chronologically | `session_metrics.timestamp` | Learning curve theory (Ebbinghaus, 1885) | `benchmark_dashboard.py:467-505` |
| **Prevention Rate Line** | Cognitive offloading prevention over time | `cognitive_offloading_prevention.overall_rate` | Cognitive load theory (Sweller, 1988) | `evaluation_metrics.py:106-141` |
| **Deep Thinking Line** | Deep thinking engagement over time | `deep_thinking_engagement.overall_rate` | Depth of processing theory (Craik & Lockhart, 1972) | `evaluation_metrics.py:143-189` |
| **Scaffolding Line** | Scaffolding effectiveness over time | `scaffolding_effectiveness.overall_rate` | Zone of Proximal Development (Vygotsky, 1978) | `evaluation_metrics.py:191-234` |

### Proficiency Distribution Pie Chart
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Proficiency Levels** | K-means clustering on graph features | `proficiency_classification.level` | Dreyfus model of skill acquisition (1980) | `graph_ml_benchmarking.py:359-395` |
| **Distribution** | Count per proficiency level | Aggregated from session classifications | Competency-based education framework | `benchmark_dashboard.py:561-595` |

---

## Cognitive Patterns Section

### Session Comparison Table
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Session ID** | Direct from data | `session_id` | Unique identifier | `benchmark_dashboard.py:776-780` |
| **Cognitive Offloading Prevention** | Session-level rate | `cognitive_offloading_prevention.overall_rate` | Bloom's Taxonomy | `evaluation_metrics.py:106-141` |
| **Deep Thinking** | Session-level engagement | `deep_thinking_engagement.overall_rate` | System 2 thinking | `evaluation_metrics.py:143-189` |
| **Scaffolding Effectiveness** | Adaptive support rate | `scaffolding_effectiveness.overall_rate` | ZPD theory | `evaluation_metrics.py:191-234` |
| **Knowledge Integration** | Source usage rate | `knowledge_integration.integration_rate` | Constructivist learning theory | `evaluation_metrics.py:236-273` |
| **Engagement** | Consistency score | `engagement_consistency.consistency_score` | Flow theory (Csikszentmihalyi, 1990) | `evaluation_metrics.py:328-355` |

### Average Cognitive Patterns Radar Chart
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Radar Dimensions** | 5 cognitive metrics averaged | Session metrics aggregated | Multi-dimensional assessment framework | `benchmark_dashboard.py:790-835` |
| **Baseline Comparison** | Literature values overlay | `[0.5, 0.35, 0.4, 0.45, 0.5]` | Meta-analysis of traditional tutoring | `benchmark_dashboard.py:918` |

---

## Learning Progression Section

### Skill Progression Over Time
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Skill Level Tracking** | Ordinal progression mapping | `skill_progression.initial/final_level` | Bloom's revised taxonomy (2001) | `evaluation_metrics.py:275-326` |
| **Progression Score** | Normalized level changes | `(final_level - initial_level) / max_progression` | Learning gain measurement | `evaluation_metrics.py:312-320` |

### Learning Velocity Chart
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Improvement Rate** | Delta metrics / time | Temporal metric differences | Learning rate theory | `benchmark_dashboard.py:1021-1065` |
| **Acceleration** | Second derivative of learning | Rate of rate change | Educational growth modeling | Calculated in visualization |

---

## Agent Performance Section

### Agent Usage Distribution
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Agent Counts** | Frequency per agent type | `agents_used` field | Multi-agent system design | `benchmark_dashboard.py:1270-1280` |
| **Usage Patterns** | Temporal agent selection | `routing_path` field | Adaptive system behavior | Aggregated from sessions |

### Agent Effectiveness Metrics
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Prevention Rate by Agent** | Agent-specific cognitive metrics | Filtered by `primary_agent` | Agent specialization theory | `benchmark_dashboard.py:1282-1315` |
| **Response Quality** | Coherence and appropriateness | `response_coherence`, `appropriate_agent_selection` | Communication effectiveness | `evaluation_metrics.py:640-680` |

### Agent Handoff Flow (Sankey Diagram)
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Transition Counts** | Sequential agent pairs | `agents_used` sequences | Workflow optimization | `benchmark_dashboard.py:1348-1380` |
| **Flow Weights** | Frequency of transitions | Counted from session data | Process mining techniques | Calculated dynamically |

---

## Comparative Analysis Section

### Improvement by Dimension
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Dimension Scores** | Pre/post metric comparison | Session start/end metrics | Educational assessment theory | `benchmark_dashboard.py:1520-1560` |
| **Improvement Percentage** | `(post - pre) / pre * 100` | Calculated per dimension | Learning gain calculation | `evaluation_metrics.py:425-450` |

### Feature Impact Analysis
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Socratic Questioning Impact** | Correlation with prevention rate | `cognitive_offloading_prevention` rates | Socratic method research | `benchmark_dashboard.py:178-180` |
| **Visual Analysis Impact** | Presence/absence comparison | `visual_artifacts_used` flag | Dual coding theory (Paivio, 1986) | `benchmark_dashboard.py:198-199` |
| **Multi-Agent Coordination** | Coordination score analysis | `agent_interaction.coordination_score` | Distributed cognition theory | `benchmark_dashboard.py:193-195` |
| **Knowledge Integration** | Source usage effectiveness | `knowledge_integration.integration_rate` | Information processing theory | `benchmark_dashboard.py:183-185` |
| **Adaptive Scaffolding** | Scaffolding rate correlation | `scaffolding_effectiveness.overall_rate` | Dynamic assessment theory | `benchmark_dashboard.py:188-190` |

---

## Anthropomorphism Analysis Section

### Cognitive Autonomy Index (CAI)
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Autonomy Ratio** | Independent thinking / total interactions | `input_type` categorization | Self-determination theory (Deci & Ryan, 1985) | `anthropomorphism_metrics_implementation.py:182-204` |
| **Dependency Score** | Direct questions / explorations | Question type analysis | Learned helplessness theory | `anthropomorphism_metrics_implementation.py:193-196` |

### Anthropomorphic Dependency Score (ADS)
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Personal Attributions** | Keyword frequency analysis | Text pattern matching | Anthropomorphism in HCI (Nass & Moon, 2000) | `anthropomorphism_metrics_implementation.py:218-250` |
| **Emotional Language** | Sentiment analysis | Response text analysis | Emotional design theory | `anthropomorphism_metrics_implementation.py:245-248` |

### Professional Boundary Index (PBI)
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Conversation Drift** | Off-topic detection | Topic modeling | Professional ethics in education | `anthropomorphism_metrics_implementation.py:258-290` |
| **Personal Intrusions** | Personal topic frequency | Keyword detection | Boundary theory in counseling | `anthropomorphism_metrics_implementation.py:275-280` |
| **Technical Discussion Score** | Architecture keyword density | Real-time text analysis | Domain-specific discourse analysis | `benchmark_dashboard.py:141-161` |

### Neural Engagement Score (NES)
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Concept Diversity** | Unique concepts / total | Concept extraction | Cognitive flexibility theory | `anthropomorphism_metrics_implementation.py:318-345` |
| **Technical Vocabulary** | Domain term frequency | Architecture lexicon matching | Academic discourse analysis | `anthropomorphism_metrics_implementation.py:326-330` |
| **Cross-Domain Thinking** | Inter-concept connections | Semantic similarity | Interdisciplinary learning theory | `anthropomorphism_metrics_implementation.py:331-335` |

---

## Linkography Analysis Section

### Design Move Detection
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Move Extraction** | Meaningful action detection | Interaction content analysis | Goldschmidt's linkography (1990, 2014) | `linkography_analyzer.py:45-120` |
| **Move Classification** | Phase categorization | Keyword and pattern matching | Design thinking phases | `linkography_types.py:15-30` |
| **Semantic Embedding** | Sentence-BERT encoding | `all-MiniLM-L6-v2` model | Semantic similarity in design | `linkography_engine.py:35-50` |

### Link Generation
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Fuzzy Linkography** | Semantic similarity threshold | Cosine similarity > 0.65 | Fuzzy design reasoning (Kan & Gero, 2008) | `linkography_engine.py:85-140` |
| **Link Density** | Links / moves | Generated linkograph | Design productivity measure | `linkography_engine.py:142-165` |
| **Critical Moves** | High connectivity nodes | Link count analysis | Key decision identification | `linkography_analyzer.py:200-230` |

### Pattern Recognition
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Phase Balance** | Move distribution by phase | Phase classifications | Balanced design process | `linkography_cognitive_mapping.py:45-80` |
| **Fixation Detection** | Repetitive patterns | Sequential similarity | Design fixation research | `linkography_cognitive_mapping.py:120-150` |
| **Breakthrough Moments** | Sudden link increases | Temporal link analysis | Creative insight theory | `linkography_cognitive_mapping.py:160-190` |

---

## Proficiency Analysis Section

### Proficiency Characteristics
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Question Quality** | Complexity scoring | `deep_thinking_engagement.question_complexity` | Bloom's question levels | `benchmark_dashboard.py:239` |
| **Reflection Depth** | Response analysis | `deep_thinking_engagement.overall_rate` | Reflective practice theory (Schön, 1983) | `benchmark_dashboard.py:243` |
| **Concept Integration** | Knowledge connection rate | `knowledge_integration.integration_rate` | Schema theory | `benchmark_dashboard.py:247` |
| **Problem Solving** | Prevention effectiveness | `cognitive_offloading_prevention.overall_rate` | Problem-based learning | `benchmark_dashboard.py:251` |
| **Critical Thinking** | Conceptual understanding | `conceptual_understanding.overall_score` | Critical thinking framework | `benchmark_dashboard.py:255` |

### Progression Potential Analysis
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Growth Potential** | Improvement trend analysis | Historical progression data | Growth mindset theory (Dweck, 2006) | `benchmark_dashboard.py:317-348` |
| **Learning Barriers** | Stagnation detection | Plateau identification | Learning plateau theory | Calculated from progression |

---

## Graph ML Analysis Section

### Graph Construction
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Node Features** | Interaction embeddings | Text encoding | Graph neural networks | `graph_ml_benchmarking.py:90-120` |
| **Edge Weights** | Semantic similarity | Cosine distance | Network analysis theory | `graph_ml_benchmarking.py:73-78` |
| **Temporal Edges** | Sequential connections | Time-ordered interactions | Temporal graph theory | `graph_ml_benchmarking.py:80-88` |

### GNN Analysis
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **GraphSAGE Model** | Neighborhood aggregation | Graph structure | Hamilton et al. (2017) | `graph_ml_benchmarking.py:250-320` |
| **Node Embeddings** | Learned representations | GNN output | Representation learning | `graph_ml_benchmarking.py:405-430` |
| **Clustering** | K-means on embeddings | Graph features | Unsupervised learning | `graph_ml_benchmarking.py:359-395` |

### Visualization Networks
| Feature | Calculation Method | Data Source | Theoretical Foundation | Implementation Location |
|---------|-------------------|-------------|----------------------|------------------------|
| **Agent Network** | Collaboration patterns | Agent interactions | Multi-agent systems | `graph_ml_visualizations.py:150-200` |
| **Cognitive Network** | Concept connections | Semantic relationships | Knowledge graphs | `graph_ml_visualizations.py:250-300` |
| **Learning Trajectories** | Session evolution | Temporal progression | Learning analytics | `graph_ml_visualizations.py:350-400` |

---

## Data Flow Architecture

### Primary Data Sources
1. **thesis_data/interactions_*.csv** - Raw interaction logs
2. **thesis_data/session_*.json** - Session summaries
3. **benchmarking/results/evaluation_reports/*.json** - Computed metrics
4. **benchmarking/results/benchmark_report.json** - Aggregated benchmarks

### Processing Pipeline
1. **Data Collection** → `interaction_logger.py`
2. **Metric Evaluation** → `evaluation_metrics.py`
3. **Graph Analysis** → `graph_ml_benchmarking.py`
4. **Linkography Processing** → `linkography_analyzer.py`
5. **Anthropomorphism Analysis** → `anthropomorphism_metrics_implementation.py`
6. **Visualization** → `benchmark_dashboard.py`

### Theoretical Foundations Summary
- **Cognitive Load Theory** (Sweller, 1988) - Basis for offloading prevention
- **Zone of Proximal Development** (Vygotsky, 1978) - Scaffolding design
- **Bloom's Taxonomy** (1956, revised 2001) - Skill progression framework
- **Linkography** (Goldschmidt, 1990, 2014) - Design process analysis
- **Self-Determination Theory** (Deci & Ryan, 1985) - Autonomy metrics
- **Graph Neural Networks** (Hamilton et al., 2017) - ML analysis framework