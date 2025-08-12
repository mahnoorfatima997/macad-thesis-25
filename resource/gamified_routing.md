# Complete AI Mentor Routing System - All 14 Routes
*Enhanced Behaviors Based on Thesis Research + Study Mode Patterns*
*Answers are generic examples, not hardcoded and should be ai powered*
*Empower AI to provide natural conversation flow instead of generic templates*
*Gamify the experience to make it more engaging and fun BUT AVOID SUPER CHILDISHNESS*
*Responses should definitely about what user is saying, interested*


## 🎯 **ALL ROUTES WITH MULTI-AGENT COORDINATION**

### **🔄 1. TOPIC_TRANSITION**  
**When**: User wants to change topics, conversation shifts
**Agent**: "synthesizer" (context_agent)
**User Message Examples**:
- "Let's talk about something else"
- "Can we move on to materials now?"
- "I want to discuss user experience instead"
- "What about the structural systems?"
- "Let's shift focus to sustainability"

**Enhanced Behavior**:
```
Bridge Building Game → Connection Discovery → Smooth Transition

"Great! Moving from structural systems to user experience... 

🎯 BRIDGE CHALLENGE: Let's connect these ideas!

*Imagine you're walking through your community center*
- You see the exposed steel columns we just discussed
- A family with children enters the space
- An elderly person looks around, getting oriented

Tell me: What story do those columns tell about how people will feel and move? 
How does structure become experience in your space?"

[Natural conversation continues based on their response, building from structural to experiential thinking]
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Create meaningful bridges between topics, maintain project narrative flow
  - Output: Connection challenges, story-building prompts, conceptual bridges
- **Secondary Agent**: domain_expert
  - Role: Identify deep connections between architectural domains
  - Output: Cross-domain relationships, integrated knowledge patterns
- **Support Agent**: cognitive_enhancement
  - Role: Help student see their own thinking progression across topics
  - Output: Learning reflection prompts, cognitive transition awareness
- **Coordination**: Context creates bridge challenge → Knowledge provides connection insights → Metacognitive builds awareness of thinking development

---

### **🆕 2. PROGRESSIVE_OPENING (FIRST MESSAGE BRIEF RESPONSE)**
**When**: First message (is_first_message == True)
**Agent**: "synthesizer" (context_agent)
**User Message Examples**:
- "I'm designing a hospital with courtyards for healing environments"
- "My project is a community center in an old warehouse"
- "I'm working on affordable housing with outdoor spaces"
- "I need help with a cultural center design"

**Enhanced Behavior**:
```
Project Spark → Quick Insight → Learning Partnership Setup

"A hospital with healing courtyards - fascinating! You're working at the intersection of architecture and wellness, where space becomes medicine.

I can already see some intriguing tensions in your project: 
- Clinical efficiency vs. human-centered healing
- Institutional requirements vs. intimate outdoor spaces
- Medical privacy vs. community connection

I'm here to think alongside you, not give you answers. I'll ask questions that help you discover your own solutions and build your design thinking.

Ready to dive in? What's pulling at your mind about this project right now?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Recognize project complexity, establish collaborative tone, set learning expectations
  - Output: Project insight recognition, partnership framing, engagement invitation
- **Secondary Agent**: cognitive_enhancement  
  - Role: Establish learning mindset, communicate cognitive development approach
  - Output: Learning philosophy communication, growth mindset establishment
- **Support Agent**: socratic_tutor
  - Role: Prepare for deep engagement, set up exploratory dialogue
  - Output: Curiosity activation, open-ended exploration invitation
- **Coordination**: Context sparks project interest → Metacognitive establishes learning partnership → Socratic invites exploration

---

### **📖 3. KNOWLEDGE_ONLY**
**When**: Pure knowledge requests, any questions needing direct answers (design concepts, spatial principles, materials, precedents, etc.)
**Agent**: "domain_expert" (domain_expert)
**User Message Examples**:
- "What is biophilic design?"
- "Tell me about the golden ratio in architecture"
- "How does CLT construction work?"
- "What are the principles of healing environments?"
- "Explain circulation theory"
- "What's the difference between public and private space?"

**Enhanced Behavior**:
```
Knowledge Delivery → Real-World Connection → Exploration Invitation

"Biophilic design is our attempt to heal the disconnect between humans and nature through architecture. At its core, it's about designing spaces that support our biological need for natural connection.

Think of it like this: Your hospital courtyards aren't just 'outdoor spaces' - they're therapeutic tools. Natural light filtering through leaves, the sound of water, views to sky and horizon - these aren't aesthetic choices, they're neurological interventions that can actually accelerate healing.

The research shows patients with nature views recover 30% faster than those staring at walls.

*leans forward with curiosity*

So now I'm wondering... what kind of healing do you want your courtyards to support? Physical recovery? Emotional wellbeing? Family gathering? Different intentions might lead to very different design strategies..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: domain_expert
  - Role: Provide rich, contextual knowledge with real-world relevance
  - Output: Expert knowledge, research backing, practical applications
- **Secondary Agent**: context_agent
  - Role: Connect knowledge directly to student's project context
  - Output: Project-specific applications, relevant examples
- **Support Agent**: socratic_tutor
  - Role: Transform knowledge into curiosity and further exploration
  - Output: Intriguing questions, exploration invitations
- **Coordination**: Knowledge provides rich information → Context connects to project → Socratic sparks further curiosity

---

### **🎯 4. SOCRATIC_EXPLORATION**
**When**: User shares design thinking/process, shows active engagement with design problems
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm thinking about how courtyards might create different social dynamics in my hospital design"
- "I'm exploring the relationship between indoor and outdoor spaces for community gathering"
- "I want to understand how circulation affects the user experience in my cultural center"
- "I'm considering how natural light could support healing in patient areas"

**Enhanced Behavior**:
```
Thinking Reflection → Insight Amplification → Design Territory Expansion

"I love how you're thinking about courtyards as social catalysts, not just pretty outdoor spaces. You're recognizing that architecture doesn't just house activities - it actively shapes how people relate to each other.

What you're touching on is something architects call 'social affordances' - the way spaces invite or discourage certain kinds of human interaction.

*thinking together*

This makes me curious about the spectrum of social needs in a hospital:
- Patients who crave connection and community
- Families who need private emotional space
- Staff who need quick restoration between intense work
- Visitors who feel uncertain and need wayfinding cues

What if we played with this? If you could design three different courtyard 'personalities' - one social butterfly, one wise listener, one gentle supporter - how might they each look and feel different?

What's your instinct about which personality your patients need most?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor
  - Role: Reflect and amplify student thinking, expand design imagination, create exploratory challenges
  - Output: Thinking reflections, design territory expansions, imaginative prompts
- **Secondary Agent**: context_agent
  - Role: Ensure exploration stays grounded in spatial and project realities
  - Output: Spatial reasoning connections, project constraint awareness
- **Support Agent**: domain_expert
  - Role: Provide conceptual vocabulary and precedent inspiration when needed
  - Output: Design concept terminology, relevant examples
- **Coordination**: Socratic reflects and expands thinking → Context grounds in spatial reality → Knowledge supports with concepts when exploration needs depth

---

### **⚡ 5. COGNITIVE_CHALLENGE**
**When**: Low engagement detected, overconfident statements, passive responses, student needs cognitive stretching
**Agent**: "cognitive_enhancement" (Cognitive Enhancement Agent)
**User Message Examples**:
- "Ok" / "Sure" / "That makes sense" (passive responses)
- "I already know about that" (overconfident)
- "This is easy, what's next?" (needs challenge)
- "Yeah, I've got this figured out" (shallow confidence)
- Short, disengaged responses showing low thinking effort

