import pandas as pd
import os
import datetime
from datetime import timezone
import pytz
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

def export_data_from_influxdb():
    """
    Export data from InfluxDB based on user-provided parameters.
    
    Returns:
    --------
    str
        Path to the exported CSV file
    """
    # Load InfluxDB configuration from file or user input
    config = load_influxdb_config()
    
    # Query options
    print("\n📊 Query options:")
    days = input("📅 Enter number of days to query (default: 3): ") or "3"
    device = input("🔌 Enter device name to filter (default: WaterMeter): ") or "WaterMeter"
    
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
            
        print(f"✅ Data retrieved. Shape: {df.shape}")
        
        # Export to CSV - Include the number of days in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{device.lower()}_data_{days}d_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Data exported to {filename}")
        
        # Display first 5 rows of the data
        print("\n👀 Preview of exported data (first 5 rows):")
        print(df.head().to_string())
        
        return filename
        
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        return None
    finally:
        client.close()

def clean_data_for_ml():
    """
    Interactive function to clean and prepare CSV data for a machine learning model.
    Allows users to remove columns and filter values.
    
    Returns:
    --------
    str
        Path to the cleaned CSV file or None if operation was canceled
    """
    # Get list of CSV files in the current directory
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in the current directory.")
        return None
    
    # Let user select a file
    print("📁 Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {file}")
    
    while True:
        try:
            file_idx = int(input("\n🔢 Select a file number: ")) - 1
            if 0 <= file_idx < len(csv_files):
                selected_file = csv_files[file_idx]
                break
            else:
                print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    # Load the CSV file
    print(f"⏳ Loading {selected_file}...")
    df = pd.read_csv(selected_file)
    
    print(f"\n✅ Data loaded. Shape: {df.shape}")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Start the interactive cleaning process
    cleaned = False
    output_filename = None
    
    while not cleaned:
        print("\n🧹 --- Data Cleaning Options ---")
        print("1️⃣ Remove a column")
        print("2️⃣ Filter values in a column")
        print("3️⃣ Show summary statistics")
        print("4️⃣ Show first 5 rows")
        print("5️⃣ Save and exit")
        print("6️⃣ Cancel (return to main menu)")
        
        try:
            choice = int(input("\n🔍 Enter your choice: "))
            
            if choice == 1:
                # Remove a column
                print(f"\n📋 Available columns: {', '.join(df.columns)}")
                col = input("🗑️ Enter the column name to remove (or 'cancel'): ")
                if col.lower() == 'cancel':
                    continue
                elif col in df.columns:
                    df = df.drop(columns=[col])
                    print(f"✅ Column '{col}' removed. New shape: {df.shape}")
                else:
                    print(f"❌ Column '{col}' not found.")
            
            elif choice == 2:
                # Filter values in a column
                print(f"\n📋 Available columns: {', '.join(df.columns)}")
                col = input("🔍 Enter column name to filter (or 'cancel'): ")
                if col.lower() == 'cancel':
                    continue
                elif col in df.columns:
                    # Show unique values or summary for the column
                    if df[col].dtype in ['object', 'string']:
                        unique_vals = df[col].unique()
                        if len(unique_vals) <= 20:  # Only show if not too many
                            print(f"🔤 Unique values in '{col}': {', '.join(map(str, unique_vals))}")
                    else:
                        print(f"📈 Column statistics: Min={df[col].min()}, Max={df[col].max()}, Mean={df[col].mean()}")
                    
                    filter_type = input("⚙️ Filter by (1) Equals, (2) Less than, (3) Greater than: ")
                    filter_val = input("💯 Enter the value: ")
                    
                    try:
                        # Convert value to appropriate type
                        if df[col].dtype in ['int64', 'float64']:
                            filter_val = float(filter_val)
                        
                        # Apply the filter
                        original_len = len(df)
                        if filter_type == '1':
                            df = df[df[col] == filter_val]
                        elif filter_type == '2':
                            df = df[df[col] < filter_val]
                        elif filter_type == '3':
                            df = df[df[col] > filter_val]
                        else:
                            print("❌ Invalid filter type.")
                            continue
                        
                        print(f"✅ Filter applied. Rows removed: {original_len - len(df)}. New shape: {df.shape}")
                    except ValueError:
                        print("❌ Invalid value for the selected column type.")
                else:
                    print(f"❌ Column '{col}' not found.")
            
            elif choice == 3:
                # Show summary statistics
                print("\n📊 Summary Statistics:")
                print(df.describe())
                
            elif choice == 4:
                # Show first 5 rows
                print("\n👀 First 5 rows:")
                print(df.head().to_string())
                
            elif choice == 5:
                # Save and exit
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{os.path.splitext(selected_file)[0]}_clean.csv"
                df.to_csv(output_filename, index=False)
                print(f"💾 Cleaned data saved to {output_filename}")
                cleaned = True
            
            elif choice == 6:
                # Cancel and return to main menu
                print("⏪ Returning to main menu...")
                cleaned = True
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number.")
        except Exception as e:
            print(f"⚠️ An error occurred: {str(e)}")
    
    return output_filename

