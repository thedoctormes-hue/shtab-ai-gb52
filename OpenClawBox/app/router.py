"""Smart router with round-robin, fallback, circuit breaker and rate limit tracking."""
import time
from dataclasses import dataclass, field
from typing import Optional
import asyncio


@dataclass
class ProviderState:
    """Track provider health and availability."""
    last_error: float = 0
    error_count: int = 0
    success_count: int = 0
    cooldown_until: float = 0
    available: bool = True


class SmartRouter:
    """Routes requests to available providers with fallback and circuit breaker."""

    def __init__(self, providers: dict):
        """
        Initialize router with provider dict.
        
        Args:
            providers: Dict of name -> provider instance
        """
        self.providers = providers
        self.states: dict[str, ProviderState] = {
            name: ProviderState() for name in providers
        }
        self.round_robin_index = 0
        self._lock = asyncio.Lock()

    def _get_available_providers(self, tokens: int = 0) -> list:
        """Get list of available providers sorted by preference."""
        now = time.time()
        available = []

        for name, provider in self.providers.items():
            state = self.states[name]
            
            # Skip if in cooldown
            if now < state.cooldown_until:
                continue
            
            # Skip if error count too high
            if state.error_count >= 3:
                continue
            
            # Check rate limits
            if not provider.can_request(tokens):
                continue
            
            available.append(name)

        return available

    async def route(self, messages: list, model: str = "auto", **kwargs) -> dict:
        """
        Route request to best available provider.
        
        Uses round-robin for load balancing, falls back on errors,
        and implements circuit breaker pattern.
        """
        tokens = kwargs.get("max_tokens", 500)
        available = self._get_available_providers(tokens)

        if not available:
            raise RuntimeError("No providers available")

        # Round-robin selection
        async with self._lock:
            # Find next available provider in rotation
            start_idx = self.round_robin_index
            for _ in range(len(available)):
                provider_name = available[self.round_robin_index % len(available)]
                self.round_robin_index = (self.round_robin_index + 1) % len(available)
                
                if provider_name in [p for p in self.providers]:
                    break
            else:
                provider_name = available[0]

        provider = self.providers[provider_name]

        try:
            result = await provider.chat(messages, model, **kwargs)
            
            # Record success
            self.states[provider_name].success_count += 1
            self.states[provider_name].error_count = 0
            
            return result

        except Exception as e:
            state = self.states[provider_name]
            state.error_count += 1
            state.last_error = time.time()

            # Circuit breaker: 3 errors = cooldown
            if state.error_count >= 3:
                state.cooldown_until = time.time() + 300  # 5 min cooldown
                state.available = False

            # Try fallback
            return await self._try_fallback(messages, model, provider_name, tokens, **kwargs)

    async def _try_fallback(self, messages: list, model: str, 
                           failed_provider: str, tokens: int, **kwargs) -> dict:
        """Try other providers as fallback."""
        available = self._get_available_providers(tokens)
        
        # Remove failed provider
        if failed_provider in available:
            available.remove(failed_provider)

        for provider_name in available:
            try:
                provider = self.providers[provider_name]
                result = await provider.chat(messages, model, **kwargs)
                
                # Reset failed provider state on success
                self.states[failed_provider].error_count = 0
                self.states[failed_provider].cooldown_until = 0
                
                return result
            except Exception:
                continue

        raise RuntimeError("All providers failed")

    def get_status(self) -> dict:
        """Get router status."""
        return {
            "providers": {
                name: {
                    "available": self.states[name].available,
                    "errors": self.states[name].error_count,
                    "cooldown_until": self.states[name].cooldown_until,
                    "success_count": self.states[name].success_count,
                }
                for name in self.providers
            },
            "round_robin_index": self.round_robin_index,
        }