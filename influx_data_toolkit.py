"""
InfluxDB Data Toolkit - Main Application Entry Point

This module serves as the main entry point for the InfluxDB Data Toolkit application.
It provides an interactive command-line interface for exporting, cleaning, and processing 
time series data from InfluxDB, primarily designed for water meter data analysis.

The toolkit integrates several specialized modules:
- Data export from InfluxDB with customizable parameters
- Interactive data cleaning tools
- Timestamp reformatting and timezone conversion
- Water consumption event labeling

Each functionality is implemented in separate modules for better maintainability.
"""

import os
import datetime
import subprocess

# Import functionality from separate modules with updated paths
from tools.exporter import export_data_from_influxdb
from tools.cleaner import clean_data_for_ml
from tools.time_utils import reformat_timestamps

def clear_screen():
    """Clear the terminal screen based on operating system"""
    # For macOS and Linux
    if os.name == 'posix':
        os.system('clear')
    # For Windows
    elif os.name == 'nt':
        os.system('cls')

def display_menu():
    """Display the main menu options"""
    clear_screen()
    print("\n" + "="*60)
    print("🌟 InfluxDB Data Toolkit 🌟".center(60))
    print("="*60)
    print("🔽 Select an option:")
    print("1️⃣ Export data from InfluxDB")
    print("2️⃣ Clean existing CSV data for machine learning")
    print("3️⃣ Reformat timestamps and adjust timezone")
    print("4️⃣ Label water consumption events")
    print("5️⃣ Exit program")
    print("\n💡 Type 'cancel' at any prompt to return to this menu")
    return input("\n🔍 Enter your choice (1-5): ")

def launch_event_labeler():
    """
    Launch the water event labeling tool as a separate process
    """
    print("🚀 Launching water event labeler in a separate process...")
    try:
        # Launch the event labeler script
        print("✅ Event labeler launched. Please complete your labeling tasks.")
        print("⏳ The main toolkit will resume after you exit the labeler.")
        result = os.system("python tools/run_event_labeler.py")
        if result != 0:
            print("❌ Event labeler module is not available.")
        else:
            print("\n✅ Returned from water event labeler.")
    except Exception as e:
        print(f"❌ Failed to launch event labeler: {str(e)}")

def main():
    """Main entry point for the application"""
    # Main program loop
    running = True
    
    while running:
        choice = display_menu()
        
        if choice.lower() == "cancel":
            continue
        
        if choice == "1":
            clear_screen()
            # Export data from InfluxDB
            exported_file = export_data_from_influxdb()
            if exported_file:
                print("\n✅ Export operation completed successfully!")
                
                # Ask if user wants to process the data further
                print("\n🔄 Next steps options:")
                print("1. Clean the data")
                print("2. Reformat timestamps")
                print("3. Label water consumption events")
                print("0. 🔙 Return to main menu")
                next_step = input("\n🔍 What would you like to do next? (0-3): ")
                
                if next_step.lower() == "cancel" or next_step == "0":
                    continue
                elif next_step == "1":
                    clear_screen()
                    clean_data_for_ml(exported_file)
                elif next_step == "2":
                    clear_screen()
                    reformat_timestamps(exported_file)
                elif next_step == "3":
                    clear_screen()
                    launch_event_labeler()
        
        elif choice == "2":
            clear_screen()
            # Clean existing CSV data
            cleaned_file = clean_data_for_ml()
            if cleaned_file:
                label_choice = input("\n🔄 Would you like to label water consumption events in this file? (y/n): ").lower()
                if label_choice == "cancel":
                    continue
                elif label_choice == 'y':
                    clear_screen()
                    launch_event_labeler()
        
        elif choice == "3":
            clear_screen()
            # Reformat timestamps
            reformatted_file = reformat_timestamps()
            if reformatted_file:
                label_choice = input("\n🔄 Would you like to label water consumption events in this file? (y/n): ").lower()
                if label_choice == "cancel":
                    continue
                elif label_choice == 'y':
                    clear_screen()
                    launch_event_labeler()
        
        elif choice == "4":
            clear_screen()
            # Launch Event Labeler
            launch_event_labeler()
        
        elif choice == "5":
            # Exit program
            clear_screen()
            print("👋 Thank you for using InfluxDB Data Toolkit. Goodbye!")
            running = False
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()