# MEGA Architectural Mentor App - Complete Functionality Overview

## 🏗️ App Purpose and Logic

The MEGA (Multi-agent Enhanced Generative Architecture) system is a research platform designed to study how different AI interaction modes affect architectural design learning. The app guides users through three phases of architectural design while comparing three distinct AI interaction approaches.

### Core Research Question
**How do different levels of AI scaffolding affect design learning outcomes in architectural education?**

The app tests three conditions:
1. **Mentor Mode**: Multi-agent socratic scaffolding system
2. **Raw GPT Mode**: Direct ChatGPT-style interaction
3. **No AI Mode**: Hardcoded questions only (control group)

## 🔄 Three-Phase Design Process

### Phase Structure
All users progress through the same three phases regardless of AI mode:

1. **🧠 Ideation Phase** (25% weight)
   - Conceptual thinking and program development
   - Site analysis and community understanding
   - Initial design concepts and parti diagrams

2. **👁️ Visualization Phase** (35% weight)
   - Spatial organization and form development
   - Circulation and experience design
   - Visual representation and sketching

3. **🔨 Materialization Phase** (40% weight)
   - Material selection and construction details
   - Technical feasibility and building systems
   - Final design refinement

## 📊 Phase Calculation System

### How Phases Are Determined

The system uses a sophisticated algorithm that analyzes conversation content to automatically detect the current design phase:

#### Calculation Method
```
Phase Detection = f(message_count, keyword_analysis, conversation_depth)
```

#### Phase Thresholds
- **Minimum Messages for Visualization**: 6 user messages
- **Minimum Messages for Materialization**: 10 user messages
- **Keyword Threshold for Visualization**: 3+ spatial keywords
- **Keyword Threshold for Materialization**: 3+ technical keywords

#### Example Phase Calculation
```
🔄 PHASE_CALCULATION: Analyzing 8 messages for session_abc123
   📊 Keyword counts: ideation=2, visualization=4, materialization=1
   🎯 Phase determination: VISUALIZATION (6+ messages, 4 viz keywords)
   📈 Progression: 45.2% (based on message count and keyword density)
   🔍 Confidence: 78% (strong keyword signals)
```

### Phase Progression Formula
```
Progression = min(1.0, current_messages / phase_threshold_messages)

For Ideation: progression = messages / 6
For Visualization: progression = (messages - 6) / 4  
For Materialization: progression = (messages - 10) / ongoing
```

### Terminal Debug Output Examples
When running the app, you'll see detailed phase analysis in the terminal:

```
🏦 PHASE_SYSTEM: Dynamic question bank initialized
   🤖 LLM-powered question generation enabled
   
🔄 PHASE_CALCULATION: Session unified_session_20250119_143022
   📝 Total messages: 12
   🔍 Analyzing keywords...
   📊 Ideation keywords: ['concept', 'program'] (count: 2)
   📊 Visualization keywords: ['space', 'form', 'circulation', 'layout'] (count: 4)  
   📊 Materialization keywords: ['material', 'construction'] (count: 3)
   
   🎯 Phase Logic:
   ✅ Messages >= 10 (materialization threshold)
   ✅ Material keywords >= 3
   ✅ Material count (3) > Visualization count (4)? No
   
   📍 RESULT: VISUALIZATION phase (67% complete)
   🔍 Confidence: 82% (strong keyword signals)
```

## 🤖 Three AI Interaction Modes

### 1. Mentor Mode (Multi-Agent System)
**Purpose**: Sophisticated socratic scaffolding using multiple AI agents

#### Agent Architecture
```
User Input → Analysis Agent → Routing Decision → Agent Orchestration
                ↓
    [Domain Expert] + [Socratic Tutor] + [Cognitive Enhancement]
                ↓
         Response Synthesis → Final Output
```

#### Example Terminal Output
```
🤖 ORCHESTRATOR: Processing student input...
   🔍 Analysis Agent: Classifying interaction type
   🎯 Routing Decision: socratic_focus + cognitive_enhancement
   🧠 Socratic Agent: Generating guiding questions
   💡 Cognitive Agent: Assessing learning state
   ⚡ Response Synthesis: Combining agent outputs
   
✅ Multi-agent response generated (1.2s)
```

#### Example Response Style
```
User: "I think a glass facade would work well here."

Mentor Response: "Glass facades can indeed create interesting visual effects. 
What specific qualities are you hoping to achieve with transparency in this 
context? Consider how the interior activities might relate to the street 
life outside. What time of day will this space be most active, and how 
might that influence your material choice?"
```

### 2. Raw GPT Mode (Direct AI)
**Purpose**: Unfiltered ChatGPT-style interaction without scaffolding

#### Processing Method
```
User Input → Direct GPT-4 API Call → Unfiltered Response
```

#### Terminal Output
```
🔄 RAW_GPT: Processing unfiltered request
   📝 Input: "I think a glass facade would work well here."
   🤖 Model: gpt-4o (temperature: 0.7)
   ⚡ Response generated (0.8s)
   
✅ Raw GPT response: no_conditioning=True, no_socratic_elements=True
```

