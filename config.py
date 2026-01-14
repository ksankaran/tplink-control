"""
Configuration management for smart devices.

This module handles loading and managing device configurations.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Default configuration file path
CONFIG_FILE = Path(".devices.json")


def load_device_config() -> Dict[str, Any]:
    """
    Load device configuration from file or environment variables.
    
    First tries to load from .devices.json file, then falls back
    to environment variables for backward compatibility.
    
    Returns:
        Dictionary containing device configurations
    """
    config = {}
    
    # Try to load from JSON file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Fall back to environment variables for backward compatibility
    # This allows existing .env setup to continue working
    device_ip = os.getenv("DEVICE_IP")
    if device_ip and "default" not in config:
        config["default"] = {
            "type": "tplink",
            "device_ip": device_ip,
        }
    
    return config


def save_device_config(config: Dict[str, Any]) -> None:
    """
    Save device configuration to file.
    
    Args:
        config: Dictionary containing device configurations
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save config file: {e}")


def get_device_config(name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific device.
    
    Args:
        name: Name of the device
        
    Returns:
        Device configuration dictionary or None if not found
    """
    config = load_device_config()
    return config.get(name)

