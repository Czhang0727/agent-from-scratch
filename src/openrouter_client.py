#!/usr/bin/env python3
"""
OpenRouter Module - Wrapper around the official OpenRouter SDK.
Provides a simplified interface for the agent to use.
"""

import os
from typing import Optional, List, Dict

from openrouter import OpenRouter


class OpenRouterClient:
    """
    Client for interacting with the OpenRouter API using the official SDK.
    """

    DEFAULT_MODEL = "qwen/qwen-2.5-7b-instruct"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: API key. If None, loads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (defaults to qwen/qwen3.5-flash)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Response content string
        """
        model = model or self.DEFAULT_MODEL

        with OpenRouter(api_key=self.api_key) as client:
            response = client.chat.send(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

    def simple_chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Simple chat interface for single-turn conversations.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Assistant's response content
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(messages)
