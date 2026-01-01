import os
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
from kasa import SmartPlug

from devices import (
    TPLinkDevice, HueDevice, NanoleafDevice, GeeniDevice, CreeDevice,
    DeviceError, DeviceConnectionError
)
from devices.registry import DeviceRegistry
from config import load_device_config

load_dotenv()

app = FastAPI()

# Initialize device registry
device_registry = DeviceRegistry()

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

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
            device = None
            
            if device_type == "tplink":
                device_ip = device_config.get("device_ip")
                if device_ip:
                    device = TPLinkDevice(device_ip=device_ip, device_id=name)
            
            elif device_type == "hue":
                bridge_ip = device_config.get("bridge_ip")
                api_key = device_config.get("api_key")
                light_id = device_config.get("light_id")
                group_id = device_config.get("group_id")
                if bridge_ip and api_key and (light_id or group_id):
                    device = HueDevice(
                        bridge_ip=bridge_ip,
                        api_key=api_key,
                        light_id=light_id,
                        group_id=group_id,
                        device_id=name
                    )
            
            elif device_type == "nanoleaf":
                device_ip = device_config.get("device_ip")
                auth_token = device_config.get("auth_token")
                if device_ip and auth_token:
                    device = NanoleafDevice(
                        device_ip=device_ip,
                        auth_token=auth_token,
                        device_id=name
                    )
            
            elif device_type == "geeni":
                device_id = device_config.get("device_id")
                device_ip = device_config.get("device_ip")
                local_key = device_config.get("local_key")
                device_version = device_config.get("device_version", "3.3")
                if device_id and device_ip and local_key:
                    device = GeeniDevice(
                        device_id=device_id,
                        device_ip=device_ip,
                        local_key=local_key,
                        device_version=device_version,
                        device_id_alias=name
                    )
            
            elif device_type == "cree":
                device_id = device_config.get("device_id")
                device_ip = device_config.get("device_ip")
                local_key = device_config.get("local_key")
                device_version = device_config.get("device_version", "3.3")
                if device_id and device_ip and local_key:
                    device = CreeDevice(
                        device_id=device_id,
                        device_ip=device_ip,
                        local_key=local_key,
                        device_version=device_version,
                        device_id_alias=name
                    )
            
            if device:
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

async def get_plug(device_name: str = "default"):
    """
    Get a TP-Link SmartPlug instance for schedule management.
    Schedules are TP-Link specific, so this function gets the underlying Kasa device.
    
    Args:
        device_name: Name of the device to retrieve (defaults to "default")
        
    Returns:
        SmartPlug instance
        
    Raises:
        HTTPException: If device is not found or not a TP-Link device
    """
    device = await get_device(device_name)
    if not isinstance(device, TPLinkDevice):
        raise HTTPException(
            status_code=400,
            detail=f"Device '{device_name}' is not a TP-Link device. Schedules are only supported for TP-Link devices."
        )
    return await device._get_device()

