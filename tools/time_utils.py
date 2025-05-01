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
    Interactive function to reformat timestamps in a CSV file.
    Prompts user for file selection and formatting options.
    (Existing interactive logic remains here for potential CLI use)
    """
    # ... (Keep existing interactive logic for now) ...
    # ... or refactor it to call reformat_timestamps_api after getting user input ...
    pass # Placeholder to avoid syntax error if removing all content

def reformat_timestamps_api(csv_file_path, target_timezone='America/New_York', convert_timezone=False, keep_time_only=False):
    """
    Reformats timestamps in a CSV file non-interactively.

    Parameters:
    -----------
    csv_file_path : str
        Absolute path to the CSV file to process.
    target_timezone : str
        The target timezone to convert to (e.g., 'America/New_York').
    convert_timezone : bool
        Whether to convert the timezone.
    keep_time_only : bool
        Whether to remove the date component and keep only the time.

    Returns:
    --------
    str
        Absolute path to the newly created CSV file with reformatted timestamps.

    Raises:
    -------
    FileNotFoundError
        If the input csv_file_path does not exist.
    KeyError
        If the '_time' column is not found in the CSV.
    ValueError
        If an invalid timezone is provided.
    Exception
        For other potential errors during processing.
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Input file not found: {csv_file_path}")

    print(f"📂 Reading {csv_file_path} for timestamp reformatting...") # Server log
    df = pd.read_csv(csv_file_path)

    if '_time' not in df.columns:
        raise KeyError("Column '_time' not found in the CSV file.")

    print(f"🔄 Processing timestamps in {os.path.basename(csv_file_path)}...") # Server log

    # Ensure timestamps are parsed as datetime objects, handling potential errors
    try:
        # Attempt conversion, inferring format might be needed or specify known formats
        df['_time'] = pd.to_datetime(df['_time'], errors='coerce') # Coerce errors to NaT
        if df['_time'].isnull().any():
             # Log or handle rows that couldn't be parsed
             print("⚠️ Warning: Some timestamps could not be parsed and were set to NaT.")
             # Optionally, raise an error or filter out NaT rows depending on requirements
             # df = df.dropna(subset=['_time']) # Example: remove rows with parse errors
             pass # Continue processing valid timestamps

    except Exception as e:
        raise ValueError(f"Error parsing '_time' column: {e}")

    # Apply timezone conversion if requested
    if convert_timezone:
        if not target_timezone:
            target_timezone = 'America/New_York' # Default if not provided but conversion requested
        print(f"🕒 Converting timestamps to {target_timezone} timezone...") # Server log
        try:
            target_tz = pytz.timezone(target_timezone)
            # Ensure the datetime column is timezone-aware (assume UTC if naive)
            if df['_time'].dt.tz is None:
                df['_time'] = df['_time'].dt.tz_localize('UTC')
            df['_time'] = df['_time'].dt.tz_convert(target_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid target timezone specified: {target_timezone}")
        except Exception as e:
            raise Exception(f"Error during timezone conversion: {e}")

    # Format based on user preference
    if keep_time_only:
        print("⏰ Removing date and keeping only time component...") # Server log
        # If timezone was converted, the object is timezone-aware.
        # If not, it might be naive. Strftime works on both.
        df['_time'] = df['_time'].dt.strftime('%H:%M:%S')
    else:
        # Format to YYYY-MM-DD HH:MM:SS
        # If timezone was converted, remove timezone info for consistent string format
        if df['_time'].dt.tz is not None:
             df['_time'] = df['_time'].dt.tz_localize(None)
        df['_time'] = df['_time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Create output filename with appropriate suffix
    data_dir = os.path.dirname(csv_file_path) # Save in the same directory (_data)
    base_filename = os.path.basename(csv_file_path)
    base_name = os.path.splitext(base_filename)[0]

    suffix = ""
    if convert_timezone and keep_time_only:
        suffix = "_time_only_tz"
    elif keep_time_only:
        suffix = "_time_only"
    elif convert_timezone:
        suffix = "_tz_converted"
    else:
        # Even if no specific operation, save to a new file to indicate processing
        suffix = "_reformatted"

    # Avoid adding duplicate suffixes if the file was already processed
    if not base_name.endswith(suffix):
         output_filename = f"{base_name}{suffix}.csv"
    else:
         # If the suffix is already there, maybe add a timestamp or number?
         # For now, just use the base name + suffix to avoid double suffixing.
         output_filename = f"{base_name}.csv" # Or potentially overwrite? Let's avoid double suffix.

    output_file_path = os.path.join(data_dir, output_filename)

    # Save to new CSV file
    df.to_csv(output_file_path, index=False)
    print(f"✅ Reformatted timestamps saved to {output_file_path}") # Server log

    return output_file_path