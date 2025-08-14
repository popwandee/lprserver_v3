#!/usr/bin/env python3
"""
Modular Architecture Configuration for AI Camera v1.3

This module defines the modular architecture that separates core modules
from optional modules, ensuring that core functionality (camera, detection, health)
can work independently of optional modules (websocket sender, storage manager).

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

from typing import Dict, List, Set, Optional
from enum import Enum

class ModuleType(Enum):
    """Module types for classification."""
    CORE = "core"           # Essential for basic functionality
    OPTIONAL = "optional"   # Can be disabled without affecting core
    DEPENDENT = "dependent" # Depends on other modules

class ModuleCategory(Enum):
    """Module categories for organization."""
    COMPONENT = "component"     # Low-level hardware/API components
    SERVICE = "service"         # Business logic services
    BLUEPRINT = "blueprint"     # Web interface blueprints
    UTILITY = "utility"         # Utility functions

class ModularArchitecture:
    """
    Modular Architecture Manager for AI Camera v1.3
    
    This class manages the modular architecture ensuring that:
    1. Core modules (camera, detection, health) work independently
    2. Optional modules (websocket sender, storage) can be disabled
    3. Dependencies are properly managed
    4. System remains functional even if optional modules fail
    """
    
    def __init__(self):
        """Initialize modular architecture configuration."""
        self.modules = self._define_modules()
        self.dependencies = self._define_dependencies()
        self.startup_sequence = self._define_startup_sequence()
    
    def _define_modules(self) -> Dict[str, Dict]:
        """Define all modules with their types and categories."""
        return {
            # === CORE MODULES (Essential) ===
            'logger': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.UTILITY,
                'description': 'Logging system',
                'required': True,
                'fallback': None
            },
            'config': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.UTILITY,
                'description': 'Configuration management',
                'required': True,
                'fallback': None
            },
            'camera_handler': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.COMPONENT,
                'description': 'Camera hardware interface',
                'required': True,
                'fallback': None
            },
            'camera_manager': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.SERVICE,
                'description': 'Camera business logic',
                'required': True,
                'fallback': None,
                'dependencies': ['camera_handler', 'logger']
            },
            'detection_processor': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.COMPONENT,
                'description': 'AI detection processing',
                'required': True,
                'fallback': None
            },
            'detection_manager': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.SERVICE,
                'description': 'Detection business logic',
                'required': True,
                'fallback': None,
                'dependencies': ['detection_processor', 'database_manager', 'logger']
            },
            'database_manager': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.COMPONENT,
                'description': 'Database operations',
                'required': True,
                'fallback': None
            },
            'health_monitor': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.COMPONENT,
                'description': 'System health monitoring',
                'required': True,
                'fallback': None
            },
            'health_service': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.SERVICE,
                'description': 'Health monitoring business logic',
                'required': True,
                'fallback': None,
                'dependencies': ['health_monitor', 'logger']
            },
            'video_streaming': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.SERVICE,
                'description': 'Video streaming service',
                'required': True,
                'fallback': None,
                'dependencies': ['camera_manager', 'logger']
            },
            
            # === OPTIONAL MODULES (Can be disabled) ===
            'websocket_sender': {
                'type': ModuleType.OPTIONAL,
                'category': ModuleCategory.SERVICE,
                'description': 'WebSocket communication with external server',
                'required': False,
                'fallback': 'offline_mode',
                'dependencies': ['database_manager', 'logger']
            },
            'storage_monitor': {
                'type': ModuleType.OPTIONAL,
                'category': ModuleCategory.COMPONENT,
                'description': 'Storage space monitoring',
                'required': False,
                'fallback': 'basic_disk_check',
                'dependencies': ['logger']
            },
            'storage_service': {
                'type': ModuleType.OPTIONAL,
                'category': ModuleCategory.SERVICE,
                'description': 'Storage management business logic',
                'required': False,
                'fallback': 'manual_cleanup',
                'dependencies': ['storage_monitor', 'logger']
            },
            
            # === WEB INTERFACE MODULES ===
            'main_blueprint': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Main dashboard',
                'required': True,
                'fallback': None
            },
            'camera_blueprint': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Camera control interface',
                'required': True,
                'fallback': None
            },
            'detection_blueprint': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Detection control interface',
                'required': True,
                'fallback': None
            },
            'health_blueprint': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Health monitoring interface',
                'required': True,
                'fallback': None
            },
            'streaming_blueprint': {
                'type': ModuleType.CORE,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Video streaming interface',
                'required': True,
                'fallback': None
            },
            'websocket_sender_blueprint': {
                'type': ModuleType.OPTIONAL,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'WebSocket sender interface',
                'required': False,
                'fallback': None
            },
            'storage_blueprint': {
                'type': ModuleType.OPTIONAL,
                'category': ModuleCategory.BLUEPRINT,
                'description': 'Storage management interface',
                'required': False,
                'fallback': None
            }
        }
    
    def _define_dependencies(self) -> Dict[str, List[str]]:
        """Define module dependencies."""
        return {
            # Core module dependencies
            'camera_manager': ['camera_handler', 'logger'],
            'detection_manager': ['detection_processor', 'database_manager', 'logger'],
            'health_service': ['health_monitor', 'logger'],
            'video_streaming': ['camera_manager', 'logger'],
            
            # Optional module dependencies
            'websocket_sender': ['database_manager', 'logger'],
            'storage_service': ['storage_monitor', 'logger'],
            
            # Blueprint dependencies
            'camera_blueprint': ['camera_manager'],
            'detection_blueprint': ['detection_manager'],
            'health_blueprint': ['health_service'],
            'streaming_blueprint': ['video_streaming'],
            'websocket_sender_blueprint': ['websocket_sender'],
            'storage_blueprint': ['storage_service']
        }
    
    def _define_startup_sequence(self) -> List[Dict]:
        """Define the startup sequence for modules."""
        return [
            # Phase 1: Core Infrastructure
            {
                'phase': 1,
                'name': 'Core Infrastructure',
                'modules': ['logger', 'config'],
                'description': 'Initialize logging and configuration',
                'required': True
            },
            
            # Phase 2: Core Components
            {
                'phase': 2,
                'name': 'Core Components',
                'modules': ['camera_handler', 'detection_processor', 'database_manager', 'health_monitor'],
                'description': 'Initialize core hardware and database components',
                'required': True
            },
            
            # Phase 3: Core Services
            {
                'phase': 3,
                'name': 'Core Services',
                'modules': ['camera_manager', 'detection_manager', 'health_service', 'video_streaming'],
                'description': 'Initialize core business logic services',
                'required': True
            },
            
            # Phase 4: Optional Components
            {
                'phase': 4,
                'name': 'Optional Components',
                'modules': ['storage_monitor'],
                'description': 'Initialize optional components',
                'required': False
            },
            
            # Phase 5: Optional Services
            {
                'phase': 5,
                'name': 'Optional Services',
                'modules': ['websocket_sender', 'storage_service'],
                'description': 'Initialize optional business logic services',
                'required': False
            },
            
            # Phase 6: Web Interface
            {
                'phase': 6,
                'name': 'Web Interface',
                'modules': ['main_blueprint', 'camera_blueprint', 'detection_blueprint', 
                           'health_blueprint', 'streaming_blueprint', 
                           'websocket_sender_blueprint', 'storage_blueprint'],
                'description': 'Register web interface blueprints',
                'required': False
            }
        ]
    
    def get_core_modules(self) -> List[str]:
        """Get list of core modules."""
        return [name for name, config in self.modules.items() 
                if config['type'] == ModuleType.CORE]
    
    def get_optional_modules(self) -> List[str]:
        """Get list of optional modules."""
        return [name for name, config in self.modules.items() 
                if config['type'] == ModuleType.OPTIONAL]
    
    def get_module_dependencies(self, module_name: str) -> List[str]:
        """Get dependencies for a specific module."""
        return self.dependencies.get(module_name, [])
    
    def can_disable_module(self, module_name: str) -> bool:
        """Check if a module can be safely disabled."""
        if module_name not in self.modules:
            return False
        
        module_config = self.modules[module_name]
        return module_config['type'] == ModuleType.OPTIONAL
    
    def get_startup_phases(self) -> List[Dict]:
        """Get the startup sequence phases."""
        return self.startup_sequence
    
    def validate_dependencies(self, enabled_modules: List[str]) -> Dict[str, List[str]]:
        """
        Validate that all dependencies are satisfied for enabled modules.
        
        Args:
            enabled_modules: List of module names to enable
            
        Returns:
            Dict with 'valid' and 'missing' dependencies
        """
        missing_deps = {}
        
        for module_name in enabled_modules:
            if module_name not in self.modules:
                continue
                
            dependencies = self.get_module_dependencies(module_name)
            missing = [dep for dep in dependencies if dep not in enabled_modules]
            
            if missing:
                missing_deps[module_name] = missing
        
        return {
            'valid': len(missing_deps) == 0,
            'missing': missing_deps
        }
    
    def get_minimal_core_config(self) -> List[str]:
        """Get minimal core configuration that ensures basic functionality."""
        return [
            'logger',
            'config', 
            'camera_handler',
            'camera_manager',
            'database_manager',
            'health_monitor',
            'health_service',
            'main_blueprint',
            'camera_blueprint',
            'health_blueprint'
        ]
    
    def get_full_config(self) -> List[str]:
        """Get full configuration with all modules."""
        return list(self.modules.keys())

# Global instance
modular_arch = ModularArchitecture()
