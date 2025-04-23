import pandas as pd
import os
import datetime
import pytz

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
        
        # Ask for target timezone
        print("\n🌍 Common timezones: America/New_York, America/Chicago, America/Denver, America/Los_Angeles, Europe/London")
        user_tz = input("🕒 Enter target timezone (default: America/New_York): ").strip()
        if user_tz.lower() == 'cancel':
            return None
    
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