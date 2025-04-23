"""
Time Utilities Module for InfluxDB Data Toolkit

This module provides functionality for reformatting timestamps in CSV data files.
It supports:
- Converting timestamps between different timezones
- Removing date components to keep only time values
- Combining timezone conversion and date removal
- Interactive file selection from both the root directory and _data directory

The processed files are saved with clear naming conventions that indicate the
transformations applied (_time_only, _tz_converted, etc.)
"""

import pandas as pd
import os
import datetime
import pytz

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

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
        clear_screen()
        # Get list of CSV files in both current directory and _data directory
        root_csv_files = [f for f in os.listdir() if f.endswith('.csv')]
        
        # Check if _data directory exists
        data_dir = "_data"
        data_csv_files = []
        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            data_csv_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        # Combine both lists
        csv_files = root_csv_files + data_csv_files
        
        if not csv_files:
            print("❌ No CSV files found in the current directory or _data folder.")
            return None
            
        # Let user select a file
        print("📁 Available CSV files:")
        for i, file in enumerate(csv_files):
            print(f"{i+1}. {file}")
        print("0. 🔙 Go back to main menu")
        
        while True:
            file_input = input("\n🔢 Select a file number (0 to go back): ")
            if file_input.lower() == 'cancel' or file_input == '0':
                return None
                
            try:
                file_idx = int(file_input) - 1
                if 0 <= file_idx < len(csv_files):
                    csv_file = csv_files[file_idx]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    clear_screen()
    print(f"📂 Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Show file info and preview immediately after loading
    print(f"\n✅ Data loaded. Shape: {df.shape}")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Show first 5 rows immediately after loading
    print("\n👀 Preview of loaded data (first 5 rows):")
    print(df.head().to_string())
        
    # Show timestamp format options menu
    print("\n🕰️ Timestamp Format Options:")
    print("1. Convert timezone")
    print("2. Remove date (keep only time)")
    print("3. Both convert timezone and remove date")
    print("0. 🔙 Go back")
    
    format_choice = input("\n🔢 Select an option (0-3): ")
    if format_choice.lower() == 'cancel' or format_choice == '0':
        return None
        
    # Initialize formatting options
    convert_timezone = False
    keep_time_only = False
    
    if format_choice == '1' or format_choice == '3':
        clear_screen()
        convert_timezone = True
        print("\n🌍 Common timezones: America/New_York, America/Chicago, America/Denver, America/Los_Angeles, Europe/London")
        user_tz = input("🕒 Enter target timezone (default: America/New_York): ").strip()
        if user_tz.lower() == 'cancel':
            return None
        elif user_tz:
            target_timezone = user_tz
    
    if format_choice == '2' or format_choice == '3':
        keep_time_only = True
    
    clear_screen()
    
    if '_time' not in df.columns:
        print("❌ Error: No '_time' column found in the CSV file.")
        input("\nPress Enter to continue...")
        return None
    
    print(f"🔄 Processing timestamps in {csv_file}...")
    
    # First make sure timestamps are parsed as datetime objects
    df['_time'] = pd.to_datetime(df['_time'])
    
    # Apply timezone conversion if requested
    if convert_timezone:
        print(f"🕒 Converting timestamps to {target_timezone} timezone...")
        # Get the timezone object
        target_tz = pytz.timezone(target_timezone)
        # Convert timestamps to the target timezone
        df['_time'] = df['_time'].dt.tz_convert(target_tz)
    
    # Format based on user preference
    if keep_time_only:
        print("⏰ Removing date and keeping only time component...")
        df['_time'] = df['_time'].dt.strftime('%H:%M:%S')
    else:
        # Format to YYYY-MM-DD HH:MM:SS
        df['_time'] = df['_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Create output filename with appropriate suffix
    data_dir = "_data"
    # Create the _data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Get basename of the file without path
    base_filename = os.path.basename(csv_file)
    base_name = os.path.splitext(base_filename)[0]
    
    if convert_timezone and keep_time_only:
        output_filename = os.path.join(data_dir, f"{base_name}_time_only_tz.csv")
    elif keep_time_only:
        output_filename = os.path.join(data_dir, f"{base_name}_time_only.csv")
    elif convert_timezone:
        output_filename = os.path.join(data_dir, f"{base_name}_tz_converted.csv")
    else:
        output_filename = os.path.join(data_dir, f"{base_name}_reformatted.csv")
    
    # Save to new CSV file
    df.to_csv(output_filename, index=False)
    print(f"✅ Reformatted timestamps saved to {output_filename}")
    
    # Display first 5 rows of the data
    print("\n👀 Preview of reformatted data (first 5 rows):")
    print(df.head().to_string())
    
    input("\nPress Enter to continue...")
    
    return output_filename