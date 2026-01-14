"""
Device registry for managing multiple smart devices.

This module provides a registry system to store and retrieve device instances.
"""

from typing import Dict, Optional, Any
from .base import SmartDevice


class DeviceRegistry:
    """
    Registry for managing multiple smart devices.
    
    Devices are registered by name and can be retrieved later.
    The registry maintains a mapping of device names to device instances.
    """
    
    def __init__(self):
        """Initialize an empty device registry."""
        self._devices: Dict[str, SmartDevice] = {}
    
    def register(self, name: str, device: SmartDevice) -> None:
        """
        Register a device with the given name.
        
        Args:
            name: Unique name for the device
            device: SmartDevice instance to register
            
        Raises:
            ValueError: If name is empty or device is None
        """
        if not name or not name.strip():
            raise ValueError("Device name cannot be empty")
        if device is None:
            raise ValueError("Device cannot be None")
        
        self._devices[name.strip()] = device
    
    def get(self, name: str) -> Optional[SmartDevice]:
        """
        Get a device by name.
        
        Args:
            name: Name of the device to retrieve
            
        Returns:
            SmartDevice instance if found, None otherwise
        """
        return self._devices.get(name.strip()) if name else None
    
    def remove(self, name: str) -> bool:
        """
        Remove a device from the registry.
        
        Args:
            name: Name of the device to remove
            
        Returns:
            True if device was removed, False if not found
        """
        if name and name.strip() in self._devices:
            del self._devices[name.strip()]
            return True
        return False
    
    def list_devices(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered devices with their basic information.
        
        Returns:
            Dictionary mapping device names to device info dictionaries
        """
        return {
            name: {
                'brand': device.brand,
                'device_type': device.device_type,
            }
            for name, device in self._devices.items()
        }
    
    def get_all_names(self) -> list[str]:
        """
        Get a list of all registered device names.
        
        Returns:
            List of device names
        """
        return list(self._devices.keys())
    
    def clear(self) -> None:
        """Remove all devices from the registry."""
        self._devices.clear()
    
    def has_device(self, name: str) -> bool:
        """
        Check if a device with the given name is registered.
        
        Args:
            name: Name of the device to check
            
        Returns:
            True if device exists, False otherwise
        """
        return name.strip() in self._devices if name else False

