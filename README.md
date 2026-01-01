# Smart Device Control

A simple web app to control your smart devices with a toggle button. Currently supports TP-Link Kasa devices, with architecture in place for extending to other smart device brands.

## Features

- **Simple Web Interface**: Clean, modern UI for controlling your devices
- **Device Adapter Architecture**: Extensible design for supporting multiple device brands
- **Backward Compatible**: Existing `.env` configuration still works
- **Error Handling**: User-friendly error messages for connection issues

## Setup

1. Clone and install dependencies:
```bash
git clone <your-repo-url>
cd tplink-control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Find your device IP address (for TP-Link devices):
```bash
kasa discover
```
This will scan your network and show all Kasa devices with their IP addresses.

3. Configure your device(s):

**Option A: Using environment variable (simple, backward compatible)**
```bash
echo "DEVICE_IP=<your-device-ip>" > .env
```

**Option B: Using JSON configuration file (for multiple devices)**
Create a `.devices.json` file:
```json
{
  "default": {
    "type": "tplink",
    "device_ip": "192.168.1.100"
  }
}
```

4. Run the app:
```bash
python app.py
```

5. Open http://localhost:8000 in your browser.

## Project Structure

```
tplink-control/
├── app.py                 # Main FastAPI application
├── config.py              # Configuration management
├── devices/               # Device adapters
│   ├── __init__.py
│   ├── base.py           # Abstract device interface
│   ├── tplink.py          # TP-Link Kasa adapter
│   └── registry.py       # Device registry
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment configuration (optional)
└── .devices.json         # JSON device configuration (optional)
```

## Architecture

The application uses a device adapter pattern that allows for easy extension to support multiple smart device brands:

- **Abstract Device Interface** (`devices/base.py`): Defines the common interface all device adapters must implement
- **Device Adapters** (`devices/tplink.py`, etc.): Brand-specific implementations
- **Device Registry** (`devices/registry.py`): Manages multiple device instances
- **Configuration** (`config.py`): Handles device configuration from environment variables or JSON files

## Requirements

- Python 3.8+
- Smart device on the same network (currently TP-Link Kasa)
- Device must be set up via the manufacturer's app first

## Supported Devices

### Currently Supported
- **TP-Link Kasa**: Smart plugs and switches

### Coming Soon
- Philips Hue
- Nanoleaf
- Geeni
- Cree
- Wyze
- Roku Smart Lights

## Configuration

### Environment Variables

- **DEVICE_IP** (optional): IP address of your TP-Link device
  - Used for backward compatibility
  - Creates a "default" device automatically

### JSON Configuration

Create a `.devices.json` file to manage multiple devices:

```json
{
  "default": {
    "type": "tplink",
    "device_ip": "192.168.1.100"
  },
  "christmas-tree": {
    "type": "tplink",
    "device_ip": "192.168.1.101"
  }
}
```

## Usage

### Web Interface

Navigate to `http://localhost:8000` to see the device control interface. You can specify a device using the `device` query parameter:

- `http://localhost:8000/?device=default` - Control the default device
- `http://localhost:8000/?device=christmas-tree` - Control a named device

### API Endpoints

- `GET /` - Display device status and control interface
- `POST /toggle` - Toggle device power state

## Error Handling

The application includes error handling for:
- Device connection failures
- Network timeouts
- Invalid device configurations

Error messages are displayed in a user-friendly format in the web interface.

## Development

The codebase is structured to make it easy to add support for new device brands. To add a new device adapter:

1. Create a new adapter class in `devices/` that inherits from `SmartDevice`
2. Implement the required methods: `turn_on()`, `turn_off()`, `is_on()`, `get_status()`
3. Register the device type in the configuration system

## License

See LICENSE file for details.
