# 🎮 Gamification UI Component Tester

A standalone test script for previewing and interacting with all gamification UI components from `dashboard/ui/enhanced_gamification.py` without running the full mentor.py application.

## 🚀 Quick Start

```bash
# Run the standalone test script
streamlit run test_gamification.py
```

The test app will open in your browser at `http://localhost:8501`

## 📋 Features

### 🎯 **Complete Component Testing**
- **Persona Challenge Game**: Test role-playing scenarios with different user personas
- **Perspective Wheel Game**: Test the spinning wheel with random perspective challenges  
- **Mystery Investigation Game**: Test detective-style problem-solving challenges
- **Constraint Puzzle Game**: Test creative constraint-based design challenges

### 🛠️ **Interactive Controls**
- **Building Type Selector**: Test with different building types (community center, library, school, etc.)
- **Theme Preview**: Visual preview of all thesis color themes
- **Reset Functionality**: Clear all game states and start fresh
- **Debug Dashboard**: Monitor session state and game data in real-time

### 🎨 **Visual Consistency**
- Uses the same styling and themes as the main mentor.py application
- Maintains thesis color palette throughout all components
- Responsive design that works on different screen sizes

### 🔍 **Debug Features**
- **Session State Monitoring**: See how each game stores and updates its state
- **Performance Metrics**: Monitor rendering performance and memory usage
- **Error Handling**: Graceful error display with detailed exception information
- **Configuration Inspection**: View theme data and renderer settings

## 📖 How to Use

### 1. **Navigation**
- Use the **sidebar** to select building types and access controls
- Use the **tabs** to switch between different gamification components
- Use the **Debug Dashboard** tab to monitor all game states

### 2. **Testing Workflow**
1. Select a building type from the sidebar
2. Navigate to a component tab (Persona, Wheel, Mystery, or Constraint)
3. Interact with the gamification elements (buttons, text inputs, etc.)
4. Check the Debug Dashboard to see how state changes
5. Use the Reset button to clear states and test again

### 3. **What to Test**
- ✅ **Visual Styling**: Ensure colors, fonts, and layouts match the main app
- ✅ **Interactions**: Test all buttons, inputs, and interactive elements
- ✅ **State Management**: Verify that game progress is tracked correctly
- ✅ **Responsiveness**: Test on different screen sizes
- ✅ **Error Handling**: Try edge cases and invalid inputs

## 🎮 Component Details

### **Persona Challenge**
- Tests user persona selection and role-playing scenarios
- Includes persona cards with descriptions and missions
- Interactive text input for user responses
- Point tracking and progress display

### **Perspective Wheel**
- Tests the spinning wheel mechanism with random perspectives
- Multiple perspective options (Child's View, Elder's View, etc.)
- Interactive challenge responses
- Spin counter and point system

### **Mystery Investigation**
- Tests detective-style problem-solving interface
- Clue discovery and evidence collection
- Interactive investigation steps
- Mystery solving with feedback

### **Constraint Puzzle**
- Tests creative constraint challenge interface
- Multiple constraint scenarios
- Interactive constraint selection
- Creative solution input and evaluation

## 🔧 Technical Details

### **Dependencies**
- Streamlit (for the web interface)
- The gamification module from `dashboard/ui/enhanced_gamification.py`
- Standard Python libraries (sys, os, typing)

### **File Structure**
```
test_gamification.py          # Main test script
README_gamification_test.md   # This documentation
dashboard/ui/enhanced_gamification.py  # Source gamification module
```

### **Session State Management**
The test script maintains separate session states for each game component:
- `persona_*`: Persona challenge states
- `wheel_*`: Perspective wheel states  
- `mystery_*`: Mystery investigation states
- `constraint_*`: Constraint puzzle states

## 🐛 Troubleshooting

### **Import Errors**
If you get import errors, ensure you're running the script from the project root directory where the `dashboard` folder is located.

### **Missing Components**
If certain gamification components don't render, check the Debug Dashboard for error messages and session state information.

### **Performance Issues**
Use the Performance Metrics section in the Debug Dashboard to monitor rendering times and memory usage.

## 🎯 Testing Checklist

- [ ] All four gamification components render without errors
- [ ] Interactive elements (buttons, inputs) work correctly
- [ ] State management persists across interactions
- [ ] Visual styling matches the main application
- [ ] Theme colors are consistent with thesis palette
- [ ] Reset functionality clears all states properly
- [ ] Debug information displays correctly
- [ ] Performance is acceptable (< 100ms render times)

## 📝 Notes

This test script is designed to be a comprehensive testing environment for the gamification UI components. It simulates the same data structures and interactions that the main mentor.py application would provide, allowing for isolated testing and debugging of the gamification system.

The script is particularly useful for:
- UI/UX refinement and testing
- Debugging state management issues
- Performance optimization
- Visual consistency verification
- Component integration testing
