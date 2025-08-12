"""
Dependency Injection Container

This module manages dependencies between components using a simple DI container pattern.
It ensures loose coupling and makes testing easier.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DependencyContainer:
    """
    Simple dependency injection container for managing service dependencies.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, service_name: str, service_class: type, singleton: bool = True):
        """
        Register a service with the container.
        
        Args:
            service_name: Name of the service
            service_class: Class to instantiate
            singleton: Whether to create a singleton instance
        """
        self._services[service_name] = {
            'class': service_class,
            'singleton': singleton
        }
        logger.debug(f"Registered service: {service_name}")
    
    def get(self, service_name: str) -> Any:
        """
        Get a service instance from the container.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not registered")
        
        service_config = self._services[service_name]
        
        if service_config['singleton']:
            # Return existing singleton instance or create new one
            if service_name not in self._singletons:
                self._singletons[service_name] = service_config['class']()
                logger.debug(f"Created singleton instance for: {service_name}")
            return self._singletons[service_name]
        else:
            # Create new instance each time
            return service_config['class']()
    
    def has(self, service_name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            True if service is registered, False otherwise
        """
        return service_name in self._services
    
    def clear(self):
        """Clear all registered services and singletons."""
        self._services.clear()
        self._singletons.clear()
        logger.debug("Dependency container cleared")

# Global dependency container instance
container = DependencyContainer()

def register_services():
    """
    Register all services with the dependency container.
    This should be called during application startup.
    """
    from services.websocket_service import WebSocketService
    from services.blacklist_service import BlacklistService
    from services.health_service import HealthService
    from services.database_service import DatabaseService
    
    # Register core services
    container.register('websocket_service', WebSocketService)
    container.register('blacklist_service', BlacklistService)
    container.register('health_service', HealthService)
    container.register('database_service', DatabaseService)
    
    logger.info("All services registered with dependency container")

def get_service(service_name: str) -> Any:
    """
    Convenience function to get a service from the global container.
    
    Args:
        service_name: Name of the service to retrieve
        
    Returns:
        Service instance
    """
    return container.get(service_name)