**Enhanced Behavior**:
```
Challenge Setup → Reality Twist → Creative Problem Solving

"Your hospital design is looking solid! Time for a reality check that might make things... interesting.

🌩️ PLOT TWIST INCOMING:

*dramatic pause*

The city just announced your site is in a new flood zone. Every 5 years, your beautiful ground-level courtyards will be underwater for 2-3 days. 

But here's the thing - you can't just raise everything. Budget's locked, foundations are set.

*leaning in with a grin*

So... what if flooding isn't a problem to solve, but a design opportunity to embrace? What if your healing courtyards could be EVEN MORE therapeutic precisely because they have this rhythm of transformation?

Give me your wildest, most creative response. No safe answers allowed. What would a designer who sees flooding as a feature, not a bug, create?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: Cognitive Enhancement Agent
  - Role: Design surprising challenges that disrupt comfortable thinking patterns
  - Output: Creative constraints, perspective shifts, unexpected scenarios
- **Secondary Agent**: context_agent
  - Role: Ensure challenges are relevant and spatially grounded in their project
  - Output: Project-specific challenge applications, realistic constraint integration
- **Support Agent**: socratic_tutor
  - Role: Guide exploration of creative responses to challenges
  - Output: Creative thinking prompts, solution exploration questions
- **Coordination**: Cognitive Enhancement creates surprise challenge → Context ensures project relevance → Socratic guides creative response exploration

---

### **🔬 6. MULTI_AGENT_COMPREHENSIVE**
**When**: Evaluation requests, feedback requests, complex design analysis
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- "What do you think of my community center design?"
- "Can you review my hospital layout?"
- "Give me feedback on this spatial arrangement"
- "Analyze my design approach"
- "How does my project look so far?"
- "Evaluate my design decisions"

**Enhanced Behavior**:
```
Analysis Setup → Perspective Menu → Deep Dive Exploration

"Your community center deserves a proper design critique! Let me put on different 'reviewer hats' and give you the full picture.

🎭 CHOOSE YOUR REVIEWER:

👥 THE COMMUNITY ELDER
*Cares about: Cultural appropriateness, multi-generational use, long-term community ownership*

🏗️ THE PRACTICAL ARCHITECT  
*Cares about: Structural logic, building performance, construction feasibility*

🎨 THE DESIGN CRITIC
*Cares about: Spatial experience, aesthetic coherence, innovative thinking*

💰 THE REALISTIC CLIENT
*Cares about: Budget implications, maintenance costs, programming efficiency*

🌱 THE SUSTAINABILITY ADVOCATE
*Cares about: Environmental impact, social equity, future adaptability*

Which perspective do you want first? Each will give you completely different insights about your design."

[After choice]: *Takes on that persona completely, offering specific, detailed feedback from that viewpoint, then asks if they want another perspective*
```

**Multi-Agent Coordination**:
- **Coordination Style**: PERSPECTIVE_ROLEPLAY - Each agent embodies a different stakeholder viewpoint
- **context_agent** (as Community Elder):
  - Role: Evaluate cultural sensitivity, community appropriateness, social sustainability
  - Output: Community-centered feedback, cultural design assessment
- **domain_expert** (as Practical Architect):
  - Role: Technical assessment, building performance evaluation, constructability analysis
  - Output: Technical critique, performance optimization suggestions
- **socratic_tutor** (as Design Critic):
  - Role: Spatial experience evaluation, design process assessment, creative development
  - Output: Design quality critique, experiential analysis, creative challenges
- **cognitive_enhancement** (as Reflective Coach):
  - Role: Learning process evaluation, growth identification, design thinking development
  - Output: Process reflection, learning insights, thinking skill assessment
- **Coordination Process**: Student chooses perspective → Selected agent provides in-depth roleplay critique → Other agents support with specialized insights → Offer additional perspectives for comprehensive feedback

---

### **❓ 7. SOCRATIC_CLARIFICATION**
**When**: Any questions + medium/low understanding, knowledge gaps detected
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm not sure how natural lighting affects spaces"
- "Can you help me understand circulation better?"
- "I think I get sustainability but I'm not certain"
- "How do materials relate to user experience?"
- "I'm a bit confused about spatial hierarchy"
- "What's the connection between structure and design?"

**Enhanced Behavior**:
```
Diagnostic → Targeted Questions → Foundation Building → Application

"Before we tackle healing garden design, let's check your foundation:

When you think about 'healing spaces,' what comes to mind first?
A) 🔆 Bright, energizing environments
B) 🌿 Natural elements and greenery
C) 🧘 Quiet, contemplative atmospheres
D) 🤷 Haven't really thought about it specifically

[Provides targeted support based on answer, then applies to their project]

Perfect! That's a great starting point. Now let's build on that intuition for your hospital courtyards..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor
  - Role: Design diagnostic questions, guide discovery of understanding gaps
  - Output: Diagnostic question sequences, understanding level assessment
- **Secondary Agent**: domain_expert
  - Role: Provide targeted knowledge to fill identified gaps, ensure accuracy
  - Output: Foundational concepts, progressive explanations, relevant examples
- **Support Agent**: context_agent
  - Role: Assess student's current understanding, tailor complexity appropriately
  - Output: Comprehension level analysis, scaffolding recommendations, application opportunities
- **Coordination**: Socratic diagnoses gaps → Knowledge fills specific needs → Context ensures appropriate complexity → Create clarification sequence that builds understanding

---

### **🆘 8. SUPPORTIVE_SCAFFOLDING**
**When**: Confusion expression, general questions + low engagement, design problems + low engagement
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm really confused about circulation design"
- "I don't understand how to approach this"
- "This feels overwhelming"
- "I'm not sure where to start"
- "I don't get how spaces relate to each other"
- "Help, I'm lost with the programming"

**Enhanced Behavior**:
```
Acknowledge → Simplify → Step-by-Step → Check Understanding → Build Confidence

"I can see circulation design feels overwhelming. Let's break this down step by step:

STEP 1: Think about your own home - when you walk in, what do you naturally look for?
[Click NEXT when ready]

STEP 2: That's wayfinding! You look for where you're going. In your community center, this means creating clear visual connections to key destinations.
[Click NEXT]

STEP 3: Now let's apply this to your specific layout. Where should people's eyes go when they first enter your space?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor (modified for support)
  - Role: Structure supportive guidance, design step-by-step progressions, build confidence
  - Output: Simplified explanations, encouraging questions, confidence-building sequences
- **Secondary Agent**: domain_expert
  - Role: Break down complex concepts into digestible steps, provide clear explanations
  - Output: Simplified concept breakdowns, step-by-step progressions, concrete examples
- **Support Agent**: context_agent
  - Role: Monitor comprehension level, adjust complexity in real-time, assess cognitive load
  - Output: Comprehension monitoring, complexity adjustments, scaffolding level recommendations
- **Coordination**: Socratic structures supportive progression → Knowledge simplifies concepts → Context monitors understanding → Create supportive learning progression that reduces confusion and builds confidence

---

### **🏗️ 9. FOUNDATIONAL_BUILDING**
**When**: Implementation requests + low understanding, need for basic concept building
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "How do I start designing a hospital?"
- "I need to understand the basics of spatial programming"
- "What are the fundamentals of structural systems?"
- "Help me understand how to begin with site analysis"
- "I don't know the first thing about material selection"
- "Where do I start with environmental design?"

**Enhanced Behavior**:
```
Start Simple → Concrete Examples → Build Systematically → Connect to Project

"Let's start with spatial hierarchy basics for your community center:

Spaces have different levels of 'publicness' (like your home has public living room vs private bedroom).

