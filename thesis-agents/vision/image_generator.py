# vision/image_generator.py
import os
import requests
import time
import base64
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class ImageStyle(Enum):
    """Different image styles for different phases"""
    ROUGH_SKETCH = "rough_sketch"
    ARCHITECTURAL_FORM = "architectural_form"
    DETAILED_RENDER = "detailed_render"

class ReplicateImageGenerator:
    """Generate phase-specific images using Replicate API"""
    
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            print("⚠️ REPLICATE_API_TOKEN not found in environment variables")
        
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Model configurations for different styles
        self.models = {
            ImageStyle.ROUGH_SKETCH: {
                "model": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "style_prompt": "rough architectural sketch, hand-drawn, pencil on paper, conceptual design, loose lines, architectural drawing style, black and white"
            },
            ImageStyle.ARCHITECTURAL_FORM: {
                "model": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "style_prompt": "architectural form study, clean lines, 3D massing model, architectural visualization, modern design, white background, professional architectural rendering"
            },
            ImageStyle.DETAILED_RENDER: {
                "model": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "style_prompt": "detailed architectural rendering, photorealistic, professional architecture visualization, high quality, detailed materials and textures, architectural photography style"
            }
        }

    def generate_phase_image(self, design_description: str, phase: str, project_context: str = "") -> Dict[str, Any]:
        """Generate an image appropriate for the given design phase"""
        
        if not self.api_token:
            return {"error": "Replicate API token not configured"}
        
        # Map phase to image style
        style_mapping = {
            "ideation": ImageStyle.ROUGH_SKETCH,
            "visualization": ImageStyle.ARCHITECTURAL_FORM,
            "materialization": ImageStyle.DETAILED_RENDER
        }
        
        image_style = style_mapping.get(phase.lower(), ImageStyle.ROUGH_SKETCH)
        
        print(f"🎨 Generating {image_style.value} image for {phase} phase")
        
        try:
            # Create the prompt
            prompt = self._create_prompt(design_description, image_style, project_context)
            
            # Generate the image
            result = self._generate_image(prompt, image_style)
            
            if "error" in result:
                return result
            
            return {
                "success": True,
                "image_url": result["image_url"],
                "prompt": prompt,
                "style": image_style.value,
                "phase": phase
            }
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            return {"error": f"Image generation failed: {str(e)}"}

    def _create_prompt(self, design_description: str, image_style: ImageStyle, project_context: str) -> str:
        """Create a detailed prompt for image generation"""
        
        model_config = self.models[image_style]
        style_prompt = model_config["style_prompt"]
        
        # Clean and prepare the design description
        clean_description = design_description.replace('\n', ' ').strip()
        if len(clean_description) > 500:
            clean_description = clean_description[:500] + "..."
        
        # Add project context if available
        context_addition = f", {project_context}" if project_context else ""
        
        # Create phase-specific prompt
        if image_style == ImageStyle.ROUGH_SKETCH:
            prompt = f"Rough architectural sketch of {clean_description}{context_addition}. {style_prompt}. Simple, conceptual, hand-drawn style."
        elif image_style == ImageStyle.ARCHITECTURAL_FORM:
            prompt = f"Architectural form study of {clean_description}{context_addition}. {style_prompt}. Clean, professional, 3D visualization."
        else:  # DETAILED_RENDER
            prompt = f"Detailed architectural rendering of {clean_description}{context_addition}. {style_prompt}. Photorealistic, high-quality visualization."
        
        return prompt

    def _generate_image(self, prompt: str, image_style: ImageStyle) -> Dict[str, Any]:
        """Generate image using Replicate API"""
        
        model_config = self.models[image_style]
        model_version = model_config["model"]
        
        # Prepare the request payload
        payload = {
            "version": model_version,
            "input": {
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "prompt_strength": 0.8,
                "refine": "expert_ensemble_refiner",
                "high_noise_frac": 0.8
            }
        }
        
        try:
            print(f"📤 Sending request to Replicate API...")
            
            # Create prediction
            response = requests.post(
                f"{self.base_url}/predictions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 201:
                return {"error": f"Failed to create prediction: {response.status_code} - {response.text}"}
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            print(f"🔄 Prediction created: {prediction_id}")
            print(f"⏳ Waiting for image generation...")
            
            # Poll for completion
            max_attempts = 60  # 5 minutes max
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                
                # Check prediction status
                status_response = requests.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=self.headers,
                    timeout=10
                )
                
                if status_response.status_code != 200:
                    return {"error": f"Failed to check status: {status_response.status_code}"}
                
                status_data = status_response.json()
                status = status_data.get("status")
                
                print(f"🔍 Status check {attempt + 1}: {status}")
                
                if status == "succeeded":
                    output = status_data.get("output")
                    if output and len(output) > 0:
                        image_url = output[0]
                        print(f"✅ Image generated successfully: {image_url}")
                        return {"image_url": image_url}
                    else:
                        return {"error": "No output received from prediction"}
                
                elif status == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    return {"error": f"Prediction failed: {error_msg}"}
                
                elif status in ["starting", "processing"]:
                    attempt += 1
                    continue
                
                else:
                    return {"error": f"Unexpected status: {status}"}
            
            return {"error": "Image generation timed out"}
            
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def download_and_save_image(self, image_url: str, filename: str) -> Optional[str]:
        """Download and save the generated image locally"""
        
        try:
            print(f"📥 Downloading image from: {image_url}")
            
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # Create directory if it doesn't exist
                os.makedirs("generated_images", exist_ok=True)
                
                filepath = os.path.join("generated_images", filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Image saved to: {filepath}")
                return filepath
            else:
                print(f"❌ Failed to download image: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading image: {e}")
            return None

    def test_connection(self) -> bool:
        """Test if the Replicate API connection is working"""
        
        if not self.api_token:
            print("❌ No API token configured")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/predictions",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Replicate API connection successful")
                return True
            else:
                print(f"❌ API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False


class DesignPromptGenerator:
    """Generate image prompts from conversation history and design context"""

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_image_prompt_from_conversation(self, conversation_history: list, phase: str, project_type: str = "community center") -> str:
        """Generate an image prompt based on conversation history and current phase"""

        try:
            # Extract relevant conversation content
            conversation_text = self._extract_conversation_content(conversation_history)

            # Create a prompt for GPT to generate the image description
            system_prompt = f"""
            You are an expert architectural visualization specialist. Based on the conversation history about a {project_type} design project, create a detailed prompt for generating a {phase} phase image.

            PHASE REQUIREMENTS:
            - IDEATION: Create a rough, conceptual sketch showing basic spatial relationships and design ideas
            - VISUALIZATION: Create a clear architectural form study showing spatial organization and massing
            - MATERIALIZATION: Create a detailed, realistic rendering showing materials, construction details, and final design

            Extract the key design elements, spatial relationships, programmatic requirements, and design concepts from the conversation. Focus on:
            1. Building program and functional requirements
            2. Spatial organization and layout concepts
            3. Site relationships and context
            4. Design concepts and architectural ideas
            5. Materials and construction approaches (if mentioned)
            6. Scale and proportion considerations

            Create a concise but detailed description (max 200 words) that captures the essence of the design as discussed. Focus on visual, spatial, and architectural qualities that can be rendered in an image.
            """

            user_prompt = f"""
            CONVERSATION HISTORY:
            {conversation_text}

            PROJECT TYPE: {project_type}
            CURRENT PHASE: {phase}

            Generate a detailed architectural description for image generation that captures the design ideas discussed in this conversation.
            """

            print(f"🤖 Generating image prompt from conversation for {phase} phase...")

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            generated_prompt = response.choices[0].message.content.strip()
            print(f"✅ Generated image prompt: {generated_prompt[:100]}...")

            return generated_prompt

        except Exception as e:
            print(f"❌ Error generating prompt from conversation: {e}")
            # Fallback to generic prompt
            return f"Modern {project_type} design, architectural {phase} phase visualization"

    def _extract_conversation_content(self, conversation_history: list) -> str:
        """Extract relevant content from conversation history"""

        if not conversation_history:
            return "No conversation history available"

        # Extract user messages and AI responses, focusing on design-related content
        relevant_content = []

        for message in conversation_history[-10:]:  # Last 10 messages for context
            if isinstance(message, dict):
                role = message.get('role', '')
                content = message.get('content', '')

                if role in ['user', 'assistant'] and content:
                    # Clean and truncate content
                    clean_content = content.replace('\n', ' ').strip()
                    if len(clean_content) > 200:
                        clean_content = clean_content[:200] + "..."

                    relevant_content.append(f"{role.upper()}: {clean_content}")
            elif isinstance(message, str):
                # Handle simple string messages
                clean_content = message.replace('\n', ' ').strip()
                if len(clean_content) > 200:
                    clean_content = clean_content[:200] + "..."
                relevant_content.append(clean_content)

        return "\n".join(relevant_content) if relevant_content else "No relevant conversation content found"
