"""
TP-Link Kasa device adapter.

This adapter uses the python-kasa library to control TP-Link Kasa smart devices.
"""

from typing import Dict, Any, Optional
from kasa import SmartPlug, SmartDevice as KasaDevice
from .base import SmartDevice, DeviceError, DeviceConnectionError


class TPLinkDevice(SmartDevice):
    """
    Adapter for TP-Link Kasa smart devices.
    
    Supports smart plugs and other TP-Link Kasa devices that use
    the same protocol.
    """
    
    def __init__(self, device_ip: str, device_id: Optional[str] = None):
        """
        Initialize TP-Link device adapter.
        
        Args:
            device_ip: IP address of the TP-Link device on the local network
            device_id: Optional device identifier (for future use with device registry)
            
        Raises:
            ValueError: If device_ip is empty or invalid
        """
        if not device_ip or not device_ip.strip():
            raise ValueError("device_ip is required and cannot be empty")
        
        self._device_ip = device_ip.strip()
        self._device_id = device_id
        self._kasa_device: Optional[KasaDevice] = None
    
    async def _get_device(self) -> KasaDevice:
        """
        Get or create the Kasa device instance and update its state.
        
        Returns:
            Kasa device instance with updated state
            
        Raises:
            DeviceConnectionError: If unable to connect to the device
        """
        try:
            if self._kasa_device is None:
                self._kasa_device = SmartPlug(self._device_ip)
            
            await self._kasa_device.update()
            return self._kasa_device
        except Exception as e:
            raise DeviceConnectionError(
                f"Failed to connect to TP-Link device at {self._device_ip}: {str(e)}"
            ) from e
    
    async def turn_on(self) -> None:
        """Turn the TP-Link device on."""
        try:
            device = await self._get_device()
            await device.turn_on()
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn on TP-Link device: {str(e)}") from e
    
    async def turn_off(self) -> None:
        """Turn the TP-Link device off."""
        try:
            device = await self._get_device()
            await device.turn_off()
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn off TP-Link device: {str(e)}") from e
    
    async def is_on(self) -> bool:
        """Check if the TP-Link device is currently on."""
        try:
            device = await self._get_device()
            return device.is_on
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get TP-Link device state: {str(e)}") from e
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the TP-Link device.
        
        Returns:
            Dictionary containing device status information
        """
        try:
            device = await self._get_device()
            return {
                'is_on': device.is_on,
                'device_type': self.device_type,
                'brand': self.brand,
                'device_ip': self._device_ip,
                'alias': getattr(device, 'alias', 'Unknown'),
                'model': getattr(device, 'model', 'Unknown'),
                'has_emeter': getattr(device, 'has_emeter', False),
            }
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get TP-Link device status: {str(e)}") from e
    
    @property
    def device_type(self) -> str:
        """Return the type of device."""
        # TP-Link devices can be plugs, switches, etc.
        # For now, we'll default to 'plug' since that's what the original app used
        return 'plug'
    
    @property
    def brand(self) -> str:
        """Return the brand name."""
        return 'tplink'
    
    @property
    def device_ip(self) -> str:
        """Get the device IP address."""
        return self._device_ip