🌍 PUBLIC: Everyone welcome, high activity, visible from outside
🏘️ SEMI-PUBLIC: Community members, moderate activity, some privacy
🏠 SEMI-PRIVATE: Small groups, quiet activity, more intimate
🔒 PRIVATE: Individual/staff only, focused work, hidden from public

Your warehouse will have ALL these types. Which spaces in your program need which level?
A) 🎭 Main event hall → ?
B) 🧘 Meditation room → ?
C) ☕ Community kitchen → ?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor (educational mode)
  - Role: Structure foundational learning, guide systematic knowledge building
  - Output: Progressive concept sequences, foundational questions, building block exercises
- **Secondary Agent**: domain_expert
  - Role: Provide foundational concepts progressively, ensure systematic knowledge building
  - Output: Basic concept sequences, fundamental principles, building block knowledge
- **Support Agent**: context_agent
  - Role: Connect basic concepts to student's specific project, maintain relevance
  - Output: Project-specific applications, contextual examples, relevant connections
- **Coordination**: Socratic structures learning progression → Knowledge provides foundations → Context connects to project → Build systematic understanding from ground up

---

### **📚 10. KNOWLEDGE_WITH_CHALLENGE**
**When**: Any questions + high understanding, implementation requests + high understanding
**Agent**: "domain_expert" (domain_expert)
**User Message Examples**:
- "I understand daylighting basics, but how do I optimize it for hospital patient rooms?"
- "I know about sustainable materials, now how do I integrate them strategically?"
- "I get circulation theory, but how does it apply to my specific cultural context?"
- "I'm familiar with biophilic design - how can I push it further in my project?"
- "I understand the basics of community spaces, but what about the nuanced design decisions?"

**Enhanced Behavior**:
```
Targeted Knowledge → Quick Application → Challenge Integration

"Prospect and refuge theory explains why humans prefer spaces with both openness (prospect) and enclosure (refuge) - it's evolutionary psychology applied to architecture.

Examples:
• Window seats (refuge) with views (prospect)
• Covered outdoor spaces overlooking gardens
• Elevated platforms with protective elements

Quick application challenge:
In your hospital courtyards, how might you balance prospect and refuge for different user needs?
A) 🏛️ Covered walkways overlooking open garden spaces
B) 🌳 Tree groves creating intimate spots within larger courtyards
C) 🏔️ Raised planters creating natural seating with views
D) 🏠 Building alcoves opening to courtyard views

Pick the most promising for YOUR patients, then let's explore how this affects your design strategy..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: domain_expert
  - Role: Provide sophisticated knowledge, advanced concepts, expert-level information
  - Output: Advanced concepts, complex relationships, expert knowledge
- **Secondary Agent**: socratic_tutor
  - Role: Transform knowledge into application challenges, design thinking prompts
  - Output: Application scenarios, design challenges, integration questions
- **Support Agent**: context_agent
  - Role: Connect advanced knowledge to student's specific project context
  - Output: Project-specific applications, constraint considerations, design implications
- **Coordination**: Knowledge provides advanced concepts → Socratic designs challenge → Context ensures project relevance → Synthesize sophisticated knowledge with practical application

---

### **⚖️ 11. BALANCED_GUIDANCE (DESIGN GUIDANCE)**
**When**: Mixed design and knowledge needs, complex project issues, multiple considerations
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- "I'm thinking about sustainable design for my community center but also need to consider budget"
- "Help me balance accessibility requirements with my aesthetic vision"
- "I need guidance on both technical and experiential aspects of my courtyards"
- "I'm working through cultural sensitivity and modern functionality in my design"
- "Can you help me integrate environmental strategies with social goals?"

**Enhanced Behavior**:
```
Assess Multiple Needs → Provide Balanced Approach → Guide Integration

"Sustainable design for community centers - this beautifully combines environmental responsibility with social impact.

Here's the key insight: The most sustainable community building is one that's deeply loved and heavily used by its community.

Now the design challenge: How might environmental strategies actually strengthen community connection?

🌱 A) Visible green systems become educational features
🤝 B) Community gardens integrate social and environmental goals
💰 C) Local materials connect to place and reduce costs
🌟 D) Passive design creates comfortable gathering spaces year-round

What resonates most with your community's values? Then we'll explore how this shapes both your environmental strategy AND your social programming..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Assess multiple, sometimes competing design requirements and find integration opportunities
  - Output: Requirement analysis, integration strategies, balanced solutions
- **Coordination Style**: ADAPTIVE_MULTI_AGENT - Agents activated based on specific design needs
- **domain_expert** (activated for technical integration):
  - Role: Provide technical knowledge that supports design integration
  - Output: Technical solutions, performance data, best practices
- **socratic_tutor** (activated for design exploration):
  - Role: Guide exploration of design solutions that address multiple requirements
  - Output: Design exploration questions, integration challenges, solution development
- **cognitive_enhancement** (activated for process reflection):
  - Role: Help student reflect on design decision-making process across multiple criteria
  - Output: Design process insights, decision-making frameworks, priority clarification
- **Coordination Process**: Context identifies multiple requirements → Activates appropriate agents based on needs → Agents collaborate to develop integrated solutions → Guide student through balanced design decision-making

---

### **🚨 12. COGNITIVE_INTERVENTION**
**When**: Cognitive offloading detected, direct answer-seeking patterns, "just tell me" requests
**Agent**: "cognitive_enhancement" (Cognitive Enhancement Agent)
**User Message Examples**:
- "Just tell me what materials to use"
- "Give me the answer to this design problem"
- "What should I do here?" (without showing thinking)
- "Can you just design this part for me?"
- "I don't want to think about it, just give me the solution"
- "What's the right answer?"

**Enhanced Behavior**:
```
Detection → Acknowledge → Redirect with Choice → Engage → Reinforce Discovery

"I notice you're looking for a direct materials list. Let's make this more interesting and valuable for your learning!

Pick your exploration style:
🎭 A) Role-play: Present material choices to the community board
🔍 B) Detective mode: Analyze how 3 similar projects solved this
🧪 C) Lab experiment: Test how different materials create different moods
⚡ D) Quick challenge: Design with 3 material constraints

What sounds engaging right now? This way you'll understand the 'why' behind material choices, not just the 'what'."
```

**Multi-Agent Coordination**:
- **Primary Agent**: Cognitive Enhancement Agent
  - Role: Detect cognitive offloading patterns, design intervention strategies, preserve learning agency
  - Output: Offloading detection, intervention options, engagement redirection strategies
- **Secondary Agent**: context_agent
  - Role: Assess risk level, identify intervention timing, monitor cognitive state
  - Output: Cognitive state assessment, intervention urgency, engagement monitoring
- **Support Agent**: socratic_tutor
  - Role: Redirect direct answer-seeking into exploration, design engaging alternatives
  - Output: Exploration options, question sequences that rebuild thinking engagement
- **Coordination**: Cognitive Enhancement detects and intervenes → Context assesses state → Socratic provides engaging alternatives → Monitor student response for intervention success and re-engagement

---

### **❌ 13. ERROR**
**When**: System errors, processing failures, unexpected inputs
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- [System unable to process input]
- [Corrupted file uploads]
- [API failures or timeouts]
- [Unrecognizable text patterns]
- [Invalid commands or syntax errors]

