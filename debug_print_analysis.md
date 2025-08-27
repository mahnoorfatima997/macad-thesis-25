# DEBUG PRINT ANALYSIS - FILES WITH EXCESSIVE PRINTS

Based on terminal analysis, here are the main files generating excessive debug prints:

## **HIGH PRIORITY - COMMENT THESE:**

### **1. thesis-agents/orchestration/orchestrator.py**
- `🔍 ORCHESTRATOR DEBUG: Phase progress data`
- `🔍 ORCHESTRATOR DEBUG: Current phase progress`
- `🔍 ORCHESTRATOR DEBUG: Completion percent`
- `🎮 ORCHESTRATOR: Found gamification metadata`
- Multiple INFO logs for workflow steps

### **2. thesis-agents/agents/*/adapter.py files**
- `🔍 DEBUG: State building_type`
- `🔍 DEBUG: State current_design_brief`
- `🔍 DEBUG: State messages count`
- `🔍 DEBUG: Socratic tutor received state.*`
- `🔍 DEBUG: Routing path detected`
- `🔍 DEBUG: Building type extracted`

### **3. thesis-agents/agents/cognitive_enhancement/processors/challenge_generator.py**
- `🎮 STRATEGY: Transformation trigger detected`
- All the gamification trigger debug prints

### **4. dashboard/unified_dashboard.py**
- `🔍 DEBUG - Metadata keys`
- `🔍 DEBUG - Scientific metrics keys`
- `🔍 DEBUG - Cognitive state keys`
- `🎯 Dashboard: Routing path`
- `🤖 Dashboard: Agents used`

### **5. thesis-agents/utils/routing_decision_tree.py**
- `🎯 ROUTING DEBUG: Selected route`
- `🔧 FIXED: Updated classification`
- `🏗️ Updated project context`

### **6. Phase progression files**
- `🎯 PHASE PROGRESSION: Processing response`
- `📊 Current phase: ideation`
- `📈 Phase progress before/after`
- `🔢 Completed steps before/after`
- `🧮 CALCULATION:` lines
- `📈 FINAL COMPLETION:`

### **7. Question bank files**
- `🏦 QUESTION_BANK: Getting next question`
- `✅ Completed steps:`
- `🎯 Next step:`

### **8. Scientific metrics**
- All the scientific metrics calculation debug prints

### **9. Logging statements**
- All the `INFO:thesis_agents.*` logging statements
- `INFO:httpx:HTTP Request:` (can be reduced to ERROR level only)

## **MEDIUM PRIORITY:**

### **10. Conversation analysis**
- Conversation pattern analysis debug prints

### **11. Context generation**
- Context metadata generation prints

## **LOW PRIORITY (Keep for now):**

### **12. Error messages and warnings**
- Keep these for debugging actual issues

### **13. Final summary prints**
- Keep the orchestration summary and process summary (they're useful)

## **RECOMMENDATION:**

Comment out debug prints in files 1-9 above. This should reduce terminal output by ~80-90%.