def reformat_timestamps(csv_file=None, target_timezone='America/New_York'):
    """
    Reformat timestamps in a CSV file from universal timezone to YYYY-MM-DD HH:MM:SS format
    in the specified target timezone.
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to the CSV file to process. If None, user will be prompted to select a file.
    target_timezone : str
        The target timezone to convert to (default: 'America/New_York')
        
    Returns:
    --------
    str
        Path to the newly created CSV file with reformatted timestamps
    """
    if csv_file is None:
        # Get list of CSV files in the current directory
        csv_files = [f for f in os.listdir() if f.endswith('.csv')]
        
        if not csv_files:
            print("❌ No CSV files found in the current directory.")
            return None
            
        # Let user select a file
        print("📁 Available CSV files:")
        for i, file in enumerate(csv_files):
            print(f"{i+1}. {file}")
        
        while True:
            try:
                file_idx = int(input("\n🔢 Select a file number: ")) - 1
                if 0 <= file_idx < len(csv_files):
                    csv_file = csv_files[file_idx]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Ask for target timezone
        print("\n🌍 Common timezones: America/New_York, America/Chicago, America/Denver, America/Los_Angeles, Europe/London")
        user_tz = input("🕒 Enter target timezone (default: America/New_York): ").strip()
        if user_tz:
            target_timezone = user_tz
    
    print(f"📂 Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    if '_time' not in df.columns:
        print("❌ Error: No '_time' column found in the CSV file.")
        return None
    
    # Parse timestamps and convert to target timezone
    print(f"🕒 Reformatting timestamps to {target_timezone} timezone...")
    
    # First make sure timestamps are parsed as datetime objects
    df['_time'] = pd.to_datetime(df['_time'])
    
    # Get the timezone object
    target_tz = pytz.timezone(target_timezone)
    
    # Convert timestamps to the target timezone
    df['_time'] = df['_time'].dt.tz_convert(target_tz)
    
    # Format to YYYY-MM-DD HH:MM:SS
    df['_time'] = df['_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Create output filename
    output_filename = f"{os.path.splitext(csv_file)[0]}_reformatted.csv"
    
    # Save to new CSV file
    df.to_csv(output_filename, index=False)
    print(f"✅ Reformatted timestamps saved to {output_filename}")
    
    # Display first 5 rows of the data
    print("\n👀 Preview of reformatted data (first 5 rows):")
    print(df.head().to_string())
    
    return output_filename

def display_menu():
    """Display the main menu options"""
    print("\n" + "="*60)
    print("🌟 InfluxDB Data Toolkit 🌟".center(60))
    print("="*60)
    print("🔽 Select an option:")
    print("1️⃣ Export data from InfluxDB")
    print("2️⃣ Clean existing CSV data for machine learning")
    print("3️⃣ Reformat timestamps and adjust timezone")
    print("4️⃣ Exit program")
    return input("\n🔍 Enter your choice (1-4): ")

if __name__ == "__main__":
    # Main program loop
    running = True
    
    while running:
        choice = display_menu()
        
        if choice == "1":
            # Export data from InfluxDB
            exported_file = export_data_from_influxdb()
            if exported_file:
                print("\n✅ Export operation completed successfully!")
                
                # Ask if user wants to clean the data
                proceed = input("\n🔄 Would you like to clean this data now? (y/n): ")
                if proceed.lower() == 'y':
                    reformat_proceed = input("🕒 Would you like to reformat timestamps first? (y/n): ")
                    if reformat_proceed.lower() == 'y':
                        reformatted_file = reformat_timestamps(exported_file)
                        if reformatted_file:
                            clean_data_for_ml()
                    else:
                        clean_data_for_ml()
            
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "2":
            # Clean existing CSV data
            cleaned_file = clean_data_for_ml()
            if cleaned_file:
                print("\n✅ Data cleaning operation completed successfully!")
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "3":
            # Reformat timestamps
            reformatted_file = reformat_timestamps()
            if reformatted_file:
                print("\n✅ Timestamp reformatting completed successfully!")
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "4":
            # Exit program
            print("👋 Thank you for using InfluxDB Data Tool. Goodbye!")
            running = False
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("\n⏸️ Press Enter to continue...")