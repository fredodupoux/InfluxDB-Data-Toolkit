import os
import json

# Configuration file path
CONFIG_FILE = "influxdb_config.json"

def load_influxdb_config():
    """
    Load InfluxDB configuration from the config file or prompt the user for input.
    
    Returns:
    --------
    dict
        Dictionary containing InfluxDB configuration (url, token, org, bucket)
    """
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
    config['url'] = input("🌐 Enter InfluxDB URL (e.g. http://localhost:8086): ")
    config['org'] = input("🏢 Enter organization ID: ")
    config['bucket'] = input("🪣 Enter bucket name: ")
    config['token'] = input("🔑 Enter access token: ")
    
    # Save configuration for future use
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Configuration saved to {CONFIG_FILE}")
        print(f"ℹ️ Note: {CONFIG_FILE} is listed in .gitignore to prevent accidental exposure.")
    except Exception as e:
        print(f"⚠️ Failed to save configuration: {str(e)}")
    
    return config