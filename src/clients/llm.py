"""
LLM Client - Interface to Claude/OpenAI for AI capabilities
"""
import os
from typing import Dict, Any, Optional, List
from loguru import logger

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMClient:
    """
    Client for LLM API calls.
    
    Supports Claude (Anthropic) and OpenAI.
    """
    
    def __init__(self, provider: str = "anthropic"):
        """
        Initialize LLM client.
        
        Args:
            provider: "anthropic" or "openai"
        """
        self.provider = provider
        
        if provider == "anthropic":
            if Anthropic is None:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.default_model = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package not installed. Run: pip install openai")
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.default_model = "gpt-4o"
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"LLM client initialized with {provider}")
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            model: Model to use (optional, uses default)
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            
        Returns:
            Response dict with 'content' and 'usage'
        """
        model = model or self.default_model
        
        try:
            if self.provider == "anthropic":
                return self._anthropic_complete(
                    prompt, system_prompt, model, max_tokens, temperature
                )
            else:
                return self._openai_complete(
                    prompt, system_prompt, model, max_tokens, temperature
                )
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            raise
    
    def _anthropic_complete(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate completion using Anthropic."""
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        return {
            "content": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "model": model,
            "provider": "anthropic"
        }
    
    def _openai_complete(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate completion using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            },
            "model": model,
            "provider": "openai"
        }
