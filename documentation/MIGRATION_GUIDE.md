# Migration Guide: Original vs Enhanced Architectural Critique System

## 🎯 **Which System Should You Use?**

### **Use Original System When:**
- ✅ You need quick, simple analysis
- ✅ Limited computational resources
- ✅ Basic critique requirements
- ✅ Legacy system compatibility
- ✅ Learning/testing purposes

### **Use Enhanced System When:**
- ✅ Professional architectural analysis
- ✅ Comprehensive design evaluation
- ✅ Compliance checking required
- ✅ Detailed spatial analysis needed
- ✅ Cost estimation and prioritization
- ✅ Multiple analysis modes required

## 📊 **Feature Comparison**

| Feature | Original | Enhanced |
|---------|----------|----------|
| **Critique Categories** | 5 | 9 |
| **Analysis Modes** | 1 (General) | 6 (Interior, Exterior, Site Plan, etc.) |
| **Spatial Analysis** | Basic | Comprehensive with relationships |
| **Compliance Checking** | ❌ | ✅ |
| **Cost Estimation** | ❌ | ✅ |
| **Configuration Options** | Basic | Advanced with validation |
| **Visual Feedback** | Simple annotations | Interactive with metrics dashboard |
| **Performance** | Fast | More comprehensive but slower |
| **Resource Usage** | Low | Higher (GPU recommended) |

## 🚀 **Migration Path**

### **Step 1: Evaluate Your Needs**
```python
# Original system - Simple usage
from arch_critique_main import ArchitecturalCritiqueApp

app = ArchitecturalCritiqueApp()
app.load_image("image.jpg")
objects = app.detect_objects()
analysis = app.analyze_spatial_relationships()
critiques = app.generate_critique_points(analysis)
```

```python
# Enhanced system - Professional usage
from enhanced_architectural_critique import EnhancedArchitecturalCritiqueApp
from enhanced_config_manager import AnalysisMode

app = EnhancedArchitecturalCritiqueApp()
app.load_image("image.jpg")
objects = app.detect_objects()
app.segment_objects()
analysis = app.analyze_spatial_relationships()
critiques = app.generate_critique_points(analysis)
```

### **Step 2: Update Dependencies**
```bash
# For enhanced system
pip install -r requirements_enhanced.txt

# For original system
pip install -r requirements.txt
```

### **Step 3: Choose Web Interface**
```bash
# Original interface
python web_interface.py

# Enhanced interface
python enhanced_web_interface.py
```

## 🔧 **Configuration Migration**

### **Original Configuration**
```python
from config_manager import ConfigManager

config = ConfigManager()
config.update_model_config(confidence_threshold=0.5)
```

### **Enhanced Configuration**
```python
from enhanced_config_manager import EnhancedConfigManager, AnalysisMode

config = EnhancedConfigManager()
config.apply_analysis_mode(AnalysisMode.INTERIOR)
config.update_model_config(confidence_threshold=0.5)
config.update_critique_config(max_critique_points=15)
```

## 📈 **Performance Considerations**

### **Original System**
- **Memory**: ~2GB RAM
- **GPU**: Optional
- **Processing Time**: 10-30 seconds
- **Model Size**: ~50MB

### **Enhanced System**
- **Memory**: ~4-8GB RAM
- **GPU**: Recommended (CUDA)
- **Processing Time**: 30-90 seconds
- **Model Size**: ~2GB (including SAM)

## 🎨 **Output Differences**

### **Original Output**
```json
{
  "overall_score": 7.5,
  "critique_points": [
    {
      "category": "functional",
      "severity": 8,
      "title": "Circulation Issues",
      "description": "Poor circulation design"
    }
  ]
}
```

### **Enhanced Output**
```json
{
  "overall_score": 7.5,
  "design_metrics": {
    "circulation_efficiency": 0.85,
    "lighting_quality": 0.72,
    "accessibility_compliance": 0.91
  },
  "critique_points": [
    {
      "category": "circulation",
      "severity": 3,
      "title": "Circulation Issues",
      "description": "Poor circulation design",
      "impact_score": 0.75,
      "priority": 1,
      "estimated_cost": "Medium to High",
      "implementation_difficulty": "Medium"
    }
  ],
  "compliance_summary": {
    "overall_compliance_score": 0.85,
    "compliance_issues": []
  },
  "improvement_priorities": [...]
}
```

## 🔄 **Gradual Migration Strategy**

### **Phase 1: Parallel Testing**
- Run both systems on same images
- Compare outputs and performance
- Identify use cases for each

### **Phase 2: Feature Adoption**
- Start with enhanced system for new projects
- Keep original system for quick checks
- Gradually migrate existing workflows

### **Phase 3: Full Migration**
- Standardize on enhanced system
- Archive original system for reference
- Update documentation and training

## 🛠️ **Troubleshooting Migration**

### **Common Issues**

1. **Import Errors**
   ```python
   # Check which system you're importing
   from arch_critique_main import ArchitecturalCritiqueApp  # Original
   from enhanced_architectural_critique import EnhancedArchitecturalCritiqueApp  # Enhanced
   ```

2. **Configuration Conflicts**
   ```python
   # Use separate config files
   config_original = ConfigManager("config.json")
   config_enhanced = EnhancedConfigManager("enhanced_config.json")
   ```

3. **Model Loading Issues**
   ```bash
   # Ensure SAM model is available for enhanced system
   ls -la sam_vit_h_4b8939.pth
   ```

## 📞 **Support**

- **Original System Issues**: Check `README.md`
- **Enhanced System Issues**: Check `ENHANCED_README.md`
- **Migration Questions**: Create issue with "migration" label

---

**Remember**: Both systems serve different purposes. Choose based on your specific needs and requirements! 