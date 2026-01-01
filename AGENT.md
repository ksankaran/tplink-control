# Agent Documentation for Smart Device Control

## Project Overview

This is a web application built with FastAPI that provides a unified interface to control smart devices from various brands. The application uses a device adapter pattern to support multiple device types while maintaining a consistent API. Currently supports TP-Link Kasa, Philips Hue, Nanoleaf, Geeni, and Cree devices.

## Technology Stack

- **Framework**: FastAPI 0.128.0
- **ASGI Server**: Uvicorn 0.39.0
- **Device Control Libraries**:
  - python-kasa 0.7.7 (TP-Link Kasa)
  - aiohue 4.8.0 (Philips Hue)
  - nanoleafapi 2.1.2 (Nanoleaf)
  - tinytuya 1.17.4 (Geeni, Cree - Tuya protocol)
- **Configuration**: python-dotenv 1.2.1
- **Python Version**: 3.8+

## Architecture

### Application Structure

```
tplink-control/
├── app.py                 # Main FastAPI application
├── config.py              # Configuration management
├── devices/               # Device adapters module
│   ├── __init__.py       # Module exports
│   ├── base.py           # Abstract device interface
│   ├── tplink.py         # TP-Link Kasa adapter
│   ├── hue.py            # Philips Hue adapter
│   ├── nanoleaf.py       # Nanoleaf adapter
│   ├── geeni.py          # Geeni adapter (Tuya protocol)
│   ├── cree.py           # Cree adapter (Tuya protocol)
│   └── registry.py       # Device registry
├── requirements.txt       # Python dependencies
├── README.md             # User documentation
├── AGENT.md              # This file
├── .env                  # Environment configuration (optional)
└── .devices.json         # JSON device configuration (optional)
```

### Core Components

1. **FastAPI Application** (`app.py`)
   - Main application entry point
   - Initializes device registry on startup
   - Supports multiple device types from configuration
   - Serves HTML directly from route handlers
   - Uses async/await for device communication
   - Enhanced error handling with user-friendly messages

2. **Abstract Device Interface** (`devices/base.py`)
   - Defines `SmartDevice` abstract base class
   - Required methods: `turn_on()`, `turn_off()`, `is_on()`, `get_status()`
   - Optional methods: `set_brightness()`, `set_color()`
   - Custom exceptions: `DeviceError`, `DeviceConnectionError`
   - All methods are async with proper type hints

3. **Device Adapters**
   - **TPLinkDevice** (`devices/tplink.py`): TP-Link Kasa devices
   - **HueDevice** (`devices/hue.py`): Philips Hue lights and groups
   - **NanoleafDevice** (`devices/nanoleaf.py`): Nanoleaf Light Panels, Canvas, Shapes
   - **GeeniDevice** (`devices/geeni.py`): Geeni smart lights (Tuya protocol)
   - **CreeDevice** (`devices/cree.py`): Cree Connected smart lights (Tuya protocol)
   - All adapters implement `SmartDevice` interface
   - Handle device-specific communication protocols
   - Implement error handling and connection management

4. **Device Registry** (`devices/registry.py`)
   - Manages multiple device instances
   - Provides device registration, retrieval, and listing
   - Supports device lookup by name

5. **Configuration Management** (`config.py`)
   - Loads device configuration from JSON file or environment variables
   - Maintains backward compatibility with `.env` setup
   - Supports multiple device configurations
   - Handles different device types with type-specific parameters

6. **Web Interface**
   - Single-page HTML application
   - Embedded CSS styling with modern gradient design
   - Responsive design with viewport meta tag
   - Error display for connection issues
   - Schedule management UI for TP-Link devices

7. **Schedule Management** (TP-Link specific)
   - Schedule on/off times for TP-Link devices
   - Day-of-week selection for recurring schedules
   - Add, view, and delete schedules
   - Integrated with device registry system

## API Endpoints

### GET `/`
- **Purpose**: Main page displaying device status and toggle button
- **Query Parameters**: 
  - `device` (optional): Name of device to control (defaults to "default")
- **Response**: HTML page with current device state
- **Behavior**: 
  - Fetches current device state from registry
  - Displays "Turn On" or "Turn Off" button based on current state
  - Shows current status (ON/OFF)
  - Displays device name/alias
  - Shows error page if device connection fails

### POST `/toggle`
- **Purpose**: Toggle device power state
- **Method**: POST
- **Form Data**:
  - `device` (optional): Name of device to toggle (defaults to "default")
- **Behavior**:
  - Retrieves device from registry
  - Checks current device state
  - Toggles to opposite state (on → off, off → on)
  - Redirects back to home page (303 redirect)
- **Response**: HTTP 303 redirect to `/`
- **Error Responses**:
  - 404: Device not found
  - 503: Device connection error
  - 500: Device operation error

### GET `/schedules` (TP-Link specific)
- **Purpose**: Display schedule management interface for TP-Link devices
- **Query Parameters**:
  - `device` (optional): Name of TP-Link device (defaults to "default")
