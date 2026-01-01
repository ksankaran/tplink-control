"""
Philips Hue device adapter.

This adapter uses the aiohue library to control Philips Hue smart lights.
"""

from typing import Dict, Any, Optional
from aiohue import HueBridgeV2
from aiohue.errors import Unauthorized, BridgeBusy, AiohueException
from .base import SmartDevice, DeviceError, DeviceConnectionError


class HueDevice(SmartDevice):
    """
    Adapter for Philips Hue smart lights.
    
    Supports individual lights or light groups connected to a Hue Bridge.
    Requires bridge IP address and API key (app key).
    """
    
    def __init__(
        self,
        bridge_ip: str,
        api_key: str,
        light_id: Optional[str] = None,
        group_id: Optional[str] = None,
        device_id: Optional[str] = None
    ):
        """
        Initialize Philips Hue device adapter.
        
        Args:
            bridge_ip: IP address of the Hue Bridge on the local network
            api_key: API key (app key) for authenticating with the bridge
            light_id: Optional ID of a specific light to control
            group_id: Optional ID of a light group to control
            device_id: Optional device identifier (for future use with device registry)
            
        Raises:
            ValueError: If bridge_ip or api_key is empty, or both light_id and group_id are provided
        """
        if not bridge_ip or not bridge_ip.strip():
            raise ValueError("bridge_ip is required and cannot be empty")
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")
        if light_id and group_id:
            raise ValueError("Cannot specify both light_id and group_id. Use one or the other.")
        if not light_id and not group_id:
            raise ValueError("Either light_id or group_id must be provided")
        
        self._bridge_ip = bridge_ip.strip()
        self._api_key = api_key.strip()
        self._light_id = light_id
        self._group_id = group_id
        self._device_id = device_id
        self._bridge: Optional[HueBridgeV2] = None
        self._initialized = False
    
    async def _get_bridge(self) -> HueBridgeV2:
        """
        Get or create the Hue Bridge instance and initialize if needed.
        
        Returns:
            Initialized HueBridgeV2 instance
            
        Raises:
            DeviceConnectionError: If unable to connect to the bridge
        """
        try:
            if self._bridge is None:
                self._bridge = HueBridgeV2(self._bridge_ip, self._api_key)
            
            if not self._initialized:
                await self._bridge.initialize()
                self._initialized = True
            
            return self._bridge
        except Unauthorized as e:
            raise DeviceConnectionError(
                f"Unauthorized access to Hue Bridge at {self._bridge_ip}. "
                "Please check your API key."
            ) from e
        except (BridgeBusy, AiohueException) as e:
            raise DeviceConnectionError(
                f"Failed to connect to Hue Bridge at {self._bridge_ip}: {str(e)}"
            ) from e
        except Exception as e:
            raise DeviceConnectionError(
                f"Failed to connect to Hue Bridge at {self._bridge_ip}: {str(e)}"
            ) from e
    
    async def _get_light_resource(self):
        """
        Get the light resource to control.
        
        Returns:
            Light resource object
        """
        bridge = await self._get_bridge()
        
        if self._light_id:
            lights = await bridge.lights.get_all()
            if self._light_id not in lights:
                raise DeviceError(f"Light '{self._light_id}' not found on bridge")
            return lights[self._light_id]
        else:
            raise DeviceError("Light ID is required for individual light control")
    
    async def _get_group_resource(self):
        """
        Get the group resource to control.
        
        Returns:
            Group resource object
        """
        bridge = await self._get_bridge()
        
        if self._group_id:
            groups = await bridge.groups.get_all()
            if self._group_id not in groups:
                raise DeviceError(f"Group '{self._group_id}' not found on bridge")
            return groups[self._group_id]
        else:
            raise DeviceError("Group ID is required for group control")
    
    async def turn_on(self) -> None:
        """Turn the Hue light(s) on."""
        try:
            bridge = await self._get_bridge()
            if self._group_id:
                # Control group
                await bridge.groups.turn_on(self._group_id)
            else:
                # Control individual light
                await bridge.lights.turn_on(self._light_id)
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn on Hue device: {str(e)}") from e
    
    async def turn_off(self) -> None:
        """Turn the Hue light(s) off."""
        try:
            bridge = await self._get_bridge()
            if self._group_id:
                # Control group
                await bridge.groups.turn_off(self._group_id)
            else:
                # Control individual light
                await bridge.lights.turn_off(self._light_id)
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to turn off Hue device: {str(e)}") from e
    
    async def is_on(self) -> bool:
        """Check if the Hue light(s) are currently on."""
        try:
            if self._group_id:
                resource = await self._get_group_resource()
            else:
                resource = await self._get_light_resource()
            # Get the current state
            state = await resource.get()
            return state.is_on
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Hue device state: {str(e)}") from e
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Hue device.
        
        Returns:
            Dictionary containing device status information
        """
        try:
            if self._group_id:
                resource = await self._get_group_resource()
            else:
                resource = await self._get_light_resource()
            
            state = await resource.get()
            
            status = {
                'is_on': state.is_on,
                'device_type': self.device_type,
                'brand': self.brand,
                'bridge_ip': self._bridge_ip,
            }
            
            # Add brightness if available
            if hasattr(state, 'dimming') and state.dimming:
                brightness = state.dimming.brightness if hasattr(state.dimming, 'brightness') else state.dimming
                status['brightness'] = brightness
            
            # Add color if available
            if hasattr(state, 'color') and state.color:
                status['color'] = {
                    'xy': getattr(state.color, 'xy', None),
                    'gamut': getattr(state.color, 'gamut', None),
                }
            
            # Add metadata
            if self._group_id:
                status['group_id'] = self._group_id
                status['name'] = getattr(state, 'metadata', {}).get('name', f"Group {self._group_id}")
            else:
                status['light_id'] = self._light_id
                status['name'] = getattr(state, 'metadata', {}).get('name', f"Light {self._light_id}")
            
            return status
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to get Hue device status: {str(e)}") from e
    
    async def set_brightness(self, level: int) -> None:
        """
        Set the brightness level of the Hue light(s) (0-100).
        
        Args:
            level: Brightness level from 0 to 100
            
        Raises:
            ValueError: If brightness level is out of range
        """
        if not 0 <= level <= 100:
            raise ValueError("Brightness level must be between 0 and 100")
        
        try:
            bridge = await self._get_bridge()
            # Hue API v2 uses 0-100 scale for brightness
            if self._group_id:
                await bridge.groups.set_brightness(self._group_id, level)
            else:
                await bridge.lights.set_brightness(self._light_id, level)
        except DeviceConnectionError:
            raise
        except Exception as e:
            raise DeviceError(f"Failed to set brightness: {str(e)}") from e
    
    async def set_color(self, color: str) -> None:
        """
        Set the color of the Hue light(s).
        
        Args:
            color: Color in hex format (e.g., '#FF0000') or color name
        """
        try:
            bridge = await self._get_bridge()
            # For now, we'll support hex colors
            # Convert hex to RGB, then to xy coordinates
            if color.startswith('#'):
                hex_color = color[1:]
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                # Simple RGB to xy conversion (simplified)
                # In production, you'd want proper color space conversion
                # For now, we'll use a basic approximation
                # Hue API v2 uses xy color coordinates
                if self._group_id:
                    await bridge.groups.set_color(self._group_id, xy=(r, g))
                else:
                    await bridge.lights.set_color(self._light_id, xy=(r, g))
            else:
                raise ValueError(f"Color format '{color}' not supported. Use hex format like '#FF0000'")
        except DeviceConnectionError:
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
        return 'hue'