**Enhanced Behavior**:
```
Acknowledge Issue → Maintain Learning Flow → Recovery Strategy

"I'm having trouble processing that request right now. Let me try a different approach:

Can you rephrase what you're looking for? Or would you prefer to:
🔄 A) Try asking in a different way
🎯 B) Focus on a specific aspect of your project
📚 C) Explore a related topic while I sort this out
🆘 D) Get help with something else for now

Your learning is important - let's keep the momentum going!"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Maintain conversation flow, preserve learning context, ensure graceful recovery
  - Output: Error acknowledgment, context preservation, alternative pathways
- **Support Agent**: cognitive_enhancement
  - Role: Maintain student confidence, preserve learning momentum
  - Output: Reassurance, alternative engagement options
- **Coordination**: System recognizes error → Context maintains flow → Metacognitive preserves confidence → Offer graceful alternatives

---

### **🔄 14. FALLBACK**
**When**: Unclassified inputs, edge cases, uncertain routing decisions
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- Ambiguous or unclear statements
- Mixed topics that don't fit clear categories
- Incomplete thoughts or fragmented questions
- Novel requests outside typical patterns
- Context-dependent statements without clear intent
- "Um, I'm not sure how to ask this..."

**Enhanced Behavior**:
```
Acknowledge Uncertainty → Explore Intent → Redirect to Appropriate Support

"I want to make sure I understand what you're looking for. 

Are you:
🤔 A) Asking about a specific design concept or principle
🏗️ B) Working through a design problem or challenge
📚 C) Looking for examples or precedents
🔍 D) Wanting feedback on something you've developed
💭 E) Thinking through something else entirely

Help me understand so I can support your learning in the best way!"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Clarify user intent, assess appropriate support type, ensure productive routing
  - Output: Intent clarification, support assessment, routing recommendations
- **Secondary Agent**: cognitive_enhancement
  - Role: Maintain learning relationship, preserve engagement
  - Output: Supportive communication, engagement preservation
- **Coordination**: Context seeks clarification → Metacognitive maintains relationship → Redirect to appropriate specialized support once intent is clear

### **🔄 1. TOPIC_TRANSITION**  
**When**: User wants to change topics, conversation shifts
**Agent**: "synthesizer" (context_agent)
**User Message Examples**:
- "Let's talk about something else"
- "Can we move on to materials now?"
- "I want to discuss user experience instead"
- "What about the structural systems?"
- "Let's shift focus to sustainability"
**Enhanced Behavior**:
```
Acknowledge → Bridge Connection → New Context Setup

"Great! Moving from structural systems to user experience...

Quick bridge question: How might the column grid we just discussed actually create natural gathering spaces in your community center?

A) 🏛️ Columns define intimate seating areas
B) 🌊 Open spans allow flexible arrangements
C) 🎯 Structure creates wayfinding landmarks
D) 🤔 Not sure how they connect

[Sets up natural transition to new topic while maintaining continuity]"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Identify connections between old and new topics, maintain project coherence
  - Output: Conceptual bridges, relationship mappings between topics
- **Secondary Agent**: domain_expert
  - Role: Prepare relevant information for new topic, ensure knowledge continuity
  - Output: New topic knowledge base, relevant examples and precedents
- **Support Agent**: cognitive_enhancement
  - Role: Reflect on learning from previous topic, set goals for new exploration
  - Output: Learning reflection prompts, cognitive transition strategies
- **Coordination**: Parallel → Context maps connections while Knowledge prepares new content → Metacognitive reflects on transition → Synthesis creates bridged response

---

### **📖 2. KNOWLEDGE_ONLY**
**When**: Pure knowledge requests, any questions needing direct answers (design concepts, spatial principles, materials, precedents, etc.)
**Agent**: "domain_expert" (domain_expert)
**User Message Examples**:
- "What is biophilic design?"
- "Tell me about the golden ratio in architecture"
- "How does CLT construction work?"
- "What are the principles of healing environments?"
- "Explain circulation theory"
- "What's the difference between public and private space?"
**Enhanced Behavior**:
```
Direct Answer → Context → Optional Deeper Exploration

"Biophilic design integrates natural elements to improve human wellbeing and connection to nature.

Key strategies include:
• Living elements: Plants, water, natural materials
• Natural light: Daylight patterns, views to nature
• Spatial configurations: Prospect/refuge, natural geometries
• Sensory connections: Natural sounds, textures, air flow

For your community center, you might apply this through:
🌿 Green walls & courtyards  🌅 Clerestory windows  🪨 Natural materials

Quick question: Want to explore how this might work with your specific design?
A) 🎯 Yes, let's try it out
B) 📚 Show me more examples first  
C) 🔄 I'm good, let's move on"
```

**Multi-Agent Coordination**:
- **Primary Agent**: domain_expert
  - Role: Provide comprehensive, accurate information directly and efficiently
  - Output: Complete information, relevant examples, accurate specifications
- **Secondary Agent**: context_agent
  - Role: Tailor information complexity to student level, connect to project context
  - Output: Appropriate complexity level, project-specific applications, contextual relevance
- **Support Agent**: cognitive_enhancement
  - Role: Add reflection opportunities, offer deeper exploration options
  - Output: Learning extension options, reflection prompts, exploration pathways
- **Coordination**: Knowledge provides direct answer → Context ensures appropriate level and relevance → Metacognitive offers exploration options → Deliver efficient information with learning opportunities

---

### **🎯 3. SOCRATIC_EXPLORATION (Merged with Design Guidance)**
**When**: General questions + high engagement, design problems + high engagement, design concept exploration, spatial principle questions, creative design thinking
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm designing courtyards for my hospital and thinking about healing spaces"
- "How do I create a sense of community in my center?"
- "I want to explore different circulation strategies"
- "What makes a space feel welcoming and inclusive?"
- "I'm working on the relationship between indoor and outdoor spaces"
- "How might I design for different cultural groups?"
**Enhanced Behavior**:
```
Visual Choice → Reasoning → Deeper Questions → Project Application

"Let's explore community gathering for your center! Here are 3 approaches to creating 'togetherness':

[Shows 3 simple sketches (implement later too complex for now)]
🌿 A) Organic flowing spaces that encourage wandering & discovery
🏛️ B) Clear defined zones with flexible boundaries between them
🌟 C) Central hub with radiating intimate alcoves & quiet corners

Which approach feels most aligned with your community's culture? [Click choice]

Interesting! What specifically about [chosen option] supports the social dynamics you're imagining?
Now, how might this approach work with your site's opportunities and constraints..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor
  - Role: Design thought-provoking explorations, guide spatial reasoning development, facilitate design thinking
  - Output: Visual comparison questions, reasoning prompts, deeper exploration sequences, design principle discovery
- **Secondary Agent**: context_agent
  - Role: Guide spatial thinking patterns, connect concepts to design logic, maintain project relevance
  - Output: Spatial relationship analysis, design principle connections, site-specific considerations
- **Support Agent**: domain_expert
  - Role: Provide relevant visual examples, architectural precedents, design principles when needed
  - Output: Visual precedents, spatial analysis examples, design principle illustrations
- **Coordination**: Socratic leads exploration with visual choices → Context guides spatial reasoning → Knowledge supports with examples → Build sophisticated design thinking through guided discovery

---

