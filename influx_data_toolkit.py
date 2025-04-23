import os
import datetime
import subprocess

# Import functionality from separate modules (excluding ML)
from exporter import export_data_from_influxdb
from cleaner import clean_data_for_ml
from time_utils import reformat_timestamps

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
    print("4️⃣ Launch ML preparation tool (separate process)")
    print("5️⃣ Exit program")
    print("\n💡 Type 'cancel' at any prompt to return to this menu")
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
                print("3. Launch ML preparation tool")
                print("0. 🔙 Return to main menu")
                next_step = input("\n🔍 What would you like to do next? (0-3): ")
                
                if next_step.lower() == "cancel" or next_step == "0":
                    continue
                elif next_step == "1":
                    clear_screen()
                    clean_data_for_ml(exported_file)
                elif next_step == "2":
                    clear_screen()
                    reformatted_file = reformat_timestamps(exported_file)
                    if reformatted_file:
                        ml_choice = input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower()
                        if ml_choice == "cancel":
                            continue
                        elif ml_choice == 'y':
                            clear_screen()
                            launch_ml_tool(reformatted_file)
                elif next_step == "3":
                    clear_screen()
                    launch_ml_tool(exported_file)
        
        elif choice == "2":
            clear_screen()
            # Clean existing CSV data
            cleaned_file = clean_data_for_ml()
            if cleaned_file:
                ml_choice = input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower()
                if ml_choice == "cancel":
                    continue
                elif ml_choice == 'y':
                    clear_screen()
                    launch_ml_tool(cleaned_file)
        
        elif choice == "3":
            clear_screen()
            # Reformat timestamps
            reformatted_file = reformat_timestamps()
            if reformatted_file:
                ml_choice = input("\n🔄 Would you like to launch the ML preparation tool with this file? (y/n): ").lower()
                if ml_choice == "cancel":
                    continue
                elif ml_choice == 'y':
                    clear_screen()
                    launch_ml_tool(reformatted_file)
        
        elif choice == "4":
            clear_screen()
            # Launch ML preparation tool
            launch_ml_tool()
        
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