#### Example Response Style
```
User: "I think a glass facade would work well here."

Raw GPT Response: "A glass facade is a great choice! Glass can provide 
excellent natural light, create visual connections between interior and 
exterior spaces, and give your building a modern, sleek appearance. You 
might want to consider energy efficiency with double or triple glazing, 
and think about privacy needs for different areas of the building."
```

### 3. No AI Mode (Control Group)
**Purpose**: Hardcoded questions only, simulating traditional learning

#### Processing Method
```
User Input → Phase Detection → Hardcoded Question Bank → Next Question
```

#### Terminal Output
```
🔄 NO_AI: Control group processing
   📊 Phase calculation: VISUALIZATION (45% complete)
   📝 Question bank: visualization_questions
   🎯 Next question: #3 of 8 visualization questions
   
✅ Hardcoded response delivered
```

#### Example Response Style
```
User: "I think a glass facade would work well here."

No AI Response: "Thank you for sharing your thoughts. How do you envision 
the relationship between the interior spaces and the surrounding context? 
What specific views or connections do you want to emphasize or screen?"
```

## 🎮 Gaming System Integration

### Gamification Triggers
The system detects specific behavioral patterns and responds with gamified elements:

#### Terminal Debug Output
```
🎮 DEBUG: Gamification analysis
   🔍 Analyzing user confidence level...
   ⚠️ Overconfidence detected: "This design is perfect"
   🎯 Trigger: cognitive_challenge
   🎨 Display type: enhanced_visual
   
🎮 GAMIFICATION: Challenge activated
   💪 Challenge type: "Design Critique Challenge"
   🎯 Goal: Consider alternative perspectives
   ⭐ Reward: Critical thinking badge
```

### Gaming Elements
- **Challenge Cards**: Pop up when overconfidence is detected
- **Progress Badges**: Awarded for phase completion
- **Reflection Prompts**: Triggered by specific conversation patterns
- **Peer Comparison**: Anonymous benchmarking against other users

## 📈 Data Collection and Analysis

### Metrics Tracked
The system continuously monitors and logs:

#### Interaction Metrics
```
📊 LOGGING: Interaction recorded
   ⏱️ Response time: 1.2s
   📝 Message length: 156 characters
   🎯 Phase: VISUALIZATION (67% complete)
   🔍 Engagement level: HIGH
   💭 Design moves extracted: 3
```

#### Linkography Analysis
```
🔗 LINKOGRAPHY: Design move analysis
   📍 Move #12: "Consider natural ventilation"
   🔗 Links to: Move #8 (sustainability), Move #15 (climate)
   📊 Link density: 0.73
   🎯 Critical move: YES (high connectivity)
```

### Export Functionality
```
💾 DATA_EXPORT: Session complete
   📁 Local save: /thesis_data/session_abc123.json
   ☁️ Dropbox sync: /MEGA_Study/participant_data/
   📊 Metrics: 47 interactions, 23 design moves, 3 phases
   
✅ Data exported successfully
```

## 🔧 Technical Architecture

### File Structure
```
mentor.py                    # Main entry point
├── dashboard/
│   ├── unified_dashboard.py # Main dashboard controller
│   ├── processors/
│   │   ├── mode_processors.py    # Routes between AI modes
│   │   ├── phase_calculator.py   # Phase detection system
│   │   ├── raw_gpt_processor.py  # Raw GPT mode
│   │   └── no_ai_processor.py    # No AI mode
│   └── ui/                       # UI components
├── thesis-agents/               # Multi-agent system (Mentor mode)
│   ├── orchestration/
│   │   └── orchestrator.py     # Agent coordination
│   └── agents/                 # Individual AI agents
└── thesis_tests/               # Research testing framework
    ├── test_dashboard.py       # Test environment
    ├── mentor_environment.py   # Mentor mode testing
    ├── generic_ai_environment.py # Raw GPT testing
    └── control_environment.py  # No AI testing
```

### Session Management
```
🔄 SESSION: unified_session_20250119_143022
   👤 Participant: anonymous_user_47
   🎯 Test group: MENTOR
   📊 Current phase: VISUALIZATION (67%)
   ⏱️ Session duration: 23 minutes
   💬 Total interactions: 15
```

## 🚀 Running the Application

### Launch Commands
```bash
# Main mentor interface
python mentor.py

# Research testing dashboard  
python launch_test_dashboard.py

# Benchmarking system
python benchmarking/run_benchmarking.py
```

### Expected Terminal Output on Startup
```
✅ Fallback to dotenv successful
🏗️ MEGA Architectural Mentor System Starting...
🔧 Initializing components...
   ✅ API keys loaded
   ✅ Session state initialized  
   ✅ Phase calculator ready
   ✅ Multi-agent system loaded
   
🌐 Dashboard available at: http://localhost:8501
🎯 Ready for architectural design mentoring!
```

This comprehensive system enables rigorous comparison of AI interaction modes while providing meaningful architectural design learning experiences across all three conditions.