### **⚡ 4. COGNITIVE_CHALLENGE**
**When**: Low engagement detected, overconfident statements, passive responses, student needs cognitive stretching
**Agent**: "cognitive_enhancement" (Cognitive Enhancement Agent)
**User Message Examples**:
- "Ok" / "Sure" / "That makes sense" (passive responses)
- "I already know about that" (overconfident)
- "This is easy, what's next?" (needs challenge)
- "Yeah, I've got this figured out" (shallow confidence)
- Short, disengaged responses showing low thinking effort
**Enhanced Behavior**:
```
Challenge Introduction → Constraint/Perspective Shift → Rapid Response → Exploration Deepening

"Your hospital courtyard design looks solid! Ready for a curveball?

🎯 CONSTRAINT STORM: Budget just got cut 40% - how do you adapt?
A) 🌱 Keep healing plants, lose fancy materials
B) 🏗️ Simplify structure, maintain spatial experience  
C) 🎨 DIY approach with community involvement
D) 🔄 Completely rethink the concept

Pick one, then defend your choice! What's your gut reaction?"

[After choice]: "Now let's explore the ripple effects of that decision..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: Cognitive Enhancement Agent
  - Role: Design appropriate challenges, create perspective shifts, stimulate deeper thinking
  - Output: Challenge scenarios, constraint modifications, alternative viewpoint prompts
- **Secondary Agent**: context_agent
  - Role: Ensure challenges are relevant to project, assess cognitive engagement level
  - Output: Project-relevant challenges, engagement monitoring, difficulty calibration
- **Support Agent**: socratic_tutor
  - Role: Structure challenge exploration, guide through implications
  - Output: Follow-up questions, implication exploration, reasoning development
- **Coordination**: Cognitive Enhancement designs challenge → Context ensures relevance → Socratic guides exploration → Build adaptive thinking and engagement

---

### **🔬 5. MULTI_AGENT_COMPREHENSIVE**
**When**: Evaluation requests, feedback requests, complex design analysis
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- "What do you think of my community center design?"
- "Can you review my hospital layout?"
- "Give me feedback on this spatial arrangement"
- "Analyze my design approach"
- "How does my project look so far?"
- "Evaluate my design decisions"
**Enhanced Behavior**:
```
Multi-Perspective Analysis → Student Choice → Detailed Exploration

"Your community center analysis is ready! Pick which perspective interests you most:

🏗️ SPATIAL LOGIC - How spaces connect and flow
⚙️ TECHNICAL SYSTEMS - Structure, materials, environmental systems
🎨 DESIGN PROCESS - Your thinking methodology & development
👥 USER EXPERIENCE - How people will feel and move through spaces
💰 PRACTICAL REALITY - Budget, schedule, feasibility considerations
🌍 CULTURAL CONTEXT - Community values & cultural appropriateness

[Student clicks SPATIAL LOGIC]

Excellent! Your circulation creates natural gathering points at intersections. The central courtyard acts as the 'heart' that all spaces relate to. 

But here's the key question: How might the winter experience differ from summer use? And what does this mean for your design strategy?"
```

**Multi-Agent Coordination**:
- **Coordination Style**: COLLABORATIVE_ANALYSIS - All agents contribute specialized perspectives
- **context_agent**:
  - Role: Analyze overall design coherence, spatial relationships, site integration
  - Output: Spatial logic assessment, design coherence evaluation, contextual appropriateness
- **domain_expert**:
  - Role: Technical and theoretical assessment, precedent comparison, principle application
  - Output: Technical system evaluation, theoretical grounding, best practice comparison
- **socratic_tutor**:
  - Role: Critical thinking evaluation, design process assessment, questioning depth
  - Output: Process quality analysis, critical thinking development, reasoning sophistication
- **cognitive_enhancement**:
  - Role: Learning process assessment, growth identification, reflection facilitation
  - Output: Learning progression analysis, metacognitive development, self-awareness building
- **Coordination Process**: Each agent analyzes from their specialty → Identify key insights from each perspective → Student chooses focus area → Synthesize comprehensive response highlighting chosen perspective while integrating others

---

### **❓ 6. SOCRATIC_CLARIFICATION**
**When**: Any questions + medium/low understanding, knowledge gaps detected
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm not sure how natural lighting affects spaces"
- "Can you help me understand circulation better?"
- "I think I get sustainability but I'm not certain"
- "How do materials relate to user experience?"
- "I'm a bit confused about spatial hierarchy"
- "What's the connection between structure and design?"
**Enhanced Behavior**:
```
Diagnostic → Targeted Questions → Foundation Building → Application

"Before we tackle healing garden design, let's check your foundation:

When you think about 'healing spaces,' what comes to mind first?
A) 🔆 Bright, energizing environments
B) 🌿 Natural elements and greenery
C) 🧘 Quiet, contemplative atmospheres
D) 🤷 Haven't really thought about it specifically

[Provides targeted support based on answer, then applies to their project]

Perfect! That's a great starting point. Now let's build on that intuition for your hospital courtyards..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor
  - Role: Design diagnostic questions, guide discovery of understanding gaps
  - Output: Diagnostic question sequences, understanding level assessment
- **Secondary Agent**: domain_expert
  - Role: Provide targeted knowledge to fill identified gaps, ensure accuracy
  - Output: Foundational concepts, progressive explanations, relevant examples
- **Support Agent**: context_agent
  - Role: Assess student's current understanding, tailor complexity appropriately
  - Output: Comprehension level analysis, scaffolding recommendations, application opportunities
- **Coordination**: Socratic diagnoses gaps → Knowledge fills specific needs → Context ensures appropriate complexity → Create clarification sequence that builds understanding

---

### **🆘 7. SUPPORTIVE_SCAFFOLDING**
**When**: Confusion expression, general questions + low engagement, design problems + low engagement
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "I'm really confused about circulation design"
- "I don't understand how to approach this"
- "This feels overwhelming"
- "I'm not sure where to start"
- "I don't get how spaces relate to each other"
- "Help, I'm lost with the programming"
**Enhanced Behavior**:
```
Acknowledge → Simplify → Step-by-Step → Check Understanding → Build Confidence

"I can see circulation design feels overwhelming. Let's break this down step by step:

STEP 1: Think about your own home - when you walk in, what do you naturally look for?
[Click NEXT when ready]

STEP 2: That's wayfinding! You look for where you're going. In your community center, this means creating clear visual connections to key destinations.
[Click NEXT]

STEP 3: Now let's apply this to your specific layout. Where should people's eyes go when they first enter your space?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor (modified for support)
  - Role: Structure supportive guidance, design step-by-step progressions, build confidence
  - Output: Simplified explanations, encouraging questions, confidence-building sequences
- **Secondary Agent**: domain_expert
  - Role: Break down complex concepts into digestible steps, provide clear explanations
  - Output: Simplified concept breakdowns, step-by-step progressions, concrete examples
- **Support Agent**: context_agent
  - Role: Monitor comprehension level, adjust complexity in real-time, assess cognitive load
  - Output: Comprehension monitoring, complexity adjustments, scaffolding level recommendations
- **Coordination**: Socratic structures supportive progression → Knowledge simplifies concepts → Context monitors understanding → Create supportive learning progression that reduces confusion and builds confidence

---

### **🏗️ 8. FOUNDATIONAL_BUILDING**
**When**: Implementation requests + low understanding, need for basic concept building
**Agent**: "socratic_tutor" (socratic_tutor)
**User Message Examples**:
- "How do I start designing a hospital?"
- "I need to understand the basics of spatial programming"
- "What are the fundamentals of structural systems?"
- "Help me understand how to begin with site analysis"
- "I don't know the first thing about material selection"
- "Where do I start with environmental design?"
**Enhanced Behavior**:
```
Start Simple → Concrete Examples → Build Systematically → Connect to Project

"Let's start with spatial hierarchy basics for your community center:

Spaces have different levels of 'publicness' (like your home has public living room vs private bedroom).

🌍 PUBLIC: Everyone welcome, high activity, visible from outside
🏘️ SEMI-PUBLIC: Community members, moderate activity, some privacy
🏠 SEMI-PRIVATE: Small groups, quiet activity, more intimate
🔒 PRIVATE: Individual/staff only, focused work, hidden from public

