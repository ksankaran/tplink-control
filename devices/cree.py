"""
Cree Connected device adapter (Tuya protocol).

This adapter uses the tinytuya library to control Cree Connected smart lights.
Cree Connected devices typically use the Tuya protocol, similar to Geeni.
"""

from typing import Dict, Any, Optional
from tinytuya import BulbDevice
from .base import SmartDevice, DeviceError, DeviceConnectionError


class CreeDevice(SmartDevice):
    """
    Adapter for Cree Connected smart lights (Tuya protocol).
    
    Supports Cree Connected smart bulbs and other Tuya-based devices.
    Requires device ID, device IP, and local key.
    """
    
    def __init__(
        self,
        device_id: str,
        device_ip: str,
        local_key: str,
        device_version: str = "3.3",
        device_id_alias: Optional[str] = None
    ):
        """
        Initialize Cree device adapter.
        
        Args:
            device_id: Tuya device ID
            device_ip: IP address of the device on the local network
            local_key: Local key for the device (obtained from Tuya app)
            device_version: Tuya protocol version (default: "3.3")
            device_id_alias: Optional device identifier (for future use with device registry)
            
        Raises:
            ValueError: If required parameters are empty
        """
        if not device_id or not device_id.strip():
            raise ValueError("device_id is required and cannot be empty")
        if not device_ip or not device_ip.strip():
            raise ValueError("device_ip is required and cannot be empty")
        if not local_key or not local_key.strip():
            raise ValueError("local_key is required and cannot be empty")
        
        self._device_id = device_id.strip()
        self._device_ip = device_ip.strip()
        self._local_key = local_key.strip()
        self._device_version = device_version
        self._device_id_alias = device_id_alias
        self._bulb: Optional[BulbDevice] = None
    
    async def _get_device(self) -> BulbDevice:
        """
        Get or create the BulbDevice instance.
        
        Returns:
            BulbDevice instance
            
        Raises:
            DeviceConnectionError: If unable to connect to the device
        """
        try:
            if self._bulb is None:
                self._bulb = BulbDevice(
                    self._device_id,
                    self._device_ip,
                    self._local_key,
                    version=self._device_version
                )
                # Set connection timeout
                self._bulb.set_socketTimeout(5.0)
            return self._bulb
        except Exception as e:
            raise DeviceConnectionError(
                f"Failed to connect to Cree device at {self._device_ip}: {str(e)}"
            ) from e
    
    async def turn_on(self) -> None:
        """Turn the Cree device on."""
        try:
            device = await self._get_device()
            device.turn_on()
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn on Cree device: {str(e)}") from e
    
    async def turn_off(self) -> None:
        """Turn the Cree device off."""
        try:
            device = await self._get_device()
            device.turn_off()
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn off Cree device: {str(e)}") from e
    
    async def is_on(self) -> bool:
        """Check if the Cree device is currently on."""
        try:
            device = await self._get_device()
            status = device.status()
            # Tuya devices typically use DPS (Data Points) for status
            # DPS 20 is usually the power state (True/False)
            # DPS 1 is also commonly used for power
            if 'dps' in status:
                dps = status['dps']
                # Try common power DPS keys
                if '20' in dps:
                    return bool(dps['20'])
                elif '1' in dps:
                    return bool(dps['1'])
                # If neither, check all boolean values
                for key, value in dps.items():
                    if isinstance(value, bool):
                        return value
            return False
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Cree device state: {str(e)}") from e
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Cree device.
        
        Returns:
            Dictionary containing device status information
        """
        try:
            device = await self._get_device()
            status = device.status()
            
            result = {
                'is_on': await self.is_on(),
                'device_type': self.device_type,
                'brand': self.brand,
                'device_id': self._device_id,
                'device_ip': self._device_ip,
            }
            
            # Add brightness if available
            if 'dps' in status:
                dps = status['dps']
                # DPS 22 is often brightness (0-1000 scale)
                if '22' in dps:
                    brightness_raw = dps['22']
                    # Convert from 0-1000 to 0-100 scale
                    result['brightness'] = int((brightness_raw / 1000) * 100)
                # DPS 2 is also sometimes brightness
                elif '2' in dps:
                    brightness_raw = dps['2']
                    if isinstance(brightness_raw, int) and brightness_raw > 100:
                        result['brightness'] = int((brightness_raw / 1000) * 100)
                    else:
                        result['brightness'] = brightness_raw
                
                # Add color information if available
                # DPS 5 is often color (hex string)
                if '5' in dps:
                    result['color'] = dps['5']
            
            # Add raw DPS data for debugging
            if 'dps' in status:
                result['raw_dps'] = status['dps']
            
            return result
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Cree device status: {str(e)}") from e
    
    async def set_brightness(self, level: int) -> None:
        """
        Set the brightness level of the Cree device (0-100).
        
        Args:
            level: Brightness level from 0 to 100
            
        Raises:
            ValueError: If brightness level is out of range
        """
        if not 0 <= level <= 100:
            raise ValueError("Brightness level must be between 0 and 100")
        
        try:
            device = await self._get_device()
            # Tuya devices typically use 0-1000 scale for brightness
            tuya_brightness = int((level / 100) * 1000)
            device.brightness(tuya_brightness)
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to set brightness: {str(e)}") from e
    
    async def set_color(self, color: str) -> None:
        """
        Set the color of the Cree device.
        
        Args:
            color: Color in hex format (e.g., '#FF0000')
        """
        try:
            device = await self._get_device()
            if color.startswith('#'):
                hex_color = color[1:]
                # Convert hex to RGB
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                device.colour_rgb(r, g, b)
            else:
                raise ValueError(f"Color format '{color}' not supported. Use hex format like '#FF0000'")
        except DeviceConnectionError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to set color: {str(e)}") from e
    
    @property
    def device_type(self) -> str:
        """Return the type of device."""
        return 'light'
    
    @property
    def brand(self) -> str:
        """Return the brand name."""
        return 'cree'

