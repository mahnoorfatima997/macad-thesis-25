# **MENTOR.PY - COMPREHENSIVE USER MANUAL**

## **Overview**

Mentor.py is an advanced AI-supported learning tool designed for architectural design education with integrated three-condition testing capabilities and dynamic subtask management. The system prevents cognitive offloading while providing structured learning support through multiple AI agents and phase-based progression.

---

## **SYSTEM ARCHITECTURE**

### **Core Components**

1. **Dashboard System** (`dashboard/`)
   - **Unified Dashboard**: Main interface integrating all components
   - **UI Components**: Chat interface, sidebar controls, phase visualization
   - **Mode Processors**: Handle different AI interaction modes
   - **Dynamic Task System**: NEW - Manages structured subtasks for testing

2. **Thesis-Agents System** (`thesis-agents/`)
   - **Multi-Agent Orchestration**: Coordinates multiple AI agents
   - **Vision System**: Processes uploaded images and sketches
   - **Phase Management**: Tracks design phase progression
   - **Knowledge Base**: Domain-specific architectural knowledge

3. **Testing Framework** (`thesis_tests/`)
   - **Three-Condition Testing**: MENTOR, GENERIC_AI, CONTROL groups
   - **Data Collection**: Comprehensive interaction logging
   - **Benchmarking**: Linkography analysis and performance metrics

4. **Phase Progression System** (`phase_progression_system.py`)
   - **Automatic Phase Detection**: Ideation → Visualization → Materialization
   - **Image Generation**: AI-generated design visualizations
   - **Progress Tracking**: Phase completion and milestone management

---

## **HOW TO USE THE SYSTEM**

### **1. Starting the Application**

```bash
# Navigate to the project directory
cd macad-thesis-25

# Run the application
streamlit run mentor.py
```

The system will start on `http://localhost:8501`

### **2. Interface Overview**

#### **Main Interface**
- **Chat Area**: Central conversation interface
- **Input Box**: Text input with image upload capability
- **Phase Circles**: Visual representation of design phase progress
- **Sidebar**: Controls, settings, and active task monitoring

#### **Sidebar Components**
- **Mode Selection**: Choose between Test Mode and Flexible Mode
- **Test Configuration**: Set test group and phase (Test Mode only)
- **Session Management**: Export data, reset sessions
- **Active Tasks**: NEW - Monitor dynamic subtasks (Test Mode only)
- **Phase Progress**: Current phase status and metrics

### **3. Operating Modes**

#### **Test Mode (Primary Research Mode)**
**Purpose**: Structured three-condition testing for research

**Configuration**:
- **Test Group**: MENTOR, GENERIC_AI, or CONTROL
- **Test Phase**: Ideation, Visualization, or Materialization
- **Fixed Challenge**: Community center adaptive reuse project

**Features**:
- Dynamic subtask activation based on conversation analysis
- Structured task progression (Test 1.1, 1.2, 2.1, 3.1, etc.)
- Comprehensive data collection for research analysis
- Phase-based progression with automatic transitions

#### **Flexible Mode (General Use)**
**Purpose**: Open-ended architectural design assistance

**Configuration**:
- **Mentor Type**: MENTOR, RAW_GPT, NO_AI, GENERIC_AI, CONTROL
- **Template Selection**: Various architectural project templates
- **Skill Level**: Beginner, Intermediate, Advanced

**Features**:
- Template-based project initialization
- Flexible conversation flow
- Gamification elements (20% frequency)
- Full agent orchestration capabilities

---

## **DYNAMIC TASK SYSTEM (NEW)**

### **Overview**
The dynamic task system automatically detects conversation patterns and activates structured subtasks based on the test logic documents. This system provides task-specific guidance while preserving natural conversation flow.

### **Task Types**

#### **Test 1.x Series - Concept Development (Ideation Phase)**
- **Test 1.1**: Architectural Concept Development (15 min)
  - **Trigger**: 0-15% ideation completion, concept/design keywords
  - **Focus**: Core design concept articulation

- **Test 1.2**: Spatial Program Development (10 min)
  - **Trigger**: 20-35% ideation completion, spatial/program keywords
  - **Focus**: Detailed spatial programming and relationships

