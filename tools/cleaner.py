"""
Data Cleaning Module for InfluxDB Data Toolkit

This module provides interactive data cleaning functionality for preparing CSV data files
for machine learning and analysis. It offers capabilities for:

- Loading CSV files from both the root directory and _data directory
- Removing columns that are not needed for analysis
- Filtering data based on column values (equals, less than, greater than)
- Renaming individual columns or multiple columns at once
- Viewing summary statistics and previewing data
- Saving cleaned data with appropriate naming conventions

The module presents an interactive menu-driven interface that guides users through
the cleaning process step by step.
"""

import pandas as pd
import os
import datetime

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

def apply_cleaning_operations(df, operations):
    """
    Apply a list of cleaning operations to a DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to clean.
    operations : list
        A list of dictionaries, each specifying an operation.
        Example: [
            {"action": "remove_column", "column": "col_name"},
            {"action": "filter", "column": "col_name", "operator": ">", "value": 10},
            {"action": "rename_column", "old_name": "old_col", "new_name": "new_col"}
        ]

    Returns:
    --------
    pd.DataFrame
        The cleaned DataFrame.

    Raises:
    -------
    ValueError
        If an invalid operation or parameter is provided.
    KeyError
        If a specified column does not exist.
    """
    df_cleaned = df.copy()
    print(f"Starting cleaning with {len(operations)} operations.") # Server log

    for op in operations:
        action = op.get('action')
        print(f"Applying operation: {action}") # Server log

        if action == 'remove_column':
            col = op.get('column')
            if not col:
                raise ValueError("Missing 'column' for remove_column operation.")
            if col in df_cleaned.columns:
                df_cleaned = df_cleaned.drop(columns=[col])
                print(f"  Removed column: {col}") # Server log
            else:
                raise KeyError(f"Column '{col}' not found for removal.")

        elif action == 'filter':
            col = op.get('column')
            operator = op.get('operator')
            value = op.get('value')
            if not col or not operator or value is None:
                raise ValueError("Missing 'column', 'operator', or 'value' for filter operation.")
            if col not in df_cleaned.columns:
                raise KeyError(f"Column '{col}' not found for filtering.")

            try:
                # Attempt type conversion based on column dtype
                col_dtype = df_cleaned[col].dtype
                if pd.api.types.is_numeric_dtype(col_dtype):
                    filter_value = float(value)
                elif pd.api.types.is_datetime64_any_dtype(col_dtype):
                    filter_value = pd.to_datetime(value)
                # Add more type checks if needed (e.g., boolean)
                else:
                    filter_value = str(value) # Default to string comparison

                original_len = len(df_cleaned)
                if operator == '==':
                    df_cleaned = df_cleaned[df_cleaned[col] == filter_value]
                elif operator == '!=':
                    df_cleaned = df_cleaned[df_cleaned[col] != filter_value]
                elif operator == '>':
                    df_cleaned = df_cleaned[df_cleaned[col] > filter_value]
                elif operator == '<':
                    df_cleaned = df_cleaned[df_cleaned[col] < filter_value]
                elif operator == '>=':
                    df_cleaned = df_cleaned[df_cleaned[col] >= filter_value]
                elif operator == '<=':
                    df_cleaned = df_cleaned[df_cleaned[col] <= filter_value]
                else:
                    raise ValueError(f"Invalid operator '{operator}' for filter operation.")
                print(f"  Filtered column '{col}' {operator} {filter_value}. Rows removed: {original_len - len(df_cleaned)}") # Server log
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value '{value}' or type mismatch for filtering column '{col}': e")

        elif action == 'rename_column':
            old_name = op.get('old_name')
            new_name = op.get('new_name')
            if not old_name or not new_name:
                raise ValueError("Missing 'old_name' or 'new_name' for rename_column operation.")
            if old_name not in df_cleaned.columns:
                raise KeyError(f"Column '{old_name}' not found for renaming.")
            df_cleaned = df_cleaned.rename(columns={old_name: new_name})
            print(f"  Renamed column '{old_name}' to '{new_name}'") # Server log

        else:
            raise ValueError(f"Unknown cleaning action: '{action}'")

    print(f"Finished cleaning. Final shape: {df_cleaned.shape}") # Server log
    return df_cleaned

