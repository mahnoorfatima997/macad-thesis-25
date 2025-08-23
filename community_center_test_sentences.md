# Community Center Design Test Sentences

## 🎯 **ROUTING TEST SENTENCES**

### **1. PROGRESSIVE_OPENING** (First message)
- "I'm designing a community center in a converted warehouse"
- "My project is a new community center for a diverse neighborhood"
- "I need to create a community center that serves all ages"
- "I'm working on a community center in a cold climate"

### **2. KNOWLEDGE_ONLY** (Pure knowledge requests - NO gamification)
- "What are the best practices for circulation design in community centers?"
- "Can you guide me about how to create good circulation inside the building?"
- "What are ADA door width requirements for public buildings?"
- "Tell me about acoustic design principles for multi-use spaces"
- "What are the standard room sizes for community center programs?"
- "How do I calculate parking requirements for a community center?"
- "What are the fire safety requirements for assembly spaces?"
- "What materials work best for high-traffic community spaces?"

### **3. SOCRATIC_EXPLORATION** (Design thinking - MAY trigger gamification)
- "I'm exploring how natural light affects social interaction in community spaces"
- "I'm thinking about how courtyards might create different social dynamics"
- "I want to understand how ceiling height impacts the feeling of community"
- "I'm considering how color choices might influence user behavior"
- "I'm exploring the relationship between acoustics and social comfort"

### **4. SOCRATIC_CLARIFICATION** (Confusion - SHOULD trigger gamification)
- "I'm not sure how to balance privacy and openness in my design"
- "I'm confused about how to create flexible spaces that work for different activities"
- "I don't understand how to make spaces feel welcoming but not overwhelming"
- "I'm unclear about how to design for both children and elderly users"
- "I'm not sure how to handle the transition between quiet and active areas"

### **5. COGNITIVE_CHALLENGE** (Passive/overconfident - SHOULD trigger gamification)
- "That makes sense" (passive response)
- "OK" (low engagement)
- "I already know about accessibility design, what's next?"
- "This is pretty straightforward"
- "I've got this figured out"
- "Universal design is easy to implement"

### **6. MULTI_AGENT_COMPREHENSIVE** (Evaluation requests - SHOULD trigger gamification)
- "What do you think of my approach to creating flexible learning spaces?"
- "Can you evaluate my circulation strategy for the community center?"
- "How would you assess my design for intergenerational programming?"
- "What's your opinion on my approach to sustainable design?"
- "Can you give me feedback on my space planning strategy?"

### **7. KNOWLEDGE_WITH_CHALLENGE** (Advanced questions - SHOULD trigger gamification)
- "How do biophilic design principles apply to community center environments?"
- "What are the psychological impacts of different spatial configurations?"
- "How does evidence-based design inform community center planning?"
- "What are the cultural considerations for inclusive community design?"

### **8. SUPPORTIVE_SCAFFOLDING** (Help requests - NO gamification)
- "I need help understanding how to approach this design problem"
- "Can you help me break down this complex design challenge?"
- "I'm new to community center design and need guidance"
- "Can you walk me through the design process step by step?"

## 🎮 **GAMIFICATION TRIGGER TEST SENTENCES**

### **ROLE-PLAY TRIGGERS** (Should trigger persona games)
- "How would a visitor feel entering this space?"
- "How would an elderly person experience this layout?"
- "What would a child think about these play areas?"
- "How would a teenager feel in this social space?"
- "How would someone with mobility issues navigate this design?"
- "What would a parent with young children experience here?"

### **CREATIVE CONSTRAINT TRIGGERS** (Should trigger constraint games)
- "I'm completely stuck on this circulation problem"
- "I need fresh ideas for flexible programming spaces"
- "I'm having trouble with the acoustics in multi-use areas"
- "I need creative solutions for limited budget constraints"
- "I'm stuck on how to handle different user groups simultaneously"

### **DETECTIVE/MYSTERY TRIGGERS** (Should trigger mystery games)
- "Users seem to avoid the main entrance area"
- "People aren't using the social spaces as intended"
- "The community room feels uncomfortable but I don't know why"
- "There are circulation bottlenecks but I can't identify the cause"
- "The space feels unwelcoming but I can't pinpoint the issue"

### **PERSPECTIVE SHIFT TRIGGERS** (Should trigger wheel games)
- "I wonder what would happen if I changed the entrance location"
- "What if I approached this from a different angle?"
- "I'm curious about alternative layout strategies"
- "What would happen if I prioritized different user needs?"

### **LOW ENGAGEMENT TRIGGERS** (Should trigger engagement games)
- "ok"
- "sure"
- "yeah"
- "I guess"
- "whatever works"
- "fine"

### **OVERCONFIDENCE TRIGGERS** (Should trigger reality check games)
- "This design problem is pretty simple"
- "I've already figured out the best solution"
- "Community centers are straightforward to design"
- "I don't need to consider accessibility much"
- "Budget constraints won't affect my design"

## 🚫 **SHOULD NOT TRIGGER GAMIFICATION**

### **Design Exploration Questions** (Should get direct guidance)
- "I am thinking about creating nooks around the building that will serve as a transitional space"
- "How should I approach designing flexible learning spaces?"
- "What would be the best way to organize spaces considering user flow?"
- "I'm considering different approaches to wayfinding design"
- "I'm thinking about how to integrate outdoor and indoor spaces"

### **Technical Questions** (Should get direct answers)
- "What are the code requirements for emergency exits?"
- "How do I calculate HVAC loads for assembly spaces?"
- "What are the structural requirements for large span spaces?"
- "What are the lighting standards for different activity areas?"

### **Best Practices Questions** (Should get direct guidance)
- "What are the best practices for inclusive design?"
- "How do successful community centers handle programming conflicts?"
- "What are proven strategies for creating welcoming entrances?"
- "What works well for flexible furniture systems?"

## 📋 **TESTING PROTOCOL**

### **Step 1: Test Routes**
1. Start fresh conversation
2. Use a progressive opening sentence
3. Follow with sentences from each route category
4. Note which route is taken for each

### **Step 2: Test Gamification Triggers**
1. Use setup context (mention community center project)
2. Try each gamification trigger sentence
3. Note if gamification activates and what type

### **Step 3: Test Non-Triggers**
1. Use design exploration questions
2. Verify they DON'T trigger gamification
3. Confirm they get direct, helpful responses

### **Step 4: Test Error Handling**
1. Try edge cases and unusual inputs
2. Verify no crashes or error messages
3. Confirm graceful fallbacks work

## 🎯 **EXPECTED RESULTS**

- **Knowledge requests** → `knowledge_only` route, no gamification
- **Design exploration** → `socratic_exploration` route, no gamification  
- **Confusion** → `socratic_clarification` route, with gamification
- **Passive responses** → `cognitive_challenge` route, with gamification
- **Role-play questions** → Appropriate route with persona games
- **Technical questions** → `knowledge_only` route, no gamification

Use this list systematically to verify that your routing and gamification system is working correctly!