- **Response**: HTML page with list of schedules and form to add new schedules
- **Behavior**:
  - Retrieves TP-Link device from registry
  - Fetches existing schedules from device
  - Displays schedule list with time, action, and days
  - Provides form to add new schedules
- **Error Responses**:
  - 400: Device is not a TP-Link device
  - 404: Device not found
  - 503: Device connection error

### POST `/schedules/add` (TP-Link specific)
- **Purpose**: Add a new schedule to a TP-Link device
- **Method**: POST
- **Form Data**:
  - `device` (optional): Name of TP-Link device (defaults to "default")
  - `time` (required): Time in HH:MM format
  - `action` (required): "on" or "off"
  - `days` (optional): List of day numbers (0=Mon, 6=Sun)
- **Behavior**:
  - Creates a schedule rule on the TP-Link device
  - Enables global scheduling if not already enabled
  - Redirects to schedules page
- **Response**: HTTP 303 redirect to `/schedules?device={device}`
- **Error Responses**:
  - 400: Device is not a TP-Link device or invalid input
  - 404: Device not found
  - 503: Device connection error

### POST `/schedules/delete` (TP-Link specific)
- **Purpose**: Delete a schedule from a TP-Link device
- **Method**: POST
- **Form Data**:
  - `device` (optional): Name of TP-Link device (defaults to "default")
  - `rule_id` (required): ID of the schedule rule to delete
- **Behavior**:
  - Deletes the specified schedule rule from the TP-Link device
  - Redirects to schedules page
- **Response**: HTTP 303 redirect to `/schedules?device={device}`
- **Error Responses**:
  - 400: Device is not a TP-Link device
  - 404: Device not found
  - 503: Device connection error

## Configuration

### Environment Variables

- **DEVICE_IP** (optional): IP address of the TP-Link Kasa device on the local network
  - Used for backward compatibility
  - Automatically creates a "default" device if set
  - Application will raise `ValueError` if neither `.env` nor `.devices.json` provides configuration

### JSON Configuration File

Create a `.devices.json` file to manage multiple devices. The configuration format varies by device type:

#### TP-Link Kasa
```json
{
  "device-name": {
    "type": "tplink",
    "device_ip": "192.168.1.100"
  }
}
```

#### Philips Hue
```json
{
  "device-name": {
    "type": "hue",
    "bridge_ip": "192.168.1.101",
    "api_key": "your-api-key",
    "light_id": "light-id"  // OR "group_id": "group-id"
  }
}
```

#### Nanoleaf
```json
{
  "device-name": {
    "type": "nanoleaf",
    "device_ip": "192.168.1.102",
    "auth_token": "your-auth-token"
  }
}
```

#### Geeni (Tuya Protocol)
```json
{
  "device-name": {
    "type": "geeni",
    "device_id": "your-device-id",
    "device_ip": "192.168.1.103",
    "local_key": "your-local-key",
    "device_version": "3.3"  // Optional, defaults to "3.3"
  }
}
```

#### Cree Connected (Tuya Protocol)
```json
{
  "device-name": {
    "type": "cree",
    "device_id": "your-device-id",
    "device_ip": "192.168.1.104",
    "local_key": "your-local-key",
    "device_version": "3.3"  // Optional, defaults to "3.3"
  }
}
```

The configuration system:
1. First tries to load from `.devices.json`
2. Falls back to environment variables for backward compatibility
3. Raises error if no configuration found

### Setup Requirements

1. Device must be on the same network as the application
2. Device must be set up via the manufacturer's app first
3. Device IP can be discovered using brand-specific tools:
   - TP-Link: `kasa discover`
   - Hue: Check router or Hue app
   - Nanoleaf: Check router or Nanoleaf app
   - Geeni/Cree: Use Tuya discovery tools

## Key Design Decisions

1. **Device Adapter Pattern**: Extensible architecture allowing easy addition of new device brands
2. **Abstract Base Class**: Ensures consistent interface across all device types
3. **Device Registry**: Centralized management of multiple device instances
4. **Backward Compatibility**: Existing `.env` setup continues to work
5. **Inline HTML/CSS**: No separate template files or static assets for simplicity
6. **Form-based POST**: Uses HTML form submission instead of JavaScript/AJAX
7. **Server-side rendering**: Device state fetched on each page load
8. **Enhanced Error Handling**: User-friendly error messages with proper HTTP status codes
9. **Type-Specific Configuration**: Each device type has its own configuration schema

## Device Adapter Pattern

### Creating a New Device Adapter

To add support for a new device brand:

1. Create a new file in `devices/` (e.g., `devices/newbrand.py`)
2. Import and inherit from `SmartDevice`:
```python
from devices.base import SmartDevice, DeviceError, DeviceConnectionError

class NewBrandDevice(SmartDevice):
    # Implementation
```

3. Implement required methods:
   - `async def turn_on(self) -> None`
   - `async def turn_off(self) -> None`
   - `async def is_on(self) -> bool`
   - `async def get_status(self) -> Dict[str, Any]`
   - `@property def device_type(self) -> str`
   - `@property def brand(self) -> str`