def clean_data_for_ml(csv_file=None):
    """
    Interactive function to clean and prepare CSV data for a machine learning model.
    Allows users to remove columns and filter values.
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to the CSV file to process. If None, user will be prompted to select a file.
    
    Returns:
    --------
    str
        Path to the cleaned CSV file or None if operation was canceled
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
                print("🔙 Operation cancelled")
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
    
    # Load the CSV file
    clear_screen()
    print(f"⏳ Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    print(f"\n✅ Data loaded. Shape: {df.shape}")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Show first 5 rows immediately after loading
    print("\n👀 Preview of loaded data (first 5 rows):")
    print(df.head().to_string())
    
    # Start the interactive cleaning process
    cleaned = False
    output_filename = None
    
    while not cleaned:
        print("\n🧹 --- Data Cleaning Options ---")
        print("1️⃣ Remove a column")
        print("2️⃣ Filter values in a column")
        print("3️⃣ Rename column(s)")
        print("4️⃣ Show summary statistics")
        print("5️⃣ Show first 5 rows")
        print("6️⃣ Save and exit")
        print("0️⃣ 🔙 Return to main menu")
        
        choice_input = input("\n🔍 Enter your choice (0-6): ")
        if choice_input.lower() == 'cancel' or choice_input == "0":
            return None
            
        try:
            choice = int(choice_input)
            
            if choice == 1:
                clear_screen()
                # Remove a column
                print(f"\n📋 Available columns: {', '.join(df.columns)}")
                col = input("🗑️ Enter the column name to remove : ")
                if col.lower() == 'cancel':
                    continue
                elif col in df.columns:
                    df = df.drop(columns=[col])
                    print(f"✅ Column '{col}' removed. New shape: {df.shape}")
                else:
                    print(f"❌ Column '{col}' not found.")
            
            elif choice == 2:
                clear_screen()
                # Filter values in a column
                print(f"\n📋 Available columns: {', '.join(df.columns)}")
                col = input("🔍 Enter column name to filter : ")
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
                    
                    filter_type = input("⚙️ Filter by (1) Equals, (2) Less than, (3) Greater than : ")
                    if filter_type.lower() == 'cancel':
                        continue
                        
                    filter_val = input("💯 Enter the value : ")
                    if filter_val.lower() == 'cancel':
                        continue
                    
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
                clear_screen()
                # Rename column(s)
                print(f"\n📋 Current columns: {', '.join(df.columns)}")
                
                # Ask user how they want to rename columns
                rename_option = input("🔄 Select an option: (1) Rename a single column, (2) Rename multiple columns : ")
                if rename_option.lower() == 'cancel':
                    continue
                
                if rename_option == '1':
                    # Rename a single column
                    old_col = input("🏷️ Enter the current column name : ")
                    if old_col.lower() == 'cancel':
                        continue
                    
                    if old_col not in df.columns:
                        print(f"❌ Column '{old_col}' not found.")
                        continue
                    
                    new_col = input(f"🔤 Enter new name for column '{old_col}' : ")
                    if new_col.lower() == 'cancel':
                        continue
                    
                    # Rename the column
                    df = df.rename(columns={old_col: new_col})
                    print(f"✅ Column '{old_col}' renamed to '{new_col}'")
                    
                elif rename_option == '2':
                    # Rename multiple columns
                    print("\n📋 Enter pairs of current and new column names (one pair per line)")
                    print("📝 Format: currentName,newName (type 'done' when finished)")
                    
                    rename_dict = {}
                    while True:
                        pair = input("🔄 Column pair (or 'done' to finish): ")
                        if pair.lower() == 'cancel':
                            break
                        elif pair.lower() == 'done':
                            break
                        
                        try:
                            old_col, new_col = pair.split(',')
                            old_col = old_col.strip()
                            new_col = new_col.strip()
                            
                            if old_col not in df.columns:
                                print(f"❌ Column '{old_col}' not found. Skipping.")
                                continue
                                
                            rename_dict[old_col] = new_col
                            print(f"✓ Will rename '{old_col}' to '{new_col}'")
                        except ValueError:
                            print("❌ Invalid format. Please use: currentName,newName")
                    
                    if rename_dict:
                        # Apply all renamings at once
                        df = df.rename(columns=rename_dict)
                        print(f"✅ Renamed {len(rename_dict)} column(s).")
                    else:
                        print("ℹ️ No columns were renamed.")
                
                else:
                    print("❌ Invalid option.")
                
                # Show updated columns
                print(f"\n📋 Updated columns: {', '.join(df.columns)}")
            
            elif choice == 4:
                clear_screen()
                # Show summary statistics
                print("\n📊 Summary Statistics:")
                print(df.describe())
                input("\nPress Enter to continue...")
                
            elif choice == 5:
                clear_screen()
                # Show first 5 rows
                print("\n👀 First 5 rows:")
                print(df.head().to_string())
                input("\nPress Enter to continue...")
                
            elif choice == 6:
                # Save and exit
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                data_dir = "_data"
                # Create the _data directory if it doesn't exist
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                
                # Get basename of the file without path
                base_filename = os.path.basename(csv_file)
                output_filename = os.path.join(data_dir, f"{os.path.splitext(base_filename)[0]}_clean.csv")
                df.to_csv(output_filename, index=False)
                clear_screen()
                print(f"💾 Cleaned data saved to {output_filename}")
                cleaned = True
            
            else:
                print("❌ Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
                clear_screen()
                
        except ValueError:
            print("❌ Please enter a valid number.")
            input("\nPress Enter to continue...")
            clear_screen()
        except Exception as e:
            print(f"⚠️ An error occurred: {str(e)}")
            input("\nPress Enter to continue...")
            clear_screen()
    
    return output_filename