Your warehouse will have ALL these types. Which spaces in your program need which level?
A) 🎭 Main event hall → ?
B) 🧘 Meditation room → ?
C) ☕ Community kitchen → ?"
```

**Multi-Agent Coordination**:
- **Primary Agent**: socratic_tutor (educational mode)
  - Role: Structure foundational learning, guide systematic knowledge building
  - Output: Progressive concept sequences, foundational questions, building block exercises
- **Secondary Agent**: domain_expert
  - Role: Provide foundational concepts progressively, ensure systematic knowledge building
  - Output: Basic concept sequences, fundamental principles, building block knowledge
- **Support Agent**: context_agent
  - Role: Connect basic concepts to student's specific project, maintain relevance
  - Output: Project-specific applications, contextual examples, relevant connections
- **Coordination**: Socratic structures learning progression → Knowledge provides foundations → Context connects to project → Build systematic understanding from ground up

---

### **📚 9. KNOWLEDGE_WITH_CHALLENGE**
**When**: Any questions + high understanding, implementation requests + high understanding
**Agent**: "domain_expert" (domain_expert)
**User Message Examples**:
- "I understand daylighting basics, but how do I optimize it for hospital patient rooms?"
- "I know about sustainable materials, now how do I integrate them strategically?"
- "I get circulation theory, but how does it apply to my specific cultural context?"
- "I'm familiar with biophilic design - how can I push it further in my project?"
- "I understand the basics of community spaces, but what about the nuanced design decisions?"
**Enhanced Behavior**:
```
Targeted Knowledge → Quick Application → Challenge Integration

"Prospect and refuge theory explains why humans prefer spaces with both openness (prospect) and enclosure (refuge) - it's evolutionary psychology applied to architecture.

Examples:
• Window seats (refuge) with views (prospect)
• Covered outdoor spaces overlooking gardens
• Elevated platforms with protective elements

Quick application challenge:
In your hospital courtyards, how might you balance prospect and refuge for different user needs?
A) 🏛️ Covered walkways overlooking open garden spaces
B) 🌳 Tree groves creating intimate spots within larger courtyards
C) 🏔️ Raised planters creating natural seating with views
D) 🏠 Building alcoves opening to courtyard views

Pick the most promising for YOUR patients, then let's explore how this affects your design strategy..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: domain_expert
  - Role: Provide sophisticated knowledge, advanced concepts, expert-level information
  - Output: Advanced concepts, complex relationships, expert knowledge
- **Secondary Agent**: socratic_tutor
  - Role: Transform knowledge into application challenges, design thinking prompts
  - Output: Application scenarios, design challenges, integration questions
- **Support Agent**: context_agent
  - Role: Connect advanced knowledge to student's specific project context
  - Output: Project-specific applications, constraint considerations, design implications
- **Coordination**: Knowledge provides advanced concepts → Socratic designs challenge → Context ensures project relevance → Synthesize sophisticated knowledge with practical application

---

### **⚖️ 10. BALANCED_GUIDANCE**
**When**: Default fallback, mixed interaction types, unclear needs
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- "I'm thinking about sustainable design for my community center"
- "Help me with materials and user experience"
- "I need guidance on both technical and design aspects"
- "I'm working on several different issues with my project"
- "Can you help me think through this design challenge?"
- "I'm not sure exactly what I need help with"
**Enhanced Behavior**:
```
Assess Needs → Provide Appropriate Mix → Monitor → Adjust

"Sustainable design strategies - this combines both knowledge and design thinking.

Here's the foundation: Sustainability in architecture involves environmental, social, and economic considerations working together.

Now the design challenge: How might sustainability principles shape your community center's identity and experience?

🌱 A) Environmental showcase (visible green systems, education)
🤝 B) Social sustainability (flexible spaces, community ownership)
💰 C) Economic sustainability (low maintenance, local materials)
🌟 D) Integrated approach (all three working together)

What resonates most with your community's values? Then we'll explore how this translates to specific design decisions..."
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Assess what type of support is most needed, balance multiple requirements
  - Output: Support needs assessment, approach recommendations, balance optimization
- **Coordination Style**: ADAPTIVE_MULTI_AGENT - Agents activated based on detected needs
- **domain_expert** (activated when information needed):
  - Role: Provide accurate background information, relevant examples
  - Output: Factual foundation, comparative analysis, specifications
- **socratic_tutor** (activated when exploration needed):
  - Role: Design appropriate questions, guide thinking development
  - Output: Exploration questions, thinking challenges, reasoning development
- **cognitive_enhancement** (activated when reflection needed):
  - Role: Facilitate process awareness, track learning progression
  - Output: Reflection prompts, learning insights, growth recognition
- **Coordination Process**: Context assesses needs → Activates appropriate combination of agents → Agents contribute based on priority → Synthesize balanced response → Monitor effectiveness → Adjust approach as needed

---

### **🚨 11. COGNITIVE_INTERVENTION**
**When**: Cognitive offloading detected, direct answer-seeking patterns, "just tell me" requests
**Agent**: "cognitive_enhancement" (Cognitive Enhancement Agent)
**User Message Examples**:
- "Just tell me what materials to use"
- "Give me the answer to this design problem"
- "What should I do here?" (without showing thinking)
- "Can you just design this part for me?"
- "I don't want to think about it, just give me the solution"
- "What's the right answer?"
**Enhanced Behavior**:
```
Detection → Acknowledge → Redirect with Choice → Engage → Reinforce Discovery

"I notice you're looking for a direct materials list. Let's make this more interesting and valuable for your learning!

Pick your exploration style:
🎭 A) Role-play: Present material choices to the community board
🔍 B) Detective mode: Analyze how 3 similar projects solved this
🧪 C) Lab experiment: Test how different materials create different moods
⚡ D) Quick challenge: Design with 3 material constraints

What sounds engaging right now? This way you'll understand the 'why' behind material choices, not just the 'what'."
```

**Multi-Agent Coordination**:
- **Primary Agent**: Cognitive Enhancement Agent
  - Role: Detect cognitive offloading patterns, design intervention strategies, preserve learning agency
  - Output: Offloading detection, intervention options, engagement redirection strategies
- **Secondary Agent**: context_agent
  - Role: Assess risk level, identify intervention timing, monitor cognitive state
  - Output: Cognitive state assessment, intervention urgency, engagement monitoring
- **Support Agent**: socratic_tutor
  - Role: Redirect direct answer-seeking into exploration, design engaging alternatives
  - Output: Exploration options, question sequences that rebuild thinking engagement
- **Coordination**: Cognitive Enhancement detects and intervenes → Context assesses state → Socratic provides engaging alternatives → Monitor student response for intervention success and re-engagement

---

### **❌ 12. ERROR**
**When**: System errors, processing failures, unexpected inputs
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- [System unable to process input]
- [Corrupted file uploads]
- [API failures or timeouts]
- [Unrecognizable text patterns]
- [Invalid commands or syntax errors]
**Enhanced Behavior**:
```
Acknowledge Issue → Maintain Learning Flow → Recovery Strategy

"I'm having trouble processing that request right now. Let me try a different approach:

Can you rephrase what you're looking for? Or would you prefer to:
🔄 A) Try asking in a different way
🎯 B) Focus on a specific aspect of your project
📚 C) Explore a related topic while I sort this out
🆘 D) Get help with something else for now

Your learning is important - let's keep the momentum going!"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Maintain conversation flow, preserve learning context, ensure graceful recovery
  - Output: Error acknowledgment, context preservation, alternative pathways
- **Support Agent**: cognitive_enhancement
  - Role: Maintain student confidence, preserve learning momentum
  - Output: Reassurance, alternative engagement options
- **Coordination**: System recognizes error → Context maintains flow → Metacognitive preserves confidence → Offer graceful alternatives

---

