# Agent Documentation for TP-Link Control

## Project Overview

This is a simple web application built with FastAPI that provides a web interface to control a TP-Link Kasa smart plug. The application serves a single-page web UI with a toggle button to turn the connected device on or off.

## Technology Stack

- **Framework**: FastAPI 0.128.0
- **ASGI Server**: Uvicorn 0.39.0
- **Device Control**: python-kasa 0.7.7
- **Configuration**: python-dotenv 1.2.1
- **Python Version**: 3.8+ (inferred from dependencies)

## Architecture

### Application Structure

```
tplink-control/
├── app.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # User documentation
├── .env                # Environment configuration (not in repo)
└── venv/               # Virtual environment
```

### Core Components

1. **FastAPI Application** (`app.py`)
   - Single-file application with minimal dependencies
   - Serves HTML directly from route handlers
   - Uses async/await for device communication

2. **Device Interface** (`get_plug()` function)
   - Creates and initializes a `SmartPlug` instance
   - Updates device state before returning
   - Uses device IP from environment variable

3. **Web Interface**
   - Single-page HTML application
   - Embedded CSS styling with modern gradient design
   - Christmas tree theme (🎄)
   - Responsive design with viewport meta tag

## API Endpoints

### GET `/`
- **Purpose**: Main page displaying device status and toggle button
- **Response**: HTML page with current device state
- **Behavior**: 
  - Fetches current device state
  - Displays "Turn On" or "Turn Off" button based on current state
  - Shows current status (ON/OFF)

### POST `/toggle`
- **Purpose**: Toggle device power state
- **Method**: POST
- **Behavior**:
  - Checks current device state
  - Toggles to opposite state (on → off, off → on)
  - Redirects back to home page (303 redirect)
- **Response**: HTTP 303 redirect to `/`

## Configuration

### Environment Variables

- **DEVICE_IP** (required): IP address of the TP-Link Kasa smart plug on the local network
  - Must be set in `.env` file or environment
  - Application raises `ValueError` if not provided

### Setup Requirements

1. Device must be on the same network as the application
2. Device must be set up via the Kasa app first
3. Device IP can be discovered using `kasa discover` command

## Key Design Decisions

1. **Single-file architecture**: All application logic in `app.py` for simplicity
2. **Inline HTML/CSS**: No separate template files or static assets
3. **Form-based POST**: Uses HTML form submission instead of JavaScript/AJAX
4. **Server-side rendering**: Device state fetched on each page load
5. **Synchronous redirect**: Uses 303 redirect after toggle for immediate feedback

## Potential Extensions for AI Agents

### Areas for Enhancement

1. **API Endpoints**
   - Add JSON API endpoints (`/api/status`, `/api/toggle`) for programmatic access
   - Add device information endpoint (power consumption, device name, etc.)

2. **Error Handling**
   - Add try/except blocks for device connection failures
   - Handle network timeouts gracefully
   - Provide user-friendly error messages

3. **State Management**
   - Add device state caching to reduce API calls
   - Implement WebSocket for real-time updates
   - Add device state history/logging

4. **Multi-device Support**
   - Support multiple smart plugs
   - Device selection interface
   - Device grouping/rooms

5. **Scheduling**
   - Add scheduled on/off times
   - Timer functionality
   - Automation rules

6. **Security**
   - Add authentication/authorization
   - Rate limiting
   - Input validation

7. **Testing**
   - Unit tests for device control logic
   - Integration tests with mock devices
   - End-to-end tests

8. **Monitoring**
   - Health check endpoint
   - Device connectivity monitoring
   - Usage statistics

## Code Patterns

### Async Device Communication
```python
async def get_plug():
    plug = SmartPlug(DEVICE_IP)
    await plug.update()
    return plug
```

### HTML Response with Dynamic Content
```python
@app.get("/", response_class=HTMLResponse)
async def index():
    plug = await get_plug()
    is_on = plug.is_on
    # ... HTML template with f-strings ...
```

### Form-based Toggle with Redirect
```python
@app.post("/toggle")
async def toggle():
    plug = await get_plug()
    if plug.is_on:
        await plug.turn_off()
    else:
        await plug.turn_on()
    return RedirectResponse(url="/", status_code=303)
```

## Dependencies Analysis

- **fastapi**: Web framework for building APIs and web apps
- **python-kasa**: Library for controlling TP-Link Kasa devices
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

## Notes for AI Agents

- The application is intentionally minimal and focused on a single use case
- No database or persistent storage is used
- All state is fetched from the device in real-time
- The UI is designed for simplicity over feature richness
- Error handling is minimal - consider adding robust error handling for production use
- The application assumes the device is always reachable on the network