def minutes_to_time(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"

def time_to_minutes(time_str: str) -> int:
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)

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
        
        # Show schedule link only for TP-Link devices
        schedule_link = ""
        if isinstance(smart_device, TPLinkDevice):
            schedule_link = '<p class="nav"><a href="/schedules">Manage Schedules</a></p>'
        
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
                .nav {{
                    margin-top: 2rem;
                }}
                .nav a {{
                    color: #94a3b8;
                    text-decoration: none;
                }}
                .nav a:hover {{
                    color: white;
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
                {schedule_link}
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

@app.get("/schedules", response_class=HTMLResponse)
async def schedules(device: str = "default"):
    plug = await get_plug(device)
    sched = plug.modules['schedule']
    rules = sched.data.get('get_rules', {}).get('rule_list', [])

    rules_html = ""
    if not rules:
        rules_html = "<p class='empty'>No schedules set</p>"
    else:
        for rule in rules:
            time_str = minutes_to_time(rule['smin'])
            action = "Turn On" if rule['sact'] == 1 else "Turn Off"
            enabled = "enabled" if rule.get('enable', 0) else "disabled"
            days = [DAYS[i] for i, on in enumerate(rule.get('wday', [0]*7)) if on]
            days_str = ", ".join(days) if days else "No days"
            name = rule.get('name', 'Unnamed')
            rule_id = rule['id']

            rules_html += f"""
            <div class="rule">
                <div class="rule-info">
                    <span class="time">{time_str}</span>
                    <span class="action {'on' if rule['sact'] == 1 else 'off'}">{action}</span>
                    <span class="days">{days_str}</span>
                </div>
                <form action="/schedules/delete" method="post" class="delete-form">
                    <input type="hidden" name="rule_id" value="{rule_id}">
                    <input type="hidden" name="device" value="{device}">
                    <button type="submit" class="delete-btn">Delete</button>
                </form>
            </div>
            """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Schedules - Smart Device Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                padding: 2rem;
                box-sizing: border-box;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
            }}
            h1 {{
                font-size: 1.5rem;
                margin-bottom: 1.5rem;
            }}
            .back {{
                color: #94a3b8;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 1rem;
            }}
            .back:hover {{
                color: white;
            }}
            .rule {{
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .rule-info {{
                display: flex;
                gap: 1rem;
                align-items: center;
            }}
            .time {{
                font-size: 1.25rem;
                font-weight: bold;
            }}
            .action {{
                padding: 0.25rem 0.5rem;
                border-radius: 5px;
                font-size: 0.875rem;
            }}
            .action.on {{
                background: #22c55e;
            }}
            .action.off {{
                background: #64748b;
            }}
            .days {{
                color: #94a3b8;
                font-size: 0.875rem;
            }}
            .delete-btn {{
                background: #ef4444;
                border: none;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                cursor: pointer;
            }}
            .delete-btn:hover {{
                background: #dc2626;
            }}
            .empty {{
                color: #94a3b8;
                text-align: center;
                padding: 2rem;
            }}
            .add-form {{
                background: rgba(255,255,255,0.05);
                padding: 1.5rem;
                border-radius: 10px;
                margin-top: 2rem;
            }}
            .add-form h2 {{
                font-size: 1rem;
                margin-bottom: 1rem;
            }}
            .form-row {{
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
                align-items: center;
            }}
            .form-row label {{
                min-width: 60px;
            }}
            input[type="time"] {{
                padding: 0.5rem;
                border-radius: 5px;
                border: none;
                font-size: 1rem;
            }}
            select {{
                padding: 0.5rem;
                border-radius: 5px;
                border: none;
                font-size: 1rem;
            }}
            .days-row {{
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }}
            .days-row label {{
                background: rgba(255,255,255,0.1);
                padding: 0.5rem 0.75rem;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.875rem;
            }}
            .days-row input:checked + span {{
                color: #22c55e;
            }}
            .days-row input {{
                display: none;
            }}
            .add-btn {{
                background: #3b82f6;
                border: none;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                width: 100%;
                margin-top: 1rem;
            }}
            .add-btn:hover {{
                background: #2563eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/?device={device}" class="back">← Back</a>
            <h1>Schedules</h1>

            {rules_html}

            <div class="add-form">
                <h2>Add Schedule</h2>
                <form action="/schedules/add" method="post">
                    <input type="hidden" name="device" value="{device}">
                    <div class="form-row">
                        <label>Time</label>
                        <input type="time" name="time" value="18:00" required>
                    </div>
                    <div class="form-row">
                        <label>Action</label>
                        <select name="action">
                            <option value="on">Turn On</option>
                            <option value="off">Turn Off</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label>Days</label>
                    </div>
                    <div class="days-row">
                        <label><input type="checkbox" name="days" value="0" checked><span>Mon</span></label>
                        <label><input type="checkbox" name="days" value="1" checked><span>Tue</span></label>
                        <label><input type="checkbox" name="days" value="2" checked><span>Wed</span></label>
                        <label><input type="checkbox" name="days" value="3" checked><span>Thu</span></label>
                        <label><input type="checkbox" name="days" value="4" checked><span>Fri</span></label>
                        <label><input type="checkbox" name="days" value="5" checked><span>Sat</span></label>
                        <label><input type="checkbox" name="days" value="6" checked><span>Sun</span></label>
                    </div>
                    <button type="submit" class="add-btn">Add Schedule</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.post("/schedules/add")
async def add_schedule(time: str = Form(...), action: str = Form(...), days: list[str] = Form(default=[]), device: str = Form("default")):
    plug = await get_plug(device)
    sched = plug.modules['schedule']

    wday = [0] * 7
    for d in days:
        wday[int(d)] = 1

    rule = {
        'stime_opt': 0,
        'wday': wday,
        'smin': time_to_minutes(time),
        'enable': 1,
        'repeat': 1,
        'etime_opt': -1,
        'name': f"{'On' if action == 'on' else 'Off'} at {time}",
        'eact': -1,
        'month': 0,
        'sact': 1 if action == 'on' else 0,
        'year': 0,
        'longitude': 0,
        'day': 0,
        'latitude': 0,
        'emin': 0
    }

    await sched.call('add_rule', rule)
    # Ensure global scheduling is enabled
    await sched.call('set_overall_enable', {'enable': 1})
    return RedirectResponse(url=f"/schedules?device={device}", status_code=303)

@app.post("/schedules/delete")
async def delete_schedule(rule_id: str = Form(...), device: str = Form("default")):
    plug = await get_plug(device)
    sched = plug.modules['schedule']
    await sched.call('delete_rule', {'id': rule_id})
    return RedirectResponse(url=f"/schedules?device={device}", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
