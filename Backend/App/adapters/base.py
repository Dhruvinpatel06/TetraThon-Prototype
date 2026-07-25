from typing import Protocol, runtime_checkable

@runtime_checkable
class DataAdapter(Protocol):
    """Protocol defining the standard interface for external data adapters."""
    
    def get_status(self) -> str:
        """Returns 'live' or 'mock' depending on adapter connectivity."""
        ...
