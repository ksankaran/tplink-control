# TP-Link Kasa Smart Plug Control

A simple web app to control your TP-Link Kasa smart plug with a toggle button.

## Setup

1. Clone and install dependencies:
```bash
git clone <your-repo-url>
cd tplink-control
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Find your device IP address:
```bash
kasa discover
```
This will scan your network and show all Kasa devices with their IP addresses.

3. Create a `.env` file with your device IP:
```bash
echo "DEVICE_IP=<your-device-ip>" > .env
```

4. Run the app:
```bash
python app.py
```

5. Open http://localhost:8000 in your browser.

## Requirements

- Python 3.8+
- TP-Link Kasa smart plug on the same network
- Device must be set up via the Kasa app first
