"""
Shared LLM client wrapper for consistent API usage across agents.
"""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from .telemetry import AgentTelemetry


class LLMClient:
    """
    Unified LLM client wrapper that provides consistent interface
    for all agents while handling retries, logging, and error handling.
    """
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.3):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.temperature = temperature
        self.telemetry = AgentTelemetry()
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        tools: Optional[List] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate completion with consistent error handling and logging.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Temperature override
            tools: Optional tools for function calling
            tool_choice: Tool choice strategy
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            self.telemetry.log_llm_call(self.model, len(messages))
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            
            response = self.client.chat.completions.create(**kwargs)
            
            result = {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else {},
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
            # Handle function calls if present
            if response.choices[0].message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": call.id,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    }
                    for call in response.choices[0].message.tool_calls
                ]
            
            self.telemetry.log_llm_response(result)
            return result
            
        except Exception as e:
            self.telemetry.log_error(f"LLM generation failed: {str(e)}")
            raise
    
    def create_system_message(self, content: str) -> Dict[str, str]:
        """Create a properly formatted system message."""
        return {"role": "system", "content": content}
    
    def create_user_message(self, content: str) -> Dict[str, str]:
        """Create a properly formatted user message."""
        return {"role": "user", "content": content}
    
    def create_assistant_message(self, content: str) -> Dict[str, str]:
        """Create a properly formatted assistant message."""
        return {"role": "assistant", "content": content} 