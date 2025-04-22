import pandas as pd
import os
import datetime

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
    
    # Load the CSV file
    print(f"⏳ Loading {csv_file}...")
    df = pd.read_csv(csv_file)
    
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
                output_filename = f"{os.path.splitext(csv_file)[0]}_clean.csv"
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