#### **Test 2.x Series - Visual Development (Visualization Phase)**
- **Test 2.1**: 2D Design Development & Analysis (20 min)
  - **Trigger**: Image upload in visualization phase (0-50% completion)
  - **Focus**: Visual analysis and design critique

- **Test 2.2**: Environmental & Contextual Integration (10 min)
  - **Trigger**: 30-70% visualization completion, environment/context keywords
  - **Focus**: Site responsiveness and environmental design

#### **Test 3.x Series - 3D and Material Systems (Materialization Phase)**
- **Test 3.1**: 3D Spatial Analysis & Material Systems (20 min)
  - **Trigger**: 0-40% materialization completion, material/construction keywords
  - **Focus**: Three-dimensional design and material considerations

- **Test 3.2**: Realization & Implementation Strategy (15 min)
  - **Trigger**: 40-80% materialization completion, implementation/strategy keywords
  - **Focus**: Project implementation and community engagement

#### **Test 4.x Series - Reflection and Evolution (Cross-Phase)**
- **Test 4.1**: Design Evolution Analysis (10 min)
  - **Trigger**: 75-90% completion in any phase, evolution/reflection keywords
  - **Focus**: Reflective analysis of design journey

- **Test 4.2**: Knowledge Transfer Challenge (15 min)
  - **Trigger**: 85-100% completion in any phase, knowledge/transfer keywords
  - **Focus**: Application to new design problems

### **Task Guidance by Test Group**

#### **MENTOR Group**
- **Socratic Questions**: Context-specific questioning patterns
- **Follow-up Prompts**: Deeper exploration of design decisions
- **Multi-agent Coordination**: All agents work together for comprehensive support

#### **GENERIC_AI Group**
- **Direct Information**: Structured architectural knowledge delivery
- **Technical Guidance**: Specific methodologies and best practices
- **Information-focused**: Less questioning, more direct assistance

#### **CONTROL Group**
- **Minimal Prompts**: Self-directed task guidance
- **Documentation Focus**: Emphasis on recording thinking process
- **Limited AI Intervention**: Minimal system assistance

### **Task Monitoring**
- **Active Tasks Panel**: Sidebar display of current tasks with phase completion ranges
- **Phase Completion Display**: Shows trigger range (e.g., "30-70%") instead of countdown timers
- **Progress Tracking**: Task completion indicators based on phase progression
- **Manual Completion**: Option to manually complete tasks
- **Phase Completion-Based Triggers**: All 8 tasks trigger based on phase completion percentages
- **Smart Trigger Ranges**: Tasks only trigger within appropriate completion ranges to prevent early/late activation
- **Document-Accurate Durations**: Task durations match test logic documents (10-20 minutes)

---

## **IMAGE PROCESSING CAPABILITIES**

### **Supported Image Types**
- **Floor Plans**: Architectural drawings showing spatial layout
- **Elevations**: Building facade representations
- **Sections**: Cut-through building views
- **Sketches**: Hand-drawn conceptual drawings
- **3D Renderings**: Three-dimensional visualizations
- **Photographs**: Site photos or reference images

### **Image Analysis Features**
- **Automatic Classification**: Identifies drawing type and medium
- **Element Extraction**: Recognizes architectural elements
- **Design Critique**: Provides analysis and improvement suggestions
- **Context Integration**: Combines image analysis with conversation context
- **Caching System**: Prevents redundant analysis of same images

### **Vision-Triggered Tasks**
- **Test 2.1 Activation**: Automatically triggered when architectural drawings are uploaded
- **Comprehensive Analysis**: Detailed visual analysis integrated with conversation
- **Multi-modal Learning**: Combines visual and textual learning modalities

---

## **PHASE PROGRESSION SYSTEM**

### **Design Phases**

#### **1. Ideation Phase**
- **Focus**: Concept development, problem definition, initial ideas
- **Duration**: Variable based on conversation depth
- **Completion Criteria**: Clear design concept articulated
- **Generated Visualization**: Conceptual sketches or diagrams

#### **2. Visualization Phase**
- **Focus**: 2D design development, spatial relationships, visual representation
- **Duration**: Typically 4-6 interactions
- **Completion Criteria**: Spatial program defined, visual representations created
- **Generated Visualization**: Floor plans, elevations, or sections