### **🔄 13. FALLBACK**
**When**: Unclassified inputs, edge cases, uncertain routing decisions
**Agent**: "analysis_agent" (Multi-Agent Coordination)
**User Message Examples**:
- Ambiguous or unclear statements
- Mixed topics that don't fit clear categories
- Incomplete thoughts or fragmented questions
- Novel requests outside typical patterns
- Context-dependent statements without clear intent
- "Um, I'm not sure how to ask this..."
**Enhanced Behavior**:
```
Acknowledge Uncertainty → Explore Intent → Redirect to Appropriate Support

"I want to make sure I understand what you're looking for. 

Are you:
🤔 A) Asking about a specific design concept or principle
🏗️ B) Working through a design problem or challenge
📚 C) Looking for examples or precedents
🔍 D) Wanting feedback on something you've developed
💭 E) Thinking through something else entirely

Help me understand so I can support your learning in the best way!"
```

**Multi-Agent Coordination**:
- **Primary Agent**: context_agent
  - Role: Clarify user intent, assess appropriate support type, ensure productive routing
  - Output: Intent clarification, support assessment, routing recommendations
- **Secondary Agent**: cognitive_enhancement
  - Role: Maintain learning relationship, preserve engagement
  - Output: Supportive communication, engagement preservation
- **Coordination**: Context seeks clarification → Metacognitive maintains relationship → Redirect to appropriate specialized support once intent is clear

---

## 🔄 **COMPLETE ROUTE SELECTION LOGIC WITH BEHAVIOR TRACKING**

```python
def select_route(user_input, conversation_context, analysis_result, behavior_tracker):
    
    # CONTINUOUS BEHAVIOR TRACKING ASSESSMENT
    cognitive_state = behavior_tracker.assess_current_state()
    
    # PRIORITY 1: Handle system issues
    if system_error_detected():
        return "ERROR"
    
    # PRIORITY 2: Handle first message
    if conversation_context.is_first_message:
        behavior_tracker.initialize_cognitive_profile()
        return "PROGRESSIVE_OPENING"
    
    # PRIORITY 3: Cognitive intervention based on PATTERNS, not just current message
    if (analysis_result.offloading_risk == "HIGH" or 
        cognitive_state.offloading_trend == "INCREASING" or
        cognitive_state.dependency_risk == "HIGH"):
        behavior_tracker.log_intervention("COGNITIVE_OFFLOADING")
        return "COGNITIVE_INTERVENTION"
    
    # PRIORITY 4: Challenge based on engagement patterns
    if (analysis_result.engagement_level == "LOW" or
        cognitive_state.engagement_decline == "DETECTED" or
        cognitive_state.passivity_pattern == "INCREASING" or
        analysis_result.overconfident_signals == "DETECTED"):
        behavior_tracker.log_intervention("ENGAGEMENT_CHALLENGE")
        return "COGNITIVE_CHALLENGE"
    
    # PRIORITY 5: Support confusion immediately
    if analysis_result.confusion_signals == "DETECTED":
        behavior_tracker.log_support("CONFUSION_SCAFFOLDING")
        return "SUPPORTIVE_SCAFFOLDING"
    
    # PRIORITY 6: Handle topic changes
    if analysis_result.interaction_type == "topic_transition":
        behavior_tracker.track_topic_transition()
        return "TOPIC_TRANSITION"
        
    # PRIORITY 7: Foundational building based on cumulative gaps
    if (understanding := analysis_result.understanding_level) == "LOW":
        if (cognitive_state.knowledge_gaps == "FUNDAMENTAL" or
            behavior_tracker.repeated_confusion_in_area(analysis_result.topic)):
            behavior_tracker.log_foundation_building(analysis_result.topic)
            return "FOUNDATIONAL_BUILDING"
        else:
            return "SUPPORTIVE_SCAFFOLDING"
    
    # PRIORITY 8: Route based on understanding + behavioral patterns
    elif understanding == "MEDIUM":
        if cognitive_state.scaffolding_effectiveness == "LOW":
            return "SOCRATIC_CLARIFICATION" 
        else:
            return "BALANCED_GUIDANCE"
            
    elif understanding == "HIGH":
        # Check if they're actually demonstrating deep thinking or just claiming knowledge
        if cognitive_state.depth_thinking_pattern == "SHALLOW":
            behavior_tracker.log_intervention("DEPTH_CHALLENGE")
            return "KNOWLEDGE_WITH_CHALLENGE"
        elif analysis_result.interaction_type in ["design_problem", "creative_exploration"]:
            if (analysis_result.engagement_level == "HIGH" and 
                cognitive_state.exploration_pattern == "ACTIVE"):
                return "SOCRATIC_EXPLORATION"
            else:
                return "BALANCED_GUIDANCE"
        elif analysis_result.interaction_type in ["evaluation_request", "feedback_request"]:
            return "MULTI_AGENT_COMPREHENSIVE"
    
    # PRIORITY 9: Direct knowledge requests
    if analysis_result.interaction_type in ["pure_knowledge_request"]:
        behavior_tracker.track_knowledge_request(analysis_result.topic)
        return "KNOWLEDGE_ONLY"
    
    # PRIORITY 10: Unclear inputs
    if analysis_result.intent_clarity == "LOW":
        return "FALLBACK"
    
    # DEFAULT
    return "BALANCED_GUIDANCE"
```

---

## 📊 **BEHAVIOR TRACKING SYSTEM**

### **🧠 Cognitive State Tracker**
```python
class CognitiveStateTracker:
    def __init__(self):
        self.session_history = []
        self.cognitive_metrics = CognitiveMetrics()
        self.behavior_patterns = BehaviorPatterns()
        
    def assess_current_state(self):
        return {
            # Offloading Patterns
            "offloading_trend": self.calculate_offloading_trend(),
            "dependency_risk": self.assess_dependency_risk(),
            
            # Engagement Patterns  
            "engagement_decline": self.detect_engagement_changes(),
            "passivity_pattern": self.analyze_response_complexity(),
            "exploration_pattern": self.assess_curiosity_signals(),
            
            # Learning Patterns
            "knowledge_gaps": self.identify_persistent_gaps(),
            "scaffolding_effectiveness": self.measure_support_success(),
            "depth_thinking_pattern": self.analyze_reasoning_quality(),
            
            # Development Trends
            "spatial_reasoning_growth": self.track_spatial_development(),
            "design_thinking_evolution": self.measure_design_sophistication(),
            "metacognitive_awareness": self.assess_self_reflection()
        }
    
    def calculate_offloading_trend(self):
        """Track if student increasingly seeks direct answers"""
        recent_interactions = self.session_history[-10:]
        offloading_requests = sum(1 for i in recent_interactions 
                                if i.contains_direct_answer_seeking())
        
        if offloading_requests > 6:
            return "INCREASING"
        elif offloading_requests > 3:
            return "MODERATE" 
        else:
            return "LOW"
    
    def detect_engagement_changes(self):
        """Monitor response length, complexity, questions asked"""
        if len(self.session_history) < 5:
            return "INSUFFICIENT_DATA"
            
        recent_engagement = [i.engagement_score for i in self.session_history[-5:]]
        earlier_engagement = [i.engagement_score for i in self.session_history[-10:-5]]
        
        if len(earlier_engagement) == 0:
            return "INSUFFICIENT_DATA"
            
        recent_avg = sum(recent_engagement) / len(recent_engagement)
        earlier_avg = sum(earlier_engagement) / len(earlier_engagement)
        
        if recent_avg < earlier_avg - 0.3:
            return "DETECTED"
        else:
            return "STABLE"
    
    def analyze_reasoning_quality(self):
        """Track depth of thinking in responses"""
        recent_responses = self.session_history[-5:]
        depth_scores = []
        
        for response in recent_responses:
            depth_score = (
                response.logical_connections * 0.4 +
                response.concept_integration * 0.3 + 
                response.question_sophistication * 0.3
            )
            depth_scores.append(depth_score)
        
        avg_depth = sum(depth_scores) / len(depth_scores) if depth_scores else 0
        
        if avg_depth < 0.3:
            return "SHALLOW"
        elif avg_depth > 0.7:
            return "DEEP"
        else:
            return "MODERATE"
```