4. Implement optional methods if device supports them:
   - `async def set_brightness(self, level: int) -> None`
   - `async def set_color(self, color: str) -> None`

5. Register the adapter in `devices/__init__.py`
6. Update `app.py` to support the new device type in `initialize_devices()`
7. Update configuration system if needed

## Code Patterns

### Device Adapter Implementation
```python
from devices.base import SmartDevice, DeviceError, DeviceConnectionError

class MyDevice(SmartDevice):
    def __init__(self, config_param: str):
        self._config = config_param
    
    async def turn_on(self) -> None:
        try:
            # Device-specific implementation
            pass
        except ConnectionError as e:
            raise DeviceConnectionError(f"Connection failed: {e}") from e
        except Exception as e:
            raise DeviceError(f"Operation failed: {e}") from e
    
    # ... implement other required methods
```

### Device Registry Usage
```python
from devices.registry import DeviceRegistry
from devices.tplink import TPLinkDevice

registry = DeviceRegistry()
device = TPLinkDevice(device_ip="192.168.1.100")
registry.register("default", device)

# Later, retrieve device
device = registry.get("default")
await device.turn_on()
```

### Configuration Loading
```python
from config import load_device_config, get_device_config

# Load all configurations
config = load_device_config()

# Get specific device config
device_config = get_device_config("default")
```

### Error Handling in Routes
```python
from devices import DeviceConnectionError, DeviceError

@app.get("/")
async def index(device: str = "default"):
    try:
        smart_device = await get_device(device)
        is_on = await smart_device.is_on()
        # ... render UI
    except DeviceConnectionError as e:
        # Show user-friendly error page
        return HTMLResponse(content=error_html, status_code=503)
```

## Dependencies Analysis

- **fastapi**: Web framework for building APIs and web apps
- **python-kasa**: Library for controlling TP-Link Kasa devices
- **aiohue**: Async library for controlling Philips Hue devices via Hue Bridge
- **nanoleafapi**: Python wrapper for Nanoleaf OpenAPI
- **tinytuya**: Library for controlling Tuya-based devices (Geeni, Cree)
- **python-dotenv**: Environment variable management
- **uvicorn**: ASGI server for running FastAPI

## Running the Application

```bash
# Development
python app.py

# Production (with uvicorn directly)
uvicorn app:app --host 0.0.0.0 --port 8000
```

The application runs on `0.0.0.0:8000` by default, making it accessible from any network interface.

## Device-Specific Notes

### TP-Link Kasa
- Uses local network communication
- No authentication required
- Supports smart plugs and switches
- **Schedule Management**: Full support for scheduling on/off times
  - Create recurring schedules with day-of-week selection
  - View and manage existing schedules
  - Schedules are stored on the device itself

### Philips Hue
- Requires Hue Bridge on local network
- API key (username) required for authentication
- Supports individual lights and light groups
- Supports brightness and color control
- Uses aiohue library (async)

### Nanoleaf
- Direct device communication on port 16021
- Authentication token required
- Token generation requires holding power button for 5-7 seconds
- Supports brightness and color control

### Geeni / Cree (Tuya Protocol)
- Uses Tuya protocol for local control
- Requires device ID, IP address, and local key
- Local key can be obtained from Tuya IoT Platform
- Supports brightness and color control
- Uses tinytuya library

## Future Extensions

The architecture is designed to support:

1. **Additional Device Brands**: Easy to add via adapter pattern
   - Wyze (planned - Phase 3)
   - Roku Smart Lights (planned - Phase 3)

2. **Advanced Features** (partially implemented):
   - ✅ Brightness control for lights (Hue, Nanoleaf, Geeni, Cree)
   - ✅ Color control for RGB devices (Hue, Nanoleaf, Geeni, Cree)
   - ✅ Schedule management (TP-Link devices)
   - Device grouping/rooms (Hue groups supported)
   - Scheduling for other device types
   - Device discovery

3. **API Enhancements**:
   - JSON API endpoints for programmatic access
   - WebSocket support for real-time updates
   - Device information endpoints
   - Brightness/color control endpoints

4. **Testing**:
   - Unit tests for device adapters
   - Integration tests with mock devices
   - End-to-end tests

## Notes for AI Agents

- The application uses a device adapter pattern for extensibility
- All device communication is async
- Error handling is implemented with custom exceptions
- Configuration supports both environment variables and JSON files
- The architecture maintains backward compatibility
- Device state is fetched in real-time (no caching)
- The UI is intentionally simple and focused
- All device adapters must implement the `SmartDevice` interface
- The device registry manages device instances at runtime
- Configuration is loaded once at startup
- Each device type has specific configuration requirements
- Tuya-based devices (Geeni, Cree) share similar implementation patterns
- Hue devices support both individual lights and groups
- Nanoleaf requires authentication token generation process
- **Schedule management is TP-Link specific**: The schedule endpoints only work with TP-Link devices
- Schedule functionality uses the underlying Kasa device directly via `_get_device()` method
- The schedule link only appears on the main page for TP-Link devices
- Schedule endpoints accept a `device` parameter to specify which TP-Link device to manage