#### **3. Materialization Phase**
- **Focus**: 3D development, materials, construction, technical resolution
- **Duration**: Variable based on technical depth
- **Completion Criteria**: Technical systems resolved, materials specified
- **Generated Visualization**: 3D renderings or construction details

### **Automatic Phase Transitions**
- **Content Analysis**: AI analyzes conversation to detect phase readiness
- **User Confirmation**: System asks for confirmation before transitions
- **Visual Feedback**: Phase circles update to show progress
- **Generated Images**: AI creates phase-appropriate visualizations

---

## **DATA COLLECTION AND EXPORT**

### **Interaction Logging**
- **Comprehensive Tracking**: All user inputs, system responses, and metadata
- **Linkography Analysis**: Design move extraction and relationship mapping
- **Phase Progression**: Detailed phase transition and completion data
- **Task Performance**: Dynamic task activation, duration, and completion metrics

### **Export Capabilities**
- **CSV Export**: Structured data for analysis
- **Session Data**: Complete conversation transcripts
- **Linkography Data**: Design move networks and relationships
- **Performance Metrics**: Task completion rates, phase progression times

### **Research Integration**
- **Benchmarking Dashboard**: Separate analysis interface
- **Statistical Analysis**: Automated metric calculation
- **Comparative Studies**: Cross-group performance analysis

---

## **TROUBLESHOOTING**

### **Common Issues**

#### **System Won't Start**
- Check Python environment and dependencies
- Verify API keys in `.env` file
- Ensure all required packages are installed

#### **Tasks Not Triggering**
- Verify Test Mode is active
- Check conversation length requirements (reduced to 1-2 exchanges)
- Ensure appropriate keywords are used
- Confirm correct test group selection
- Check phase completion percentage (tasks now align with actual phase progression)
- Verify image uploads for visual analysis tasks (Test 2.1)

#### **Image Upload Issues**
- Supported formats: JPG, PNG, GIF
- Maximum file size: 10MB
- Ensure image contains architectural content
- Check internet connection for analysis

#### **Phase Transitions Not Working**
- Verify phase progression system is enabled
- Check conversation depth and content
- Ensure user confirmation for transitions
- Review phase completion criteria

### **Performance Optimization**
- **Caching**: System uses intelligent caching for images and responses
- **Session Management**: Regular session resets prevent memory issues
- **API Rate Limiting**: Built-in throttling prevents API overuse

---

## **ADVANCED FEATURES**

### **Gamification System**
- **Frequency**: 20% of interactions (1 in 5 messages)
- **Trigger Pattern**: 1 game, 2 normal messages, then next game
- **Variety**: Role-play scenarios, design challenges, interactive elements
- **Context-Aware**: Games relate to current conversation topic

### **Multi-Agent Orchestration**
- **Context Agent**: Analyzes conversation context and user needs
- **Domain Expert**: Provides architectural knowledge and examples
- **Socratic Tutor**: Generates thought-provoking questions
- **Cognitive Enhancement**: Prevents cognitive offloading
- **Analysis Agent**: Performs deep conversation analysis

### **Knowledge Base Integration**
- **Domain-Specific**: Architectural design knowledge
- **Dynamic Search**: Context-aware knowledge retrieval
- **Example Generation**: Real project examples and case studies
- **Best Practices**: Industry standards and methodologies

---

## **SYSTEM REQUIREMENTS**

### **Hardware**
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: 5GB free space for system and data
- **Internet**: Stable connection for AI API calls

### **Software**
- **Python**: 3.8 or higher
- **Streamlit**: Latest version
- **Dependencies**: See requirements.txt

### **API Keys Required**
- **OpenAI**: For AI agent responses and image analysis
- **Optional**: Dropbox for cloud data backup

---

## **SUPPORT AND MAINTENANCE**

### **Logging System**
- **Comprehensive Logs**: All system operations logged
- **Error Tracking**: Detailed error messages and stack traces
- **Performance Monitoring**: Response times and system metrics

### **Data Backup**
- **Local Storage**: All data stored locally by default
- **Cloud Backup**: Optional Dropbox integration
- **Export Functions**: Manual data export capabilities

### **Updates and Maintenance**
- **Modular Design**: Easy component updates
- **Backward Compatibility**: Maintains compatibility with existing data
- **Configuration Management**: Centralized settings and configuration

---

**For technical support or questions, refer to the system logs or contact the development team.**
