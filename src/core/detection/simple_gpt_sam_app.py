#!/usr/bin/env python3
"""
Simple GPT Vision + SAM App
Uses GPT Vision to analyze architectural images and provide coordinates directly to SAM for segmentation
"""

import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image
import tempfile
import json
from datetime import datetime
import base64
import re

# Import required modules
from sam2_module_fixed import SAM2Segmenter

# Import OpenAI for GPT Vision
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.error("OpenAI not available. Install with: pip install openai")

# Configure Streamlit page
st.set_page_config(
    page_title="🏗️ Simple AI Architectural Analyzer",
    page_icon="🏗️",
    layout="wide"
)

class SimpleGPTVisionAnalyzer:
    """Simple analyzer that uses GPT Vision to get coordinates and SAM to segment"""
    
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.sam = SAM2Segmenter(model_name="facebook/sam-vit-base")
        print("✅ Simple GPT Vision + SAM analyzer initialized")
    
    def encode_image(self, image_path):
        """Encode image to base64 for GPT Vision"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_with_coordinates(self, image_path):
        """Use GPT Vision to analyze image and get precise coordinates"""
        
        # Get image dimensions
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        
        base64_image = self.encode_image(image_path)
        
        # Prompt GPT Vision to provide coordinates
        prompt = f"""
        Analyze this architectural image ({width}x{height} pixels) and provide precise coordinates for segmentation.
        
        You are an expert architectural analyst. Identify all rooms, doors, windows, and architectural elements.
        
        For each element you identify, provide:
        1. Exact bounding box coordinates [x1, y1, x2, y2] in pixels
        2. Element type (room, door, window, wall, etc.)
        3. Description of what you see
        4. Confidence level (0.0-1.0)
        
        COORDINATE SYSTEM:
        - Origin (0,0) is top-left corner
        - X increases rightward (0 to {width})
        - Y increases downward (0 to {height})
        
        Return ONLY a valid JSON object with this structure:
        {{
            "image_dimensions": {{"width": {width}, "height": {height}}},
            "analysis_confidence": 0.9,
            "spatial_elements": [
                {{
                    "type": "room",
                    "label": "living_room",
                    "description": "Large rectangular living space in center",
                    "bounding_box": [120, 80, 450, 280],
                    "center_point": [285, 180],
                    "coordinate_confidence": 0.9,
                    "area_pixels": 92400,
                    "visual_evidence": "clearly defined by wall boundaries"
                }},
                {{
                    "type": "door",
                    "label": "main_entrance",
                    "description": "Entry door on south wall",
                    "bounding_box": [200, 340, 240, 380],
                    "center_point": [220, 360],
                    "coordinate_confidence": 0.85,
                    "visual_evidence": "break in wall line with door symbol"
                }}
            ],
            "spatial_narrative": "Detailed description of the layout and spatial relationships",
            "circulation_analysis": {{
                "primary_path": "foyer -> living_room -> kitchen",
                "secondary_paths": ["living_room -> bedrooms"],
                "bottlenecks": ["narrow hallway"]
            }},
            "design_insights": {{
                "strengths": ["open living area", "good natural light"],
                "issues": ["small bedrooms", "narrow circulation"],
                "suggestions": ["enlarge master bedroom", "widen hallway"]
            }}
        }}
        
        Be as precise as possible with coordinates. Ensure all coordinates are within the image bounds.
        IMPORTANT: Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            print(f"🔍 GPT Vision response length: {len(content)} characters")
            
            # Try to extract JSON
            json_result = self._extract_json_from_response(content)
            if json_result:
                return json_result
            
            # If JSON extraction fails, create fallback response
            print("🔄 Creating fallback response from text...")
            return self._create_fallback_from_text(content, width, height)
                
        except Exception as e:
            print(f"❌ GPT Vision API error: {e}")
            return self._create_error_response(width, height, str(e))
    
    def _extract_json_from_response(self, content):
        """Extract JSON from GPT response using multiple strategies"""
        
        # Strategy 1: Direct JSON extraction with regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                json_result = json.loads(json_str)
                print("✅ JSON extracted successfully")
                return json_result
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                # Try to fix common JSON issues
                try:
                    fixed_json = self._fix_common_json_issues(json_str)
                    json_result = json.loads(fixed_json)
                    print("✅ JSON fixed and parsed successfully")
                    return json_result
                except:
                    print("❌ Could not fix JSON automatically")
        
        # Strategy 2: Extract from code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
            try:
                json_result = json.loads(json_str)
                print("✅ JSON extracted from code block")
                return json_result
            except json.JSONDecodeError:
                print("❌ JSON in code block is invalid")
        
        return None
    
    def _fix_common_json_issues(self, json_str):
        """Fix common JSON formatting issues"""
        # Remove trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        return json_str
    
    def _create_fallback_from_text(self, content, width, height):
        """Create fallback response from text content"""
        return {
            "image_dimensions": {"width": width, "height": height},
            "analysis_confidence": 0.6,
            "spatial_elements": [
                {
                    "type": "room",
                    "label": "general_space",
                    "description": "General architectural space",
                    "bounding_box": [0, 0, width, height],
                    "center_point": [width//2, height//2],
                    "coordinate_confidence": 0.5,
                    "area_pixels": width * height,
                    "visual_evidence": "fallback analysis"
                }
            ],
            "spatial_narrative": content[:500] + "..." if len(content) > 500 else content,
            "circulation_analysis": {
                "primary_path": "unknown",
                "secondary_paths": [],
                "bottlenecks": []
            },
            "design_insights": {
                "strengths": ["Layout detected"],
                "issues": ["Unable to provide detailed analysis"],
                "suggestions": ["Consider uploading a clearer image"]
            },
            "analysis_method": "text_fallback"
        }
    
    def _create_error_response(self, width, height, error_msg):
        """Create error response"""
        return {
            "image_dimensions": {"width": width, "height": height},
            "analysis_confidence": 0.3,
            "spatial_elements": [
                {
                    "type": "room",
                    "label": "error_space",
                    "description": "Error in analysis",
                    "bounding_box": [0, 0, width, height],
                    "center_point": [width//2, height//2],
                    "coordinate_confidence": 0.3,
                    "area_pixels": width * height,
                    "visual_evidence": "error analysis"
                }
            ],
            "spatial_narrative": f"Error in analysis: {error_msg}",
            "circulation_analysis": {
                "primary_path": "unknown",
                "secondary_paths": [],
                "bottlenecks": []
            },
            "design_insights": {
                "strengths": [],
                "issues": [f"Analysis failed: {error_msg}"],
                "suggestions": ["Check your API key and try again"]
            },
            "analysis_method": "error_fallback"
        }
    
    def segment_with_sam(self, image_path, gpt_analysis):
        """Use SAM to segment based on GPT Vision coordinates"""
        
        spatial_elements = gpt_analysis.get("spatial_elements", [])
        
        if not spatial_elements:
            return {"error": "No spatial elements to segment"}
        
        # Extract bounding boxes from GPT analysis
        boxes = []
        labels = []
        
        for element in spatial_elements:
            bbox = element.get("bounding_box", [])
            label = element.get("label", "")
            confidence = element.get("coordinate_confidence", 0)
            
            if len(bbox) == 4 and confidence > 0.3:  # Filter low confidence detections
                boxes.append(bbox)
                labels.append(label)
        
        if not boxes:
            return {"error": "No valid bounding boxes for segmentation"}
        
        print(f"🎨 Creating SAM segments for {len(boxes)} elements")
        
        # Run SAM segmentation
        try:
            segmentation_results = self.sam.segment_image(image_path, boxes=boxes)
            return {
                "segments": segmentation_results.get("segments", []),
                "num_segments": len(boxes),
                "detection_labels": labels,
                "gpt_analysis": gpt_analysis
            }
        except Exception as e:
            print(f"❌ SAM segmentation error: {e}")
            return {"error": f"SAM segmentation failed: {e}"}
    
    def create_visualization(self, image_path, gpt_analysis, sam_results):
        """Create visualization of GPT analysis and SAM segmentation"""
        
        # Load the original image
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Could not load image for visualization")
            return None
        
        # Create a copy for visualization
        viz_image = image.copy()
        height, width = viz_image.shape[:2]
        
        # Colors for different element types
        colors = {
            "room": (0, 255, 0),      # Green
            "door": (255, 0, 0),      # Red
            "window": (0, 0, 255),    # Blue
            "wall": (255, 255, 0),    # Cyan
            "kitchen": (255, 0, 255), # Magenta
            "bathroom": (0, 255, 255), # Yellow
            "bedroom": (128, 0, 128),  # Purple
            "living_room": (0, 128, 0), # Dark Green
            "dining_room": (128, 128, 0), # Olive
            "default": (255, 255, 255)  # White
        }
        
        # Draw GPT Vision spatial elements
        spatial_elements = gpt_analysis.get("spatial_elements", [])
        for element in spatial_elements:
            element_type = element.get("type", "default")
            bbox = element.get("bounding_box", [])
            label = element.get("label", "")
            confidence = element.get("coordinate_confidence", 0)
            
            if len(bbox) == 4:
                x1, y1, x2, y2 = map(int, bbox)
                color = colors.get(element_type, colors["default"])
                
                # Draw bounding box
                cv2.rectangle(viz_image, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label_text = f"{label} ({confidence:.2f})"
                font_scale = 0.6
                thickness = 1
                font = cv2.FONT_HERSHEY_SIMPLEX
                
                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
                
                # Draw background rectangle for text
                cv2.rectangle(viz_image, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
                
                # Draw text
                cv2.putText(viz_image, label_text, (x1, y1 - 5), font, font_scale, (0, 0, 0), thickness)
        
        # Draw SAM segmentation masks (if available)
        if "segments" in sam_results:
            segments = sam_results["segments"]
            for i, segment in enumerate(segments):
                mask = segment.get("mask")
                label = segment.get("label", f"segment_{i}")
                
                if mask is not None and len(mask.shape) == 2:
                    # Create colored mask
                    colored_mask = np.zeros_like(viz_image)
                    color = colors.get(label.lower(), colors["default"])
                    colored_mask[mask > 0] = color
                    
                    # Blend with original image
                    alpha = 0.3
                    viz_image = cv2.addWeighted(viz_image, 1 - alpha, colored_mask, alpha, 0)
                    
                    # Draw contour
                    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        cv2.drawContours(viz_image, contours, -1, color, 2)
        
        # Add legend
        legend_y = 30
        legend_x = width - 200
        
        # Draw legend background
        cv2.rectangle(viz_image, (legend_x - 10, legend_y - 20), (legend_x + 180, legend_y + 200), (0, 0, 0), -1)
        cv2.rectangle(viz_image, (legend_x - 10, legend_y - 20), (legend_x + 180, legend_y + 200), (255, 255, 255), 2)
        
        # Add legend text
        legend_items = [
            ("GPT Vision", colors["default"]),
            ("Room", colors["room"]),
            ("Door", colors["door"]),
            ("Window", colors["window"]),
            ("Kitchen", colors["kitchen"]),
            ("Bathroom", colors["bathroom"])
        ]
        
        for i, (text, color) in enumerate(legend_items):
            y_pos = legend_y + i * 25
            cv2.rectangle(viz_image, (legend_x, y_pos - 15), (legend_x + 15, y_pos), color, -1)
            cv2.putText(viz_image, text, (legend_x + 20, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add analysis summary
        summary_text = f"GPT Elements: {len(spatial_elements)} | SAM Segments: {len(sam_results.get('segments', []))}"
        cv2.putText(viz_image, summary_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(viz_image, summary_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        
        return viz_image

def main():
    """Main Streamlit application"""
    
    st.title("🏗️ Simple AI Architectural Analyzer")
    st.markdown("**Powered by GPT Vision + SAM - Direct coordinate analysis**")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key handling
        st.subheader("🔑 OpenAI API Key")
        env_api_key = os.getenv("OPENAI_API_KEY")
        
        if env_api_key:
            st.success("✅ API key loaded from environment")
            api_key = env_api_key
        else:
            api_key = st.text_input(
                "Enter your OpenAI API Key:",
                type="password",
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            
            if not api_key:
                st.warning("⚠️ Please set OPENAI_API_KEY or enter your API key")
        
        # Model status
        if api_key:
            st.subheader("🤖 System Status")
            try:
                analyzer = SimpleGPTVisionAnalyzer(api_key)
                st.success("✅ GPT Vision: Ready")
                st.success("✅ SAM: Ready")
            except Exception as e:
                st.error(f"❌ System Error: {e}")
        
        # Pipeline information
        st.subheader("🔄 Simple Pipeline")
        st.markdown("""
        **Step 1**: 🧠 GPT Vision analyzes image and provides coordinates
        
        **Step 2**: 🎨 SAM segments based on GPT coordinates
        
        **Step 3**: 📊 Display results and insights
        """)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Your Design")
        uploaded_file = st.file_uploader(
            "Choose an architectural drawing or floor plan",
            type=['png', 'jpg', 'jpeg'],
            help="Upload floor plans, elevations, or architectural sketches"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Design", use_container_width=True)
            
            # Image info
            width, height = image.size
            st.info(f"📐 Image dimensions: {width} × {height} pixels")
    
    with col2:
        st.header("🤖 AI Analysis")
        
        if uploaded_file and api_key:
            try:
                analyzer = SimpleGPTVisionAnalyzer(api_key)
                
                if st.button("🚀 Analyze Design", type="primary", help="Run AI analysis"):
                    
                    # Save uploaded image temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        image.save(tmp_file.name)
                        temp_image_path = tmp_file.name
                    
                    try:
                        # Run analysis
                        with st.spinner("🧠 Running AI analysis... This may take 30-60 seconds"):
                            progress_bar = st.progress(0)
                            
                            # Step 1: GPT Vision analysis
                            progress_bar.progress(30)
                            st.caption("Analyzing with GPT Vision...")
                            
                            gpt_analysis = analyzer.analyze_with_coordinates(temp_image_path)
                            
                            # Step 2: SAM segmentation
                            progress_bar.progress(70)
                            st.caption("Segmenting with SAM...")
                            
                            sam_results = analyzer.segment_with_sam(temp_image_path, gpt_analysis)
                            
                            progress_bar.progress(100)
                            st.caption("Analysis complete!")
                        
                        # Store results in session state
                        st.session_state['gpt_analysis'] = gpt_analysis
                        st.session_state['sam_results'] = sam_results
                        st.session_state['analyzed_image'] = image
                        st.session_state['temp_image_path'] = temp_image_path
                        
                        st.success("✅ Analysis Complete!")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
                
            except Exception as e:
                st.error(f"❌ Failed to initialize analyzer: {e}")
        
        elif uploaded_file and not api_key:
            st.info("👆 Enter your OpenAI API key to analyze your design")
        else:
            st.info("👆 Upload a design image to start AI analysis")
    
    # Display results if available
    if 'gpt_analysis' in st.session_state and 'sam_results' in st.session_state:
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        gpt_analysis = st.session_state['gpt_analysis']
        sam_results = st.session_state['sam_results']
        analyzed_image = st.session_state['analyzed_image']
        temp_image_path = st.session_state['temp_image_path']
        
        # Create visualization
        try:
            analyzer = SimpleGPTVisionAnalyzer(api_key)
            viz_image = analyzer.create_visualization(temp_image_path, gpt_analysis, sam_results)
            
            if viz_image is not None:
                # Convert to RGB for Streamlit
                viz_rgb = cv2.cvtColor(viz_image, cv2.COLOR_BGR2RGB)
                st.image(viz_rgb, caption="AI Analysis Visualization", use_container_width=True)
            else:
                st.warning("Could not create visualization")
        except Exception as e:
            st.error(f"Visualization error: {e}")
        
        # Display GPT Analysis
        st.subheader("🧠 GPT Vision Analysis")
        
        if "error" in gpt_analysis:
            st.error(f"❌ Analysis Error: {gpt_analysis['error']}")
        else:
            # Basic metrics
            spatial_elements = gpt_analysis.get("spatial_elements", [])
            analysis_confidence = gpt_analysis.get("analysis_confidence", 0)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rooms = [e for e in spatial_elements if e.get("type") == "room"]
                st.metric("🏠 Rooms Found", len(rooms))
            
            with col2:
                doors = [e for e in spatial_elements if e.get("type") == "door"]
                st.metric("🚪 Doors/Openings", len(doors))
            
            with col3:
                windows = [e for e in spatial_elements if e.get("type") == "window"]
                st.metric("🪟 Windows", len(windows))
            
            with col4:
                st.metric("🎯 AI Confidence", f"{analysis_confidence:.1%}")
            
            # Spatial narrative
            spatial_narrative = gpt_analysis.get("spatial_narrative", "")
            if spatial_narrative:
                st.markdown("### 📍 Spatial Analysis")
                st.write(spatial_narrative)
            
            # Design insights
            design_insights = gpt_analysis.get("design_insights", {})
            if design_insights:
                st.markdown("### 💡 Design Insights")
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown("**✅ Strengths**")
                    strengths = design_insights.get("strengths", [])
                    for strength in strengths:
                        st.write(f"• {strength}")
                
                with col_b:
                    st.markdown("**⚠️ Issues**")
                    issues = design_insights.get("issues", [])
                    for issue in issues:
                        st.write(f"• {issue}")
                
                with col_c:
                    st.markdown("**💡 Suggestions**")
                    suggestions = design_insights.get("suggestions", [])
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
            
            # Detailed elements
            if spatial_elements:
                st.markdown("### 📍 Detected Elements")
                
                for i, element in enumerate(spatial_elements):
                    with st.expander(f"{element.get('type', 'element').title()}: {element.get('label', f'Element {i+1}')}", expanded=False):
                        col_x, col_y = st.columns([2, 1])
                        
                        with col_x:
                            st.write(f"**Description**: {element.get('description', 'No description')}")
                            st.write(f"**Confidence**: {element.get('coordinate_confidence', 0):.1%}")
                            st.write(f"**Visual Evidence**: {element.get('visual_evidence', 'Not specified')}")
                        
                        with col_y:
                            bbox = element.get("bounding_box", [])
                            if len(bbox) == 4:
                                st.write(f"**Coordinates**: ({bbox[0]}, {bbox[1]}) → ({bbox[2]}, {bbox[3]})")
                            
                            center = element.get("center_point", [])
                            if len(center) == 2:
                                st.write(f"**Center**: ({center[0]}, {center[1]})")
        
        # Display SAM Results
        st.subheader("🎨 SAM Segmentation")
        
        if "error" in sam_results:
            st.error(f"❌ Segmentation Error: {sam_results['error']}")
        else:
            segments = sam_results.get("segments", [])
            st.metric("Segments Created", len(segments))
            
            if segments:
                st.markdown("### 🎨 Segmentation Details")
                for i, segment in enumerate(segments):
                    with st.expander(f"Segment {i+1}: {segment.get('label', 'Unknown')}", expanded=False):
                        st.write(f"**Label**: {segment.get('label', 'Unknown')}")
                        st.write(f"**Confidence**: {segment.get('confidence', 0):.1%}")
                        st.write(f"**Area**: {segment.get('area', 0):,.0f} pixels")
        
        # Download results
        st.markdown("---")
        
        # JSON download
        results = {
            "gpt_analysis": gpt_analysis,
            "sam_results": sam_results,
            "analysis_timestamp": datetime.now().isoformat(),
            "pipeline_version": "simple_gpt_sam_v1.0"
        }
        
        results_json = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=results_json,
            file_name=f"simple_ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download complete analysis results"
        )
        
        # Clear results button
        if st.button("🗑️ Clear Results", help="Clear current analysis to start over"):
            if 'gpt_analysis' in st.session_state:
                del st.session_state['gpt_analysis']
            if 'sam_results' in st.session_state:
                del st.session_state['sam_results']
            if 'analyzed_image' in st.session_state:
                del st.session_state['analyzed_image']
            if 'temp_image_path' in st.session_state:
                # Clean up temp file
                if os.path.exists(st.session_state['temp_image_path']):
                    os.unlink(st.session_state['temp_image_path'])
                del st.session_state['temp_image_path']
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p><strong>🏗️ Simple AI Architectural Analyzer</strong> | 
    Powered by GPT-4 Vision + SAM | 
    Direct coordinate analysis for architectural insights</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 