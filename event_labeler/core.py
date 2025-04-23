"""
Core functionality for the water event labeler
"""

import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .utils import clear_screen

def load_data(csv_file=None):
    """
    Load water consumption data from a CSV file.
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to the CSV file to process. If None, user will be prompted to select a file.
    
    Returns:
    --------
    pandas.DataFrame
        Loaded data or None if operation was canceled
    str
        Path to the loaded file
    """
    if csv_file is None:
        # Look for CSV files in both the current directory and the _data directory
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
            return None, None
        
        # Let user select a file
        print("📁 Available CSV files:")
        for i, file in enumerate(csv_files):
            print(f"{i+1}. {file}")
        print("0. 🔙 Cancel operation")
        
        while True:
            file_input = input("\n🔢 Select a file number (0 to cancel): ")
            if file_input.lower() == 'cancel' or file_input == '0':
                print("🔙 Operation cancelled")
                return None, None
                
            try:
                file_idx = int(file_input) - 1
                if 0 <= file_idx < len(csv_files):
                    csv_file = csv_files[file_idx]
                    break
                else:
                    print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    # Load the CSV file
    print(f"⏳ Loading {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
        
        # Check if the required columns are present
        required_columns = ["time", "eventLength", "eventVolume", "avgFlowRate", "maxFlowRate"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return None, None
        
        # Check if time column needs processing
        if 'time' in df.columns:
            # Convert time to datetime if it's not in datetime format
            if not pd.api.types.is_datetime64_any_dtype(df['time']):
                try:
                    # First check if it's a time-only column (HH:MM:SS)
                    if ":" in str(df['time'].iloc[0]) and len(str(df['time'].iloc[0])) <= 8:
                        # This is just a time column without date, add a dummy date
                        df['time'] = pd.to_datetime("2025-01-01 " + df['time'].astype(str))
                    else:
                        df['time'] = pd.to_datetime(df['time'])
                    print("✅ Time column converted to datetime format")
                except Exception as e:
                    print(f"⚠️ Warning: Could not convert time column to datetime: {str(e)}")
        
        print(f"\n✅ Data loaded. Shape: {df.shape}")
        print(f"📊 Columns: {', '.join(df.columns)}")
        
        # Show preview of loaded data
        print("\n👀 Preview of loaded data (first 5 rows):")
        print(df.head().to_string())
        
        return df, csv_file
        
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return None, None


def manually_label_events(df):
    """
    Manually label water consumption events.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with manual labels applied
    """
    from .visualization import visualize_event
    
    df_manual = df.copy()
    
    # Add label column if it doesn't exist
    if 'label' not in df_manual.columns:
        # Initialize with empty strings instead of NaN to avoid dtype issues
        df_manual['label'] = ''
    elif df_manual['label'].dtype != 'object':
        # Convert to string type if it's not already
        df_manual['label'] = df_manual['label'].astype(str)
        # Replace 'nan' strings with empty strings
        df_manual['label'] = df_manual['label'].replace('nan', '')
    
    # Define common water fixture types
    fixture_types = [
        "shower", "bathroom_faucet", "kitchen_faucet", 
        "toilet", "washing_machine", "dishwasher", 
        "ice_maker", "irrigation", "other"
    ]
    
    print("\n👋 Manual Event Labeling")
    print(f"You have {len(df_manual)} events to label.")
    
    # Ask if the user wants to label all events or just unlabeled ones
    label_option = input("Label (1) all events, (2) only unlabeled events, (3) specific events? ")
    
    if label_option == "1":
        # Label all events
        events_to_label = range(len(df_manual))
    elif label_option == "2":
        # Label only unlabeled events
        events_to_label = df_manual[df_manual['label'] == ''].index.tolist()
    elif label_option == "3":
        # Label specific events
        print("Enter event indices to label (comma-separated, e.g. '0,5,10'):")
        indices_input = input("Event indices: ")
        try:
            events_to_label = [int(idx.strip()) for idx in indices_input.split(',')]
            # Validate indices
            valid_indices = [idx for idx in events_to_label if 0 <= idx < len(df_manual)]
            if len(valid_indices) != len(events_to_label):
                print(f"⚠️ Some indices were out of range and will be skipped.")
            events_to_label = valid_indices
        except ValueError:
            print("❌ Invalid input. Using all unlabeled events.")
            events_to_label = df_manual[df_manual['label'] == ''].index.tolist()
    else:
        print("❌ Invalid option. Using all unlabeled events.")
        events_to_label = df_manual[df_manual['label'] == ''].index.tolist()
    
    print(f"🔍 {len(events_to_label)} events selected for labeling.")
    
    # Start the labeling process
    for i, event_idx in enumerate(events_to_label):
        # Clear any existing plot
        plt.close('all')
        
        # Display progress
        print(f"\n📌 Event {i+1}/{len(events_to_label)} (index {event_idx})")
        
        # Visualize the event
        visualize_event(df_manual, event_idx)
        
        # Ask for the label
        print("\n💧 Available labels:")
        for i, fixture in enumerate(fixture_types):
            print(f"{i+1}. {fixture}")
        print(f"{len(fixture_types)+1}. Custom label")
        print("0. Skip this event")
        
        label_input = input("Enter label number or custom label: ")
        
        if label_input == "0":
            # Skip this event
            print("⏭️ Event skipped.")
            continue
            
        try:
            label_idx = int(label_input) - 1
            if 0 <= label_idx < len(fixture_types):
                label = fixture_types[label_idx]
            elif label_idx == len(fixture_types):
                label = input("Enter custom label: ")
            else:
                print("❌ Invalid selection. Event will be skipped.")
                continue
        except ValueError:
            # User entered a custom label directly
            label = label_input
        
        # Apply the label
        df_manual.loc[event_idx, 'label'] = label
        print(f"✅ Event labeled as '{label}'")
        
        # Ask if user wants to continue
        if i < len(events_to_label) - 1:  # Not the last event
            cont = input("\nContinue labeling? (y/n): ")
            if cont.lower() != 'y':
                break
    
    # Report results
    labeled_count = (df_manual['label'] != '').sum()
    total_count = len(df_manual)
    print(f"\n✅ Manual labeling complete.")
    print(f"📊 Total events labeled: {labeled_count}/{total_count} ({labeled_count/total_count*100:.1f}%)")
    
    # Close any remaining plots
    plt.close('all')
    
    return df_manual


def train_test_split_by_time(df, test_size=0.2):
    """
    Split the dataset into training and testing sets based on time.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing water events with time and label columns
    test_size : float
        Proportion of the dataset to include in the test split
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with a new column 'dataset' indicating 'train' or 'test'
    """
    df_split = df.copy()
    
    # Check that we have time and label columns
    if 'time' not in df_split.columns:
        print("❌ No 'time' column found in the dataset.")
        return df_split
    
    if 'label' not in df_split.columns:
        print("❌ No 'label' column found in the dataset.")
        return df_split
    
    # Make sure time is a datetime
    if not pd.api.types.is_datetime64_any_dtype(df_split['time']):
        try:
            df_split['time'] = pd.to_datetime(df_split['time'])
        except Exception as e:
            print(f"❌ Could not convert time to datetime: {str(e)}")
            return df_split
    
    # Sort by time
    df_split = df_split.sort_values('time').reset_index(drop=True)
    
    # Calculate the split point
    split_idx = int(len(df_split) * (1 - test_size))
    
    # Add dataset column
    df_split['dataset'] = 'train'
    df_split.loc[split_idx:, 'dataset'] = 'test'
    
    # Report results
    train_count = (df_split['dataset'] == 'train').sum()
    test_count = (df_split['dataset'] == 'test').sum()
    
    print(f"\n✅ Dataset split into training and testing sets.")
    print(f"📊 Training set: {train_count} events ({train_count/len(df_split)*100:.1f}%)")
    print(f"📊 Testing set: {test_count} events ({test_count/len(df_split)*100:.1f}%)")
    
    return df_split