import os
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv

from devices import TPLinkDevice, DeviceError, DeviceConnectionError
from devices.registry import DeviceRegistry
from config import load_device_config

load_dotenv()

app = FastAPI()

# Initialize device registry
device_registry = DeviceRegistry()

# Initialize default device from environment or config
def initialize_devices():
    """Initialize devices from configuration."""
    config = load_device_config()
    
    # If no config, try environment variable for backward compatibility
    device_ip = os.getenv("DEVICE_IP")
    if device_ip:
        default_device = TPLinkDevice(device_ip=device_ip)
        device_registry.register("default", default_device)
    elif config:
        # Load devices from config
        for name, device_config in config.items():
            device_type = device_config.get("type", "tplink")
            if device_type == "tplink":
                device_ip = device_config.get("device_ip")
                if device_ip:
                    device = TPLinkDevice(device_ip=device_ip, device_id=name)
                    device_registry.register(name, device)
    else:
        raise ValueError(
            "No device configuration found. Please set DEVICE_IP environment variable "
            "or create a .devices.json configuration file."
        )

# Initialize devices on startup
initialize_devices()

async def get_device(device_name: str = "default"):
    """
    Get a device from the registry.
    
    Args:
        device_name: Name of the device to retrieve (defaults to "default")
        
    Returns:
        SmartDevice instance
        
    Raises:
        HTTPException: If device is not found
    """
    device = device_registry.get(device_name)
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_name}' not found. Available devices: {', '.join(device_registry.get_all_names())}"
        )
    return device

@app.get("/", response_class=HTMLResponse)
async def index(device: str = "default"):
    """
    Main page displaying device status and toggle button.
    
    Args:
        device: Name of the device to control (defaults to "default")
    """
    try:
        smart_device = await get_device(device)
        is_on = await smart_device.is_on()
        device_info = await smart_device.get_status()
        device_display_name = device_info.get('alias', device)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Device Control</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: white;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                }}
                h1 {{
                    font-size: 2rem;
                    margin-bottom: 2rem;
                }}
                .tree {{
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }}
                .toggle {{
                    background: {'#22c55e' if is_on else '#64748b'};
                    border: none;
                    padding: 1rem 3rem;
                    font-size: 1.5rem;
                    border-radius: 50px;
                    cursor: pointer;
                    color: white;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                }}
                .toggle:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
                }}
                .status {{
                    margin-top: 1rem;
                    opacity: 0.7;
                }}
                .error {{
                    color: #ef4444;
                    margin-top: 1rem;
                    padding: 1rem;
                    background: rgba(239, 68, 68, 0.1);
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="tree">🎄</div>
                <h1>{device_display_name}</h1>
                <form action="/toggle" method="post">
                    <input type="hidden" name="device" value="{device}">
                    <button type="submit" class="toggle">
                        {'Turn Off' if is_on else 'Turn On'}
                    </button>
                </form>
                <p class="status">Currently: {'ON' if is_on else 'OFF'}</p>
            </div>
        </body>
        </html>
        """
        return html
    except DeviceConnectionError as e:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Connection Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: white;
                }}
                .container {{
                    text-align: center;
                    padding: 2rem;
                }}
                .error {{
                    color: #ef4444;
                    margin-top: 1rem;
                    padding: 1rem;
                    background: rgba(239, 68, 68, 0.1);
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">
                    <h2>Connection Error</h2>
                    <p>{str(e)}</p>
                    <p>Please check that your device is powered on and connected to the network.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=503)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/toggle")
async def toggle(device: str = Form("default")):
    """
    Toggle device power state.
    
    Args:
        device: Name of the device to toggle (defaults to "default")
    """
    try:
        smart_device = await get_device(device)
        is_on = await smart_device.is_on()
        
        if is_on:
            await smart_device.turn_off()
        else:
            await smart_device.turn_on()
        
        return RedirectResponse(url=f"/?device={device}", status_code=303)
    except DeviceConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Device connection error: {str(e)}")
    except DeviceError as e:
        raise HTTPException(status_code=500, detail=f"Device error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
