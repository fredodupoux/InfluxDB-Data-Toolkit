"""
InfluxDB Data Exporter Module

This module handles the export of time series data from InfluxDB to CSV files.
It provides an interactive interface for configuring and executing data queries
against an InfluxDB instance, with options for:

- Selecting time range (number of days to query)
- Filtering by device name
- Automatic handling of multi-table results
- Data cleaning and sorting
- CSV export with standardized naming conventions

Exported files are saved to the _data directory with timestamped filenames.
"""

import pandas as pd
import datetime
from tools.config import load_influxdb_config, load_influxdb_config_from_file
import os

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

def export_data_from_influxdb(days=3, device="WaterMeter", config=None):
    """
    Export data from InfluxDB based on provided parameters.

    Parameters:
    -----------
    days : int, optional
        Number of days to query (default is 3).
    device : str, optional
        Device name to filter (default is "WaterMeter").
    config : dict, optional
        InfluxDB configuration dictionary. If None, attempts to load from file.

    Returns:
    --------
    str
        Path to the exported CSV file.

    Raises:
    -------
    Exception
        If configuration loading fails or the query/export process encounters an error.
    """
    # Load InfluxDB configuration if not provided
    if config is None:
        try:
            config = load_influxdb_config_from_file()
        except Exception as e:
            print(f"Error loading config: {e}")
            raise Exception(f"Failed to load InfluxDB configuration: {e}")

    # Validate config
    if not all(k in config for k in ['url', 'token', 'org', 'bucket']):
        raise ValueError("InfluxDB configuration is incomplete.")

    # Ensure days is an integer
    try:
        days = int(days)
    except ValueError:
        raise ValueError("Invalid value for 'days'. Must be an integer.")

    # Construct the query
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

    # Import here to keep dependency local to function if possible
    from influxdb_client import InfluxDBClient

    # Increase timeout
    client = InfluxDBClient(url=config['url'], token=config['token'], org=config['org'], timeout=60000)
    query_api = client.query_api()

    try:
        print(f"Querying data from InfluxDB at {config['url']} for the last {days} days for device '{device}'...")
        tables = query_api.query_data_frame(query)

        if tables is None or (isinstance(tables, list) and not tables) or tables.empty:
             raise ValueError(f"No data returned from InfluxDB for the specified parameters (bucket: {config['bucket']}, days: {days}, device: {device}). Check query and data source.")

        # Convert to a single dataframe if results are in multiple tables
        if isinstance(tables, list):
            print(f"Received {len(tables)} data tables. Combining...")
            df = pd.concat(tables, ignore_index=True)
        else:
            df = tables

        # Clean up the dataframe
        df = df.loc[:, ~df.columns.duplicated()]
        if '_time' in df.columns:
            df = df.sort_values('_time')

        print(f"Data retrieved. Shape: {df.shape}")

        # Export to CSV
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        data_dir = "_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Sanitize device name for filename
        safe_device_name = "".join(c if c.isalnum() else "_" for c in device)
        filename = os.path.join(data_dir, f"{safe_device_name}_data_{days}d_{timestamp}.csv")

        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")

        return filename

    except Exception as e:
        print(f"Error during InfluxDB export: {str(e)}")
        raise Exception(f"An error occurred during data export: {str(e)}")
    finally:
        client.close()

def interactive_export_data_from_influxdb():
    """
    Interactive version to export data from InfluxDB based on user-provided parameters.

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

    days_str = input("📅 Enter number of days to query (default: 3): ")
    if days_str.lower() == 'cancel':
        return None
    days_str = days_str or "3"

    device = input("🔌 Enter device name to filter (default: WaterMeter): ")
    if device.lower() == 'cancel':
        return None
    device = device or "WaterMeter"

    try:
        days = int(days_str)
        # Call the refactored function
        filename = export_data_from_influxdb(days=days, device=device, config=config)

        # Display results (similar to original interactive function)
        if filename:
             clear_screen()
             print(f"💾 Data exported to {filename}")
             try:
                 df_preview = pd.read_csv(filename, nrows=5)
                 print("\n👀 Preview of exported data (first 5 rows):")
                 print(df_preview.to_string())
             except Exception as preview_err:
                 print(f"Could not generate preview: {preview_err}")
             input("\nPress Enter to continue...")
        return filename

    except ValueError as ve:
         print(f"⚠️ Input Error: {ve}")
         input("\nPress Enter to continue...")
         return None
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        input("\nPress Enter to continue...")
        return None

# Example of how to run interactively if needed
# if __name__ == "__main__":
#     interactive_export_data_from_influxdb()