import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from kasa import SmartPlug
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DEVICE_IP = os.getenv("DEVICE_IP")
if not DEVICE_IP:
    raise ValueError("DEVICE_IP environment variable is required")

async def get_plug():
    plug = SmartPlug(DEVICE_IP)
    await plug.update()
    return plug

@app.get("/", response_class=HTMLResponse)
async def index():
    plug = await get_plug()
    is_on = plug.is_on

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Christmas Tree Control</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="tree">🎄</div>
            <h1>Christmas Tree</h1>
            <form action="/toggle" method="post">
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

@app.post("/toggle")
async def toggle():
    plug = await get_plug()
    if plug.is_on:
        await plug.turn_off()
    else:
        await plug.turn_on()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
