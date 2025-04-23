"""
Water Event Labeler - Main Entry Point

This module serves as the main entry point for the Water Event Labeler application,
which is designed for analyzing and labeling water consumption events from time series data.

Key functionalities:
- Loading and preprocessing water consumption event data
- Manual labeling of events with customizable fixture types
- Rule-based automatic event labeling
- Visualization of water consumption events
- Train/test splitting for machine learning model development
- Exporting labeled datasets for further analysis

The module provides an interactive command-line interface to guide users through
the event labeling process, with options for both manual and automated approaches.
"""

import os
import datetime
import matplotlib.pyplot as plt

from .utils import clear_screen, display_menu
from .core import load_data, manually_label_events, train_test_split_by_time
from .visualization import visualize_event, visualize_clusters, visualize_time_patterns
from .rules import define_labeling_rules, apply_rules, save_rules, load_rules


def main():
    """
    Main entry point for the water event labeling application.
    """
    # Show welcome message
    clear_screen()
    print("\n" + "="*60)
    print("🌟 Welcome to the Water Event Labeler 🌟".center(60))
    print("="*60)
    print("This tool helps you label water consumption events in your dataset.")
    print("Use it to classify events as shower, faucet, toilet, washing machine, etc.")
    
    # Initialize variables
    df = None
    csv_file = None
    rules = None
    
    # Main program loop
    running = True
    while running:
        choice = display_menu()
        
        if choice == "1":
            # Load dataset
            clear_screen()
            df, csv_file = load_data()
        
        elif choice == "2" and df is not None:
            # Visualize events
            clear_screen()
            print("\n📊 Visualization options:")
            print("1. Cluster events by characteristics")
            print("2. Analyze events by time of day")
            print("3. View specific event")
            
            viz_choice = input("\n🔍 Enter your choice (1-3): ")
            
            if viz_choice == "1":
                # Visualize clusters
                n_clusters = input("Enter number of clusters (default: 6): ")
                try:
                    n_clusters = int(n_clusters)
                except ValueError:
                    n_clusters = 6
                
                visualize_clusters(df, n_clusters=n_clusters)
                input("\n⏸️ Press Enter to continue...")
                plt.close('all')
                
            elif viz_choice == "2":
                # Visualize time patterns
                visualize_time_patterns(df)
                input("\n⏸️ Press Enter to continue...")
                plt.close('all')
                
            elif viz_choice == "3":
                # View specific event
                event_idx = input("Enter event index to view: ")
                try:
                    event_idx = int(event_idx)
                    if 0 <= event_idx < len(df):
                        visualize_event(df, event_idx)
                        input("\n⏸️ Press Enter to continue...")
                        plt.close('all')
                    else:
                        print(f"❌ Invalid index. Must be between 0 and {len(df)-1}.")
                        input("\n⏸️ Press Enter to continue...")
                except ValueError:
                    print("❌ Invalid input. Must be a number.")
                    input("\n⏸️ Press Enter to continue...")
            
            else:
                print("❌ Invalid choice.")
                input("\n⏸️ Press Enter to continue...")
            
        elif choice == "3":
            # Define auto-labeling rules
            clear_screen()
            rules = define_labeling_rules()
            
            # Ask if user wants to save rules
            save_choice = input("Save rules to file? (y/n): ")
            if save_choice.lower() == 'y':
                save_rules(rules)
                
            input("\n⏸️ Press Enter to continue...")
            
        elif choice == "4" and df is not None:
            # Apply auto-labeling rules
            clear_screen()
            
            # If no rules defined, ask if user wants to load from file
            if rules is None:
                load_choice = input("No rules defined. Load from file? (y/n): ")
                if load_choice.lower() == 'y':
                    rules = load_rules()
                else:
                    print("❌ No rules available. Please define rules first.")
                    input("\n⏸️ Press Enter to continue...")
                    continue
            
            # Apply rules if available
            if rules:
                df = apply_rules(df, rules)
                input("\n⏸️ Press Enter to continue...")
            else:
                print("❌ No valid rules available.")
                input("\n⏸️ Press Enter to continue...")
                
        elif choice == "5" and df is not None:
            # Manually label events
            clear_screen()
            df = manually_label_events(df)
            input("\n⏸️ Press Enter to continue...")
            
        elif choice == "6" and df is not None:
            # Create train/test split
            clear_screen()
            test_size = input("Enter test set size (0.0-1.0, default: 0.2): ")
            try:
                test_size = float(test_size)
                if not (0 < test_size < 1):
                    test_size = 0.2
            except ValueError:
                test_size = 0.2
                
            df = train_test_split_by_time(df, test_size=test_size)
            input("\n⏸️ Press Enter to continue...")
            
        elif choice == "7" and df is not None:
            # Save labeled dataset
            clear_screen()
            
            # Check if we have a label column
            if 'label' not in df.columns:
                print("❌ No 'label' column found in the dataset.")
                input("\n⏸️ Press Enter to continue...")
                continue
                
            labeled_count = (df['label'] != '').sum()
            if labeled_count == 0:
                print("⚠️ Warning: No events are labeled yet.")
                proceed = input("Proceed with saving anyway? (y/n): ")
                if proceed.lower() != 'y':
                    continue
            
            # Generate filename
            data_dir = "_data"
            # Create the _data directory if it doesn't exist
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                
            if csv_file:
                # Use just the basename of the file without path
                base_filename = os.path.basename(csv_file)
                base_name = os.path.splitext(base_filename)[0]
                default_filename = os.path.join(data_dir, f"{base_name}_labeled.csv")
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = os.path.join(data_dir, f"water_events_labeled_{timestamp}.csv")
            
            filename = input(f"Enter filename (default: {default_filename}): ")
            if not filename:
                filename = default_filename
            # If the user entered a filename without path, add the _data directory
            elif not os.path.dirname(filename):
                filename = os.path.join(data_dir, filename)
            
            # Add .csv extension if not present
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Save the dataset
            try:
                df.to_csv(filename, index=False)
                print(f"✅ Labeled dataset saved to {filename}")
            except Exception as e:
                print(f"❌ Error saving dataset: {str(e)}")
            
            input("\n⏸️ Press Enter to continue...")
            
        elif choice == "8":
            # Exit program
            print("👋 Thank you for using the Water Event Labeler. Goodbye!")
            running = False
            
        elif df is None and choice in ["2", "4", "5", "6", "7"]:
            print("❌ Please load a dataset first.")
            input("\n⏸️ Press Enter to continue...")
            
        else:
            print("❌ Invalid choice. Please try again.")
            input("\n⏸️ Press Enter to continue...")


if __name__ == "__main__":
    main()