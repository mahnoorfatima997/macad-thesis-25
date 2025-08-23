# 🎮 Gamification Trigger Guide for mentor.py

This guide provides specific user inputs that will trigger each gamification game in mentor.py conversations. Use these examples to test the interactive games during actual design conversations.

## 🎯 How Gamification is Triggered

The gamification system is triggered based on:
1. **User intent detection** - Specific keywords and phrases in user messages
2. **Conversation context** - Current design phase and discussion topics  
3. **Cognitive enhancement needs** - When the system detects opportunities for deeper thinking
4. **Challenge type mapping** - Different inputs map to different game types

---

## 👤 Persona Challenge Game

**Triggers when:** User wants to understand different user perspectives or experiences

### Example User Inputs:
```
"I want to understand how different users experience my community center"
"How would a child versus an adult see this space?"
"What would it feel like to be a visitor in this building?"
"Help me think about user perspectives"
"I need to consider different viewpoints on my design"
"How do elderly people navigate my building differently?"
"What's the experience like for someone with mobility issues?"
"I want to role-play as different users of my space"
"How does my design feel from a teenager's perspective?"
"What would a parent with young children think about this layout?"
```

**Game Features:**
- Select from different user personas (Parent, Teen, Senior, etc.)
- Experience the space from their perspective
- Record insights and observations
- Earn points for thoughtful responses

---

## 🎯 Perspective Wheel Game

**Triggers when:** User seeks alternative approaches or fresh perspectives

### Example User Inputs:
```
"What are some alternative approaches to this design problem?"
"I'm stuck - can you suggest different ways to think about this?"
"Show me other perspectives on this architectural challenge"
"What if I approached this completely differently?"
"I need fresh ideas for my design"
"Help me see this from a new angle"
"What are some unconventional solutions?"
"I want to challenge my assumptions"
"Give me a different way to look at this problem"
"What would happen if I flipped my approach?"
```

**Game Features:**
- Spin wheel to get random perspectives (Child's View, Artist's View, etc.)
- Each perspective provides unique challenges
- Record insights from different viewpoints
- Multiple spins for varied perspectives

---

## 🔍 Mystery Investigation Game

**Triggers when:** User notices problems but can't identify the cause

### Example User Inputs:
```
"Why do people keep avoiding the main entrance?"
"I notice users behaving strangely in this space - why?"
"Something isn't working in my design but I can't figure out what"
"Help me investigate what's wrong with this space"
"I need to understand the underlying issues in my building"
"People seem uncomfortable in this area - what's causing it?"
"There's a problem with circulation but I can't pinpoint it"
"Users aren't using the space as intended - why?"
"Something feels off about this design but I can't identify it"
"Help me solve this design mystery"
```

**Game Features:**
- Investigate clues about design problems
- Distinguish between important clues and red herrings
- Submit hypothesis about the root cause
- Reveal solution after investigation

---

## 🧩 Constraint Puzzle Game

**Triggers when:** User faces design limitations or resource constraints

### Example User Inputs:
```
"My budget just got cut in half - what do I do?"
"The site has major limitations - how do I work with them?"
"I have too many requirements and not enough space"
"Help me solve this design problem with limited resources"
"I need creative solutions for these constraints"
"The zoning restrictions are really limiting my options"
"How do I design with such a tight budget?"
"The site floods regularly - how do I deal with this?"
"I need to fit twice as many people in the same space"
"The building codes are really restrictive here"
```

**Game Features:**
- Select up to 3 active constraints (Budget Cut, Time Crunch, Site Issues, etc.)
- Develop creative solutions within limitations
- Points based on number of constraints tackled
- Constraint-specific challenges and prompts

---

## 📚 Storytelling Challenge Game

**Triggers when:** User wants to explore narrative aspects of their design

### Example User Inputs:
```
"What story does my building tell?"
"How do I create a narrative through my spaces?"
"I want my building to have a clear spatial sequence"
"Help me think about the user journey through my design"
"How can architecture tell stories?"
"What's the narrative arc of moving through my building?"
"I want to create a sense of progression in my design"
"How do I choreograph the user experience?"
"What emotional journey should people have in my space?"
"Help me design a spatial story"
```

**Game Features:**
- Progress through story chapters (dawn, morning, midday, evening)
- Continue the narrative of your building
- Explore different times and scenarios
- Build a complete spatial story

---

## ⏰ Time Travel Challenge Game

**Triggers when:** User considers temporal aspects of their design

### Example User Inputs:
```
"How will my building age over time?"
"What did this site look like 20 years ago?"
"How should I design for future changes?"
"I want to understand the temporal aspects of my design"
"How does time affect architectural spaces?"
"What will this building be like in 50 years?"
"How do I design for adaptability over time?"
"What's the lifecycle of this building?"
"How has this neighborhood changed over the decades?"
"I need to consider the building's evolution"
```

**Game Features:**
- Travel between Past, Present, and Future
- Explore how your building changes over time
- Record temporal insights and observations
- Consider long-term adaptability

---

## 🏗️ Transformation Challenge Game

**Triggers when:** User needs flexible or adaptive spaces

### Example User Inputs:
```
"My building needs to adapt to different uses"
"How can I design flexible spaces?"
"The program keeps changing - how do I accommodate this?"
"I need spaces that can transform based on needs"
"Help me design for adaptability and change"
"How do I create multi-use spaces?"
"The building needs to serve different functions at different times"
"I want spaces that can evolve with user needs"
"How do I design for maximum flexibility?"
"The program requirements keep shifting"
```

**Game Features:**
- Choose transformation types (Adaptive, Seasonal, Functional, Community)
- Describe how spaces transform and why
- Explore different adaptation scenarios
- Track evolution of your design

---

## 🎮 Testing Tips

### For Best Results:
1. **Start conversations naturally** - Don't just paste trigger phrases
2. **Provide context** - Mention your building type and design challenges
3. **Be specific** - The more detailed your problem, the better the game response
4. **Engage fully** - Complete the games for the best learning experience

### Example Conversation Flow:
```
User: "I'm designing a community center for a diverse neighborhood. I'm struggling with the main entrance - people seem to avoid it and use the side doors instead. I can't figure out why this is happening."

[This would trigger the Mystery Investigation Game]
```

### Building Types That Work Well:
- Community centers
- Libraries  
- Schools
- Museums
- Hospitals
- Office buildings
- Residential complexes
- Cultural centers

---

## 🔧 Troubleshooting

**If games don't trigger:**
- Make sure you're in a design conversation context
- Mention specific design challenges or problems
- Use more descriptive language about your struggles
- Try combining multiple trigger phrases

**If you get the wrong game:**
- Be more specific about what type of help you need
- Use keywords from the specific game you want
- Provide more context about your design situation

---

## 📊 Game Compatibility

All games work with the **gamification_visualizer.py** script for testing and enhancement. Use that tool to:
- Preview games before triggering them in conversations
- Customize game content and themes
- Test visual enhancements
- Export custom configurations

**Happy gaming! 🎮**
