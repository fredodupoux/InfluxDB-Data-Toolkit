#!/usr/bin/env python
"""
Machine Learning Preparation Toolkit - InfluxDB Data Toolkit extension

This script provides ML preparation features for time series data analysis, separate
from the main InfluxDB Data Toolkit to avoid dependencies loading time impacting the
main application.
"""

import os
import datetime
import sys

print("\n🔄 Loading ML libraries. This may take a moment...")

# Import the ML preparation functionality
from ml_prep import prepare_data_for_ml

# Import the event labeler functionality
try:
    from event_labeler import main as event_labeler_main
    HAS_EVENT_LABELER = True
except ImportError:
    print("⚠️ Event labeler module not found. Some features will be disabled.")
    HAS_EVENT_LABELER = False

def display_ml_menu():
    """Display the ML toolkit menu options"""
    print("\n" + "="*60)
    print("🧠 Machine Learning Preparation Toolkit 🧠".center(60))
    print("="*60)
    print("🔽 Select an option:")
    print("1️⃣ Prepare data for machine learning")
    print("2️⃣ Label water consumption events")
    print("3️⃣ Exit ML toolkit")
    return input("\n🔍 Enter your choice (1-3): ")

def main():
    """Main entry point for the ML toolkit application"""
    # Show welcome message
    print("\n" + "="*60)
    print("🌟 Welcome to the Machine Learning Preparation Toolkit 🌟".center(60))
    print("="*60)
    print("This tool helps prepare your time series data for machine learning applications.")
    print("You can perform feature engineering, normalization, event labeling, and more.")
    
    # Check for any command line arguments for CSV file
    initial_file = None
    if len(sys.argv) > 1:
        potential_file = sys.argv[1]
        if os.path.exists(potential_file) and potential_file.endswith('.csv'):
            initial_file = potential_file
            print(f"\n📄 Found CSV file from command line: {initial_file}")
    
    # Main program loop
    running = True
    first_run = True
    
    while running:
        # If we have an initial file and this is the first run, auto-start ML preparation
        if initial_file and first_run:
            print("\n🔄 Auto-starting ML preparation with the provided file...")
            prepared_file = prepare_data_for_ml(initial_file)
            if prepared_file:
                print("\n✅ Data preparation for ML completed successfully!")
            input("\n⏸️ Press Enter to continue...")
            # Reset first_run flag and initial_file
            first_run = False
            initial_file = None
            continue
            
        choice = display_ml_menu()
        
        if choice == "1":
            # Prepare data for machine learning
            prepared_file = prepare_data_for_ml()
            if prepared_file:
                print("\n✅ Data preparation for ML completed successfully!")
            input("\n⏸️ Press Enter to continue...")
        
        elif choice == "2":
            # Launch event labeler
            if HAS_EVENT_LABELER:
                print("\n📊 Launching Water Event Labeler...")
                # Save and restore terminal state since the event labeler uses clear_screen()
                event_labeler_main()
            else:
                print("❌ Event labeler module is not available.")
                print("Please make sure the event_labeler directory is in your project.")
                input("\n⏸️ Press Enter to continue...")
        
        elif choice == "3":
            # Exit program
            print("👋 Thank you for using the ML Preparation Toolkit. Goodbye!")
            running = False
        
        else:
            print("❌ Invalid choice. Please try again.")
            input("\n⏸️ Press Enter to continue...")

if __name__ == "__main__":
    main()