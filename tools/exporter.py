import pandas as pd
import datetime
from tools.config import load_influxdb_config
import os

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

def export_data_from_influxdb():
    """
    Export data from InfluxDB based on user-provided parameters.
    
    Returns:
    --------
    str
        Path to the exported CSV file, or None if cancelled
    """
    clear_screen()
    # Load InfluxDB configuration from file or user input
    config = load_influxdb_config()
    
    # If config is empty, user cancelled
    if not config:
        return None
    
    clear_screen()
    # Query options
    print("\n📊 Query options:")
    print("1. Continue with query parameters")
    print("0. 🔙 Go back to main menu")
    
    query_choice = input("\n🔍 Enter your choice (0-1): ")
    if query_choice == "0" or query_choice.lower() == 'cancel':
        return None
    
    days = input("📅 Enter number of days to query (default: 3): ")
    if days.lower() == 'cancel':
        return None
    days = days or "3"
    
    device = input("🔌 Enter device name to filter (default: WaterMeter): ")
    if device.lower() == 'cancel':
        return None
    device = device or "WaterMeter"
    
    clear_screen()
    # Updated query with user parameters
    query = f'''
    from(bucket: "{config['bucket']}")
      |> range(start: -{days}d)
      |> filter(fn: (r) => r["device"] == "{device}")
      |> filter(fn: (r) => contains(value: r["_field"], set: [
          "peakFlowRate", "eventVolume", "eventPeaks", "eventLength", 
          "avgFlowRate", "peakCount", "totalGallons"
      ]))
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> drop(columns: ["_start", "_stop", "result", "table"])
      |> yield(name: "formatted_results")
    '''

    # Import here to avoid requiring the package if not using this option
    from influxdb_client import InfluxDBClient
    
    # Increase timeout to 60 seconds
    client = InfluxDBClient(url=config['url'], token=config['token'], org=config['org'], timeout=60000)
    query_api = client.query_api()

    try:
        print(f"🔄 Querying data from InfluxDB at {config['url']} for the last {days} days...")
        tables = query_api.query_data_frame(query)
        
        # Convert to a single dataframe if results are in multiple tables
        if isinstance(tables, list):
            print(f"📊 Received {len(tables)} data tables. Combining...")
            df = pd.concat(tables)
        else:
            df = tables
        
        # Clean up the dataframe
        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Sort by timestamp
        if '_time' in df.columns:
            df = df.sort_values('_time')
        
        clear_screen()    
        print(f"✅ Data retrieved. Shape: {df.shape}")
        print(f"📊 Columns: {', '.join(df.columns)}")
        
        # Export to CSV - Include the number of days in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create _data directory if it doesn't exist
        data_dir = "_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        filename = os.path.join(data_dir, f"{device.lower()}_data_{days}d_{timestamp}.csv")
        df.to_csv(filename, index=False)
        print(f"💾 Data exported to {filename}")
        
        # Display first 5 rows of the data
        print("\n👀 Preview of exported data (first 5 rows):")
        print(df.head().to_string())
        
        input("\nPress Enter to continue...")
        
        return filename
        
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        input("\nPress Enter to continue...")
        return None
    finally:
        client.close()