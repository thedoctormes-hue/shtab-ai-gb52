"""Base provider adapter."""

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(self, messages: list, model: str = None, **kwargs):
        """Send chat request to provider."""
        pass