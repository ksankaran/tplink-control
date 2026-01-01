# Smart Device Control

A simple web app to control your smart devices with a toggle button. Supports multiple device brands including TP-Link Kasa, Philips Hue, Nanoleaf, Geeni, and Cree.

## Features

- **Simple Web Interface**: Clean, modern UI for controlling your devices
- **Multi-Device Support**: Control devices from multiple brands through a unified interface
- **Device Adapter Architecture**: Extensible design for supporting multiple device brands
- **Backward Compatible**: Existing `.env` configuration still works
- **Error Handling**: User-friendly error messages for connection issues
- **Brightness & Color Control**: Support for advanced features on compatible devices

## Setup

1. Clone and install dependencies:
```bash
git clone <your-repo-url>
cd tplink-control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure your device(s):

**Option A: Using environment variable (simple, backward compatible for TP-Link)**
```bash
echo "DEVICE_IP=<your-device-ip>" > .env
```

**Option B: Using JSON configuration file (for multiple devices)**
Create a `.devices.json` file (see Configuration section below for examples).

3. Run the app:
```bash
python app.py
```

4. Open http://localhost:8000 in your browser.

## Project Structure

```
tplink-control/
├── app.py                 # Main FastAPI application
├── config.py              # Configuration management
├── devices/               # Device adapters
│   ├── __init__.py
│   ├── base.py           # Abstract device interface
│   ├── tplink.py          # TP-Link Kasa adapter
│   ├── hue.py             # Philips Hue adapter
│   ├── nanoleaf.py        # Nanoleaf adapter
│   ├── geeni.py           # Geeni adapter (Tuya protocol)
│   ├── cree.py            # Cree adapter (Tuya protocol)
│   └── registry.py       # Device registry
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment configuration (optional)
└── .devices.json         # JSON device configuration (optional)
```

## Architecture

The application uses a device adapter pattern that allows for easy extension to support multiple smart device brands:

- **Abstract Device Interface** (`devices/base.py`): Defines the common interface all device adapters must implement
- **Device Adapters** (`devices/tplink.py`, `devices/hue.py`, etc.): Brand-specific implementations
- **Device Registry** (`devices/registry.py`): Manages multiple device instances
- **Configuration** (`config.py`): Handles device configuration from environment variables or JSON files

## Requirements

- Python 3.8+
- Smart device on the same network
- Device must be set up via the manufacturer's app first
- For Hue devices: Hue Bridge and API key required
- For Nanoleaf devices: Authentication token required
- For Geeni/Cree devices: Device ID and local key required (Tuya protocol)

## Supported Devices

### Currently Supported
- **TP-Link Kasa**: Smart plugs and switches
- **Philips Hue**: Smart lights (individual lights and groups)
- **Nanoleaf**: Light Panels, Canvas, and Shapes
- **Geeni**: Smart lights (Tuya protocol)
- **Cree Connected**: Smart lights (Tuya protocol)

### Coming Soon
- Wyze
- Roku Smart Lights

## Configuration

### Environment Variables

- **DEVICE_IP** (optional): IP address of your TP-Link device
  - Used for backward compatibility
  - Creates a "default" device automatically

### JSON Configuration

Create a `.devices.json` file to manage multiple devices. Here are examples for each device type:

#### TP-Link Kasa
```json
{
  "default": {
    "type": "tplink",
    "device_ip": "192.168.1.100"
  }
}
```

#### Philips Hue
```json
{
  "hue-light": {
    "type": "hue",
    "bridge_ip": "192.168.1.101",
    "api_key": "your-hue-api-key",
    "light_id": "light-id-here"
  },
  "hue-group": {
    "type": "hue",
    "bridge_ip": "192.168.1.101",
    "api_key": "your-hue-api-key",
    "group_id": "group-id-here"
  }
}
```

**Getting Hue API Key**: Press the button on your Hue Bridge, then make a POST request to `http://<bridge-ip>/api` with body `{"devicetype":"your-app-name"}`. The response will contain your username (API key).

#### Nanoleaf
```json
{
  "nanoleaf": {
    "type": "nanoleaf",
    "device_ip": "192.168.1.102",
    "auth_token": "your-auth-token"
  }
}
```

**Getting Nanoleaf Auth Token**: Hold the power button on your Nanoleaf device for 5-7 seconds, then make a POST request to `http://<device-ip>:16021/api/v1/new`. The response will contain your auth token.

#### Geeni (Tuya Protocol)
```json
{
  "geeni-light": {
    "type": "geeni",
    "device_id": "your-device-id",
    "device_ip": "192.168.1.103",
    "local_key": "your-local-key",
    "device_version": "3.3"
  }
}
```

**Getting Tuya Device Credentials**: Use the Tuya IoT Platform or tools like `tinytuya` scanner to discover device ID and local key.

#### Cree Connected (Tuya Protocol)
```json
{
  "cree-light": {
    "type": "cree",
    "device_id": "your-device-id",
    "device_ip": "192.168.1.104",
    "local_key": "your-local-key",
    "device_version": "3.3"
  }
}
```

#### Multiple Devices Example
```json
{
  "default": {
    "type": "tplink",
    "device_ip": "192.168.1.100"
  },
  "living-room-hue": {
    "type": "hue",
    "bridge_ip": "192.168.1.101",
    "api_key": "your-api-key",
    "light_id": "1"
  },
  "nanoleaf-panels": {
    "type": "nanoleaf",
    "device_ip": "192.168.1.102",
    "auth_token": "your-token"
  }
}
```

## Usage

### Web Interface

Navigate to `http://localhost:8000` to see the device control interface. You can specify a device using the `device` query parameter:

- `http://localhost:8000/?device=default` - Control the default device
- `http://localhost:8000/?device=hue-light` - Control a named device

### API Endpoints

- `GET /` - Display device status and control interface
- `POST /toggle` - Toggle device power state

## Device Features

### Basic Features (All Devices)
- Turn on/off
- Check current state
- Get device status

### Advanced Features (Supported Devices)
- **Brightness Control**: Hue, Nanoleaf, Geeni, Cree
- **Color Control**: Hue, Nanoleaf, Geeni, Cree

## Error Handling

The application includes error handling for:
- Device connection failures
- Network timeouts
- Invalid device configurations
- Authentication failures

Error messages are displayed in a user-friendly format in the web interface.

## Development

The codebase is structured to make it easy to add support for new device brands. To add a new device adapter:

1. Create a new adapter class in `devices/` that inherits from `SmartDevice`
2. Implement the required methods: `turn_on()`, `turn_off()`, `is_on()`, `get_status()`
3. Optionally implement: `set_brightness()`, `set_color()`
4. Register the device type in the configuration system
5. Update `app.py` to initialize the new device type

## License

See LICENSE file for details.