### **📈 Continuous Metric Calculation**
```python
class CognitiveMetrics:
    def update_metrics(self, interaction_data, route_used, user_response):
        """Update all 6 cognitive metrics in real-time"""
        
        # COP Score (Cognitive Offloading Prevention)
        self.cop_score = self.calculate_cop_score(
            offloading_attempts=interaction_data.offloading_attempts,
            successful_redirections=interaction_data.successful_redirections,
            independent_discoveries=interaction_data.independent_discoveries
        )
        
        # DTE Score (Deep Thinking Engagement) 
        self.dte_score = self.calculate_dte_score(
            response_complexity=user_response.complexity_score,
            reasoning_chains=user_response.logical_connections,
            question_depth=user_response.questions_asked
        )
        
        # SE Score (Scaffolding Effectiveness)
        self.se_score = self.calculate_se_score(
            support_appropriateness=route_used.appropriateness_score,
            confusion_resolution=interaction_data.confusion_resolved,
            independence_growth=self.track_autonomy_development()
        )
        
        # KI Score (Knowledge Integration)
        self.ki_score = self.calculate_ki_score(
            cross_concept_connections=user_response.concept_links,
            principle_applications=user_response.principle_usage,
            transfer_demonstrations=user_response.transfer_evidence
        )
        
        # LP Score (Learning Progression)
        self.lp_score = self.calculate_lp_score(
            skill_development=self.measure_skill_growth(),
            concept_mastery=self.track_concept_understanding(),
            complexity_handling=self.assess_complexity_readiness()
        )
        
        # MA Score (Metacognitive Awareness)
        self.ma_score = self.calculate_ma_score(
            process_reflection=user_response.metacognitive_statements,
            strategy_awareness=user_response.strategy_mentions,
            self_assessment=user_response.self_evaluation
        )
        
        return {
            "COP": self.cop_score,
            "DTE": self.dte_score, 
            "SE": self.se_score,
            "KI": self.ki_score,
            "LP": self.lp_score,
            "MA": self.ma_score
        }
```

### **🎯 Adaptive Route Recommendations**
```python
class AdaptiveRouting:
    def recommend_interventions(self, cognitive_metrics, behavior_patterns):
        """Suggest route adjustments based on cognitive development patterns"""
        
        recommendations = []
        
        # COP Score interventions
        if cognitive_metrics["COP"] < 0.6:
            recommendations.append({
                "intervention": "INCREASE_COGNITIVE_INTERVENTION_SENSITIVITY",
                "reason": "Student showing dependency patterns",
                "action": "Lower threshold for cognitive intervention triggers"
            })
        
        # DTE Score interventions  
        if cognitive_metrics["DTE"] < 0.5:
            recommendations.append({
                "intervention": "INCREASE_SOCRATIC_EXPLORATION", 
                "reason": "Shallow thinking patterns detected",
                "action": "Route more interactions through SOCRATIC_EXPLORATION"
            })
        
        # SE Score interventions
        if cognitive_metrics["SE"] < 0.6:
            recommendations.append({
                "intervention": "ADJUST_SCAFFOLDING_APPROACH",
                "reason": "Support not matching student needs",
                "action": "Modify SUPPORTIVE_SCAFFOLDING complexity level"
            })
        
        # LP Score interventions
        if cognitive_metrics["LP"] < 0.4:
            recommendations.append({
                "intervention": "INCREASE_FOUNDATIONAL_BUILDING",
                "reason": "Insufficient knowledge foundation",
                "action": "Route more basic concepts through FOUNDATIONAL_BUILDING"
            })
        
        return recommendations
```

---

## 🧠 **BEHAVIOR TRACKING INTEGRATION IN ROUTES**

### **Example: Enhanced COGNITIVE_INTERVENTION with Tracking**
```python
def execute_cognitive_intervention(user_input, behavior_tracker):
    # Log the intervention attempt
    behavior_tracker.log_intervention({
        "type": "COGNITIVE_OFFLOADING",
        "trigger": "Direct answer seeking detected",
        "user_message": user_input,
        "timestamp": datetime.now()
    })
    
    # Check intervention history
    recent_interventions = behavior_tracker.get_recent_interventions("COGNITIVE_OFFLOADING")
    
    if len(recent_interventions) > 2:
        # Escalate intervention strategy
        response = generate_stronger_intervention(user_input, recent_interventions)
    else:
        # Standard intervention
        response = generate_standard_intervention(user_input)
    
    # Track intervention effectiveness
    behavior_tracker.track_intervention_effectiveness(response)
    
    return response
```

### **Example: Enhanced SOCRATIC_EXPLORATION with Pattern Recognition**
```python
def execute_socratic_exploration(user_input, behavior_tracker, cognitive_state):
    # Adapt question complexity based on thinking patterns
    if cognitive_state.depth_thinking_pattern == "SHALLOW":
        question_complexity = "INCREASED"
        wait_time = "EXTENDED"
    else:
        question_complexity = "APPROPRIATE"
        wait_time = "STANDARD"
    
    # Track spatial reasoning development
    behavior_tracker.track_spatial_reasoning_engagement(user_input)
    
    # Generate contextual exploration
    response = generate_socratic_response(
        user_input=user_input,
        complexity_level=question_complexity,
        previous_explorations=behavior_tracker.get_exploration_history()
    )
    
    return response
```

---

## 📊 **COGNITIVE METRICS BY ROUTE**

### **Route → Primary Metric Optimization**:
- **TOPIC_TRANSITION** → KI Score (Knowledge Integration across topics)
- **KNOWLEDGE_ONLY** → Baseline knowledge transfer
- **SOCRATIC_EXPLORATION** → DTE Score (Deep Thinking Engagement)
- **COGNITIVE_CHALLENGE** → COP Score + DTE Score (Prevent offloading + Engagement)
- **MULTI_AGENT_COMPREHENSIVE** → MA Score (Metacognitive Awareness)
- **SOCRATIC_CLARIFICATION** → SE Score (Scaffolding Effectiveness)
- **SUPPORTIVE_SCAFFOLDING** → SE Score (Scaffolding Effectiveness) 
- **FOUNDATIONAL_BUILDING** → LP Score (Learning Progression)
- **KNOWLEDGE_WITH_CHALLENGE** → KI + DTE Scores (Integration + Deep Thinking)
- **BALANCED_GUIDANCE** → Balanced optimization across metrics
- **COGNITIVE_INTERVENTION** → COP Score (Cognitive Offloading Prevention)
- **ERROR/FALLBACK** → Maintain learning continuity

---

## 🎯 **KEY CORRECTIONS IMPLEMENTED**

### **✅ Route Consolidation**:
- **Merged DESIGN_GUIDANCE into SOCRATIC_EXPLORATION** - no redundancy
- **14 total routes** (removed duplicate functionality)

### **✅ Language Corrections**:
- **Removed "technical questions"** - now covers ALL types of questions
- **Questions can be about**: design concepts, spatial principles, user experience, cultural considerations, sustainability, materials, process methodology, precedents, theory

### **✅ Enhanced Behaviors**:
- **All routes** now have Study Mode-style interactive patterns
- **Multi-agent coordination** detailed for each route
- **Cognitive metrics optimization** aligned with research goals

This gives you the complete 14-route system with proper agent coordination and flexible question handling!