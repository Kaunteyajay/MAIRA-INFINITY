"""
LLM Router

Routes requests to different providers with fallback and load balancing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, AsyncIterator, Any
from dataclasses import dataclass

from maira.llm.base import (
    LLMProvider, Message, StreamChunk, 
    ProviderError, RateLimitError, AuthError, ModelNotFoundError
)
from maira.llm.providers.claude import ClaudeProvider
from maira.llm.providers.ollama import OllamaProvider
from maira.core.event_bus import EventBus, LLMRequestEvent, LLMTokenEvent, LLMResponseEvent

logger = logging.getLogger(__name__)

@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    enabled: bool = True
    priority: int = 1  # Lower = higher priority
    fallback: bool = True
    models: List[str] = None

class LLMRouter:
    """Routes LLM requests across multiple providers."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.providers: Dict[str, LLMProvider] = {}
        self.configs: Dict[str, ProviderConfig] = {}
        self.default_provider = "claude"
        
    def register_provider(self, provider: LLMProvider, config: ProviderConfig) -> None:
        """Register an LLM provider."""
        self.providers[provider.name] = provider
        self.configs[provider.name] = config
        logger.info(f"Registered LLM provider: {provider.name}")
    
    async def setup_providers(self, api_keys: Dict[str, str]) -> None:
        """Setup providers with API keys."""
        try:
            # Claude
            if "anthropic" in api_keys and api_keys["anthropic"]:
                claude = ClaudeProvider(api_keys["anthropic"])
                self.register_provider(claude, ProviderConfig(priority=1))
                logger.info("Claude provider initialized")
            
            # Ollama (local)
            ollama = OllamaProvider()
            if await ollama.check_connection():
                self.register_provider(ollama, ProviderConfig(priority=3, fallback=True))
                logger.info("Ollama provider initialized")
            else:
                logger.warning("Ollama not available (not running?)")
            
            # TODO: Add OpenAI, Gemini providers
            
        except Exception as e:
            logger.exception(f"Error setting up providers: {e}")
    
    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        conversation_id: str = "default",
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream chat completion with provider fallback."""
        
        # Determine provider order
        if provider and provider in self.providers:
            provider_order = [provider]
        else:
            provider_order = self._get_provider_order(tools is not None)
        
        last_error = None
        
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue
                
            provider_instance = self.providers[provider_name]
            config = self.configs[provider_name]
            
            if not config.enabled:
                continue
            
            try:
                logger.info(f"Attempting LLM request with {provider_name}")
                
                # Publish request start event
                await self.event_bus.publish(LLMRequestEvent(
                    provider=provider_name,
                    model=model or "default",
                    conversation_id=conversation_id
                ))
                
                # Stream from provider
                token_count = 0
                full_response = ""
                
                async for chunk in provider_instance.stream_chat(
                    messages=messages,
                    tools=tools,
                    model=model,
                    **kwargs
                ):
                    if chunk.text:
                        full_response += chunk.text
                        token_count += 1
                        
                        # Publish token event
                        await self.event_bus.publish(LLMTokenEvent(
                            token=chunk.text,
                            conversation_id=conversation_id
                        ))
                    
                    yield chunk
                    
                    if chunk.done:
                        # Publish completion event
                        await self.event_bus.publish(LLMResponseEvent(
                            text=full_response,
                            tokens_used=token_count,
                            provider=provider_name,
                            conversation_id=conversation_id
                        ))
                        return
                
                # If we get here, the stream completed successfully
                return
                
            except RateLimitError as e:
                logger.warning(f"Rate limit with {provider_name}: {e}")
                last_error = e
                continue
                
            except AuthError as e:
                logger.error(f"Auth error with {provider_name}: {e}")
                last_error = e
                continue
                
            except ModelNotFoundError as e:
                logger.warning(f"Model not found with {provider_name}: {e}")
                last_error = e
                continue
                
            except ProviderError as e:
                logger.warning(f"Provider error with {provider_name}: {e}")
                last_error = e
                continue
                
            except Exception as e:
                logger.exception(f"Unexpected error with {provider_name}: {e}")
                last_error = e
                continue
        
        # All providers failed
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        logger.error(error_msg)
        raise ProviderError(error_msg)
    
    def _get_provider_order(self, needs_tools: bool = False) -> List[str]:
        """Get provider order based on priority and capabilities."""
        available_providers = []
        
        for name, provider in self.providers.items():
            config = self.configs[name]
            
            if not config.enabled:
                continue
            
            # Skip providers that don't support tools if needed
            if needs_tools and not provider.supports_tools:
                continue
            
            available_providers.append((name, config.priority))
        
        # Sort by priority (lower number = higher priority)
        available_providers.sort(key=lambda x: x[1])
        
        return [name for name, _ in available_providers]
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models from all providers."""
        models = {}
        
        for name, provider in self.providers.items():
            config = self.configs[name]
            if config.enabled:
                try:
                    models[name] = provider.get_models()
                except Exception as e:
                    logger.warning(f"Failed to get models from {name}: {e}")
                    models[name] = []
        
        return models
    
    def set_default_provider(self, provider: str) -> None:
        """Set the default provider."""
        if provider in self.providers:
            self.default_provider = provider
            logger.info(f"Default provider set to: {provider}")
        else:
            raise ValueError(f"Provider {provider} not registered")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        
        for name, provider in self.providers.items():
            config = self.configs[name]
            status[name] = {
                "enabled": config.enabled,
                "priority": config.priority,
                "supports_tools": provider.supports_tools,
                "supports_vision": provider.supports_vision,
                "models": len(provider.get_models())
            }
        
        return status