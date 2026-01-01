"""
Nanoleaf device adapter.

This adapter uses the nanoleafapi library to control Nanoleaf smart lights.
"""

from typing import Dict, Any, Optional
from nanoleafapi import Nanoleaf, NanoleafConnectionError, NanoleafRegistrationError
from .base import SmartDevice, DeviceError, DeviceConnectionError


class NanoleafDevice(SmartDevice):
    """
    Adapter for Nanoleaf smart lights.
    
    Supports Nanoleaf Light Panels, Canvas, and Shapes.
    Requires device IP address and authentication token.
    """
    
    def __init__(
        self,
        device_ip: str,
        auth_token: str,
        device_id: Optional[str] = None
    ):
        """
        Initialize Nanoleaf device adapter.
        
        Args:
            device_ip: IP address of the Nanoleaf device on the local network
            auth_token: Authentication token for the device
            device_id: Optional device identifier (for future use with device registry)
            
        Raises:
            ValueError: If device_ip or auth_token is empty
            DeviceConnectionError: If unable to connect to the device
        """
        if not device_ip or not device_ip.strip():
            raise ValueError("device_ip is required and cannot be empty")
        if not auth_token or not auth_token.strip():
            raise ValueError("auth_token is required and cannot be empty")
        
        self._device_ip = device_ip.strip()
        self._auth_token = auth_token.strip()
        self._device_id = device_id
        self._nanoleaf: Optional[Nanoleaf] = None
    
    async def _get_device(self) -> Nanoleaf:
        """
        Get or create the Nanoleaf device instance.
        
        Returns:
            Nanoleaf device instance
            
        Raises:
            DeviceConnectionError: If unable to connect to the device
        """
        try:
            if self._nanoleaf is None:
                # Note: nanoleafapi connects immediately on init
                # We'll catch connection errors and convert them
                self._nanoleaf = Nanoleaf(
                    self._device_ip,
                    self._auth_token,
                    print_errors=False
                )
            return self._nanoleaf
        except NanoleafConnectionError as e:
            raise DeviceConnectionError(
                f"Failed to connect to Nanoleaf device at {self._device_ip}. "
                "Please check the IP address and ensure the device is powered on."
            ) from e
        except NanoleafRegistrationError as e:
            raise DeviceConnectionError(
                f"Authentication failed for Nanoleaf device at {self._device_ip}. "
                "Please check your auth token. You may need to hold the power button "
                "for 5-7 seconds and generate a new token."
            ) from e
        except Exception as e:
            raise DeviceConnectionError(
                f"Failed to connect to Nanoleaf device at {self._device_ip}: {str(e)}"
            ) from e
    
    async def turn_on(self) -> None:
        """Turn the Nanoleaf device on."""
        try:
            device = await self._get_device()
            result = device.power_on()
            if not result:
                raise DeviceError("Failed to turn on Nanoleaf device")
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn on Nanoleaf device: {str(e)}") from e
    
    async def turn_off(self) -> None:
        """Turn the Nanoleaf device off."""
        try:
            device = await self._get_device()
            result = device.power_off()
            if not result:
                raise DeviceError("Failed to turn off Nanoleaf device")
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn off Nanoleaf device: {str(e)}") from e
    
    async def is_on(self) -> bool:
        """Check if the Nanoleaf device is currently on."""
        try:
            device = await self._get_device()
            info = device.get_info()
            return info.get('state', {}).get('on', {}).get('value', False)
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Nanoleaf device state: {str(e)}") from e
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Nanoleaf device.
        
        Returns:
            Dictionary containing device status information
        """
        try:
            device = await self._get_device()
            info = device.get_info()
            
            status = {
                'is_on': info.get('state', {}).get('on', {}).get('value', False),
                'device_type': self.device_type,
                'brand': self.brand,
                'device_ip': self._device_ip,
                'name': info.get('name', 'Unknown'),
                'model': info.get('model', 'Unknown'),
            }
            
            # Add brightness if available
            brightness = info.get('state', {}).get('brightness', {})
            if brightness:
                status['brightness'] = brightness.get('value', 0)
                status['brightness_min'] = brightness.get('min', 0)
                status['brightness_max'] = brightness.get('max', 100)
            
            # Add color if available
            color = info.get('state', {}).get('colorMode', None)
            if color:
                status['color_mode'] = color
            
            # Add effect if available
            effect = info.get('effects', {}).get('select', None)
            if effect:
                status['current_effect'] = effect
            
            return status
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Nanoleaf device status: {str(e)}") from e
    
    async def set_brightness(self, level: int) -> None:
        """
        Set the brightness level of the Nanoleaf device (0-100).
        
        Args:
            level: Brightness level from 0 to 100
            
        Raises:
            ValueError: If brightness level is out of range
        """
        if not 0 <= level <= 100:
            raise ValueError("Brightness level must be between 0 and 100")
        
        try:
            device = await self._get_device()
            result = device.set_brightness(level)
            if not result:
                raise DeviceError("Failed to set brightness")
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to set brightness: {str(e)}") from e
    
    async def set_color(self, color: str) -> None:
        """
        Set the color of the Nanoleaf device.
        
        Args:
            color: Color in hex format (e.g., '#FF0000') or color name
        """
        try:
            device = await self._get_device()
            
            # Convert hex to RGB if needed
            if color.startswith('#'):
                hex_color = color[1:]
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                result = device.set_color((r, g, b))
            else:
                # Try to use predefined colors from nanoleafapi
                color_map = {
                    'red': device.RED,
                    'green': device.GREEN,
                    'blue': device.BLUE,
                    'yellow': device.YELLOW,
                    'orange': device.ORANGE,
                    'pink': device.PINK,
                    'purple': device.PURPLE,
                    'white': device.WHITE,
                    'light_blue': device.LIGHT_BLUE,
                }
                color_lower = color.lower()
                if color_lower in color_map:
                    result = device.set_color(color_map[color_lower])
                else:
                    raise ValueError(
                        f"Color '{color}' not supported. "
                        "Use hex format like '#FF0000' or a color name: "
                        f"{', '.join(color_map.keys())}"
                    )
            
            if not result:
                raise DeviceError("Failed to set color")
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
        return 'nanoleaf'

