"""
Raw GPT processor for handling direct GPT responses without multi-agent system.
Used for research comparison purposes.
"""

import os
from typing import Dict, Any


async def get_raw_gpt_response(user_input: str, project_context: str = "") -> Dict[str, Any]:
    """Get a direct GPT response for comparison with the Socratic agent"""
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a prompt for direct GPT response
        prompt = f"""
        You are an architectural expert. Answer this student's question directly and comprehensively:
        
        STUDENT QUESTION: "{user_input}"
        PROJECT CONTEXT: {project_context}
        
        Provide a detailed, informative answer that directly addresses their question. 
        Give specific architectural advice, examples, and technical information.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        return {
            "response": raw_response,
            "metadata": {
                "response_type": "raw_gpt",
                "agents_used": ["gpt-4o"],
                "interaction_type": "direct_answer",
                "confidence_level": "high",
                "understanding_level": "high",
                "engagement_level": "medium",
                "sources": [],
                "response_time": 0,
                "routing_path": "raw_gpt"
            },
            "routing_path": "raw_gpt",
            "classification": {
                "interaction_type": "direct_answer",
                "confidence_level": "high",
                "understanding_level": "high",
                "engagement_level": "medium"
            }
        }
        
    except Exception as e:
        print(f"❌ Raw GPT response failed: {e}")
        return {
            "response": "I apologize, but I'm unable to provide a response at the moment. Please try again.",
            "metadata": {
                "response_type": "error",
                "agents_used": [],
                "error": str(e)
            },
            "routing_path": "error",
            "classification": {}
        } 