"""
Image Generation Module
Handles phase-specific architectural image generation using Replicate API.
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import replicate

class GenerationPhase(Enum):
    """Design phases for image generation"""
    IDEATION = "ideation"
    VISUALIZATION = "visualization"
    MATERIALIZATION = "materialization"

@dataclass
class GeneratedImage:
    """Results from image generation"""
    image_id: str
    phase: GenerationPhase
    prompt: str
    image_url: str
    local_path: Optional[str]
    building_type: str
    design_summary: str
    generation_params: Dict[str, Any]
    timestamp: datetime
    session_id: str

class ImageGenerator:
    """Handles phase-specific architectural image generation"""
    
    def __init__(self):
        # Set up Replicate API
        os.environ["REPLICATE_API_TOKEN"] = "r8_BtcdAmX0aPP00cIP1toJ1ObFjTNOg3P2bMdZg"
        self.client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
        
        # Storage setup
        self.generated_images_path = "thesis_data/generated_images"
        os.makedirs(self.generated_images_path, exist_ok=True)
        
        # Phase-specific generation parameters
        self.phase_configs = {
            GenerationPhase.IDEATION: {
                "style": "architectural sketch, hand-drawn, conceptual, loose lines, pencil drawing",
                "detail_level": "conceptual",
                "model": "ideogram-ai/ideogram-v2a-turbo",
                "guidance_scale": 7.5,
                "num_inference_steps": 20
            },
            GenerationPhase.VISUALIZATION: {
                "style": "architectural visualization, 3D rendering, materials visible, spatial clarity",
                "detail_level": "detailed",
                "model": "ideogram-ai/ideogram-v2a-turbo",
                "guidance_scale": 10.0,
                "num_inference_steps": 30
            },
            GenerationPhase.MATERIALIZATION: {
                "style": "photorealistic architectural rendering, high detail, construction details, materials",
                "detail_level": "photorealistic",
                "model": "ideogram-ai/ideogram-v2a-turbo",
                "guidance_scale": 12.0,
                "num_inference_steps": 50
            }
        }
    
    def create_phase_prompt(self, phase: GenerationPhase, building_type: str, 
                           design_summary: str, conversation_context: str = "") -> str:
        """Create phase-specific prompt for image generation"""
        
        config = self.phase_configs[phase]
        base_style = config["style"]
        
        # Phase-specific prompt templates
        if phase == GenerationPhase.IDEATION:
            prompt = f"""
            {base_style}, conceptual architectural sketch of a {building_type}.
            Design concept: {design_summary}
            Style: Hand-drawn, loose sketchy lines, architectural drawing, concept sketch,
            black and white pencil drawing, architectural ideation, preliminary design,
            simple forms, basic massing, conceptual layout.
            Context: {conversation_context[:200]}
            """
        
        elif phase == GenerationPhase.VISUALIZATION:
            prompt = f"""
            {base_style}, architectural visualization of a {building_type}.
            Design: {design_summary}
            Style: 3D architectural rendering, spatial organization visible, 
            materials indicated, lighting and shadow, architectural visualization,
            clear spatial relationships, design development drawing.
            Context: {conversation_context[:200]}
            """
        
        else:  # MATERIALIZATION
            prompt = f"""
            {base_style}, photorealistic rendering of a {building_type}.
            Final design: {design_summary}
            Style: High-quality architectural rendering, detailed materials,
            realistic lighting, construction details visible, photorealistic,
            professional architectural visualization, final design presentation.
            Context: {conversation_context[:200]}
            """
        
        # Clean up the prompt
        prompt = " ".join(prompt.split())  # Remove extra whitespace
        prompt = prompt.replace("\n", " ").strip()
        
        return prompt
    
    async def generate_phase_image(self, phase: GenerationPhase, building_type: str,
                                 design_summary: str, conversation_context: str = "",
                                 session_id: str = "") -> GeneratedImage:
        """Generate phase-specific architectural image"""
        
        # Create prompt
        prompt = self.create_phase_prompt(phase, building_type, design_summary, conversation_context)
        config = self.phase_configs[phase]
        
        try:
            # Generate image using Replicate
            output = self.client.run(
                config["model"],
                input={
                    "prompt": prompt,
                    "guidance_scale": config["guidance_scale"],
                    "num_inference_steps": config["num_inference_steps"],
                    "width": 768,
                    "height": 768,
                    "num_outputs": 1
                }
            )
            
            # Get the image URL
            if isinstance(output, list) and len(output) > 0:
                image_url = output[0]
            else:
                image_url = str(output)
            
            # Download and save the image locally
            local_path = await self._download_image(image_url, phase, session_id)
            
            # Create GeneratedImage object
            image_id = f"gen_{phase.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            generated_image = GeneratedImage(
                image_id=image_id,
                phase=phase,
                prompt=prompt,
                image_url=image_url,
                local_path=local_path,
                building_type=building_type,
                design_summary=design_summary,
                generation_params=config,
                timestamp=datetime.now(),
                session_id=session_id
            )
            
            # Store generation metadata
            self._store_generation_metadata(generated_image)
            
            return generated_image
            
        except Exception as e:
            print(f"Image generation failed: {e}")
            # Return placeholder result
            return GeneratedImage(
                image_id=f"gen_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                phase=phase,
                prompt=prompt,
                image_url="",
                local_path=None,
                building_type=building_type,
                design_summary=design_summary,
                generation_params=config,
                timestamp=datetime.now(),
                session_id=session_id
            )
    
    async def _download_image(self, image_url: str, phase: GenerationPhase, session_id: str) -> str:
        """Download generated image and save locally"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session_id}_{phase.value}_{timestamp}.png"
            local_path = os.path.join(self.generated_images_path, filename)
            
            # Save image
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return local_path
            
        except Exception as e:
            print(f"Failed to download image: {e}")
            return None
    
    def _store_generation_metadata(self, generated_image: GeneratedImage):
        """Store generation metadata to JSON file"""
        metadata = {
            "image_id": generated_image.image_id,
            "phase": generated_image.phase.value,
            "prompt": generated_image.prompt,
            "image_url": generated_image.image_url,
            "local_path": generated_image.local_path,
            "building_type": generated_image.building_type,
            "design_summary": generated_image.design_summary,
            "generation_params": generated_image.generation_params,
            "timestamp": generated_image.timestamp.isoformat(),
            "session_id": generated_image.session_id
        }
        
        # Save metadata
        metadata_file = os.path.join(self.generated_images_path, f"{generated_image.image_id}_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def should_generate_phase_image(self, phase: GenerationPhase, phase_progress: float, 
                                  messages_count: int) -> bool:
        """Determine if it's time to generate a phase image"""
        
        # Generation thresholds for each phase
        thresholds = {
            GenerationPhase.IDEATION: {"progress": 0.7, "min_messages": 5},
            GenerationPhase.VISUALIZATION: {"progress": 0.8, "min_messages": 8},
            GenerationPhase.MATERIALIZATION: {"progress": 0.9, "min_messages": 12}
        }
        
        threshold = thresholds.get(phase, {"progress": 0.8, "min_messages": 6})
        
        return (phase_progress >= threshold["progress"] and 
                messages_count >= threshold["min_messages"])
    
    def get_generated_images_for_session(self, session_id: str) -> List[GeneratedImage]:
        """Get all generated images for a specific session"""
        images = []
        
        for filename in os.listdir(self.generated_images_path):
            if filename.endswith("_metadata.json") and session_id in filename:
                metadata_path = os.path.join(self.generated_images_path, filename)
                try:
                    with open(metadata_path, 'r') as f:
                        data = json.load(f)
                    
                    image = GeneratedImage(
                        image_id=data["image_id"],
                        phase=GenerationPhase(data["phase"]),
                        prompt=data["prompt"],
                        image_url=data["image_url"],
                        local_path=data["local_path"],
                        building_type=data["building_type"],
                        design_summary=data["design_summary"],
                        generation_params=data["generation_params"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        session_id=data["session_id"]
                    )
                    images.append(image)
                    
                except Exception as e:
                    print(f"Failed to load image metadata {filename}: {e}")
        
        return sorted(images, key=lambda x: x.timestamp)
    
    def extract_design_summary_from_conversation(self, messages: List[Dict], phase: GenerationPhase) -> str:
        """Extract design summary from conversation for image generation"""
        
        # Get recent user messages
        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
        recent_content = ' '.join(user_messages[-5:])  # Last 5 messages
        
        # Phase-specific extraction
        if phase == GenerationPhase.IDEATION:
            # Look for concepts, ideas, goals
            summary = f"Conceptual design exploring {recent_content[:200]}"
        elif phase == GenerationPhase.VISUALIZATION:
            # Look for spatial, layout, organization
            summary = f"Spatial design with {recent_content[:200]}"
        else:  # MATERIALIZATION
            # Look for materials, construction, details
            summary = f"Detailed design featuring {recent_content[:200]}"
        
        return summary.strip()
