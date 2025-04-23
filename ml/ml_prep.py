import pandas as pd
import os
import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_data_for_ml(csv_file=None):
    """
    Prepare data for machine learning models with feature engineering, 
    normalization, and train-test splitting.
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to the CSV file to process. If None, user will be prompted to select a file.
        
    Returns:
    --------
    str
        Path to the newly created prepared data CSV file
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
    
    print(f"📂 Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    print(f"\n✅ Data loaded. Shape: {df.shape}")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Check if time column exists
    has_time_col = '_time' in df.columns
    if has_time_col:
        # Convert to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['_time']):
            df['_time'] = pd.to_datetime(df['_time'])
    
    # Start the ML preparation process
    preparing = True
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    X = df[numerical_cols].copy()  # Start with numerical columns only
    
    while preparing:
        print("\n🧠 --- ML Data Preparation Options ---")
        print("1️⃣ Generate time-based features")
        print("2️⃣ Handle missing values")
        print("3️⃣ Normalize/scale data")
        print("4️⃣ Detect anomalies")
        print("5️⃣ Create train/test split")
        print("6️⃣ Visualize data")
        print("7️⃣ Save prepared data")
        print("8️⃣ Cancel and return to main menu")
        
        try:
            choice = int(input("\n🔍 Enter your choice: "))
            
            if choice == 1 and has_time_col:
                # Generate time-based features
                print("\n⏱️ Generating time-based features...")
                
                # Extract basic time components
                df['hour'] = df['_time'].dt.hour
                df['day'] = df['_time'].dt.day
                df['day_of_week'] = df['_time'].dt.dayofweek
                df['month'] = df['_time'].dt.month
                df['year'] = df['_time'].dt.year
                df['is_weekend'] = df['_time'].dt.dayofweek >= 5
                df['is_weekend'] = df['is_weekend'].astype(int)
                
                # Create lag features for numerical columns
                lag_options = input("⏱️ Enter lag periods (comma-separated, e.g., '1,3,6'): ")
                if lag_options:
                    lag_periods = [int(x.strip()) for x in lag_options.split(',')]
                    for col in numerical_cols:
                        if col == '_time':
                            continue
                        for lag in lag_periods:
                            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
                
                # Update numerical columns
                numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
                X = df[numerical_cols].copy()
                
                print(f"✅ Time features created. New shape: {df.shape}")
                
            elif choice == 1 and not has_time_col:
                print("❌ No time column found in the dataset.")
                
            elif choice == 2:
                # Handle missing values
                print("\n🔍 Checking for missing values...")
                missing_counts = df.isna().sum()
                columns_with_nulls = missing_counts[missing_counts > 0]
                
                if columns_with_nulls.empty:
                    print("✅ No missing values found!")
                else:
                    print("📊 Columns with missing values:")
                    for col, count in columns_with_nulls.items():
                        print(f"  - {col}: {count} missing values")
                    
                    print("\n🧩 Missing value handling options:")
                    print("1. Drop rows with any missing values")
                    print("2. Fill with mean (numeric columns)")
                    print("3. Fill with median (numeric columns)")
                    print("4. Fill with 0")
                    print("5. Fill with forward fill (use previous value)")
                    
                    fill_option = input("\n🔍 Select option: ")
                    
                    if fill_option == "1":
                        original_shape = df.shape[0]
                        df = df.dropna()
                        print(f"✅ Dropped {original_shape - df.shape[0]} rows with missing values.")
                    elif fill_option == "2":
                        for col in numerical_cols:
                            if col in columns_with_nulls:
                                df[col] = df[col].fillna(df[col].mean())
                        print("✅ Filled numeric missing values with mean.")
                    elif fill_option == "3":
                        for col in numerical_cols:
                            if col in columns_with_nulls:
                                df[col] = df[col].fillna(df[col].median())
                        print("✅ Filled numeric missing values with median.")
                    elif fill_option == "4":
                        for col in columns_with_nulls.index:
                            df[col] = df[col].fillna(0)
                        print("✅ Filled missing values with 0.")
                    elif fill_option == "5":
                        df = df.fillna(method='ffill')
                        print("✅ Filled missing values with previous values.")
                    else:
                        print("❌ Invalid option, no changes made.")
                
                # Update X after handling missing values
                X = df[numerical_cols].copy()
                
            elif choice == 3:
                # Normalize/scale data
                print("\n📏 Data normalization options:")
                print("1. Min-Max Scaling (scale to 0-1 range)")
                print("2. Standard Scaling (mean=0, std=1)")
                print("3. Cancel")
                
                scale_option = input("\n🔍 Select scaling method: ")
                
                if scale_option == "1":
                    # Min-Max scaling
                    scaler = MinMaxScaler()
                    cols_to_scale = [col for col in numerical_cols if col != '_time' and 'is_' not in col]
                    
                    if cols_to_scale:
                        # Create new scaled columns
                        scaled_data = scaler.fit_transform(df[cols_to_scale])
                        
                        # Add new columns with _scaled suffix
                        for i, col in enumerate(cols_to_scale):
                            df[f"{col}_scaled"] = scaled_data[:, i]
                            
                        print(f"✅ Applied Min-Max scaling to {len(cols_to_scale)} columns.")
                    else:
                        print("❌ No suitable numerical columns found for scaling.")
                
                elif scale_option == "2":
                    # Standard scaling
                    scaler = StandardScaler()
                    cols_to_scale = [col for col in numerical_cols if col != '_time' and 'is_' not in col]
                    
                    if cols_to_scale:
                        # Create new scaled columns
                        scaled_data = scaler.fit_transform(df[cols_to_scale])
                        
                        # Add new columns with _scaled suffix
                        for i, col in enumerate(cols_to_scale):
                            df[f"{col}_standardized"] = scaled_data[:, i]
                            
                        print(f"✅ Applied Standard scaling to {len(cols_to_scale)} columns.")
                    else:
                        print("❌ No suitable numerical columns found for scaling.")
                
                elif scale_option == "3":
                    print("⏪ Scaling canceled.")
                    
                else:
                    print("❌ Invalid option, no changes made.")
                
                # Update numerical columns after scaling
                numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
                X = df[numerical_cols].copy()
            
            elif choice == 4:
                # Detect anomalies using Isolation Forest
                print("\n🔍 Anomaly detection with Isolation Forest")
                
                # Select columns for anomaly detection
                print(f"📋 Available numerical columns: {', '.join(numerical_cols)}")
                cols_input = input("🔍 Enter column names to use for anomaly detection (comma-separated, or 'all' for all numeric): ")
                
                if cols_input.lower() == 'all':
                    cols_for_detection = [col for col in numerical_cols if col != '_time' and not col.startswith('is_')]
                else:
                    cols_for_detection = [col.strip() for col in cols_input.split(',') if col.strip() in numerical_cols]
                
                if cols_for_detection:
                    # Ask for contamination parameter
                    contamination = input("🔢 Enter contamination parameter (0.0-0.5, default: 0.1): ") or "0.1"
                    try:
                        contamination = float(contamination)
                        
                        # Train isolation forest
                        print("🧠 Training anomaly detection model...")
                        iso_forest = IsolationForest(contamination=contamination, random_state=42)
                        anomaly_scores = iso_forest.fit_predict(df[cols_for_detection])
                        
                        # Convert predictions to binary anomaly indicator (-1 = anomaly, 1 = normal)
                        df['is_anomaly'] = np.where(anomaly_scores == -1, 1, 0)
                        
                        # Count anomalies
                        anomaly_count = df['is_anomaly'].sum()
                        print(f"✅ Detected {anomaly_count} anomalies ({anomaly_count/len(df)*100:.2f}% of data)")
                        
                        # Ask if user wants to see the anomalies
                        show_anomalies = input("👁️ Show anomalies? (y/n): ")
                        if show_anomalies.lower() == 'y':
                            print("\n⚠️ Anomalies detected:")
                            print(df[df['is_anomaly'] == 1].head(10))
                            
                            if anomaly_count > 10:
                                print(f"(showing first 10 of {anomaly_count} anomalies)")
                    
                    except ValueError:
                        print("❌ Invalid contamination value. Must be a float between 0.0 and 0.5.")
                else:
                    print("❌ No valid columns selected for anomaly detection.")
            
            elif choice == 5:
                # Create train/test split
                print("\n🧩 Create train/test split")
                
                # Ask for test size
                test_size = input("🔢 Enter test size (0.0-1.0, default: 0.2): ") or "0.2"
                try:
                    test_size = float(test_size)
                    
                    # Ask for target variable
                    print(f"\n📋 Available columns: {', '.join(df.columns)}")
                    target_col = input("🎯 Enter target column name (or 'none' for unsupervised): ")
                    
                    # Generate the split
                    if target_col.lower() == 'none' or target_col not in df.columns:
                        # Unsupervised case or invalid column
                        if target_col not in df.columns and target_col.lower() != 'none':
                            print(f"❌ Column '{target_col}' not found. Creating split without target.")
                            
                        # Generate indices for train/test split
                        indices = np.arange(len(df))
                        train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=42)
                        
                        # Create new column indicating the split
                        df['data_split'] = 'train'
                        df.loc[test_idx, 'data_split'] = 'test'
                        
                        # Report split sizes
                        train_count = len(train_idx)
                        test_count = len(test_idx)
                        print(f"✅ Data split created: {train_count} training samples, {test_count} test samples")
                        print("✅ Added 'data_split' column to identify train/test rows")
                        
                    else:
                        # Supervised case
                        X = df.drop(columns=[target_col])
                        y = df[target_col]
                        
                        # Generate indices for train/test split
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=test_size, random_state=42
                        )
                        
                        # Create new column indicating the split
                        df['data_split'] = 'train'
                        df.loc[X_test.index, 'data_split'] = 'test'
                        
                        # Report split sizes
                        print(f"✅ Data split created: {len(X_train)} training samples, {len(X_test)} test samples")
                        print("✅ Added 'data_split' column to identify train/test rows")
                        print(f"🎯 Target variable: {target_col}")
                        
                except ValueError:
                    print("❌ Invalid test size. Must be a float between 0.0 and 1.0.")
            
            elif choice == 6:
                # Visualize data
                visualize_data(df, numerical_cols, has_time_col)
            
            elif choice == 7:
                # Save prepared data
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{os.path.splitext(csv_file)[0]}_ml_ready.csv"
                df.to_csv(output_filename, index=False)
                print(f"💾 ML-ready data saved to {output_filename}")
                
                print("\n📊 Final data shape:", df.shape)
                print("📈 Features engineered:", len(df.columns) - X.shape[1])
                
                # Also save a description of the data preparation steps
                with open(f"{os.path.splitext(output_filename)[0]}_info.txt", 'w') as f:
                    f.write(f"Data preparation info for {output_filename}\n")
                    f.write(f"Original file: {csv_file}\n")
                    f.write(f"Timestamp: {datetime.datetime.now()}\n\n")
                    f.write(f"Original shape: {X.shape}\n")
                    f.write(f"Final shape: {df.shape}\n\n")
                    f.write("Column descriptions:\n")
                    for col in df.columns:
                        f.write(f"- {col}: {df[col].dtype}\n")
                
                preparing = False
                return output_filename
            
            elif choice == 8:
                # Cancel and return to main menu
                print("⏪ Returning to main menu...")
                preparing = False
                return None
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except Exception as e:
            print(f"⚠️ An error occurred: {str(e)}")
    
    return None

def visualize_data(df, numerical_cols, has_time_col):
    """
    Create various data visualizations based on user input.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to visualize
    numerical_cols : list
        List of numerical column names
    has_time_col : bool
        Whether the dataframe has a _time column
    """
    # Visualize data
    print("\n📊 Data Visualization Options:")
    print("1. Time series plot")
    print("2. Correlation heatmap")
    print("3. Feature distributions")
    print("4. Scatter plot matrix")
    print("5. Cancel")
    
    viz_option = input("\n🔍 Select visualization type: ")
    
    if viz_option == "1" and has_time_col:
        # Time series plot
        print(f"\n📋 Available numerical columns: {', '.join(numerical_cols)}")
        cols_to_plot = input("📈 Enter columns to plot (comma-separated, max 5): ")
        
        if cols_to_plot:
            cols_list = [col.strip() for col in cols_to_plot.split(',') if col.strip() in numerical_cols][:5]
            
            if cols_list:
                plt.figure(figsize=(12, 6))
                for col in cols_list:
                    plt.plot(df['_time'], df[col], label=col)
                plt.title('Time Series Plot')
                plt.xlabel('Time')
                plt.ylabel('Value')
                plt.legend()
                plt.tight_layout()
                
                # Save plot to file
                plot_file = f"time_series_plot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(plot_file)
                plt.close()
                print(f"✅ Time series plot saved to {plot_file}")
            else:
                print("❌ No valid columns selected.")
                
    elif viz_option == "1" and not has_time_col:
        print("❌ No time column found for time series plot.")
    
    elif viz_option == "2":
        # Correlation heatmap
        print("\n📊 Generating correlation heatmap...")
        
        # Calculate correlation matrix
        corr_matrix = df.select_dtypes(include=['number']).corr()
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        
        # Save plot to file
        plot_file = f"correlation_heatmap_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_file)
        plt.close()
        print(f"✅ Correlation heatmap saved to {plot_file}")
        
        # Show strongest correlations
        print("\n💪 Top 5 strongest correlations:")
        # Get correlation pairs and sort
        corr_pairs = []
        for col1 in corr_matrix.columns:
            for col2 in corr_matrix.columns:
                if col1 != col2 and col1 < col2:  # Avoid duplicates and self-correlations
                    corr_value = corr_matrix.loc[col1, col2]
                    corr_pairs.append((col1, col2, abs(corr_value), corr_value))
        
        # Sort by absolute correlation and get top 5
        corr_pairs.sort(key=lambda x: x[2], reverse=True)
        for col1, col2, abs_corr, corr in corr_pairs[:5]:
            print(f"  - {col1} ↔️ {col2}: {corr:.3f}")
    
    elif viz_option == "3":
        # Feature distributions
        print(f"\n📋 Available numerical columns: {', '.join(numerical_cols)}")
        cols_to_plot = input("📈 Enter columns to plot distributions (comma-separated, max 4): ")
        
        if cols_to_plot:
            cols_list = [col.strip() for col in cols_to_plot.split(',') if col.strip() in numerical_cols][:4]
            
            if cols_list:
                # Create subplot grid
                fig, axes = plt.subplots(len(cols_list), 2, figsize=(14, 4*len(cols_list)))
                if len(cols_list) == 1:
                    axes = axes.reshape(1, 2)
                    
                # Plot histograms and box plots
                for i, col in enumerate(cols_list):
                    # Histogram with KDE
                    sns.histplot(df[col], kde=True, ax=axes[i, 0])
                    axes[i, 0].set_title(f'Distribution of {col}')
                    
                    # Box plot
                    sns.boxplot(x=df[col], ax=axes[i, 1])
                    axes[i, 1].set_title(f'Box Plot of {col}')
                
                plt.tight_layout()
                
                # Save plot to file
                plot_file = f"feature_distributions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(plot_file)
                plt.close()
                print(f"✅ Feature distributions plot saved to {plot_file}")
            else:
                print("❌ No valid columns selected.")
    
    elif viz_option == "4":
        # Scatter plot matrix
        print(f"\n📋 Available numerical columns: {', '.join(numerical_cols)}")
        cols_to_plot = input("📈 Enter columns for scatter matrix (comma-separated, max 4): ")
        
        if cols_to_plot:
            cols_list = [col.strip() for col in cols_to_plot.split(',') if col.strip() in numerical_cols][:4]
            
            if cols_list:
                # Create scatter matrix
                sns.set(style="ticks")
                plot = sns.pairplot(df[cols_list], diag_kind="kde", markers="o", corner=True)
                plt.suptitle('Scatter Plot Matrix', y=1.02)
                
                # Save plot to file
                plot_file = f"scatter_matrix_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(plot_file)
                plt.close()
                print(f"✅ Scatter plot matrix saved to {plot_file}")
            else:
                print("❌ No valid columns selected.")
    
    elif viz_option == "5":
        print("⏪ Visualization canceled.")
        
    else:
        print("❌ Invalid option selected.")