import os
import datetime
import subprocess

# Import functionality from separate modules (excluding ML)
from exporter import export_data_from_influxdb
from cleaner import clean_data_for_ml
from time_utils import reformat_timestamps

def display_menu():
    """Display the main menu options"""
    print("\n" + "="*60)
    print("🌟 InfluxDB Data Toolkit 🌟".center(60))
    print("="*60)
    print("🔽 Select an option:")
    print("1️⃣ Export data from InfluxDB")
    print("2️⃣ Clean existing CSV data for machine learning")
    print("3️⃣ Reformat timestamps and adjust timezone")
    print("4️⃣ Launch ML preparation tool (separate process)")
    print("5️⃣ Exit program")
    return input("\n🔍 Enter your choice (1-5): ")

def launch_ml_tool(csv_file=None):
    """
    Launch the ML preparation tool as a separate process
    
    Parameters:
    -----------
    csv_file : str, optional
        Path to a CSV file to pass to the ML toolkit
    """
    print("🚀 Launching ML preparation tool in a separate process...")
    try:
        # Prepare the command with or without a file argument
        command = ["python", "ml_toolkit.py"]
        if csv_file:
            command.append(csv_file)
            print(f"📄 Passing {csv_file} to the ML toolkit")
        
        # Launch the ML tool script as a full separate process
        # Using os.system instead of subprocess.Popen to ensure it completes before continuing
        print("✅ ML tool launched. Please complete your ML preparation tasks.")
        print("⏳ The main toolkit will resume after you exit the ML tool.")
        os.system(" ".join(command))
        print("\n✅ Returned from ML preparation toolkit.")
    except Exception as e:
        print(f"❌ Failed to launch ML tool: {str(e)}")

def main():
    """Main entry point for the application"""
    # Main program loop
    running = True
    
    while running:
        choice = display_menu()
        
        if choice == "1":
            # Export data from InfluxDB
            exported_file = export_data_from_influxdb()
            if exported_file:
                print("\n✅ Export operation completed successfully!")
                
                # Ask if user wants to process the data further
                print("\n🔄 Next steps options:")
                print("1. Clean the data")
                print("2. Reformat timestamps")
                print("3. Launch ML preparation tool")
                print("4. Return to main menu")
                next_step = input("\n🔍 What would you like to do next? (1-4): ")
                
                if next_step == "1":
                    clean_data_for_ml(exported_file)
                elif next_step == "2":
                    reformatted_file = reformat_timestamps(exported_file)
                    if reformatted_file and input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower() == 'y':
                        launch_ml_tool(reformatted_file)
                elif next_step == "3":
                    launch_ml_tool(exported_file)
            
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "2":
            # Clean existing CSV data
            cleaned_file = clean_data_for_ml()
            if cleaned_file and input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower() == 'y':
                launch_ml_tool(cleaned_file)
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "3":
            # Reformat timestamps
            reformatted_file = reformat_timestamps()
            if reformatted_file and input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower() == 'y':
                launch_ml_tool(reformatted_file)
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "4":
            # Launch ML preparation tool
            launch_ml_tool()
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "5":
            # Exit program
            print("👋 Thank you for using InfluxDB Data Toolkit. Goodbye!")
            running = False
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("\n⏸️ Press Enter to continue...")

if __name__ == "__main__":
    main()