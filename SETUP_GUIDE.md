# Quick Setup Guide for Enhanced Image Processing

## 🚀 Getting Started

Your system has been enhanced with powerful image processing and generation capabilities! Here's how to get everything working:

## 1. Add Replicate API Key

To enable image generation, you need a Replicate API token:

1. **Get API Key**: 
   - Go to [replicate.com](https://replicate.com)
   - Sign up for an account
   - Go to your account settings and create an API token

2. **Add to Environment**:
   - Open your `.env` file
   - Replace the placeholder with your actual token:
   ```
   REPLICATE_API_TOKEN=r8_your_actual_token_here
   ```

## 2. Test the System

Run the test script to verify everything is working:

```bash
python test_image_generation.py
```

You should see all tests pass:
- ✅ Enhanced Image Analysis
- ✅ Replicate Integration  
- ✅ Phase System Integration
- ✅ Dashboard Integration
- ✅ Conversation Prompt Generation

## 3. Start the Dashboard

Launch your dashboard as usual:

```bash
streamlit run dashboard/unified_dashboard.py
```

## 🎨 What's New

### Enhanced Image Analysis
- **Much Better Understanding**: When you upload images, the system now provides incredibly detailed analysis
- **Comprehensive Descriptions**: The AI can now see and describe architectural elements, spatial relationships, and design concepts in much greater detail

### Automatic Image Generation
- **Phase Transitions**: When you complete a design phase, the system automatically generates a visualization of your ideas
- **Three Styles**:
  - **Ideation**: Rough, hand-drawn conceptual sketches
  - **Visualization**: Clean architectural form studies
  - **Materialization**: Detailed, photorealistic renderings

### Interactive Feedback
- **Rate Generated Images**: Tell the system if the generated images match your thinking
- **Improve Over Time**: Your feedback helps the system learn and improve

## 🔧 Troubleshooting

### Image Generation Not Working?
1. **Check API Key**: Make sure your `REPLICATE_API_TOKEN` is set correctly in `.env`
2. **Check Balance**: Ensure your Replicate account has sufficient credits
3. **Check Logs**: Look at the console output for detailed error messages

### Images Not Displaying?
1. **Internet Connection**: Generated images are served from Replicate's servers
2. **Browser Issues**: Try refreshing the page or clearing browser cache
3. **Firewall**: Ensure your firewall allows connections to Replicate's image servers

### System Running Slowly?
- **Normal Behavior**: Image generation takes 30-60 seconds - this is normal
- **Background Processing**: The system continues working while images generate
- **Timeout Protection**: Images will timeout after 5 minutes if generation fails

## 💡 Tips for Best Results

### For Better Image Analysis
- **High Quality Images**: Upload clear, well-lit images for best analysis
- **Architectural Drawings**: The system works best with architectural plans, sections, and sketches
- **Context Matters**: Provide context about your project for more relevant analysis

### For Better Image Generation
- **Detailed Conversations**: The more you describe your design ideas, the better the generated images
- **Specific Language**: Use architectural terminology when discussing your project
- **Iterative Process**: Generated images improve as you progress through phases

## 🎯 Using the New Features

### During Normal Design Work
1. **Upload Images**: Upload your sketches and drawings as usual
2. **Get Enhanced Analysis**: Receive much more detailed feedback about your designs
3. **Progress Through Phases**: Work through ideation, visualization, and materialization
4. **Automatic Visualizations**: Get generated images when transitioning between phases
5. **Provide Feedback**: Rate the generated images to help improve the system

### Understanding Generated Images
- **Ideation Images**: Rough sketches showing basic spatial concepts
- **Visualization Images**: Cleaner form studies showing spatial organization
- **Materialization Images**: Detailed renderings showing materials and construction

## 📞 Support

If you encounter any issues:

1. **Check the Console**: Look for error messages in the terminal where you started the dashboard
2. **Run Tests**: Use `python test_image_generation.py` to diagnose issues
3. **Check Configuration**: Verify your `.env` file has the correct API keys
4. **Review Logs**: The system provides detailed logging for troubleshooting

## 🎉 Enjoy Your Enhanced System!

Your architectural mentoring system now has powerful AI-driven image processing and generation capabilities. The system will help you better understand your design ideas and provide visual feedback throughout your design journey.

Remember: All existing functionality remains exactly the same - these are pure enhancements that make your design process even better!
