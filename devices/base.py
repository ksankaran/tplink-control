"""
Abstract base class for smart device adapters.

This module defines the common interface that all device adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class SmartDevice(ABC):
    """
    Abstract base class for all smart device adapters.
    
    All device adapters must inherit from this class and implement
    the required methods. Optional methods can be implemented if
    the device supports those features.
    """
    
    @abstractmethod
    async def turn_on(self) -> None:
        """
        Turn the device on.
        
        Raises:
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If the device operation fails
        """
        pass
    
    @abstractmethod
    async def turn_off(self) -> None:
        """
        Turn the device off.
        
        Raises:
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If the device operation fails
        """
        pass
    
    @abstractmethod
    async def is_on(self) -> bool:
        """
        Check if the device is currently on.
        
        Returns:
            True if the device is on, False if off
            
        Raises:
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If unable to retrieve device state
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device.
        
        Returns:
            Dictionary containing device status information.
            Must include at least:
            - 'is_on': bool - Whether device is on or off
            - 'device_type': str - Type of device (e.g., 'plug', 'light')
            - 'brand': str - Brand name (e.g., 'tplink', 'hue')
            
        Raises:
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If unable to retrieve device status
        """
        pass
    
    async def set_brightness(self, level: int) -> None:
        """
        Set the brightness level of the device (0-100).
        
        This is an optional method. If the device doesn't support
        brightness control, raise NotImplementedError.
        
        Args:
            level: Brightness level from 0 to 100
            
        Raises:
            NotImplementedError: If device doesn't support brightness control
            ValueError: If brightness level is out of range
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If the device operation fails
        """
        raise NotImplementedError("This device does not support brightness control")
    
    async def set_color(self, color: str) -> None:
        """
        Set the color of the device.
        
        This is an optional method. If the device doesn't support
        color control, raise NotImplementedError.
        
        Args:
            color: Color in hex format (e.g., '#FF0000') or color name
            
        Raises:
            NotImplementedError: If device doesn't support color control
            DeviceConnectionError: If unable to connect to the device
            DeviceError: If the device operation fails
        """
        raise NotImplementedError("This device does not support color control")
    
    @property
    @abstractmethod
    def device_type(self) -> str:
        """
        Return the type of device (e.g., 'plug', 'light', 'strip').
        
        Returns:
            String describing the device type
        """
        pass
    
    @property
    @abstractmethod
    def brand(self) -> str:
        """
        Return the brand name of the device.
        
        Returns:
            String with the brand name (e.g., 'tplink', 'hue', 'nanoleaf')
        """
        pass


class DeviceError(Exception):
    """Base exception for device-related errors."""
    pass


class DeviceConnectionError(DeviceError):
    """Raised when unable to connect to a device."""
    pass

