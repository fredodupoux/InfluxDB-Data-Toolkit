"""
Configuration Module for InfluxDB Data Toolkit

This module handles loading and saving InfluxDB connection configuration.
It supports both retrieving configuration from a JSON file and interactively
prompting the user for configuration details when no file exists.

Configuration is stored in config/influxdb_config.json and includes:
- InfluxDB server URL
- Organization ID
- Bucket name
- Access token
"""

import os
import json

# Configuration file path
CONFIG_FILE = os.path.join("config", "influxdb_config.json")

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

def load_influxdb_config():
    """
    Load InfluxDB configuration from the config file or prompt the user for input.
    
    Returns:
    --------
    dict
        Dictionary containing InfluxDB configuration (url, token, org, bucket)
        Returns empty dict if user cancels
    """
    clear_screen()
    # Check if configuration file exists
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print("🔐 InfluxDB configuration loaded from file.")
                return config
        except Exception as e:
            print(f"⚠️ Error loading configuration file: {str(e)}")
            # Fall through to prompt the user
    else:
        print("📝 No configuration file found. Please enter your InfluxDB details:")
    
    # Prompt the user for configuration
    config = {}
    url = input("🌐 Enter InfluxDB URL (e.g. http://localhost:8086): ")
    if url.lower() == 'cancel':
        print("🔙 Configuration cancelled")
        return {}
    config['url'] = url
    
    org = input("🏢 Enter organization ID : ")
    if org.lower() == 'cancel':
        print("🔙 Configuration cancelled")
        return {}
    config['org'] = org
    
    bucket = input("🪣 Enter bucket name : ")
    if bucket.lower() == 'cancel':
        print("🔙 Configuration cancelled")
        return {}
    config['bucket'] = bucket
    
    token = input("🔑 Enter access token : ")
    if token.lower() == 'cancel':
        print("🔙 Configuration cancelled")
        return {}
    config['token'] = token
    
    # Save configuration for future use
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration saved to {CONFIG_FILE}")
        print(f"ℹ️ Note: {CONFIG_FILE} is listed in .gitignore to prevent accidental exposure.")
    except Exception as e:
        print(f"⚠️ Failed to save configuration: {str(e)}")
    
    input("\nPress Enter to continue...")
    return config